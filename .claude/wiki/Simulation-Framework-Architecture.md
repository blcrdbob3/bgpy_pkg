# Simulation Framework Architecture
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

This page provides an architectural overview of the simulation framework, focusing on how the `Simulation` class orchestrates the execution of BGP security scenario evaluations. It covers the initialization process, the configuration system through `ScenarioConfig`, and how different components interact during simulation execution.

For detailed information about specific components:

- For the step-by-step execution pipeline and propagation mechanics, see [Simulation Class and Execution Pipeline](/blcrdbob3/bgpy_pkg/4.1-simulation-class-and-execution-pipeline)
- For AS graph topology construction and properties, see [AS Graph Structure and Properties](/blcrdbob3/bgpy_pkg/5.1-as-graph-structure-and-properties)
- For policy implementation details, see [Base BGP Policies](/blcrdbob3/bgpy_pkg/6.1-base-bgp-policies)
- For attack scenario implementations, see [Pre-ROV Attack Scenarios](/blcrdbob3/bgpy_pkg/7.1-pre-rov-attack-scenarios)

---

## The Simulation Orchestrator

The `Simulation` class serves as the central coordinator for all BGP security simulations. It manages the entire lifecycle from configuration to result generation, coordinating five primary subsystems:

**Sources:**[bgpy/simulation_framework/simulation.py52-153](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L52-L153)

```
Analysis Pipeline

Execution Components

Configuration System

Core Orchestration

User Interface Layer

CLI Entry Point
main.py

Simulation.init()
Configuration & Validation

Simulation.run()
Main Coordinator

scenario_configs
tuple[ScenarioConfig, ...]

percent_adoptions
tuple[float | SpecialPercentAdoptions, ...]

ScenarioConfig
ScenarioCls, AdoptPolicyCls
BasePolicyCls, num_attackers, etc.

ASGraphConstructorCls
CAIDAASGraphConstructor
Downloads & Constructs Topology

SimulationEngineCls
SimulationEngine
BGP Propagation Logic

ScenarioCls
Scenario Instances
Attack Implementation

ASGraphAnalyzerCls
ASGraphAnalyzer
Outcome Classification

GraphDataAggregatorCls
GraphDataAggregator
Statistical Aggregation

GraphFactory
Visualization Generation
```

**Sources:**[bgpy/simulation_framework/simulation.py55-153](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L55-L153)

---

## Initialization Architecture

The `Simulation.__init__()` method establishes the simulation environment through a multi-stage initialization process:

**Sources:**[bgpy/simulation_framework/simulation.py55-160](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L55-L160)

```
Stage 6: Tracking Setup

Stage 5: Component Classes

Stage 4: Validation

Stage 3: Path Setup

Stage 2: Random Seeding

Stage 1: Parameter Storage

Simulation.init()

Store Configuration
percent_adoptions
num_trials
parse_cpus
scenario_configs

_seed_random()
Set python_hash_seed
Validate PYTHONHASHSEED env

Configure Paths
sim_name → default_sim_name
output_dir → default_output_dir
Create directories

_validate_scenario_configs()
Check BGPFull mixups
Prevent duplicate labels

_validate_ram()
Estimate memory usage
Warn if insufficient

Store Class References
ASGraphConstructorCls
SimulationEngineCls
ASGraphAnalyzerCls
GraphDataAggregatorCls

Create _tqdm_tracking_dir
Temporary directory for
multiprocess progress tracking
```

**Sources:**[bgpy/simulation_framework/simulation.py55-160](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L55-L160)

### Key Initialization Parameters
ParameterTypeDefaultPurpose`sim_name``str | None``"bgpy_sims"`Identifies this simulation run`percent_adoptions``tuple[float | SpecialPercentAdoptions, ...]``(ONLY_ONE, 0.1, 0.2, 0.5, 0.8, 0.99)`Policy adoption rates to test`scenario_configs``tuple[ScenarioConfig, ...]``(ScenarioConfig(...),)`Attack/defense scenarios to evaluate`num_trials``int``args.trials` (CLI arg)Statistical sample size`parse_cpus``int``max(cpu_count() - 1, 1)`Parallel processing cores`python_hash_seed``int | None``None`Reproducibility seed`ASGraphConstructorCls``type[ASGraphConstructor]``CAIDAASGraphConstructor`Topology builder`SimulationEngineCls``type[BaseSimulationEngine]``SimulationEngine`BGP propagation engine
**Sources:**[bgpy/simulation_framework/simulation.py55-109](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L55-L109)

