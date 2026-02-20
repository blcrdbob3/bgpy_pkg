# Simulation Framework Deep Dive
Relevant source files
- [.github/workflows/tests.yml](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/.github/workflows/tests.yml)
- [.pre-commit-config.yaml](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/.pre-commit-config.yaml)
- [LICENSE.txt](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/LICENSE.txt)
- [MANIFEST.in](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/MANIFEST.in)
- [README.md](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/README.md)
- [bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py)
- [bgpy/shared/enums.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/shared/enums.py)
- [bgpy/simulation_framework/scenarios/scenario.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py)
- [bgpy/simulation_framework/scenarios/scenario_config.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py)
- [bgpy/simulation_framework/simulation.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py)
- [pyproject.toml](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml)
- [requirements.txt](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/requirements.txt)
- [requirements_dev.txt](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/requirements_dev.txt)
- [setup.cfg](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/setup.cfg)
- [tox.ini](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/tox.ini)

## Purpose and Scope

This document provides detailed technical documentation of BGPy's simulation framework, focusing on the architecture, execution model, and configuration system. The simulation framework is responsible for orchestrating BGP security simulations across the entire Internet topology, managing parallel execution, and collecting results.

This page covers the high-level architecture and core components of the simulation framework. For detailed information about specific subsystems, see:

- **Simulation execution pipeline and trial management**: [4.1](/blcrdbob3/bgpy_pkg/4.1-simulation-class-and-execution-pipeline)
- **ScenarioConfig and simulation parameters**: [4.2](/blcrdbob3/bgpy_pkg/4.2-scenario-configuration)
- **Parallel processing and performance optimization**: [4.3](/blcrdbob3/bgpy_pkg/4.3-multi-processing-and-performance)

For information about the underlying AS graph structure, see [5](/blcrdbob3/bgpy_pkg/5-as-graph-system). For details about BGP policies and attack scenarios, see [6](/blcrdbob3/bgpy_pkg/6-bgp-policy-reference) and [7](/blcrdbob3/bgpy_pkg/7-attack-scenario-reference) respectively.

---

## System Architecture

The simulation framework is built around the `Simulation` class, which acts as the main orchestrator for all simulation activities. The system follows a clear separation of concerns, with distinct components handling configuration, execution, analysis, and visualization.

### High-Level Component Diagram

```
configures with

creates

uses

constructs

analyzes with

aggregates via

visualizes with

configures

defines policies for

propagates on

examines

feeds data to

provides data to

Simulation
(simulation.py:52)

ScenarioConfig
(scenario_config.py:28)

Scenario
(scenario.py:20)

SimulationEngine
(simulation_engine/)

ASGraph
(as_graphs/)

ASGraphAnalyzer
(as_graph_analyzers/)

GraphDataAggregator
(graph_data_aggregator.py)

GraphFactory
(graphing/)
```

**Sources:**[bgpy/simulation_framework/simulation.py1-605](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L1-L605)[bgpy/simulation_framework/scenarios/scenario_config.py1-243](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L1-L243)[bgpy/simulation_framework/scenarios/scenario.py1-487](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L1-L487)

---

## Core Components

### The Simulation Class

The `Simulation` class is the primary entry point for running simulations. It is responsible for:

1. **Configuration validation** - ensures scenario configs are valid and RAM constraints are met
2. **AS graph construction** - downloads and caches CAIDA topology data
3. **Trial orchestration** - manages multiple trials with different random seeds
4. **Parallel execution** - distributes work across CPU cores when available
5. **Data aggregation** - collects metrics across all trials
6. **Visualization generation** - produces graphs and charts from results

**Key Initialization Parameters:**
ParameterTypeDefaultPurpose`scenario_configs``tuple[ScenarioConfig, ...]`SubprefixHijack with ROVDefines attack/defense scenarios to simulate`percent_adoptions``tuple[float | SpecialPercentAdoptions, ...]``(ONLY_ONE, 0.1, 0.2, 0.5, 0.8, 0.99)`Security policy adoption rates to test`num_trials``int`1Number of randomized trials per adoption rate`parse_cpus``int``cpu_count() - 1`Number of CPU cores for parallel processing`output_dir``Path | None``~/Desktop/sims/{sim_name}`Directory for results and graphs
**Sources:**[bgpy/simulation_framework/simulation.py52-153](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L52-L153)

