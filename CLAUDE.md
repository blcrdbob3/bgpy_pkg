# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Is

BGPy is a Python BGP (Border Gateway Protocol) security simulator for academic research. It simulates internet topology and BGP routing policies to test attack/defense scenarios (hijacks, ROV, ASPA, BGPsec, etc.) at scale, using real CAIDA topology data.

## Commands

```bash
# Testing
pytest bgpy                          # Run all tests
pytest bgpy -n auto                  # Parallel (recommended)
pytest bgpy -m engine                # Only engine tests
pytest bgpy --overwrite              # Update ground truth outputs
pytest bgpy --view                   # Show diagram PDF after tests

# Linting & type checking
ruff check bgpy
ruff format bgpy
mypy bgpy
tox                                  # All checks across Python versions

# Install
pip install -e ".[test]"
```

Running a single test: `pytest bgpy/tests/engine_tests/test_engine.py::TestEngine::test_engine[conf0]`

## Architecture

The stack has three main layers, each depending on the one below it:

**1. `as_graphs/`** - Network topology (the internet graph)
- `ASGraph`: Nodes are `AS` objects linked by customer-provider and peer relationships
- `CAIDAASGraph`: Fetches/caches real CAIDA topology data
- AS nodes hold a `Policy` instance that makes routing decisions

**2. `simulation_engine/`** - BGP protocol simulation
- `Announcement` (frozen dataclass with `__slots__`): The core BGP message unit
- `Policy` (ABC): Base class for all routing policies. Maintains a class registry via `__init_subclass__`. Key methods: `receive_ann()`, `process_incoming_anns()`, `propagate_to_*()`
- 60+ policy implementations in `policies/`: BGP, ROV, ASPA, ASRA, BGPSec, BGPiSec, and variants. Most have "Full" (complete RIB) and "Lite" (minimal state) versions
- `SimulationEngine`: Runs announcement propagation rounds by relationship type

**3. `simulation_framework/`** - Attack/defense scenario orchestration
- `Scenario` (ABC): Defines attackers, victims, adopters, announcements, and ROAs for one trial
- `ScenarioConfig`: Composes `ScenarioCls`, `AdoptPolicyCls`, and `BasePolicyCls`
- `Simulation`: Runs N trials across adoption percentages using `multiprocessing.Pool`, then graphs results

## Key Design Patterns

**Class registry**: All `Policy` and `Scenario` subclasses auto-register via `__init_subclass__`, enabling dynamic instantiation and YAML serialization (`YamlAble`).

**Attached functions**: `ASGraph` organizes complex algorithms as module-level functions assigned as class attributes (e.g., `_gen_graph = _gen_graph`). This keeps logic organized without a single giant file.

**Frozen dataclass announcements**: `Announcement` uses `@dataclass(slots=True, frozen=True)` for immutability and performance. Use `.copy()` to create modified copies.

**Weakref proxies**: `AS` objects use `weakref.proxy()` for back-references to `ASGraph` and `Policy.as_` to prevent GC cycles.

**Engine tests use ground truth**: Tests in `engine_tests/` compare against saved outputs in `engine_test_outputs/`. Use `--overwrite` to regenerate when intentionally changing behavior.

## Settings API (`bgpy/settings.py`)

`Settings` is a registry/lookup class introduced on the `settings` branch as an alternative to importing policy and scenario classes directly.

```python
from bgpy.settings import Settings, PolicyConfig

# Look up by name
PolicyCls = Settings.get_policy("ROV")               # Lite variant
PolicyCls = Settings.get_policy("ROV", full_rib=True) # Full variant
ScenarioCls = Settings.get_scenario("SubprefixHijack")

# Dynamic composition via multiple inheritance
Combined = Settings.compose_policy(["ROV", "ASPA"])

# Serializable config object
config = PolicyConfig(features=("ROV", "ASPA"), full_rib=False)
PolicyCls = Settings.resolve_policy(config)

# Discovery
Settings.get_policy_names()    # sorted tuple of all policy .name attributes
Settings.get_scenario_names()  # sorted tuple of all scenario class names
```

Key caveats: Policy names use the `.name` class attribute (e.g. `"ROV"`, `"BGP Full"`). Scenario names use the Python class name (e.g. `"SubprefixHijack"`). User-defined `Scenario` subclasses defined *after* `bgpy.settings` is first imported will not appear in the scenario registry (Policy subclasses are always live via `__init_subclass__`).

`compose_policy()` creates classes via `type()` with multiple inheritance; results are cached. The registry snapshot/restore pattern in `compose_policy()` prevents composed classes from shadowing real classes in `name_to_subclass_dict`.

## Extension Points

- **New policy**: Subclass `Policy` (or an existing policy). It auto-registers.
- **New attack scenario**: Subclass `Scenario`, override `_get_announcements()` and `_get_roas()`.
- **Custom topology**: Pass a custom `ASGraphCls` to `Simulation`; or use `ASGraph` directly for small graphs without CAIDA data.