---

## Configuration System: ScenarioConfig

The `ScenarioConfig` dataclass encapsulates all parameters needed to define a simulation scenario. It is immutable (`frozen=True`) to enable safe reuse across multiple trials.

**Sources:**[bgpy/simulation_framework/scenarios/scenario_config.py28-81](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L28-L81)

```
ScenarioConfig Attributes

Core Configuration
ScenarioCls: type[Scenario]
propagation_rounds: int

Policy Configuration
BasePolicyCls: type[Policy]
AdoptPolicyCls: type[Policy]
AttackerBasePolicyCls: type[Policy] | None

Participant Selection
num_attackers: int
num_victims: int
attacker_subcategory_attr: str
victim_subcategory_attr: str

Adoption Configuration
adoption_subcategory_attrs: tuple[str, ...]
hardcoded_asn_cls_dict: frozendict[int, type[Policy]]
hardcoded_base_asn_cls_dict: frozendict[int, type[Policy]]

Override Parameters
override_attacker_asns: frozenset[int] | None
override_victim_asns: frozenset[int] | None
override_adopting_asns: frozenset[int] | None
override_announcements: tuple[Ann, ...] | None
override_roas: tuple[ROA, ...] | None

Labeling
scenario_label: str
csv_label: str
```

**Sources:**[bgpy/simulation_framework/scenarios/scenario_config.py28-81](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L28-L81)

### ScenarioConfig Post-Initialization Logic

The `__post_init__()` method performs critical setup and validation:

**Sources:**[bgpy/simulation_framework/scenarios/scenario_config.py82-133](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L82-L133)
StepMethod/LogicPurpose1. Set `propagation_rounds`Line 94-109Defaults to `ScenarioCls.min_propagation_rounds`; BGP-iSec requires 2 rounds2. Validate minimum roundsLine 111-117Ensures scenario requirements are met3. Default `AdoptPolicyCls`Line 119-120If `MISSINGPolicy`, set to `BasePolicyCls`4. Validate `hardcoded_asn_cls_dict`Line 122-127Must be `frozendict` for immutability5. Set `scenario_label`Line 129-130Defaults to `AdoptPolicyCls.name`6. Set `AttackerBasePolicyCls`Line 135-144Auto-configures for ASPA scenarios7. Validate withdrawal mixingLine 146-159Warns when mixing `BGPFull` with non-`BGPFull` policies
**Sources:**[bgpy/simulation_framework/scenarios/scenario_config.py82-173](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L82-L173)

---

## High-Level Execution Flow

The `Simulation.run()` method orchestrates the complete simulation lifecycle:

**Sources:**[bgpy/simulation_framework/simulation.py250-267](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L250-L267)

```
Phase 5: Cleanup

Phase 4: Visualization

Phase 3: Persistence

Phase 2: Trial Execution

Phase 1: Graph Preparation

Simulation.run()

ASGraphConstructorCls.run()
Download CAIDA data
Cache TSV file

_get_data()
Run all trials
Single or multiprocess

GraphDataAggregator
Accumulate results

write_data()
CSV + Pickle outputs

_graph_data()
GraphFactory.generate_graphs()

Delete aggregator
gc.collect()
rmtree(_tqdm_tracking_dir)
```

**Sources:**[bgpy/simulation_framework/simulation.py250-267](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L250-L267)

### Single-Process vs Multi-Process Execution

The `_get_data()` method selects execution mode based on `parse_cpus`:

**Sources:**[bgpy/simulation_framework/simulation.py283-303](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L283-L303)
ModeConditionMethodProgress Tracking**Single-Process**`parse_cpus == 1``_get_single_process_results()``tqdm` in `_get_run_chunk_iter()`**Multi-Process**`parse_cpus > 1``_get_mp_results()`File-based via `_tqdm_tracking_dir`
**Multi-Processing Architecture:**