### ScenarioConfig: Immutable Configuration Objects

`ScenarioConfig` is a frozen dataclass that encapsulates all parameters needed to set up a scenario. Because it is immutable (frozen), the same config can be safely shared across multiple trials and parallel processes.

```
specifies

specifies

specifies

optionally specifies

defines

defines

defines

defines

ScenarioConfig
(frozen dataclass)

ScenarioCls
(e.g., SubprefixHijack)

AdoptPolicyCls
(e.g., ROV)

BasePolicyCls
(e.g., BGP)

AttackerBasePolicyCls
(custom attacker policy)

num_attackers: int

num_victims: int

propagation_rounds: int

adoption_subcategory_attrs
(e.g., stubs, etc, input_clique)
```

**Key Fields:**

- `ScenarioCls`: The attack scenario class (e.g., `PrefixHijack`, `SubprefixHijack`)
- `AdoptPolicyCls`: The security policy being evaluated (e.g., `ROV`, `ASPA`)
- `BasePolicyCls`: The baseline policy for non-adopting ASes (typically `BGP`)
- `AttackerBasePolicyCls`: Optional custom policy for attackers (used for ASPA evasion attacks)
- `propagation_rounds`: Number of BGP propagation rounds to simulate
- `hardcoded_asn_cls_dict`: Mapping of specific ASNs to specific policy classes

**Sources:**[bgpy/simulation_framework/scenarios/scenario_config.py28-243](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L28-L243)

### Scenario: Single Trial Instance

While `ScenarioConfig` is immutable and reused, a `Scenario` object represents a single trial with specific randomly-selected attackers, victims, and adopting ASes.

**Responsibilities:**

1. **Random selection** - chooses attacker, victim, and adopting ASNs based on config
2. **Announcement generation** - creates BGP announcements for the scenario
3. **ROA generation** - generates ROAs for RPKI validation
4. **Policy assignment** - determines which policy each AS should use via `get_policy_cls()`
5. **Engine setup** - configures the simulation engine with announcements and policies
6. **Hooks** - provides `pre_aggregation_hook()` and `post_propagation_hook()` for custom behavior

**Sources:**[bgpy/simulation_framework/scenarios/scenario.py20-487](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L20-L487)

---

## Configuration and Initialization Flow

The following diagram shows how a `Simulation` object is initialized and configured:

```
checks

checks

estimates

warns if

downloads

caches to

Simulation.init()

_validate_scenario_configs()
(line 188)

_validate_ram()
(line 215)

_seed_random()
(line 269)

ASGraphConstructor.run()
(line 258)

output_dir.mkdir()
(line 133)

No duplicate scenario_labels

BGPFull policy consistency

0.9-2.3 GB per core

Estimated > Available

CAIDA relationship data

SINGLE_DAY_CACHE_DIR
```

**Sources:**[bgpy/simulation_framework/simulation.py55-159](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L55-L159)[bgpy/simulation_framework/simulation.py176-248](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L176-L248)

---

## Execution Model Overview

### The run() Method

The simulation execution is triggered by calling `Simulation.run()`. This method orchestrates the entire pipeline:

1. **Cache AS graph** - ensure CAIDA data is downloaded and cached
2. **Run trials** - execute all trials (single-process or multi-process)
3. **Aggregate data** - combine results from all trials
4. **Write outputs** - save CSV, pickle, and YAML files
5. **Generate graphs** - create visualizations using `GraphFactory`

**Sources:**[bgpy/simulation_framework/simulation.py250-267](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L250-L267)

### Trial Execution Strategy

