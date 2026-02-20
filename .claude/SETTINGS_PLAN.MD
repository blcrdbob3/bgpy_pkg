# Settings Class Implementation Plan

## Context

BGPy currently uses a deep, wide inheritance tree (60+ Policy subclasses) to vary behavior.
Every combination of features (e.g. ROV + EnforceFirstAS + Full RIB) requires its own subclass.
This makes the codebase hard to extend compositionally and hard for new users to discover what
is available.

The `Settings` class is a first step toward composition over inheritance. It provides a stable,
discoverable API for looking up Policy and Scenario classes by name, using the existing
auto-registration registries (populated via `__init_subclass__` on Policy) without requiring
direct imports of every subclass. Old code remains unchanged; `Settings` is a new alternative.

---

## Approach: Registry/Lookup Class

`Settings` is a pure-static class with no instances. It delegates to:
- `Policy.name_to_subclass_dict` (already exists, keyed by `Policy.name` attribute)
- A module-level dict built at import time by walking `Scenario.__subclasses__()` recursively
  (Scenario has no built-in name registry; the dict is keyed by `cls.__name__`)

New exceptions (`PolicyNotFoundError`, `ScenarioNotFoundError`) live in `bgpy/settings.py`
itself since we cannot modify the existing `bgpy/shared/exceptions.py`.

---

## Files Created

| File | Purpose |
|------|---------|
| `bgpy/settings.py` | Main Settings class with registry lookup API |
| `bgpy/tests/settings_tests/__init__.py` | Package marker |
| `bgpy/tests/settings_tests/test_settings.py` | 24 unit tests (all passing) |

---

## Key Design Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| File location | `bgpy/settings.py` | Top-level, spans both sub-packages, most discoverable |
| Class variables for policies | None | Defeats registry purpose; naming collision with imports |
| Exceptions location | `bgpy/settings.py` | Cannot modify existing `bgpy/shared/exceptions.py` |
| Exception base | `KeyError` | Standard Python idiom for lookup failures |
| Scenario registry key | `cls.__name__` | Scenario has no `.name` attribute |
| Scenario registry build | BFS of `__subclasses__()` at import time | Simple, additive, no changes to `scenario.py` |
| User-defined scenarios after import | NOT auto-included | Known limitation, documented in module docstring |
| Export from `__init__.py` | Not done | Cannot modify existing files |

---

## Usage

```python
from bgpy.settings import Settings

# Look up policies by name (Policy.name attribute)
PolicyCls = Settings.get_policy("ROV")
PolicyCls = Settings.get_policy("ASPA")

# Discover all available policy names
print(Settings.get_policy_names())  # sorted tuple of 60+ names

# Look up scenarios by class name
ScenarioCls = Settings.get_scenario("SubprefixHijack")

# Discover all available scenario names
print(Settings.get_scenario_names())

# Get full registry dicts (copies)
policy_dict = Settings.policy_registry()
scenario_dict = Settings.scenario_registry()
```

---

## Implementation Notes

- `bgpy/__init__.py` already imports `simulation_engine` and `simulation_framework`,
  so all registries are fully populated before `settings.py` module-level code runs.
- Attacker policies that masquerade as legitimate policies (e.g., `ShortestPathPrefixASPAAttacker`
  uses `name = "BGP"`) will overwrite the legitimate class in the registry. This is existing
  codebase behavior and intentional for attack simulation.

---

## Verification

```bash
.venv/bin/pytest bgpy/tests/settings_tests/ -v   # 24 tests, all pass
.venv/bin/ruff check bgpy/settings.py bgpy/tests/settings_tests/
```