```
Worker Process 2

Worker Process 1

Main Process

_get_chunks(parse_cpus)
Split trials into chunks
trials[i::cpus]

multiprocessing.Pool(parse_cpus)

apply_async(_run_chunk, (chunk_id, trials))

While tasks running:
_update_tqdm_progress_bar()
Read {chunk_id}.txt files

Collect completed tasks
Sum GraphDataAggregators

_run_chunk(0, trials[0::cpus])
_seed_random(seed_suffix='0')
_get_engine_for_run_chunk()

_write_tqdm_progress(0, completed)
Write to _tqdm_tracking_dir/0.txt

_run_chunk(1, trials[1::cpus])
_seed_random(seed_suffix='1')
_get_engine_for_run_chunk()

_write_tqdm_progress(1, completed)
Write to _tqdm_tracking_dir/1.txt
```

**Sources:**[bgpy/simulation_framework/simulation.py309-372](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L309-L372)[bgpy/simulation_framework/simulation.py377-439](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L377-L439)

**Why reconstruct the AS graph per worker?** The engine contains `weakref` objects which cannot be pickled for multiprocessing. Each worker reconstructs the graph from cached TSV data instead.

**Sources:**[bgpy/simulation_framework/simulation.py461-474](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L461-L474)

---

## Trial Execution Details

Each chunk processes multiple trials, iterating over percent adoptions and scenario configs:

**Sources:**[bgpy/simulation_framework/simulation.py377-439](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L377-L439)

```
Trial Loop

Reuse Logic

Setup

_run_chunk(chunk_id, trials)

_seed_random(seed_suffix=chunk_id)

_get_engine_for_run_chunk()
Reconstruct ASGraph from TSV
Create SimulationEngine

GraphDataAggregator()
Initialize for this chunk

_get_reuse_attacker_asns()
_get_reuse_victim_asns()
_get_reuse_adopting_asns()

for trial in trials:

trial_attacker_asns = None
trial_victim_asns = None

for percent_adopt in percent_adoptions:

adopting_asns = None

for scenario_config in scenario_configs:

scenario = ScenarioCls(
scenario_config,
percent_adopt,
engine,
trial_attacker_asns,
trial_victim_asns,
adopting_asns
)

scenario.setup_engine(engine)

for propagation_round in range(propagation_rounds):

_single_engine_run(
engine, percent_adopt,
trial, scenario,
propagation_round,
graph_data_aggregator
)

if reuse_attacker_asns:
  trial_attacker_asns = scenario.attacker_asns
if reuse_victim_asns:
  trial_victim_asns = scenario.victim_asns
if reuse_adopting_asns:
  adopting_asns = scenario.adopting_asns

_write_tqdm_progress(chunk_id, completed)
```

**Sources:**[bgpy/simulation_framework/simulation.py377-439](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L377-L439)

### ASN Reuse Strategy

To ensure fair comparisons across scenarios, the framework reuses attacker, victim, and adopting ASNs when possible:

**Sources:**[bgpy/simulation_framework/simulation.py441-459](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L441-L459)
MethodConditionPurpose`_get_reuse_attacker_asns()`All configs have same `num_attackers` and `attacker_subcategory_attr`Compare different policies against the same attacker`_get_reuse_victim_asns()`All configs have same `num_victims` and `victim_subcategory_attr`Keep victim constant across scenarios`_get_reuse_adopting_asns()`All configs have same `adoption_subcategory_attrs`Isolate policy differences from adoption distribution
**Sources:**[bgpy/simulation_framework/simulation.py441-459](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L441-L459)

---

## Single Engine Run Lifecycle

The `_single_engine_run()` method executes one propagation round with hooks for scenario customization:

**Sources:**[bgpy/simulation_framework/simulation.py499-537](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L499-L537)

```
_single_engine_run()

engine.run(
propagation_round,
scenario
)

scenario.pre_aggregation_hook(
  engine,
  percent_adopt,
  trial,
  propagation_round
)

_collect_engine_run_data()
1. ASGraphAnalyzer.analyze()
2. graph_data_aggregator.aggregate_and_store_trial_data()

scenario.post_propagation_hook(
  engine,
  percent_adopt,
  trial,
  propagation_round
)
```

**Sources:**[bgpy/simulation_framework/simulation.py499-567](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L499-L567)

### Hook Usage Examples
HookUsed ByPurpose`pre_aggregation_hook()`(Default: no-op)Modify state before outcome analysis`post_propagation_hook()``AccidentalRouteLeak`Inject route leaks after initial propagation
**Sources:**[bgpy/simulation_framework/scenarios/scenario.py404-425](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L404-L425)