Each simulation runs multiple **trials** to account for randomness in attacker/victim selection and adopting AS selection. For each trial, the system tests multiple **adoption rates** (e.g., 10%, 50%, 80%), and for each adoption rate, it may test multiple **scenario configs** (different attacks or policies).

The execution structure is:

```
for trial in range(num_trials):
    for percent_adoption in percent_adoptions:
        for scenario_config in scenario_configs:
            for propagation_round in range(scenario_config.propagation_rounds):
                # Run simulation engine
                # Analyze outcomes
                # Aggregate results

```

**Sources:**[bgpy/simulation_framework/simulation.py377-439](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L377-L439)

### Single-Process vs Multi-Process Execution

The `Simulation` class supports both single-process and multi-process execution modes:

**Single-Process Mode** (`parse_cpus == 1`):

- Uses `tqdm` progress bar directly in the main process
- Simpler debugging and error handling
- Suitable for small simulations or debugging

**Multi-Process Mode** (`parse_cpus > 1`):

- Uses `multiprocessing.Pool` to distribute trials across CPU cores
- Each worker process gets a **chunk** of trials to execute
- Progress tracking via temporary files in `_tqdm_tracking_dir`
- Each worker reconstructs the AS graph from TSV data (avoids pickling weakrefs)

```
Worker Process 2

Worker Process 1

Main Process

Simulation.run()

_get_chunks(cpus)
Divide trials

multiprocessing.Pool

_update_tqdm_progress_bar()
Monitor temp files

_run_chunk(chunk_id=0)

Reconstruct ASGraph
from TSV

Execute trials[0::cpus]

Write to
{chunk_id}.txt

_run_chunk(chunk_id=1)

Reconstruct ASGraph
from TSV

Execute trials[1::cpus]

Write to
{chunk_id}.txt
```

**Chunk Distribution:**

Trials are distributed using a round-robin approach: `trials[i::cpus]` for worker `i`. This ensures even distribution even if the number of trials is not evenly divisible by the number of CPUs.

Example with 10 trials and 3 CPUs:

- Worker 0: trials [0, 3, 6, 9]
- Worker 1: trials [1, 4, 7]
- Worker 2: trials [2, 5, 8]

**Sources:**[bgpy/simulation_framework/simulation.py309-372](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L309-L372)[bgpy/simulation_framework/simulation.py377-439](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L377-L439)

---

## Data Flow Through the System

### From Simulation to Results

```
loop back for

Simulation.run()

_run_chunk(chunk_id, trials)

Scenario.init()
Select attackers/victims

scenario.setup_engine()
Assign policies

engine.run()
Propagate announcements

ASGraphAnalyzer.analyze()
Determine outcomes

graph_data_aggregator.aggregate_and_store_trial_data()

graph_data_aggregator.write_data()
CSV + Pickle

GraphFactory.generate_graphs()
```

**Sources:**[bgpy/simulation_framework/simulation.py250-267](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L250-L267)[bgpy/simulation_framework/simulation.py499-567](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L499-L567)

### Trial Data Collection

For each engine run, the system collects data through the following pipeline:

1. **Engine completes propagation** - all ASes have processed BGP announcements
2. **ASGraphAnalyzer examines outcomes** - determines if each AS routes to attacker, victim, or is disconnected
3. **TrialData created** - stores numerator/denominator for this specific trial
4. **GraphDataAggregator stores data** - indexed by `DataPointKey` (adoption rate, scenario, round)
5. **Statistical aggregation** - at end, compute means and standard errors across trials

**Key Data Structures:**
ClassPurposeKey Fields`DataPointKey`Uniquely identifies a point on a graph`percent_adopt`, `scenario_config`, `propagation_round``TrialData`Results from a single trial`numerator`, `denominator` (counts of ASes)`DataPointAggData`Aggregated statistics across trials`value` (mean), `yerr` (standard error)
**Sources:**[bgpy/simulation_framework/graph_data_aggregator.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graph_data_aggregator.py)

---

## Key Design Patterns

### Immutability for Safe Parallelization

`ScenarioConfig` is a frozen dataclass, making it immutable and safe to share across processes. This design choice:

