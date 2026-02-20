# Settings Class: Phase 2 Design

## What the Current Settings Class Actually Solves

The current `Settings` class is a thin registry wrapper. It solves the **discovery problem**:
users can enumerate what policies and scenarios exist without importing every individual class.
It does NOT solve the **composition problem**: you still need a pre-existing, explicitly defined
subclass for every combination of features you want.

This document explores how to extend `Settings` to address composition more directly.

---

## Root Cause Analysis: What Makes the Tree So Wide

The 60+ policy subclasses come from two orthogonal axes that are currently conflated:

**Axis 1: Security feature (what validation logic to apply)**
- BGP, ROV, ASPA, ASRA, EnforceFirstAS, EdgeFilter, BGPSec, PeerlockLite, ...
- Each policy overrides `_valid_ann()` and (rarely) `_policy_propagate()`

**Axis 2: RIB depth (how much state to track)**
- Lite: only `local_rib` + `recv_q`, no withdrawal support
- Full: adds `ribs_in`, `ribs_out`, and explicit withdrawal handling

Every Lite policy has a corresponding Full variant created with an empty class body:
```python
class ROVFull(ROV, BGPFull): pass
class ASPAFull(ASPA, ROVFull): pass
```
This is purely mechanical duplication driven by the two-axis problem.

A third, smaller source of duplication is **feature combinations**: `ROVEdgeFilter`,
`ROVEnforceFirstAS`, and `BGPiSecTransitiveOnlyToCustomers` exist as explicit subclasses
because there was no other way to combine two features.

---

## Key Technical Finding: Cooperative `_valid_ann()` Chain

Before proposing solutions, the critical structural property to understand:

**Every policy that overrides `_valid_ann()` calls `super()._valid_ann()` in at least one
code path.** The invariant pattern is:

```python
def _valid_ann(self, ann, from_rel):
    if self._my_condition_fails(ann, from_rel):
        return False
    return super()._valid_ann(ann, from_rel)  # always delegated
```

This means the validation chain is fully cooperative. Dynamically composing two policies
via Python's `type()` will produce correct behavior: both policies' checks run, in MRO order.

**What is NOT cooperative:** `BGPFull.process_incoming_anns()` completely replaces the
base BGP implementation and does not call `super()`. This is intentional (the two
implementations are architecturally incompatible, not just additive). This means Full semantics
must be handled separately from feature composition.

---

## Proposed Extensions

### Extension 1: `full_rib` Parameter on `get_policy()`

The lowest-effort improvement. Add a `full_rib` keyword argument to `get_policy()` that
returns the Full variant when available:

```python
Settings.get_policy("ROV")                  # returns ROV
Settings.get_policy("ROV", full_rib=True)   # returns ROVFull
Settings.get_policy("BGP", full_rib=True)   # returns BGPFull
```

**Implementation (additive, no existing file changes):**

Build a `_lite_to_full_map` at import time by inspecting the registry:

```python
_FULL_SUFFIX = " Full"

def _build_lite_to_full_map() -> dict[str, str]:
    """Map Lite policy names to their Full variant names where a pair exists."""
    names = set(Policy.name_to_subclass_dict.keys())
    result = {}
    for name in names:
        full_name = name + _FULL_SUFFIX
        if full_name in names:
            result[name] = full_name
    return result

_lite_to_full_map = _build_lite_to_full_map()
```

Then in `get_policy()`:
```python
@staticmethod
def get_policy(name: str, *, full_rib: bool = False) -> type[Policy]:
    if full_rib:
        full_name = _lite_to_full_map.get(name)
        if full_name is None:
            # No Full variant exists; return what was asked for
            # (BGPFullIgnoreInvalid, BGPFullSuppressWithdrawals, etc. are
            # already Full-rib classes with no separate Lite counterpart)
            pass
        else:
            name = full_name
    try:
        return Policy.name_to_subclass_dict[name]
    except KeyError:
        ...
```

**Trade-offs:**
- Zero risk: purely additive, backward compatible
- Eliminates the need to know the " Full" naming convention
- Does not reduce the number of subclasses, just hides their names
- Name matching relies on the " Full" suffix convention being consistent

---

### Extension 2: `compose_policy()` Dynamic Factory

A method that accepts multiple policy names and returns a dynamically composed class.
Relies on the cooperative `super()` chain described above.

```python
Settings.compose_policy(["ROV", "EnforceFirstAS"])
Settings.compose_policy(["ASPA", "EdgeFilter"], full_rib=True)
```

**Implementation sketch (additive, no existing file changes):**

