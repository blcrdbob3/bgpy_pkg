# BGPsimulator Settings Implementation Analysis

Source: https://github.com/jfuruness/bgpsimulator (fork of bgpy_pkg for the BGPSimulator.com web app)

---

## Overview

BGPsimulator replaces bgpy_pkg's OOP inheritance model (60+ Policy subclasses) with a **flat boolean settings array** approach. Every AS has a single `Policy` instance holding a `tuple[bool, ...]` where each index corresponds to a named setting. Policy logic is monolithic — one `Policy` class with explicit `if settings[X]` guards — rather than composed via class hierarchies.

---

## The `Settings` Enum

**File:** `bgpsimulator/shared/enums.py`

```python
class Settings(IntEnum):
    ANNOUNCE_THEN_WITHDRAW = 0
    AS_PATH_EDGE_FILTER = 1
    ASPA = 2
    ASPA_W_N = 3          # ASPAwN (ASPA with Neighbors)
    ASPAPP = 4            # ASPA++
    ASRA = 5
    BGPSEC = 6
    BGP_FULL = 7          # Full RIB mode (withdrawals, RIBs In/Out)
    BGP_I_SEC = 8
    BGP_I_SEC_TRANSITIVE = 9
    ENFORCE_FIRST_AS = 10
    FIRST_ASN_STRIPPING_PREFIX_HIJACK_CUSTOMERS = 11  # internal/attack use
    LEAKER = 12
    NEVER_PROPAGATE_WITHDRAWALS = 13
    NEVER_WITHDRAW = 14
    ONLY_TO_CUSTOMERS = 15
    ORIGIN_PREFIX_HIJACK_CUSTOMERS = 16               # internal/attack use
    PATH_END = 17
    PEERLOCK_LITE = 18
    PEER_ROV = 19
    PROVIDER_CONE_ID = 20
    ROST = 21
    ROV = 22
    ROVPP_V1_LITE = 23
    ROVPP_V2I_LITE = 24
    ROVPP_V2_LITE = 25
```

The integer value is the **index** into the settings tuple. `len(Settings)` == number of entries == length of every settings tuple.

---

## The `Policy` Class — Settings Storage

**File:** `bgpsimulator/simulation_engine/policy/policy.py`

```python
class Policy:
    __slots__ = ("local_rib", "recv_q", "settings", "as_", "adj_ribs_in", "adj_ribs_out")

    def __init__(self, as_, settings=None, ...):
        if settings:
            self.settings: tuple[bool, ...] = settings
        else:
            self.settings = tuple([False for _ in Settings])  # all disabled by default
```

- `settings` is a **fixed-length tuple of booleans**, one per `Settings` member
- Default state: every flag `False` (plain BGP behavior)
- Accessed everywhere as `self.settings[Settings.ROV]`, `self.settings[Settings.ASPA]`, etc.
- Per-AS: each `AS` object has its own `Policy` instance with its own `settings` tuple

---

## Policy Extensions — Stateless Mixin Classes

**Directory:** `bgpsimulator/simulation_engine/policy/policy_extensions/`

Each setting maps to a standalone class with **only `@staticmethod` methods**. No `__init__`, no instance state. They receive the calling `Policy` as first argument (essentially module-level functions in a namespace).

### Extension interface patterns

**Validation extension** (`valid_ann`):
```python
class ROV:
    @staticmethod
    def valid_ann(policy: "Policy", ann: "Ann", from_rel: Relationships) -> bool:
        (roa_validity, _) = policy.route_validator.get_roa_outcome(ann.prefix, ann.origin)
        return not ROAValidity.is_invalid(roa_validity)
```

**Propagation modifier** (`get_policy_propagate_vals` → `PolicyPropagateInfo`):
```python
class NeverPropagateWithdrawals:
    @staticmethod
    def get_policy_propagate_vals(policy, neighbor_as, ann, propagate_to, send_rels) -> PolicyPropagateInfo:
        if ann.withdraw:
            return PolicyPropagateInfo(policy_propagate_bool=True, ann=ann, send_ann_bool=False)
        else:
            return PolicyPropagateInfo(policy_propagate_bool=False, ann=ann, send_ann_bool=True)
```

