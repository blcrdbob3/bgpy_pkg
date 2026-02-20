# Testing and Development
Relevant source files
- [.github/workflows/tests.yml](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/.github/workflows/tests.yml)
- [.pre-commit-config.yaml](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/.pre-commit-config.yaml)
- [LICENSE.txt](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/LICENSE.txt)
- [MANIFEST.in](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/MANIFEST.in)
- [README.md](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/README.md)
- [bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py)
- [bgpy/shared/constants.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/shared/constants.py)
- [bgpy/shared/enums.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/shared/enums.py)
- [bgpy/simulation_framework/graph_data_aggregator/__init__.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graph_data_aggregator/__init__.py)
- [bgpy/simulation_framework/scenarios/scenario.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py)
- [bgpy/simulation_framework/scenarios/scenario_config.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py)
- [bgpy/simulation_framework/simulation.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py)
- [bgpy/tests/conftest.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/conftest.py)
- [bgpy/tests/engine_tests/utils/engine_tester.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_tester.py)
- [bgpy/utils/engine_runner/simulator_codec/simulator_codec.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/simulator_codec/simulator_codec.py)
- [pyproject.toml](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml)
- [requirements.txt](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/requirements.txt)
- [requirements_dev.txt](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/requirements_dev.txt)
- [setup.cfg](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/setup.cfg)
- [tox.ini](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/tox.ini)

This page documents BGPy's testing infrastructure, development practices, and contribution guidelines. It covers the test framework architecture, ground truth management, code quality tools, and CI/CD workflows. For information about running simulations (non-test), see [Getting Started](/blcrdbob3/bgpy_pkg/2-getting-started). For details on the `Simulation` class that the test framework reuses components from, see [Simulation Framework Deep Dive](/blcrdbob3/bgpy_pkg/4-simulation-framework-deep-dive).

---

## Test Framework Overview

BGPy uses a specialized testing framework built on pytest that validates BGP simulation correctness by comparing engine states and outcomes against stored ground truth data. The framework supports regression testing, visual diagram generation, and deterministic simulation validation.

### Core Testing Classes

The testing framework consists of two main classes:
ClassFilePurpose`EngineRunner``bgpy/utils/engine_runner/`Base class that runs simulation engine with scenarios and generates YAML output`EngineTester``bgpy/tests/engine_tests/utils/engine_tester.py`Extends `EngineRunner` to compare outputs against ground truth
The `EngineTester` class runs simulations, stores results as YAML/CSV/pickle files, and compares them against previously validated ground truth data. This ensures that code changes do not break existing simulation behavior.