```python
_compose_cache: dict[tuple[str, ...], type[Policy]] = {}

@staticmethod
def compose_policy(
    names: list[str] | tuple[str, ...],
    *,
    full_rib: bool = False,
) -> type[Policy]:
    """Return a Policy class that combines all named policies.

    The returned class applies all validation checks in the order given,
    each delegating to the next via super(). The policies must all be
    cooperative (call super()._valid_ann()), which is true of all built-in
    policies.

    If full_rib=True, BGPFull is mixed in to add RIBs In, RIBs Out, and
    withdrawal support. BGPFull is appended at the end of the MRO so that
    the Full semantics apply without interfering with validation order.

    Results are cached; the same combination always returns the same class.

    Args:
        names: Policy .name attributes, in validation-priority order.
        full_rib: Whether to include BGPFull semantics.

    Raises:
        PolicyNotFoundError: If any name is not in the registry.
        TypeError: If the resulting MRO is invalid (conflicting bases).
    """
    key = (tuple(names), full_rib)
    if key in _compose_cache:
        return _compose_cache[key]

    bases: list[type[Policy]] = [Settings.get_policy(n) for n in names]
    if full_rib:
        bgp_full = Settings.get_policy("BGP Full")
        if bgp_full not in bases:
            bases.append(bgp_full)

    composed_name = "_".join(names) + ("_Full" if full_rib else "")
    try:
        cls = type(composed_name, tuple(bases), {})
    except TypeError as exc:
        raise TypeError(
            f"Cannot compose policies {names!r}: invalid MRO. "
            f"Original error: {exc}"
        ) from exc

    _compose_cache[key] = cls
    return cls
```

**MRO behavior for common combinations:**

| `compose_policy(["ROV", "EnforceFirstAS"])` | MRO |
|---------------------------------------------|-----|
| ROV checks ROA, calls super | EnforceFirstAS checks first AS, calls super | BGP checks loop prevention |

| `compose_policy(["ASPA", "OnlyToCustomers"])` | MRO |
|-----------------------------------------------|-----|
| ASPA checks AS path, calls super | OnlyToCustomers checks OTC attribute, calls super | BGP |

**Known limits:**
- Policies with non-cooperative methods (anything that completely replaces a base method
  without calling `super()`) will not compose correctly for that method.
  For built-in policies this only affects `process_incoming_anns()`, which is why
  `full_rib` is a separate flag rather than just another name in the list.
- Attacker policies (e.g., `ShortestPathPrefixASPAAttacker`) should generally not be
  composed. They are designed for simulation roles, not stacking.
- The composed class is not added to `name_to_subclass_dict` and will not appear in
  `get_policy_names()`. This is intentional: composed classes are runtime artifacts.

---

### Extension 3: `PolicyConfig` Dataclass

A serializable, hashable specification for a policy configuration. Useful for experiment
configuration files (YAML, JSON) and reproducible logging.

```python
from bgpy.settings import PolicyConfig, Settings

cfg = PolicyConfig(features=("ROV", "EnforceFirstAS"), full_rib=True)
PolicyCls = Settings.resolve_policy(cfg)
```

**Implementation (additive, no existing file changes):**

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class PolicyConfig:
    """Serializable specification for a Policy class selection or composition.

    Use Settings.resolve_policy(config) to convert a PolicyConfig to a
    concrete Policy subclass.

    Attributes:
        features: Tuple of Policy .name attributes to compose, in order.
            A single-element tuple returns that policy directly.
        full_rib: Whether to include BGPFull (RIBs In, RIBs Out, withdrawals).
    """
    features: tuple[str, ...] = ("BGP",)
    full_rib: bool = False

    def __post_init__(self) -> None:
        if not self.features:
            raise ValueError("features must contain at least one policy name")
```

And on `Settings`:

```python
@staticmethod
def resolve_policy(config: "PolicyConfig") -> type[Policy]:
    """Return the Policy class described by config.

    For single-feature configs, delegates to get_policy(). For multi-feature
    configs, delegates to compose_policy(). Results are cached.
    """
    if len(config.features) == 1:
        return Settings.get_policy(config.features[0], full_rib=config.full_rib)
    return Settings.compose_policy(config.features, full_rib=config.full_rib)
```

**Benefit:** `PolicyConfig` can be serialized and deserialized from YAML/JSON without
custom pickle support, making experiment configurations reproducible and human-readable:

```yaml
scenario_config:
  policy:
    features: ["ASPA", "EnforceFirstAS"]
    full_rib: true
```

---

## What Would Require Modifying Existing Files

The extensions above are all purely additive. The following improvements would require
touching existing files and are included here for completeness, not as immediate actions.

### Exporting from `bgpy/__init__.py`

`Settings`, `PolicyConfig`, `PolicyNotFoundError`, and `ScenarioNotFoundError` currently
require `from bgpy.settings import ...`. Adding them to `bgpy/__init__.py` would make them
first-class exports on par with `Policy`, `ROV`, etc. This requires editing `bgpy/__init__.py`.

### Live Scenario Registry

The scenario registry is built once at import time via `Scenario.__subclasses__()`. User-defined
`Scenario` subclasses defined after import do not appear. The clean fix is to add
`__init_subclass__` to `Scenario` (analogous to what `Policy` already does). This requires
editing `bgpy/simulation_framework/scenarios/scenario.py`.

### Eliminating Empty Full Variants

The 22 empty-body Full classes (`ROVFull`, `ASPAFull`, etc.) could be auto-generated and
eliminated as explicit source files. They could be replaced with:

```python
# In bgpy/simulation_engine/policies/__init__.py (or a new file)
import bgpy.simulation_engine  # ensure all Lite classes are registered