`PolicyPropagateInfo` has three fields:
- `policy_propagate_bool`: whether this extension handled propagation (if True, Policy won't do default send)
- `ann`: the (possibly modified) announcement to use
- `send_ann_bool`: whether to actually send the announcement at all (False = drop silently)

**Announcement processor** (`process_ann`):
```python
class BGPiSecTransitive:
    @staticmethod
    def process_ann(policy, ann, from_rel) -> Ann:
        # Returns modified announcement (e.g. adds security fields)
        ...
```

**Lifecycle hook** (`pre_propagation_hook`):
```python
class Leaker:
    @staticmethod
    def pre_propagation_hook(policy, propagation_round, scenario):
        if propagation_round == 1:
            # Modify local_rib to simulate route leaks
            ...
```

---

## Central `Policy.valid_ann()` — Explicit Flag Checks

All validation guards are in one method with explicit `if settings[X]` checks:

```python
def valid_ann(self, ann, from_rel) -> bool:
    settings = self.settings

    if not BGP.valid_ann(self, ann, from_rel):   # always checked (loop prevention)
        return False
    # ASPA superset logic: ASRA > ASPAwN > ASPA
    if settings[Settings.ASPA] and not settings[Settings.ASRA] and not settings[Settings.ASPA_W_N]:
        if not ASPA.valid_ann(self, ann, from_rel):
            return False
    if settings[Settings.ASPA_W_N] and not settings[Settings.ASRA]:
        if not ASPAwN.valid_ann(self, ann, from_rel):
            return False
    if settings[Settings.ASRA]:
        if not ASRA.valid_ann(self, ann, from_rel):
            return False
    # ROV family: all use ROV.valid_ann (ROV++V1/V2/V2i are supersets that add blackholing)
    if settings[Settings.ROV] or settings[Settings.ROVPP_V1_LITE] or settings[Settings.ROVPP_V2_LITE] or settings[Settings.ROVPP_V2I_LITE]:
        if not ROV.valid_ann(self, ann, from_rel):
            return False
    # ... more checks for PEER_ROV, PATH_END, PEERLOCK_LITE, BGP_I_SEC, PROVIDER_CONE_ID, ASPAPP, etc.
    return True
```

Superset/priority relationships are handled by guard conditions directly in code — no MRO magic.

---

## Per-AS Settings — Storage on `AS`

**File:** `bgpsimulator/as_graphs/as_graph/base_as.py`

```python
class AS:
    def __init__(self, asn, ..., policy_json=None):
        self.policy: Policy = (
            Policy.from_json(policy_json, self) if policy_json else Policy(self)
        )
```

- Each `AS` owns exactly one `Policy` instance
- Settings live on `self.policy.settings`
- To configure an AS with specific settings, construct a `settings` tuple with the appropriate booleans set to `True`, then pass as `policy_json` or set directly after construction

---

## JSON Serialization

`Policy.to_json()` serializes the settings tuple as a plain list of booleans:

```python
def to_json(self) -> dict:
    return {
        "local_rib": {...},
        "settings": list(self.settings),   # [False, False, True, False, ...]
        "adj_ribs_in": ...,
        "adj_ribs_out": ...,
    }

@classmethod
def from_json(cls, json_obj, as_):
    return cls(
        as_=as_,
        settings=tuple(json_obj.get("settings", [])),
        ...
    )
```

The full graph serializes to JSON via `ASGraph.to_json()` → `AS.to_json()` → `Policy.to_json()`. This is the web UI's persistence mechanism: the frontend sends/receives a JSON blob that encodes the entire topology including per-AS settings.

---

## Engine Entry Point — `EngineRunConfig` + `EngineRunner`

**Files:** `bgpsimulator/engine_runner/`

The web UI constructs an `EngineRunConfig` (scenario + pre-configured `ASGraph`) and passes it to `EngineRunner.run()`. Settings flow is:

1. User clicks AS in web UI → checks/unchecks setting boxes
2. Frontend updates the `settings` list in its JSON state
3. On "Run", frontend POSTs the full `EngineRunConfig` JSON to backend
4. Backend calls `EngineRunConfig.from_json()` which calls `ASGraph.from_json()` → `AS.from_json()` → `Policy.from_json()` with the settings tuple
5. `EngineRunner.run()` propagates announcements; each AS's `Policy.valid_ann()` gates routing decisions using `self.settings[Settings.X]`

---

## Key Design Differences vs bgpy_pkg

| Aspect | bgpy_pkg | bgpsimulator |
|---|---|---|
| Policy model | 60+ subclasses via inheritance | Single `Policy` class + 25 boolean flags |
| Settings storage | Class identity (e.g. `ROV()`) | `tuple[bool]` on each `Policy` instance |
| Per-AS config | All ASes share a `BasePolicyCls` | Each AS has independent settings |
| Extension mechanism | `super()._valid_ann()` chain | Explicit `if settings[X]` guards in monolith |
| Priority/supersetting | MRO order | Explicit conditions in `valid_ann()` |
| Serialization | YAML via `YamlAble` | JSON tuple of booleans |
| Discovery | `Policy.name_to_subclass_dict` | `Settings` enum members |
| Composition | `Settings.compose_policy()` (dynamic `type()`) | Set multiple flags simultaneously |

---

## Notable Observations for Settings Revamp

1. **Boolean tuple indexed by IntEnum** is simple, fast, and JSON-trivial. Iteration over `Settings` (e.g. `for _ in Settings`) gives the correct tuple length.

2. **Superset semantics are explicit**: ASRA supersedes ASPAwN supersedes ASPA. BGP-iSec Transitive supersedes BGPSec. ROV++V2i supersedes V2 supersedes V1 (see `policy_propagate()` elif chains). These are not inferred from class hierarchy — they're written as guard conditions.

3. **`BGP_FULL` is a setting flag** (not a separate class), enabling/disabling RIBs In, RIBs Out, and withdrawal processing throughout the policy methods.

4. **Two internal/attack-only settings** (`FIRST_ASN_STRIPPING_PREFIX_HIJACK_CUSTOMERS`, `ORIGIN_PREFIX_HIJACK_CUSTOMERS`) exist for the web simulator's built-in attack scenarios. Not exposed as user-facing checkboxes.

5. **`Leaker` and `AnnounceThenWithdraw`** are implemented as per-AS settings (not scenario-level), because the web UI lets users mark individual ASes as leakers/attackers rather than configuring a scenario class.

6. **`NEVER_WITHDRAW` is checked in `process_incoming_anns()`** (suppresses processing withdrawals from neighbors), while **`NEVER_PROPAGATE_WITHDRAWALS`** is a propagation modifier (suppresses sending withdrawals to neighbors). These are distinct behaviors.