- Prevents accidental modification during parallel execution
- Allows hashing for use as dictionary keys
- Enables safe serialization/deserialization

**Sources:**[bgpy/simulation_framework/scenarios/scenario_config.py28-243](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L28-L243)

### Factory Pattern for Extensibility

The simulation framework uses type parameters for key components:

- `ASGraphConstructorCls`: customize how topology is loaded
- `SimulationEngineCls`: customize BGP propagation logic
- `ASGraphAnalyzerCls`: customize outcome analysis
- `GraphDataAggregatorCls`: customize metric collection
- `GraphFactoryCls`: customize visualization generation

This allows users to extend BGPy without modifying core code.

**Sources:**[bgpy/simulation_framework/simulation.py78-109](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L78-L109)

### Hook Methods for Customization

The `Scenario` class provides two hook methods that subclasses can override:

1. **`pre_aggregation_hook()`** - called after engine runs but before data collection

- Useful for validating engine state
- Can modify engine state before analysis
2. **`post_propagation_hook()`** - called after data collection

- Used by `AccidentalRouteLeak` to inject route leaks after initial propagation
- Enables multi-round attacks

**Sources:**[bgpy/simulation_framework/scenarios/scenario.py404-425](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L404-L425)[bgpy/simulation_framework/simulation.py499-537](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L499-L537)

---

## Configuration Validation

The `Simulation` class performs extensive validation during initialization to catch configuration errors early:

### Scenario Config Validation

Checks performed by `_validate_scenario_configs()`:

1. **No duplicate scenario labels** - each `ScenarioConfig` must have a unique `scenario_label`
2. **BGPFull consistency** - if `AdoptPolicyCls` inherits from `BGPFull`, `BasePolicyCls` must also inherit from `BGPFull`

**Rationale:** Duplicate labels would cause metric aggregation to incorrectly combine data from different scenarios. BGPFull policies handle withdrawals, which are incompatible with basic BGP policies.

**Sources:**[bgpy/simulation_framework/simulation.py188-213](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L188-L213)

### RAM Validation

`_validate_ram()` estimates memory usage and warns if available RAM is insufficient:

**Estimated RAM per CPU Core (PyPy):**

- **0.9 GB**: default (no customer/provider cones stored)
- **1.6 GB**: one set of cones stored
- **2.3 GB**: both customer and provider cones stored

The system warns if `estimated_ram * 1.1 > available_ram`.

**Sources:**[bgpy/simulation_framework/simulation.py215-248](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L215-L248)

---

## Output Files and Formats

After simulation completion, results are written to `output_dir`:

### Data Files
FileFormatContents`data.csv`CSVHuman-readable metrics with one row per data point`data.pickle`Python pickle`GraphDataAggregator` object for programmatic access`graphs/*.png`PNG imagesVisualizations generated by `GraphFactory`
### YAML State Files (Testing)

During testing, additional YAML files are generated:

- `engine_gt.yaml`: serialized engine state
- `outcomes_gt.yaml`: serialized outcome classifications
- `metrics_gt.csv/pickle`: ground truth metrics for comparison

**Sources:**[bgpy/simulation_framework/simulation.py573-605](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L573-L605)

---

## Summary

The simulation framework provides a robust, extensible architecture for evaluating BGP security policies:

- **`Simulation`** orchestrates the entire pipeline from configuration to visualization
- **`ScenarioConfig`** provides immutable, reusable configuration objects
- **`Scenario`** represents individual trials with random attacker/victim selection
- **Multi-processing** enables efficient parallel execution across CPU cores
- **Validation** catches configuration errors before expensive computation
- **Extensibility** via factory pattern and hook methods enables customization without modifying core code

For detailed information about specific components, see the subsection pages [4.1](/blcrdbob3/bgpy_pkg/4.1-simulation-class-and-execution-pipeline), [4.2](/blcrdbob3/bgpy_pkg/4.2-scenario-configuration), and [4.3](/blcrdbob3/bgpy_pkg/4.3-multi-processing-and-performance).