**Sources:**[bgpy/tests/engine_tests/utils/engine_tester.py1-239](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_tester.py#L1-L239)[bgpy/tests/conftest.py1-88](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/conftest.py#L1-L88)

---

## Test Execution Architecture

```
Teardown

Ground Truth Storage

Test Execution (per test)

Test Discovery and Setup

pytest Discovery
finds test_*.py files

pytest_configure Hook
conftest.py:15-21

CAIDAASGraphCollector.run()
Cache CAIDA data once

EngineTester.init
engine_tester.py:13-59

EngineTester.test_engine()
engine_tester.py:60-79

EngineRunner.run_engine()
Runs SimulationEngine

_store_gt_data
engine_tester.py:81-99

_generate_gt_diagrams
engine_tester.py:147-172

_compare_data
engine_tester.py:174-188

engine_gt.yaml
Engine state serialization

outcomes_gt.yaml
ASN outcome mapping

graph_data_gt.csv
Metrics in CSV format

graph_data_gt.pickle
Metrics in pickle format

pytest_sessionfinish Hook
conftest.py:24-51

DiagramAggregator
Combine all diagrams

Aggregated PDF Output
engine_test_outputs/
```

**Sources:**[bgpy/tests/conftest.py14-51](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/conftest.py#L14-L51)[bgpy/tests/engine_tests/utils/engine_tester.py60-211](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_tester.py#L60-L211)

---

## Running Tests

### Basic Test Commands
CommandDescription`pytest bgpy`Run all tests`pytest bgpy -n auto`Run tests in parallel using all CPU cores`pytest bgpy -k test_name`Run specific test by name`pytest bgpy -m slow`Run tests marked as "slow"`pytest bgpy --overwrite`Regenerate ground truth files`pytest bgpy --view`Open aggregated diagrams PDF after tests`pytest bgpy --dpi 150`Set diagram resolution (default: 96)
### Custom pytest Options

BGPy defines three custom command-line options configured in [bgpy/tests/conftest.py64-87](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/conftest.py#L64-L87):

```
parser.addoption("--view", action="store_true", default=False)
parser.addoption("--overwrite", action="store_true", default=False)  
parser.addoption("--dpi", type=int, default=96)
```

These options are exposed as pytest fixtures and used throughout the test suite:

- **`--view`**: Automatically opens the aggregated test diagrams PDF when all tests complete
- **`--overwrite`**: Regenerates ground truth YAML/CSV/pickle files (see Ground Truth Management below)
- **`--dpi`**: Controls diagram rendering resolution (higher values = larger, clearer diagrams)

### Multi-Version Testing with Tox

The project uses tox for automated testing across multiple Python versions:

```
tox                    # Test all configured environments
tox -e python3.10      # Test specific Python version
tox -e mypy            # Run type checking
tox -e ruff            # Run linting and formatting
```

Tox is configured to test PyPy 3.11, Python 3.10-3.14, plus code quality environments. See [tox.ini1-33](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/tox.ini#L1-L33) for the full configuration.

**Sources:**[bgpy/tests/conftest.py64-87](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/conftest.py#L64-L87)[tox.ini1-33](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/tox.ini#L1-L33)

---

## Ground Truth Management

### Storage Format and Files

Ground truth data is stored in three formats per test case, located in test-specific directories under `bgpy/tests/engine_tests/engine_test_outputs/`:
FileFormatContentSerialization Method`engine_gt.yaml`YAMLComplete engine state including AS RIBs, announcements, and graph structure`SimulatorCodec.dump()``outcomes_gt.yaml`YAMLDictionary mapping ASN → Outcome enum (ATTACKER_SUCCESS, VICTIM_SUCCESS, etc.)`SimulatorCodec.dump()``graph_data_gt.csv`CSVHuman-readable metrics aggregated by trial`GraphDataAggregator.write_data()``graph_data_gt.pickle`PicklePython objects for metrics with full precision`GraphDataAggregator.write_data()`
### YAML Serialization with SimulatorCodec

The `SimulatorCodec` class extends `YamlCodec` to handle BGPy-specific types including enums, announcement containers, and complex graph structures:

```
Registration

SimulatorCodec

Serializable Types

YamlAbleEnum
Outcomes, Relationships, Plane

AnnContainer
Announcement containers

BaseSimulationEngine
Engine state

Policy Objects
BGP, ROV, ASPA, etc.

to_yaml_dict()
codec.py:61-71

from_yaml_dict()
codec.py:43-58

types_to_yaml_tags
codec.py:15-19

yaml_tags_to_types
codec.py:20

YamlAbleEnum.init_subclass
enums.py:9-16

AnnContainer.subclasses
ann_container.py

SimulatorCodec.register_with_pyyaml()
codec.py:89
```

**Key features:**

- Automatic enum serialization via `YamlAbleEnum.__init_subclass__` tracking all enum subclasses
- Custom `__to_yaml_dict__` and `__from_yaml_dict__` methods for complex objects
- Type-safe deserialization with error reporting

**Sources:**[bgpy/utils/engine_runner/simulator_codec/simulator_codec.py1-90](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/simulator_codec/simulator_codec.py#L1-L90)[bgpy/shared/enums.py1-129](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/shared/enums.py#L1-L129)

### Ground Truth Comparison Logic

The comparison process validates three aspects of simulation correctness:

```
Comparison Assertions

Load Ground Truth

Load Current Run Data

Run SimulationEngine
EngineRunner.run_engine()

Dump to Guess Files
engine_guess.yaml
outcomes_guess.yaml
graph_data_guess.*

SimulatorCodec.load()
engine_gt.yaml

SimulatorCodec.load()
outcomes_gt.yaml

Read CSV/Pickle
graph_data_gt.*

Engine Equality
engine_tester.py:178-180
assert engine_guess == engine_gt

Outcomes Equality
engine_tester.py:182-184
assert outcomes_guess == outcomes_gt

Metrics Equality
engine_tester.py:189-210
Compare CSV rows and pickle data

Test Passes
```

**Engine comparison** validates:

- AS graph topology (links, relationships)
- Local RIBs at each AS
- Policy classes assigned to each AS
- Seeded announcements

**Outcomes comparison** validates:

- ASN → Outcome mapping for all ASes
- Outcome types: `ATTACKER_SUCCESS`, `VICTIM_SUCCESS`, `DISCONNECTED`, `UNDETERMINED`

**Metrics comparison** (optional, disabled by default):

- Statistical aggregations across trials
- Graph category breakdowns
- Data plane vs control plane metrics

**Sources:**[bgpy/tests/engine_tests/utils/engine_tester.py174-210](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_tester.py#L174-L210)

### The Overwrite Flag

The `--overwrite` flag controls ground truth regeneration. When enabled, it updates stored files while avoiding unnecessary writes when data hasn't changed:

**Overwrite Logic Flow:**

1. **If ground truth doesn't exist:** Always create new ground truth files
2. **If `--overwrite` is False:** Skip writing, only compare against existing ground truth
3. **If `--overwrite` is True:**
- Write new guess files
- Compare guess against existing ground truth
- Only overwrite ground truth if data actually differs (prevents unnecessary git diffs)

This intelligent comparison prevents spurious file changes when CSV/pickle layouts remain functionally identical. See [bgpy/tests/engine_tests/utils/engine_tester.py101-145](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_tester.py#L101-L145) for the implementation.

**Common use cases:**

```
# Validate code changes didn't break existing tests
pytest bgpy

# Regenerate ground truth after intentional behavior change
pytest bgpy --overwrite

# Regenerate specific test's ground truth
pytest bgpy -k test_prefix_hijack --overwrite
```

**Sources:**[bgpy/tests/engine_tests/utils/engine_tester.py13-59](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_tester.py#L13-L59)[bgpy/tests/engine_tests/utils/engine_tester.py81-145](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_tester.py#L81-L145)

---

## Development Tools and Code Quality

BGPy enforces code quality through static analysis tools configured in [pyproject.toml1-323](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L1-L323)

### Type Checking with mypy

Mypy validates type hints across the codebase with strict mode enabled:
ConfigurationValuePurpose`strict = true`EnabledEnforce comprehensive type checking`ignore_missing_imports = true`EnabledAllow third-party libraries without stubs`show_error_codes = true`EnabledDisplay error codes for easier debugging`warn_unreachable = true`EnabledDetect unreachable code paths
Run type checking:

```
mypy bgpy          # Check entire package
tox -e mypy        # Check via tox environment
```

**Sources:**[pyproject.toml126-138](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L126-L138)

### Linting and Formatting with ruff

Ruff provides fast linting and auto-formatting with 200+ rules enabled. Key configurations:

**Enabled rule categories:**

- `ALL` base rules with selective ignores for project-specific patterns
- Automatically fixes import sorting, trailing whitespace, and formatting issues

**Notable rule exceptions:**

- `D100-D419`: Relaxed docstring requirements to avoid over-documentation
- `ANN`: Type annotation enforcement (handled by mypy instead)
- `S101`: Allows runtime assertions for validation
- `N803`, `N806`: Allows uppercase variable names for class references
- `ISC001`: Disabled to avoid conflicts with `ruff format`

Run linting:

```
ruff check bgpy              # Check for violations
ruff check bgpy --fix        # Auto-fix violations
ruff format bgpy             # Format code
tox -e ruff                  # Lint via tox environment
```

**Per-file ignores:**

- `__init__.py` files exempt from import sorting (I rule) to avoid circular import issues
- Test files exempt from private member access checks (SLF001)

**Sources:**[pyproject.toml161-323](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L161-L323)

### Pre-commit Hooks

Minimal pre-commit configuration prevents large file commits:

```
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
    -   id: check-added-large-files
```

Install hooks:

```
pre-commit install
pre-commit run --all-files
```

**Sources:**[.pre-commit-config.yaml1-6](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/.pre-commit-config.yaml#L1-L6)

### Dependency Management

Dependencies are specified in three locations:
FilePurposeSync Requirement`pyproject.toml`Source of truth for package dependenciesMust match other files`requirements.txt`Production dependencies onlySubset of pyproject.toml`requirements_dev.txt`Production + development dependenciesSuperset of requirements.txt
**Core dependencies:**

- `pytest==9.0.2`: Test framework
- `pytest-xdist==3.8.0`: Parallel test execution
- `yamlable==1.1.1`: YAML serialization framework
- `roa-checker~=3.0`: RPKI validation
- `frozendict==2.4.7`: Immutable dictionaries for configuration

**Type checking stubs:**

- `types-beautifulsoup4`, `types-requests`, `types-PyYAML`, etc.

**Sources:**[pyproject.toml57-94](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L57-L94)[requirements.txt1-15](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/requirements.txt#L1-L15)[requirements_dev.txt1-26](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/requirements_dev.txt#L1-L26)

---

## CI/CD Pipeline

### GitHub Actions Workflow

The test suite runs automatically on every push and pull request via GitHub Actions:

```
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        python-version: ['pypy-3.11', '3.10', '3.11', '3.12', '3.13', '3.14']
```

**Test matrix dimensions:**

- **Operating Systems:** Ubuntu (Linux), macOS (both Intel and ARM via universal runner)
- **Python Versions:** PyPy 3.11, CPython 3.10-3.14 (6 versions)
- **Total combinations:** 12 test jobs per CI run

**Workflow steps:**

1. Checkout repository
2. Install Graphviz system dependency (for diagram generation)
3. Set up specified Python version
4. Install tox and dependencies
5. Run `tox` (automatically selects correct environment via `gh-actions` mapping)

The `tox-gh-actions` plugin maps Python versions to tox environments:

```
[gh-actions]
python =
    pypy-3.11: pypy3
    3.10: python3.10, ruff, mypy
    3.11: python3.11
    3.12: python3.12
    3.13: python3.13
    3.14: python3.14
```

Note: Python 3.10 also runs `ruff` and `mypy` checks as the "base" version for code quality.

**Sources:**[.github/workflows/tests.yml1-29](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/.github/workflows/tests.yml#L1-L29)[tox.ini6-13](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/tox.ini#L6-L13)

### Tox Environment Configuration

```
Dependencies

Commands

Tox Environments

Base Test Environment
testenv

python3.10
+ ruff + mypy

python3.11

python3.12

python3.13

python3.14

pypy3

Ruff Linting
testenv:ruff

Mypy Type Checking
testenv:mypy

pytest bgpy
Run all tests

pytest bgpy -n auto
Parallel execution

ruff check + format

mypy bgpy

requirements_dev.txt
Full dev dependencies

pytest + pytest-xdist
Minimal test deps
```

Each environment is isolated, ensuring tests validate compatibility across Python versions and implementations (CPython vs PyPy).

**Sources:**[tox.ini1-33](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/tox.ini#L1-L33)

---

## Writing and Extending Tests

### Test Organization

Tests are organized under `bgpy/tests/` with markers for categorization:
MarkerPurposeExample`slow`Long-running integration testsFull simulation runs`framework`Framework functionality tests`Simulation` class tests`unit_tests`Fast unit testsIndividual function tests`engine`Engine-specific testsBGP propagation tests
Mark tests using pytest decorators:

```
@pytest.mark.slow
@pytest.mark.engine
def test_complex_scenario():
    ...
```

Run specific markers:

```
pytest bgpy -m "engine and not slow"
pytest bgpy -m unit_tests
```

**Sources:**[pyproject.toml108-119](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L108-L119)

### Extending EngineTester

To create new engine tests, subclass `EngineTester` or use it directly with custom scenarios:

**Basic test structure:**

1. **Define scenario configuration:**

```
from bgpy.simulation_framework import ScenarioConfig, PrefixHijack
from bgpy.simulation_engine import BGP, ROV

config = ScenarioConfig(
    ScenarioCls=PrefixHijack,
    AdoptPolicyCls=ROV,
    BasePolicyCls=BGP,
)
```
2. **Initialize EngineTester:**

```
from bgpy.tests.engine_tests.utils import EngineTester

tester = EngineTester(
    scenario_config=config,
    overwrite=False,  # From pytest fixture
)
```
3. **Run test:**

```
tester.test_engine()  # Runs simulation and validates
```

### Test Data Persistence

Tests automatically create output directories:

```
bgpy/tests/engine_tests/engine_test_outputs/
├── test_name/
│   ├── engine_gt.yaml          # Ground truth engine state
│   ├── outcomes_gt.yaml        # Ground truth outcomes
│   ├── graph_data_gt.csv       # Ground truth metrics (CSV)
│   ├── graph_data_gt.pickle    # Ground truth metrics (pickle)
│   ├── ground_truth.gv         # AS graph diagram (ground truth)
│   ├── engine_guess.yaml       # Current run engine state
│   ├── outcomes_guess.yaml     # Current run outcomes
│   ├── graph_data_guess.csv    # Current run metrics (CSV)
│   └── graph_data_guess.pickle # Current run metrics (pickle)

```

Diagram files (`.gv`) are generated using Graphviz and aggregated into a single PDF at the end of the test session.

**Sources:**[bgpy/tests/engine_tests/utils/engine_tester.py1-239](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_tester.py#L1-L239)

### Diagram Generation During Tests

Each test generates AS graph diagrams showing:

- Network topology with AS relationships
- Announcement propagation paths
- Policy assignments (colored nodes)
- Outcome classifications per AS

The `DiagramAggregator` collects all generated diagrams and combines them into a single PDF for easy review:

```
# Automatic in conftest.py:24-51
def pytest_sessionfinish(session, exitstatus):
    if not hasattr(session.config, "workerinput"):  # Main process only
        DiagramAggregator(DIAGRAM_PATH).aggregate_diagrams()
        if session.config.getoption("view"):
            # Open PDF automatically
            subprocess.call([command, str(agg_path)])
```

**Sources:**[bgpy/tests/conftest.py24-51](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/conftest.py#L24-L51)[bgpy/tests/engine_tests/utils/engine_tester.py147-172](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_tester.py#L147-L172)

---

## Best Practices

### When to Regenerate Ground Truth

Regenerate ground truth files (`--overwrite`) when:

✅ **Intentional behavior changes:**

- Policy algorithm improvements
- Attack scenario refinements
- Engine propagation logic modifications

✅ **New features:**

- Adding new policy classes
- Implementing new attack scenarios
- Extending announcement types

❌ **Do NOT regenerate for:**

- Refactoring without behavior changes
- Documentation updates
- Performance optimizations that preserve output

### Avoiding False Positive Test Failures

Common causes of test failures and solutions:
IssueCauseSolutionEngine comparison failsASN ordering in sets changedReview engine diff, regenerate if ordering-only changeMetrics differ slightlyFloating point precisionCheck if differences are meaningful or rounding errorsYAML deserialization errorMissing type registrationEnsure class is registered in `SimulatorCodec`Parallel test conflictsShared file accessUse pytest-xdist worker isolation correctly
### Testing Determinism

Ensure reproducible tests:

1. **Seed randomness:** Tests should use `PYTHONHASHSEED` environment variable for deterministic random number generation
2. **Avoid time-based logic:** Don't use `datetime.now()` in tests
3. **Freeze external data:** Cache CAIDA data once in `pytest_configure` hook
4. **Validate idempotency:** Running the same test multiple times should produce identical results

**Sources:**[bgpy/tests/conftest.py14-22](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/conftest.py#L14-L22)[bgpy/simulation_framework/simulation.py269-281](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L269-L281)

---

## Summary: Testing and Development Workflow

**Typical development cycle:**

1. **Make code changes** to policies, scenarios, or engine logic
2. **Run tests locally:**`pytest bgpy -n auto` (parallel execution)
3. **Review failures:** Check if behavior change is intentional
4. **Update ground truth if needed:**`pytest bgpy --overwrite -k failing_test_name`
5. **Verify diagrams:**`pytest bgpy --view` to visually inspect changes
6. **Check code quality:**`tox -e mypy` and `tox -e ruff`
7. **Push to CI:** GitHub Actions runs full matrix test suite
8. **Monitor CI results:** Ensure tests pass on all Python versions and OS combinations

**Key files for contributors:**

- [bgpy/tests/conftest.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/conftest.py) - pytest configuration and hooks
- [bgpy/tests/engine_tests/utils/engine_tester.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_tester.py) - Main testing class
- [pyproject.toml](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml) - Tool configurations (mypy, ruff, pytest)
- [tox.ini](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/tox.ini) - Multi-version test environments
- [.github/workflows/tests.yml](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/.github/workflows/tests.yml) - CI/CD pipeline definition