# Ground Truth Management
Relevant source files
- [bgpy/shared/constants.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/shared/constants.py)
- [bgpy/simulation_framework/graph_data_aggregator/__init__.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graph_data_aggregator/__init__.py)
- [bgpy/tests/conftest.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/conftest.py)
- [bgpy/tests/engine_tests/utils/engine_tester.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_tester.py)
- [bgpy/utils/engine_runner/simulator_codec/simulator_codec.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/simulator_codec/simulator_codec.py)

## Purpose and Scope

This document describes the ground truth management system in BGPy's testing framework. Ground truth refers to the expected, correct outputs of test simulations that are stored and compared against future test runs to detect regressions. This system ensures that changes to the codebase do not inadvertently alter simulation behavior.

For information about the overall test framework architecture, see [Test Framework Architecture](/blcrdbob3/bgpy_pkg/9.1-test-framework-architecture). For details on development practices and CI/CD integration, see [Development Practices](/blcrdbob3/bgpy_pkg/9.3-development-practices).

## Overview

The ground truth system captures three aspects of a simulation run:

1. **Engine State**: The complete state of the `BaseSimulationEngine` after propagation, including all AS local RIBs and announcements
2. **Outcomes**: The classification of each AS (attacker success, victim success, or disconnected) after analysis
3. **Graph Data**: Statistical metrics aggregated across trials (optional, disabled by default)

Each test case maintains its own ground truth files in a dedicated directory. When tests run, the current simulation output is compared against these stored ground truth files. Any discrepancies indicate potential regressions.

