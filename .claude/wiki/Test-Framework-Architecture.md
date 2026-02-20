# Test Framework Architecture
Relevant source files
- [bgpy/shared/constants.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/shared/constants.py)
- [bgpy/simulation_framework/graph_data_aggregator/__init__.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graph_data_aggregator/__init__.py)
- [bgpy/tests/conftest.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/conftest.py)
- [bgpy/tests/engine_tests/utils/engine_tester.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_tester.py)
- [bgpy/utils/engine_runner/simulator_codec/simulator_codec.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/simulator_codec/simulator_codec.py)

## Purpose and Scope

This document describes the test framework architecture used to validate BGPy's simulation engine correctness. The framework uses pytest to orchestrate regression tests that compare simulation outputs against stored ground truth data. For information about managing ground truth files and the overwrite mechanism, see [Ground Truth Management](/blcrdbob3/bgpy_pkg/9.2-ground-truth-management). For broader development practices including CI/CD integration, see [Development Practices](/blcrdbob3/bgpy_pkg/9.3-development-practices).

The test framework provides:

- Deterministic regression testing of simulation engine behavior
- YAML-based ground truth storage for human-readable diffs
- Automatic diagram generation for visual validation
- Optional metrics comparison for data aggregation validation

---

## Architecture Overview

The test framework consists of three main layers: the pytest integration layer, the test execution layer, and the serialization layer.

```
Storage

Serialization Layer

Test Execution Layer

pytest Integration Layer

pytest
Test Discovery

conftest.py
pytest_configure
pytest_sessionfinish

Fixtures
overwrite, dpi

EngineTester
test_engine()

EngineRunner
run_engine()

Comparison Logic
_compare_data()

Diagram Generation
_generate_gt_diagrams()

DiagramAggregator
aggregate_diagrams()

SimulatorCodec
dump() / load()

YamlAbleEnum
Enum Serialization

AnnContainer
to_yaml_dict()

engine_gt.yaml
SimulationEngine State

outcomes_gt.yaml
ASN→Outcome Mapping

graph_data_gt.csv
graph_data_gt.pickle

ground_truth.gv
AS Graph Diagrams
```