---

## Scenario Instantiation Process

When a `Scenario` instance is created, it performs random selection and initialization:

**Sources:**[bgpy/simulation_framework/scenarios/scenario.py33-89](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L33-L89)

```
Prefix Hierarchy

Announcement & ROA Setup

ASN Selection

Validation

Scenario.init()

assert scenario_config.ScenarioCls == self.class

_get_attacker_asns(
override_attacker_asns,
prev_attacker_asns,
engine
)

_get_victim_asns(
override_victim_asns,
prev_victim_asns,
engine
)

_get_adopting_asns(
override_adopting_asns,
prev_adopting_asns,
engine
)

announcements = _get_announcements(engine)
or scenario_config.override_announcements

roas = _get_roas(announcements, engine)
or scenario_config.override_roas

_reset_and_add_roas_to_roa_checker()
Policy.roa_checker.clear()
Insert all ROAs

ordered_prefix_subprefix_dict =
_get_ordered_prefix_subprefix_dict()
Maps each prefix to its subprefixes
```

**Sources:**[bgpy/simulation_framework/scenarios/scenario.py33-89](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L33-L89)

### Attacker Selection Logic

The `_get_attacker_asns()` method has multiple branches:

**Sources:**[bgpy/simulation_framework/scenarios/scenario.py101-166](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L101-L166)
BranchConditionAction0`override_attacker_asns` providedUse override (from YAML)1Previous attackers match `num_attackers`Reuse previous attackers2Previous attackers < `num_attackers`Add more attackers to superset3First initializationRandom sample from `_get_possible_attacker_asns()`
**Sources:**[bgpy/simulation_framework/scenarios/scenario.py101-166](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L101-L166)

### Adopting ASN Randomization

The `_get_randomized_adopting_asns()` method handles special adoption values:

**Sources:**[bgpy/simulation_framework/scenarios/scenario.py262-301](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L262-L301)
`percent_adoption`Value of `k`Meaning`SpecialPercentAdoptions.ONLY_ONE``1`Exactly one AS adopts (minimum deployment)`SpecialPercentAdoptions.ALL_BUT_ONE``len(possible_adopters) - 1`Nearly full deployment`0.0``0`No adoption (testing baseline)`0.1` to `0.99``math.ceil(len(possible_adopters) * percent)`Proportional adoption
**Sources:**[bgpy/simulation_framework/scenarios/scenario.py262-301](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L262-L301)

---

## Policy Assignment Mechanism

During `scenario.setup_engine()`, each AS receives its policy class via `get_policy_cls()`:

**Sources:**[bgpy/simulation_framework/scenarios/scenario.py350-373](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L350-L373)

```
Yes

No

Yes

No

Yes

No

Yes

No

Yes

No

scenario.get_policy_cls(as_obj)

asn in attacker_asns
AND AttackerBasePolicyCls?

asn in _default_adopters?

asn in hardcoded_asn_cls_dict?

asn in adopting_asns?

asn in hardcoded_base_asn_cls_dict?

return AttackerBasePolicyCls

return AdoptPolicyCls

return hardcoded_asn_cls_dict[asn]

return AdoptPolicyCls

return hardcoded_base_asn_cls_dict[asn]

return BasePolicyCls
```

**Sources:**[bgpy/simulation_framework/scenarios/scenario.py358-373](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L358-L373)

**Priority Order:**

1. Attacker-specific policy (if `AttackerBasePolicyCls` set)
2. Default adopters (victims always adopt by default)
3. Hardcoded ASN overrides (`hardcoded_asn_cls_dict`)
4. Randomly selected adopting ASNs
5. Hardcoded base ASN overrides (`hardcoded_base_asn_cls_dict`)
6. Base policy (`BasePolicyCls`)

**Sources:**[bgpy/simulation_framework/scenarios/scenario.py358-373](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L358-L373)

---

## Output Generation

After trial execution completes, results are persisted and visualized:

**Sources:**[bgpy/simulation_framework/simulation.py259-267](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L259-L267)

### Data Persistence
FileFormatContentGenerated By`data.csv`CSVHuman-readable metrics table`GraphDataAggregator.write_data()``data.pickle`PicklePython objects for re-analysis`GraphDataAggregator.write_data()``graphs/*.png`PNGVisualization plots`GraphFactory.generate_graphs()`
**Sources:**[bgpy/simulation_framework/simulation.py573-604](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L573-L604)