Sources: [bgpy/tests/engine_tests/utils/engine_tester.py10-80](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_tester.py#L10-L80)

## Ground Truth File Structure

```
Visualization

Current Run Files

Ground Truth Files

Test Case Directory
(e.g., engine_test_outputs/test_name/)

engine_gt.yaml
Complete engine state
after propagation

outcomes_gt.yaml
AS outcome classifications
(dict: asn → outcome)

graph_data_gt.csv
Metrics in CSV format
(optional)

graph_data_gt.pickle
Metrics in pickle format
(optional)

engine_guess.yaml
Engine state from
current test run

outcomes_guess.yaml
Outcomes from
current test run

graph_data_guess.csv
Metrics from
current test run

graph_data_guess.pickle
Metrics from
current test run

ground_truth.gv
AS graph diagram with
traceback information
```

### File Path Properties

The `EngineTester` class defines properties for accessing these file paths:
PropertyPathPurpose`engine_ground_truth_path``storage_dir/engine_gt.yaml`Ground truth engine state`outcomes_ground_truth_path``storage_dir/outcomes_gt.yaml`Ground truth outcomes`graph_data_ground_truth_path_csv``storage_dir/graph_data_gt.csv`Ground truth metrics (CSV)`graph_data_ground_truth_path_pickle``storage_dir/graph_data_gt.pickle`Ground truth metrics (pickle)`engine_guess_path`Inherited from `EngineRunner`Current run engine state`outcomes_guess_path`Inherited from `EngineRunner`Current run outcomes`graph_data_guess_path_csv`Inherited from `EngineRunner`Current run metrics (CSV)`graph_data_guess_path_pickle`Inherited from `EngineRunner`Current run metrics (pickle)
Sources: [bgpy/tests/engine_tests/utils/engine_tester.py216-238](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_tester.py#L216-L238)

## Test Execution Flow

```
No

Yes

Yes

No

No

Yes

Yes

No

Match

Mismatch

Match

Mismatch

Yes

No

Match

Mismatch

test_engine() called

run_engine()
Execute simulation

_store_gt_data()
Store or verify ground truth

engine_gt.yaml
exists?

overwrite
flag set?

Create engine_gt.yaml
codec.dump(engine)

Use existing
engine_gt.yaml

outcomes_gt.yaml
exists?

Create outcomes_gt.yaml
codec.dump(outcomes)

Use existing
outcomes_gt.yaml

_store_gt_metrics()
Handle metric ground truth

_generate_gt_diagrams()
Create visualization

_compare_data()
Compare guess vs ground truth

Load and compare
engine_guess == engine_gt

Load and compare
outcomes_guess == outcomes_gt

compare_graph_data
enabled?

_compare_graph_data_to_gt()
Compare CSV and pickle

Test passes

AssertionError
Test fails
```

Sources: [bgpy/tests/engine_tests/utils/engine_tester.py60-80](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_tester.py#L60-L80)[bgpy/tests/engine_tests/utils/engine_tester.py174-210](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_tester.py#L174-L210)

## Ground Truth Storage

### Engine and Outcomes Storage

The `_store_gt_data()` method handles storing ground truth for engine state and outcomes. The logic is straightforward:

```
No

Yes

Yes

No

No

Yes

Yes

No

engine
outcomes
graph_data_aggregator

engine_gt.yaml
exists?

overwrite?

codec.dump(engine,
engine_ground_truth_path)

Keep existing
engine_gt.yaml

outcomes_gt.yaml
exists?

overwrite?

codec.dump(outcomes,
outcomes_ground_truth_path)

Keep existing
outcomes_gt.yaml

_store_gt_metrics()
```

Sources: [bgpy/tests/engine_tests/utils/engine_tester.py81-99](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_tester.py#L81-L99)

### Metrics Storage

Metrics storage is more complex due to a historical issue where files would appear modified in git even when metrics were functionally identical. The `_store_gt_metrics()` method implements a comparison-before-write strategy:

```
No

Yes

No

Yes

Yes

No

Yes

No (AssertionError)

Yes

No (AssertionError)

_store_gt_metrics(graph_data_aggregator)

Both CSV and pickle
ground truth exist?

Write both files:
graph_data_aggregator.write_data()

overwrite
flag set?

graph_data_guess
pickle exists?

_compare_graph_data_to_gt()

Metrics
match?

Skip writing
(already identical)

Write ground truth
(metrics differ)

Write to guess files first

_compare_graph_data_to_gt()

Metrics
match?

Skip writing
(already identical)

Write ground truth
(metrics differ)

Return
```

This complex logic prevents unnecessary git diffs when metrics haven't actually changed, reducing noise in version control.

Sources: [bgpy/tests/engine_tests/utils/engine_tester.py101-146](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_tester.py#L101-L146)

## Comparison Mechanism

### Engine and Outcomes Comparison

The `_compare_data()` method performs the actual comparison:

```
# Load guess files (from current run)
engine_guess = self.codec.load(self.engine_guess_path)
outcomes_guess = self.codec.load(self.outcomes_guess_path)

# Load ground truth files
engine_gt = self.codec.load(self.engine_ground_truth_path)
outcomes_gt = self.codec.load(self.outcomes_ground_truth_path)

# Assert equality
assert engine_guess == engine_gt, f"{self.conf.name} failed engine check"
assert outcomes_guess == outcomes_gt, f"{self.conf.name} failed outcomes check"
```

The comparison relies on Python's `__eq__` implementations for the serialized objects. Because the `SimulatorCodec` deserializes YAML into the original Python objects, standard equality checks work correctly.

Sources: [bgpy/tests/engine_tests/utils/engine_tester.py174-188](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_tester.py#L174-L188)

### Metrics Comparison

When `compare_graph_data` is enabled, the `_compare_graph_data_to_gt()` method compares both CSV and pickle formats:

**CSV Comparison**: Reads both files as sets of tuples (rows) and compares for set equality. This handles potential row ordering differences.

**Pickle Comparison**: Loads the pickle files as dictionaries mapping `GraphCategory` → `DataPointKey` → `DataPointAggData` and performs nested equality checks in both directions to ensure no keys are missing or extra.
Data StructureTypeContents`GraphCategory`Enum-likeIdentifies graph type (plane, AS group, outcome, adoption status)`DataPointKey`DataclassIdentifies a point on a graph (propagation round, adoption percentage, scenario config)`DataPointAggData`DataclassContains aggregated value and error bars (yerr)
Sources: [bgpy/tests/engine_tests/utils/engine_tester.py189-210](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_tester.py#L189-L210)[bgpy/simulation_framework/graph_data_aggregator/__init__.py1-13](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graph_data_aggregator/__init__.py#L1-L13)

## The Overwrite Flag

### Configuration

The `overwrite` flag is configured via pytest command-line arguments:

```
pytest --overwrite  # Regenerate all ground truth files
pytest              # Normal mode: compare against existing ground truth
```

The flag is defined in `pytest_addoption()` and passed to test cases via a pytest fixture:

```
@pytest.fixture(scope="session")
def overwrite(pytestconfig):
    return pytestconfig.getoption("overwrite")
```

Sources: [bgpy/tests/conftest.py53-56](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/conftest.py#L53-L56)[bgpy/tests/conftest.py64-78](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/conftest.py#L64-L78)

### When to Use Overwrite

Use the `--overwrite` flag in these situations:
ScenarioActionReasonCreating new tests`--overwrite` requiredNo ground truth exists yetIntentional behavior change`--overwrite` after verificationUpdate ground truth to new expected behaviorBug fix that changes outputs`--overwrite` after verificationCorrect behavior differs from old ground truthRefactoring with no behavior changeNormal runShould pass without overwriteAdding new metrics`--overwrite` (if `compare_graph_data=True`)New metrics won't match old ground truth
### Overwrite Decision Tree

```
No

Yes

Yes

No

Test fails

Ground truth
files exist?

Run with --overwrite
to create ground truth

Manually verify
current behavior is correct

Current behavior
is correct?

Fix the bug in
simulation code

Run test again
without --overwrite

Run with --overwrite
to update ground truth

Commit updated
ground truth files

Test passes
```

## YAML Serialization with SimulatorCodec

### Overview

The `SimulatorCodec` class extends `YamlCodec` to handle serialization of BGPy-specific objects, including enums, announcement containers, and simulation engines.

```
Core Methods

Type Mappings

Serializable Types

SimulatorCodec
extends YamlCodec

YamlAbleEnum subclasses
(ASGroups, Outcomes, etc.)

AnnContainer subclasses
(Announcement, ROVPPAnn, etc.)

Other simulation objects

types_to_yaml_tags
(type → yaml tag string)

yaml_tags_to_types
(yaml tag string → type)

to_yaml_dict(obj)
→ (tag, dict)

from_yaml_dict(tag, dict)
→ object

dump(obj, path)
Write YAML file

load(path)
Read YAML file
```

### Type Registration

The codec maintains bidirectional mappings between Python types and YAML tags:

```
# YamlAbleEnum subclasses use their yaml_suffix() method
types_to_yaml_tags = {
    X: X.yaml_suffix() for X in YamlAbleEnum.yamlable_enums()
}

# AnnContainer subclasses use their class name
types_to_yaml_tags.update({
    Cls: Cls.__name__ for Cls in AnnContainer.subclasses
})

# Reverse mapping for deserialization
yaml_tags_to_types = {v: k for k, v in types_to_yaml_tags.items()}
```

Sources: [bgpy/utils/engine_runner/simulator_codec/simulator_codec.py14-20](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/simulator_codec/simulator_codec.py#L14-L20)

### Serialization Process

**To YAML**:

1. `to_yaml_dict()` is called with an object
2. Type is looked up in `types_to_yaml_tags`
3. Returns tuple of (tag, dict):

- `YamlAbleEnum`: `{"value": obj.value, "name": obj.name}`
- `AnnContainer`: `obj.__to_yaml_dict__()`
- Other: `vars(obj)`

**From YAML**:

1. `from_yaml_dict()` is called with (tag, dict)
2. Type is looked up in `yaml_tags_to_types`
3. Object is reconstructed:

- `YamlAbleEnum`: `typ(value=dct["value"])`
- `AnnContainer`: `typ.__from_yaml_dict__(dct=dct, yaml_tag=tag)`
- Other: `typ(**dct)`

### Dump and Load Methods

The `dump()` method configures YAML to ignore aliases for better readability:

```
def dump(self, obj, path=None):
    # Ignores references for more readable output
    yaml.Dumper.ignore_aliases = lambda *args: True
    if path is None:
        yaml.dump(obj)
    else:
        with path.open(mode="w") as f:
            yaml.dump(obj, f)
```

The `load()` method uses a custom `SimulatorLoader` that knows how to reconstruct BGPy objects.

Sources: [bgpy/utils/engine_runner/simulator_codec/simulator_codec.py23-89](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/simulator_codec/simulator_codec.py#L23-L89)

## Ground Truth Diagrams

### Generation

The `_generate_gt_diagrams()` method creates a visual representation of the ground truth:

```
def _generate_gt_diagrams(
    self, scenario: Scenario, graph_data_aggregator: GraphDataAggregator
) -> None:
    # Load ground truth files
    engine_gt = self.codec.load(self.engine_ground_truth_path)
    outcomes_gt = self.codec.load(self.outcomes_ground_truth_path)
    
    # Get diagram ranks (AS positioning)
    static_order = bool(self.conf.as_graph_info.diagram_ranks)
    diagram_obj_ranks = self._get_diagram_obj_ranks(engine_gt)
    
    # Generate diagram
    self.conf.DiagramCls().generate_as_graph(
        engine_gt,
        scenario,
        outcomes_gt,
        f"({self.conf.name} Ground Truth)\n{self.conf.desc}",
        graph_data_aggregator,
        diagram_obj_ranks,
        static_order=static_order,
        path=self.storage_dir / "ground_truth.gv",
        view=False,
        dpi=self.dpi,
    )
```

These diagrams are saved as `ground_truth.gv` files (GraphViz format) in each test directory. For details on diagram generation, see [Diagram Generation](/blcrdbob3/bgpy_pkg/8.4-diagram-generation).

Sources: [bgpy/tests/engine_tests/utils/engine_tester.py147-172](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_tester.py#L147-L172)

### Aggregation

After all tests complete, the `pytest_sessionfinish` hook aggregates all diagrams into a single PDF:

```
def pytest_sessionfinish(session, exitstatus):
    # Only run in master thread after all tests finish
    if not hasattr(session.config, "workerinput"):
        try:
            DiagramAggregator(DIAGRAM_PATH).aggregate_diagrams()
            # Optionally open PDF for viewing
            if session.config.getoption("view"):
                agg_path = DiagramAggregator(DIAGRAM_PATH).aggregated_diagrams_path
                command = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([command, str(agg_path)])
        except Exception as e:
            bgpy_logger.exception(f"Diagram aggregator failed: {e}")
```

The `--view` flag automatically opens the aggregated PDF after tests complete.

Sources: [bgpy/tests/conftest.py24-51](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/conftest.py#L24-L51)

## Metrics Ground Truth Considerations

### Why Metrics Comparison is Disabled by Default

The `compare_graph_data` parameter defaults to `False` for several reasons documented in the code:
IssueDescription**Frequent overwrite requirement**Any metrics change requires overwriting all test ground truth**Layout brittleness**JSON/CSV layout changes cause failures without actual code changes**Git noise**Metrics files change frequently, cluttering git diffs**Framework variability**Different projects have different metric trackers; some have none**Single responsibility**Engine tests should test the engine, not the metrics framework
The feature remains available for projects that need comprehensive metrics validation, but most tests can adequately validate behavior through engine state and outcomes alone.

Sources: [bgpy/tests/engine_tests/utils/engine_tester.py20-46](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_tester.py#L20-L46)

### Enabling Metrics Comparison

To enable metrics comparison for specific tests:

```
tester = EngineTester(
    # ... other arguments ...
    compare_graph_data=True,
    overwrite=False,
)
tester.test_engine()
```

When enabled, the test will fail if `graph_data_gt.csv` or `graph_data_gt.pickle` differ from current run outputs.

## Ground Truth Lifecycle

```
Test created

Run with --overwrite

Test runs successfully

Code change breaks behavior

Examine engine_guess.yaml
vs engine_gt.yaml

Bug found in new code

New behavior is correct

Fix code, rerun test

Run with --overwrite

Test continues to pass

NoGroundTruth

GroundTruthCreated

PassingTests

FailingTests

Investigation

BugFixed

GroundTruthUpdated
```

This lifecycle emphasizes that ground truth files are living documentation of expected behavior. They should be updated deliberately when behavior changes intentionally, not automatically on every test failure.

Sources: [bgpy/tests/engine_tests/utils/engine_tester.py10-80](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_tester.py#L10-L80)