**Sources:**[bgpy/tests/conftest.py1-88](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/conftest.py#L1-L88)[bgpy/tests/engine_tests/utils/engine_tester.py1-239](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_tester.py#L1-L239)

---

## Core Components

### EngineTester Class

The `EngineTester` class extends `EngineRunner` to add test validation functionality. It orchestrates the entire test lifecycle: running simulations, storing ground truth, generating diagrams, and comparing results.

```
EngineRunner

+codec: SimulatorCodec

+conf: TestConfig

+storage_dir: Path

+run_engine() : tuple

#_get_diagram_obj_ranks()

#_store_metrics()

EngineTester

+overwrite: bool

+compare_graph_data: bool

+engine_ground_truth_path: Path

+outcomes_ground_truth_path: Path

+graph_data_ground_truth_path_csv: Path

+graph_data_ground_truth_path_pickle: Path

+test_engine() : None

#_store_gt_data()

#_store_gt_metrics()

#_generate_gt_diagrams()

#_compare_data()

#_compare_graph_data_to_gt()
```

**Key Attributes:**
AttributeTypePurpose`overwrite``bool`Controls whether to overwrite existing ground truth files`compare_graph_data``bool`Enables optional comparison of metrics CSV/pickle files`codec``SimulatorCodec`YAML serialization/deserialization handler`storage_dir``Path`Directory for storing ground truth and test outputs
The `compare_graph_data` flag is disabled by default [bgpy/tests/engine_tests/utils/engine_tester.py20-46](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_tester.py#L20-L46) This design decision reflects that metric tracking belongs to the simulation framework layer, not the engine layer. Changes to metric formats or layouts would otherwise require regenerating all ground truth files, even when engine behavior is unchanged.

**Sources:**[bgpy/tests/engine_tests/utils/engine_tester.py10-59](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_tester.py#L10-L59)

---

### Test Execution Flow

The `test_engine()` method orchestrates the complete test lifecycle. This diagram shows the step-by-step execution flow:

```
"File System"
"SimulatorCodec"
"SimulationEngine"
"EngineRunner"
"EngineTester"
"pytest Test Function"
"File System"
"SimulatorCodec"
"SimulationEngine"
"EngineRunner"
"EngineTester"
"pytest Test Function"
alt
[compare_graph_data enabled]
test_engine()
run_engine()
Setup & propagate
engine, outcomes, graph_data
return results
_store_gt_data()
dump(engine, engine_gt.yaml)
Write YAML
dump(outcomes, outcomes_gt.yaml)
Write YAML
_store_gt_metrics()
Write CSV/pickle (if changed)
_generate_gt_diagrams()
load(engine_gt.yaml)
engine_gt
load(outcomes_gt.yaml)
outcomes_gt
Write ground_truth.gv
_compare_data()
load(engine_guess_path)
engine_guess
load(engine_ground_truth_path)
engine_gt
assert engine_guess == engine_gt
load(outcomes_guess_path)
outcomes_guess
load(outcomes_ground_truth_path)
outcomes_gt
assert outcomes_guess == outcomes_gt
_compare_graph_data_to_gt()
Load CSV/pickle files
assert equality
pass/fail
```

**Sources:**[bgpy/tests/engine_tests/utils/engine_tester.py60-80](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_tester.py#L60-L80)

---

### Ground Truth Storage Strategy

Ground truth files are stored in a test-specific directory structure. The storage logic includes intelligent comparison to avoid unnecessary git diffs when metrics haven't actually changed.

**File Layout:**

```
bgpy/tests/engine_tests/engine_test_outputs/
└── {test_name}/
    ├── engine_gt.yaml           # Serialized SimulationEngine state
    ├── outcomes_gt.yaml         # ASN → Outcome mapping
    ├── graph_data_gt.csv        # Optional metrics (human-readable)
    ├── graph_data_gt.pickle     # Optional metrics (Python objects)
    ├── engine_guess.yaml        # Current test run engine state
    ├── outcomes_guess.yaml      # Current test run outcomes
    ├── graph_data_guess.csv     # Current test run metrics
    ├── graph_data_guess.pickle  # Current test run metrics
    └── ground_truth.gv          # Graphviz diagram

```

The `_store_gt_data()` method implements the storage logic [bgpy/tests/engine_tests/utils/engine_tester.py81-99](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_tester.py#L81-L99) Ground truth files are created if they don't exist, or overwritten if the `overwrite` flag is set.

The `_store_gt_metrics()` method includes special logic to prevent unnecessary file writes [bgpy/tests/engine_tests/utils/engine_tester.py101-146](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_tester.py#L101-L146) When overwriting, it first compares the new metrics to the existing ground truth. Only if they differ are the ground truth files updated. This prevents spurious git diffs when metric file serialization produces different byte orderings for identical data.

**Sources:**[bgpy/tests/engine_tests/utils/engine_tester.py81-146](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_tester.py#L81-L146)[bgpy/tests/engine_tests/utils/engine_tester.py216-238](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_tester.py#L216-L238)

---

### pytest Integration

The test framework integrates with pytest through hooks defined in `conftest.py`. These hooks manage setup, teardown, and cross-worker coordination.

```
BGPy Teardown

BGPy Setup

pytest Lifecycle

pytest Start

pytest_configure

Test Execution

pytest_sessionfinish

pytest End

CAIDAASGraphCollector.run()
Download & Cache Topology

DiagramAggregator.aggregate_diagrams()

open aggregated_diagrams.pdf
```

**pytest_configure Hook:**

The `pytest_configure` hook runs once before test parallelization [bgpy/tests/conftest.py15-21](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/conftest.py#L15-L21) It caches CAIDA topology data to avoid race conditions where multiple parallel workers attempt to download the same file simultaneously. The `hasattr(config, "workerinput")` check ensures this only runs in the master process, not in xdist worker processes.

**pytest_sessionfinish Hook:**

The `pytest_sessionfinish` hook runs once after all tests complete [bgpy/tests/conftest.py24-50](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/conftest.py#L24-L50) It aggregates all generated AS graph diagrams into a single PDF for visual inspection. If the `--view` flag is provided, the PDF is automatically opened. Error handling ensures that diagram aggregation failures don't suppress actual test failures.

**Custom Command Line Options:**
OptionTypeDefaultPurpose`--view`flagFalseAutomatically open aggregated diagrams PDF after tests`--overwrite`flagFalseOverwrite ground truth files with current test results`--dpi`int96Set DPI for rendered diagrams
These options are defined in `pytest_addoption`[bgpy/tests/conftest.py64-87](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/conftest.py#L64-L87) and exposed as pytest fixtures [bgpy/tests/conftest.py53-60](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/conftest.py#L53-L60)

**Sources:**[bgpy/tests/conftest.py1-88](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/conftest.py#L1-L88)

---

## Serialization Mechanism

The `SimulatorCodec` class handles YAML serialization of complex BGPy objects. It extends the `YamlCodec` base class from the `yamlable` library to support custom serialization for enums and announcement containers.

### Supported Types

The codec maintains bidirectional mappings between Python types and YAML tags:

```
YAML Tags

Python Types

types_to_yaml_tags

yaml_tags_to_types

types_to_yaml_tags

yaml_tags_to_types

YamlAbleEnum Subclasses
Relationships, Outcomes, etc.

AnnContainer Subclasses
Announcement, BGPSecAnn, etc.

!simulator_codec/Relationships
!simulator_codec/Outcomes

!simulator_codec/Announcement
!simulator_codec/BGPSecAnn
```

**Type Registration:**

The codec builds type mappings at module import time [bgpy/utils/engine_runner/simulator_codec/simulator_codec.py14-20](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/simulator_codec/simulator_codec.py#L14-L20):

```
types_to_yaml_tags: dict[type[Any], str] = {
    X: X.yaml_suffix() for X in YamlAbleEnum.yamlable_enums()
}
types_to_yaml_tags.update({Cls: Cls.__name__ for Cls in AnnContainer.subclasses})
```

**Serialization Methods:**
MethodPurposeKey Logic`to_yaml_dict(obj)`Convert Python object to YAML dictUses `__to_yaml_dict__()` for AnnContainers, `vars(obj)` for others [bgpy/utils/engine_runner/simulator_codec/simulator_codec.py61-71](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/simulator_codec/simulator_codec.py#L61-L71)`from_yaml_dict(tag, dct)`Reconstruct Python object from YAML dictUses `__from_yaml_dict__()` for AnnContainers, direct instantiation for others [bgpy/utils/engine_runner/simulator_codec/simulator_codec.py43-58](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/simulator_codec/simulator_codec.py#L43-L58)`dump(obj, path)`Write object to YAML fileDisables YAML aliases for readability [bgpy/utils/engine_runner/simulator_codec/simulator_codec.py73-81](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/simulator_codec/simulator_codec.py#L73-L81)`load(path)`Read object from YAML fileUses custom `SimulatorLoader`[bgpy/utils/engine_runner/simulator_codec/simulator_codec.py83-86](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/simulator_codec/simulator_codec.py#L83-L86)
**Enum Serialization:**

`YamlAbleEnum` subclasses serialize both their value and name for debugging. When deserializing, only the value is used to reconstruct the enum [bgpy/utils/engine_runner/simulator_codec/simulator_codec.py48-50](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/simulator_codec/simulator_codec.py#L48-L50):

```
!simulator_codec/Outcomes
name: VICTIM_SUCCESS
value: 1
```

**YAML Alias Suppression:**

The codec disables YAML's reference aliasing feature [bgpy/utils/engine_runner/simulator_codec/simulator_codec.py75-76](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/simulator_codec/simulator_codec.py#L75-L76) This produces larger but more human-readable YAML files where repeated objects are written in full rather than using YAML anchors and aliases.

**Sources:**[bgpy/utils/engine_runner/simulator_codec/simulator_codec.py1-90](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/simulator_codec/simulator_codec.py#L1-L90)

---

## Comparison Logic

The `_compare_data()` method performs equality assertions between current test runs and stored ground truth [bgpy/tests/engine_tests/utils/engine_tester.py174-187](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_tester.py#L174-L187)

**Engine and Outcomes Comparison:**

```
Yes

No

_compare_data()

Load engine_guess.yaml

Load engine_gt.yaml

assert engine_guess == engine_gt

Load outcomes_guess.yaml

Load outcomes_gt.yaml

assert outcomes_guess == outcomes_gt

compare_graph_data?

_compare_graph_data_to_gt()

Done
```

**Metrics Comparison:**

When `compare_graph_data` is enabled, the `_compare_graph_data_to_gt()` method performs a two-stage comparison [bgpy/tests/engine_tests/utils/engine_tester.py189-210](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_tester.py#L189-L210):

1. **CSV Comparison:** Loads both files as sets of tuples and asserts equality. This catches differences in tabular metrics.
2. **Pickle Comparison:** Loads both pickle files and compares the nested data structures. This validates the full `GraphDataAggregator` state including `DataPointKey` and `DataPointAggData` objects.

The comparison iterates through both directions (guess→gt and gt→guess) to catch both missing and extra data points.

**Sources:**[bgpy/tests/engine_tests/utils/engine_tester.py174-210](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_tester.py#L174-L210)

---

## Diagram Generation

The `_generate_gt_diagrams()` method produces Graphviz diagrams visualizing the AS graph with announcement propagation and outcomes [bgpy/tests/engine_tests/utils/engine_tester.py147-172](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_tester.py#L147-L172)

**Diagram Components:**
ComponentSourcePurposeAS nodes`engine_gt`Show ASes with their policies and local RIB stateEdges`engine_gt`Show AS relationships (customer/provider/peer)Traceback paths`outcomes_gt`Highlight data plane paths to attackers/victimsRanks`conf.as_graph_info.diagram_ranks`Control diagram layout order
The diagram is saved as `ground_truth.gv` in the test's storage directory. The `view=False` parameter prevents automatic opening, as diagrams are aggregated in `pytest_sessionfinish` instead.

**Sources:**[bgpy/tests/engine_tests/utils/engine_tester.py147-172](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_tester.py#L147-L172)

---

## Integration with Test Discovery

Tests using `EngineTester` follow a standard pattern:

```
def test_scenario_name(overwrite, dpi):
    """Test specific scenario configuration"""
    tester = EngineTester(
        scenario_config=scenario_config,
        as_graph_constructor=as_graph_constructor,
        overwrite=overwrite,
        compare_graph_data=False,  # Usually disabled
    )
    tester.test_engine()
```

The `overwrite` and `dpi` fixtures come from `conftest.py` and allow command-line control of test behavior. When `overwrite=True`, the test regenerates ground truth files instead of validating against them.

**Sources:**[bgpy/tests/conftest.py53-60](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/conftest.py#L53-L60)[bgpy/tests/engine_tests/utils/engine_tester.py10-50](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_tester.py#L10-L50)