### Default Output Directory

```
default_output_dir = Path(DIRS.user_desktop_dir) / "sims" / sim_name
# Example: ~/Desktop/sims/bgpy_sims/
```

**Sources:**[bgpy/simulation_framework/simulation.py165-167](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L165-L167)

---

## Validation Mechanisms

The `Simulation` class performs multiple validation checks during initialization:

**Sources:**[bgpy/simulation_framework/simulation.py176-248](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L176-L248)

### Scenario Configuration Validation

**Method:**`_validate_scenario_configs()`

**Checks:**

```
Yes

No

Yes

No

_validate_scenario_configs()

AdoptPolicyCls inherits
from BGPFull
BUT
BasePolicyCls does NOT?

raise TypeError
'You may want to pass
BasePolicyCls=BGPFull'

Duplicate
scenario_labels?

raise ValueError
'Please pass unique
scenario_label'

Validation passes
```

**Sources:**[bgpy/simulation_framework/simulation.py188-213](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L188-L213)

### RAM Validation

**Method:**`_validate_ram()`

Estimates memory usage based on graph storage configuration:

**Sources:**[bgpy/simulation_framework/simulation.py215-248](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L215-L248)
ConfigurationRAM per Core (PyPy)Both customer & provider cones stored2.3 GBOne cone type stored1.6 GBNo cone ASNs stored (default)0.9 GB
Formula: `expected_ram = parse_cpus * gb_per_core`

If `expected_ram * 1.1 > available_ram`, a warning is issued.

**Sources:**[bgpy/simulation_framework/simulation.py215-248](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L215-L248)

---

## Key Extension Points

Users can customize simulations by subclassing or providing alternative implementations:
Extension PointDefaultPurposeReferenced In`ASGraphConstructorCls``CAIDAASGraphConstructor`Topology source[AS Graph Structure](/blcrdbob3/bgpy_pkg/5.1-as-graph-structure-and-properties)`SimulationEngineCls``SimulationEngine`Propagation logic[Simulation Class](/blcrdbob3/bgpy_pkg/4.1-simulation-class-and-execution-pipeline)`ASGraphAnalyzerCls``ASGraphAnalyzer`Outcome classification[Outcome Analysis](/blcrdbob3/bgpy_pkg/8.1-outcome-analysis)`GraphDataAggregatorCls``GraphDataAggregator`Statistical aggregation[Data Aggregation](/blcrdbob3/bgpy_pkg/8.2-data-aggregation)`GraphFactoryCls``GraphFactory`Visualization generation[Graph Generation](/blcrdbob3/bgpy_pkg/8.3-graph-generation)`ScenarioCls`Various (e.g., `SubprefixHijack`)Attack implementation[Attack Scenarios](/blcrdbob3/bgpy_pkg/7.1-pre-rov-attack-scenarios)`AdoptPolicyCls`Various (e.g., `ROV`)Security policy[BGP Policies](/blcrdbob3/bgpy_pkg/6.1-base-bgp-policies)
**Sources:**[bgpy/simulation_framework/simulation.py55-109](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L55-L109)[bgpy/simulation_framework/simulation.py250-254](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L250-L254)

---

## Summary

The `Simulation` class provides a comprehensive framework for evaluating BGP security mechanisms through:

1. **Declarative Configuration**: `ScenarioConfig` objects define attack scenarios and policies without procedural code
2. **Statistical Rigor**: Multiple trials with configurable adoption rates enable confidence in results
3. **Scalability**: Automatic multiprocessing based on available CPU cores
4. **Reproducibility**: Random seeding with validation ensures deterministic results
5. **Extensibility**: Class-based injection points allow custom implementations
6. **Robustness**: Validation checks prevent common configuration errors

The orchestration flow ensures that complex simulations involving thousands of ASes, multiple attack types, and various security policies can be executed with minimal user code, while still providing extensive customization options for advanced users.

**Sources:**[bgpy/simulation_framework/simulation.py1-605](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L1-L605)[bgpy/simulation_framework/scenarios/scenario_config.py1-243](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L1-L243)[bgpy/simulation_framework/scenarios/scenario.py1-487](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L1-L487)