def _make_full(lite_cls, name_suffix=" Full"):
    full_cls = type(
        lite_cls.__name__ + "Full",
        (lite_cls, BGPFull),
        {"name": lite_cls.name + name_suffix},
    )
    return full_cls

ROVFull = _make_full(ROV)
ASPAFull = _make_full(ASPA)
# ...
```

This would require removing the existing empty class files (or deprecating them as re-exports)
and updating `bgpy/simulation_engine/__init__.py`. It is a significant refactor with high
backward-compatibility risk. The existing empty classes should be kept as re-exports if this
is ever done.

---

## Recommended Phasing

### Phase 1: Purely Additive (current session)

All additions go in `bgpy/settings.py` and `bgpy/tests/settings_tests/`:

1. `_build_lite_to_full_map()` helper and `_lite_to_full_map` module variable
2. `full_rib` parameter on `Settings.get_policy()`
3. `_compose_cache` module variable
4. `Settings.compose_policy()` method
5. `PolicyConfig` frozen dataclass
6. `Settings.resolve_policy()` method
7. New test coverage for all added methods

No existing files are modified.

### Phase 2: Minor File Touches (if approved)

1. Add `Settings`, `PolicyConfig`, error classes to `bgpy/__init__.py`
2. Add `__init_subclass__` to `Scenario` for a live registry

### Phase 3: Architectural (if scope permits)

1. Auto-generate Full variants programmatically
2. Reduce the explicit subclass list to only policies with non-trivial logic
3. Document the formal mixin protocol for third-party policy authors

---

## Risk Matrix

| Change | Risk | Backward Compatible |
|--------|------|---------------------|
| `full_rib` parameter | Very low | Yes (new keyword arg) |
| `compose_policy()` | Low | Yes (new method) |
| `PolicyConfig` + `resolve_policy()` | Low | Yes (new types) |
| Export from `__init__.py` | Low | Yes (additive) |
| Live `Scenario` registry | Medium | Yes (registry grows, not shrinks) |
| Auto-generate Full variants | High | Only if originals kept as re-exports |

---

## Motivating Example: Policy Variations Without New Subclasses

The central use case for `compose_policy()` is creating a **variation** of an existing policy
by combining features, without writing a new subclass.

**Before (explicit subclass required):**

```python
# Want BGP with both ROV and OnlyToCustomers active simultaneously.
# Must write and register a new file with an empty class body:

from bgpy.simulation_engine import ROV, OnlyToCustomers

class ROVWithOTC(ROV, OnlyToCustomers):
    name: str = "ROV With OTC"
    # No logic - purely wiring two existing policies together

# And for Full RIB support, yet another class:
class ROVWithOTCFull(ROVWithOTC, BGPFull):
    name: str = "ROV With OTC Full"

# Then import and use:
from my_policies import ROVWithOTC
ScenarioConfig(ScenarioCls=SubprefixHijack, AdoptPolicyCls=ROVWithOTC)
```

**After (compose at runtime):**

```python
from bgpy.settings import Settings

MyPolicy = Settings.compose_policy(["ROV", "OnlyToCustomers"])
MyPolicyFull = Settings.compose_policy(["ROV", "OnlyToCustomers"], full_rib=True)

ScenarioConfig(ScenarioCls=SubprefixHijack, AdoptPolicyCls=MyPolicy)
ScenarioConfig(ScenarioCls=SubprefixHijack, AdoptPolicyCls=MyPolicyFull)
```

No new files, no new class definitions, no name registration. Both policies' validation checks
run in MRO order because `_valid_ann()` is fully cooperative across all built-in policies.

Note: `compose_policy()` only combines existing policies. Genuinely new validation logic
(new conditions, new data structures) still requires writing a subclass. The tool eliminates
mechanical empty-body combination classes, not authored logic.

---

## Example: What Phase 1 Enables (Full API)

```python
from bgpy.settings import Settings, PolicyConfig

# Discoverable Full RIB variant without knowing the " Full" naming convention:
ROVFull = Settings.get_policy("ROV", full_rib=True)

# Runtime composition without a dedicated subclass:
MyPolicy = Settings.compose_policy(["ROV", "EnforceFirstAS"], full_rib=True)

# Config-driven experiment setup (serializable, YAML-friendly):
cfg = PolicyConfig(features=("ASPA", "OnlyToCustomers"), full_rib=False)
PolicyCls = Settings.resolve_policy(cfg)
sim = Simulation(
    scenario_configs=[ScenarioConfig(ScenarioCls=SubprefixHijack, AdoptPolicyCls=PolicyCls)]
)
```
