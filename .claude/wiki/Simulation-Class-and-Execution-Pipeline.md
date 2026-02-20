# Simulation Class and Execution Pipeline
Relevant source files
- [.github/workflows/tests.yml](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/.github/workflows/tests.yml)
- [.pre-commit-config.yaml](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/.pre-commit-config.yaml)
- [LICENSE.txt](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/LICENSE.txt)
- [MANIFEST.in](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/MANIFEST.in)
- [README.md](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/README.md)
- [bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py)
- [bgpy/shared/enums.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/shared/enums.py)
- [bgpy/simulation_engine/policies/bgp/bgp/gao_rexford.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/gao_rexford.py)
- [bgpy/simulation_engine/policies/custom_attackers/first_asn_stripping_prefix_aspa_attacker.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/custom_attackers/first_asn_stripping_prefix_aspa_attacker.py)
- [bgpy/simulation_engine/policies/custom_attackers/shortest_path_prefix_aspa_attacker.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/custom_attackers/shortest_path_prefix_aspa_attacker.py)
- [bgpy/simulation_engine/simulation_engines/base_simulation_engine.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/simulation_engines/base_simulation_engine.py)
- [bgpy/simulation_engine/simulation_engines/simulation_engine.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/simulation_engines/simulation_engine.py)
- [bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py)
- [bgpy/simulation_framework/scenarios/custom_scenarios/victims_prefix.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/victims_prefix.py)
- [bgpy/simulation_framework/scenarios/scenario.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py)
- [bgpy/simulation_framework/scenarios/scenario_config.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py)
- [bgpy/simulation_framework/simulation.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py)
- [pyproject.toml](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml)
- [requirements.txt](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/requirements.txt)
- [requirements_dev.txt](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/requirements_dev.txt)
- [setup.cfg](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/setup.cfg)
- [tox.ini](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/tox.ini)

## Purpose and Scope

This page documents the `Simulation` class and the execution pipeline that orchestrates BGP security simulations. The `Simulation` class is the main entry point for running simulations, coordinating scenario configuration, AS graph construction, trial execution, data collection, and visualization.

For information about scenario and policy configuration, see [Scenario Configuration](/blcrdbob3/bgpy_pkg/4.2-scenario-configuration). For details on parallel execution and performance, see [Multi-Processing and Performance](/blcrdbob3/bgpy_pkg/4.3-multi-processing-and-performance). For AS graph construction details, see [AS Graph System](/blcrdbob3/bgpy_pkg/5-as-graph-system). For analysis and visualization details, see [Analysis and Visualization](/blcrdbob3/bgpy_pkg/8-analysis-and-visualization).

---

## Simulation Class Overview

The `Simulation` class ([bgpy/simulation_framework/simulation.py52-605](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L52-L605)) serves as the main orchestrator for BGP security simulations. It manages the complete lifecycle from initialization through data collection and visualization.

### Key Responsibilities
ResponsibilityMethodsDescription**Configuration**`__init__`, `_validate_init`Parse and validate simulation parameters**Execution**`run`, `_get_data`Orchestrate trial execution and data collection**Trial Management**`_run_chunk`, `_single_engine_run`Execute individual trials and propagation rounds**Multi-Processing**`_get_chunks`, `_get_mp_results`Distribute work across CPU cores**Output**`_graph_data`, `csv_path`, `pickle_path`Generate results and visualizations
**Sources:**[bgpy/simulation_framework/simulation.py52-605](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L52-L605)

---

## Class Initialization

The `Simulation.__init__` method ([bgpy/simulation_framework/simulation.py55-159](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L55-L159)) initializes all components needed for simulation execution.

### Initialization Parameters

```
def __init__(
    self,
    *,
    sim_name: str | None = None,
    percent_adoptions: tuple[float | SpecialPercentAdoptions, ...] = (...),
    scenario_configs: tuple[ScenarioConfig, ...] = (...),
    num_trials: int = args.trials,
    output_dir: Path | None = None,
    parse_cpus: int = max(cpu_count() - 1, 1),
    python_hash_seed: int | None = None,
    ASGraphConstructorCls: type[ASGraphConstructor] = CAIDAASGraphConstructor,
    as_graph_constructor_kwargs=frozendict(...),
    SimulationEngineCls: type[BaseSimulationEngine] = SimulationEngine,
    ASGraphAnalyzerCls: type[BaseASGraphAnalyzer] = ASGraphAnalyzer,
    GraphDataAggregatorCls: type[GraphDataAggregator] = GraphDataAggregator,
    data_plane_tracking: bool = True,
    control_plane_tracking: bool = False,
    graph_categories: tuple[GraphCategory, ...] = tuple(get_all_graph_categories()),
)
```

### Initialization Flow Diagram

```
init called

Store parameters:
percent_adoptions,
num_trials,
parse_cpus

_get_filtered_scenario_configs:
Filter scenario_configs

_seed_random:
Seed random with
python_hash_seed

Set sim_name and
output_dir paths

_validate_init

_validate_scenario_configs:
Check for duplicate labels,
BGPFull consistency

_validate_ram:
Check memory requirements
based on cone storage

Store class references:
ASGraphConstructorCls,
SimulationEngineCls,
ASGraphAnalyzerCls

Create _tqdm_tracking_dir
for progress monitoring

Initialization complete
```

### Validation Details

**Scenario Configuration Validation** ([bgpy/simulation_framework/simulation.py188-213](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L188-L213)):

- Checks for duplicate `scenario_label` values that would break aggregation
- Ensures `BasePolicyCls` is `BGPFull` if `AdoptPolicyCls` inherits from `BGPFull`
- Prevents mixing withdrawal-capable policies with non-withdrawal policies

**RAM Validation** ([bgpy/simulation_framework/simulation.py215-248](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L215-L248)):

- Estimates RAM usage based on cone storage settings:

- Both customer and provider cones: 2.3 GB per core
- Single cone type: 1.6 GB per core
- No cone storage: 0.9 GB per core
- Compares estimated usage against available RAM
- Issues warning if usage exceeds 110% of available memory

**Sources:**[bgpy/simulation_framework/simulation.py55-248](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L55-L248)

---

## Execution Pipeline

The `Simulation.run` method ([bgpy/simulation_framework/simulation.py250-267](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L250-L267)) orchestrates the complete simulation pipeline.

### Pipeline Stages Diagram

```
run method

ASGraphConstructorCls.run:
Cache CAIDA graph

_get_data:
Execute all trials

write_data:
Save to csv_path
and pickle_path

_graph_data:
Generate graphs via
GraphFactoryCls

Cleanup:
Delete aggregator,
gc.collect,
rmtree tracking_dir

Simulation complete
```

### Data Collection (`_get_data`)

The `_get_data` method ([bgpy/simulation_framework/simulation.py283-303](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L283-L303)) determines execution mode:

```
def _get_data(self):
    """Runs trials for graph and aggregates data"""
    
    # Single process
    if self.parse_cpus == 1:
        return sum(
            self._get_single_process_results(),
            start=self.GraphDataAggregatorCls(
                graph_categories=self.graph_categories
            ),
        )
    # Multiprocess
    else:
        return sum(
            self._get_mp_results(),
            start=self.GraphDataAggregatorCls(
                graph_categories=self.graph_categories
            ),
        )
```

**Single-Process Mode** ([bgpy/simulation_framework/simulation.py322-325](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L322-L325)):

- Uses `tqdm` progress bar directly in main process
- Calls `_run_chunk` for each chunk sequentially
- Simpler debugging and deterministic execution order

**Multi-Process Mode** ([bgpy/simulation_framework/simulation.py327-348](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L327-L348)):

- Uses `multiprocessing.Pool` with `apply_async`
- Distributes trial chunks across `parse_cpus` workers
- File-based progress tracking via `_tqdm_tracking_dir`
- Main process monitors completion and updates progress bar

**Sources:**[bgpy/simulation_framework/simulation.py250-348](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L250-L348)

---

## Trial Execution Flow

The `_run_chunk` method ([bgpy/simulation_framework/simulation.py377-439](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L377-L439)) executes a subset of trials assigned to one worker process.

### Trial Chunk Execution Diagram

```
Yes

No

Yes

No

Yes

No

Yes

No

_run_chunk(chunk_id, trials)

_seed_random(chunk_id):
Seed randomness per chunk

_get_engine_for_run_chunk:
Reconstruct ASGraph
and SimulationEngine

Create GraphDataAggregator

Determine reuse flags:
_get_reuse_attacker_asns,
_get_reuse_victim_asns,
_get_reuse_adopting_asns

For each trial in trials

trial_attacker_asns = None
trial_victim_asns = None

For each percent_adopt
in percent_adoptions

adopting_asns = None

For each scenario_config
in scenario_configs

Create Scenario instance:
Pass attacker_asns,
victim_asns,
adopting_asns if reused

scenario.setup_engine(engine):
Set AS policy classes,
seed announcements

For propagation_round
in range(propagation_rounds)

_single_engine_run:
Run engine.run,
hooks, collect data

More prop rounds?

If reuse_*_asns:
Save attacker_asns,
victim_asns,
adopting_asns

More scenarios?

_write_tqdm_progress:
Update progress file

More adoptions?

More trials?

Return GraphDataAggregator
```

### ASN Reuse Logic

The simulation reuses attacker, victim, and adopting ASNs when appropriate for statistical consistency:

**Attacker ASN Reuse** ([bgpy/simulation_framework/simulation.py441-446](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L441-L446)):

- Reuses across percent adoptions and scenario configs if:

- All scenario configs have same `num_attackers`
- All scenario configs have same `attacker_subcategory_attr`

**Victim ASN Reuse** ([bgpy/simulation_framework/simulation.py448-453](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L448-L453)):

- Reuses across percent adoptions and scenario configs if:

- All scenario configs have same `num_victims`
- All scenario configs have same `victim_subcategory_attr`

**Adopting ASN Reuse** ([bgpy/simulation_framework/simulation.py455-459](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L455-L459)):

- Reuses across scenario configs (but not percent adoptions) if:

- All scenario configs have same `adoption_subcategory_attrs`

**Sources:**[bgpy/simulation_framework/simulation.py377-459](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L377-L459)

---

## Engine Setup and Propagation

### Engine Construction for Worker Processes

The `_get_engine_for_run_chunk` method ([bgpy/simulation_framework/simulation.py461-474](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L461-L474)) creates a fresh `SimulationEngine` for each worker:

```
def _get_engine_for_run_chunk(self) -> BaseSimulationEngine:
    """Returns SimulationEngine for the _run_chunk method
    
    engine isn't picklable or dillable, as it has weakrefs, which
    will deserialize to dead refs
    """
    constructor_kwargs = dict(self.as_graph_constructor_kwargs)
    constructor_kwargs["tsv_path"] = None
    as_graph: ASGraph = self.ASGraphConstructorCls(**constructor_kwargs).run()
    engine = self.SimulationEngineCls(
        as_graph,
        cached_as_graph_tsv_path=self.as_graph_constructor_kwargs.get("tsv_path"),
    )
    return engine
```

**Key Implementation Detail:** The AS graph is reconstructed from cached TSV data rather than pickled, because the graph contains `weakref` objects that would deserialize to dead references.

### Single Engine Run

The `_single_engine_run` method ([bgpy/simulation_framework/simulation.py499-537](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L499-L537)) executes one propagation round:

```
_single_engine_run

engine.run:
Execute propagation

scenario.pre_aggregation_hook:
Custom pre-analysis logic

_collect_engine_run_data:
Analyze outcomes,
aggregate metrics

scenario.post_propagation_hook:
Custom post-prop logic

Return
```

### SimulationEngine Propagation

The `SimulationEngine.run` method ([bgpy/simulation_engine/simulation_engines/simulation_engine.py61-74](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/simulation_engines/simulation_engine.py#L61-L74)) validates state and invokes propagation:

```
def run(self, propagation_round: int = 0, scenario: Optional["Scenario"] = None):
    """Propogates announcements and ensures proper setup"""
    
    # Ensure that the simulator is ready to run this round
    if self.ready_to_run_round != propagation_round:
        raise RuntimeError(
            f"Engine not set up to run for {propagation_round} round"
        )
    assert scenario, "This can't be empty"
    
    # Propogate anns
    self._propagate(propagation_round, scenario)
    # Increment the ready to run round
    self.ready_to_run_round += 1
```

### Gao-Rexford Propagation Order

The `_propagate` method ([bgpy/simulation_engine/simulation_engines/simulation_engine.py76-143](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/simulation_engines/simulation_engine.py#L76-L143)) follows Gao-Rexford valley-free routing:

```
_propagate

_propagate_to_providers:
Ascending propagation_ranks

_propagate_to_peers:
All ASes simultaneously

_propagate_to_customers:
Descending propagation_ranks
```

**Propagation Ranks** are computed during AS graph construction based on customer-provider relationships. Lower ranks (stubs) propagate first to higher ranks (input clique), then back down.

**Sources:**

- [bgpy/simulation_framework/simulation.py461-567](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L461-L567)
- [bgpy/simulation_engine/simulation_engines/simulation_engine.py20-143](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/simulation_engines/simulation_engine.py#L20-L143)

---

## Scenario and Policy Assignment

### Scenario Initialization

When a `Scenario` is instantiated ([bgpy/simulation_framework/scenarios/scenario.py33-89](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L33-L89)), it:

1. Validates `scenario_config.ScenarioCls` matches the instantiated class
2. Gets attacker ASNs via `_get_attacker_asns`
3. Gets victim ASNs via `_get_victim_asns`
4. Gets adopting ASNs via `_get_adopting_asns`
5. Gets announcements via `_get_announcements`
6. Gets ROAs via `_get_roas`
7. Resets `Policy.roa_checker` and adds new ROAs

### Engine Setup by Scenario

The `Scenario.setup_engine` method ([bgpy/simulation_framework/scenarios/scenario.py350-356](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L350-L356)) calls `engine.setup(self)`, which triggers:

**SimulationEngine.setup** ([bgpy/simulation_engine/simulation_engines/simulation_engine.py20-25](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/simulation_engines/simulation_engine.py#L20-L25)):

```
def setup(self, scenario: "Scenario") -> None:
    """Sets AS classes and seeds announcements"""
    
    self._set_as_classes(scenario)
    self._seed_announcements(scenario.announcements)
    self.ready_to_run_round = 0
```

### Policy Class Assignment

The `SimulationEngine._set_as_classes` method ([bgpy/simulation_engine/simulation_engines/simulation_engine.py27-42](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/simulation_engines/simulation_engine.py#L27-L42)) assigns policy classes to each AS:

```
def _set_as_classes(self, scenario: "Scenario") -> None:
    """Resets Engine ASes and changes their AS class"""
    
    for as_obj in self.as_graph:
        # Delete the old policy and remove references
        del as_obj.policy.as_
        # set the AS class to be the proper type of AS
        Cls = scenario.get_policy_cls(as_obj)
        as_obj.policy = Cls(as_=as_obj)
```

### Policy Selection Logic

The `Scenario.get_policy_cls` method ([bgpy/simulation_framework/scenarios/scenario.py358-373](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L358-L373)) determines which policy class to assign:

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

get_policy_cls(as_obj)

Is AS in
attacker_asns?

Return
AttackerBasePolicyCls
if defined

Is AS in
_default_adopters
victim_asns?

Return
AdoptPolicyCls

Is AS in
hardcoded_asn_cls_dict?

Return
hardcoded_asn_cls_dict[asn]

Is AS in
adopting_asns?

Return
AdoptPolicyCls

Is AS in
hardcoded_base_asn_cls_dict?

Return
hardcoded_base_asn_cls_dict[asn]

Return
BasePolicyCls
```

**Sources:**

- [bgpy/simulation_framework/scenarios/scenario.py33-373](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L33-L373)
- [bgpy/simulation_engine/simulation_engines/simulation_engine.py20-55](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/simulation_engines/simulation_engine.py#L20-L55)

---

## Hooks System

The scenario hooks provide extension points for custom behavior during simulation execution.

### Hook Types
HookCalled WhenTypical Use Cases`pre_aggregation_hook`After `engine.run`, before data collectionState validation, debugging`post_propagation_hook`After data collectionMulti-round scenarios, state modification
### Hook Invocation Sequence

```
ASGraphAnalyzer
Scenario
SimulationEngine
Simulation
ASGraphAnalyzer
Scenario
SimulationEngine
Simulation
engine.run(propagation_round, scenario)
_propagate(propagation_round, scenario)
Propagation complete
pre_aggregation_hook(engine, percent_adopt, trial, round)
Custom pre-analysis logic
Hook complete
ASGraphAnalyzer(engine, scenario)
analyze()
outcomes
graph_data_aggregator.aggregate_and_store_trial_data(...)
post_propagation_hook(engine, percent_adopt, trial, round)
Custom post-propagation logic
Hook complete
```

### AccidentalRouteLeak Example

The `AccidentalRouteLeak` scenario ([bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py71-132](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py#L71-L132)) demonstrates advanced `post_propagation_hook` usage:

**Round 0 Behavior:**

1. Valid prefix propagates normally
2. In `post_propagation_hook`, extract announcement from attacker's local RIB
3. Modify announcement to have `recv_relationship=ORIGIN` (so it appears as if received from customer)
4. Clear graph state via `setup_engine`
5. Set `engine.ready_to_run_round = 1` to prepare for next round

**Round 1 Behavior:**

- Modified announcements propagate, causing accidental leak
- Attacker exports to providers and peers (valley-free violation)

This approach avoids the need for `BGPFull` and withdrawal processing, significantly improving performance.

**Sources:**

- [bgpy/simulation_framework/simulation.py499-537](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L499-L537)
- [bgpy/simulation_framework/scenarios/scenario.py404-425](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L404-L425)
- [bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py71-132](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py#L71-L132)

---

## Multi-Processing Architecture

### Trial Chunking

The `_get_chunks` method ([bgpy/simulation_framework/simulation.py309-320](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L309-L320)) distributes trials across workers:

```
def _get_chunks(self, cpus: int) -> list[list[int]]:
    """Returns chunks of trial inputs based on number of CPUs running"""
    
    trials_list = list(range(self.num_trials))
    return [trials_list[i::cpus] for i in range(cpus)]
```

For example, with `num_trials=10` and `cpus=3`:

- Chunk 0: [0, 3, 6, 9]
- Chunk 1: [1, 4, 7]
- Chunk 2: [2, 5, 8]

This interleaved distribution provides better load balancing than sequential chunks.

### Progress Tracking

**File-Based Progress** ([bgpy/simulation_framework/simulation.py491-497](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L491-L497)):

Each worker writes its progress to `{chunk_id}.txt` in `_tqdm_tracking_dir`:

```
def _write_tqdm_progress(self, chunk_id: int, completed: int) -> None:
    """Writes total number of percent adoption trial pairs to file"""
    
    if self.parse_cpus > 1:
        with (self._tqdm_tracking_dir / f"{chunk_id}.txt").open("w") as f:
            f.write(str(completed))
```

**Progress Bar Update** ([bgpy/simulation_framework/simulation.py360-371](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L360-L371)):

Main process aggregates progress from all chunk files:

```
def _update_tqdm_progress_bar(self, pbar: tqdm) -> None:
    """Updates tqdm progress bar"""
    
    total_completed = 0
    for file_path in self._tqdm_tracking_dir.iterdir():
        try:
            total_completed += int(file_path.read_text())
        except ValueError:
            pass  # File being written
    pbar.n = total_completed
    pbar.refresh()
```

### Multi-Processing Execution Flow

```
Yes

No

_get_mp_results

Create Pool(parse_cpus)

_get_chunks(parse_cpus):
Distribute trials

Submit apply_async(_run_chunk, chunk)
for each chunk

Monitor loop

_get_completed_and_tasks:
Check task.ready()

_update_tqdm_progress_bar:
Read chunk files,
update tqdm

time.sleep(0.5)

More tasks?

Close Pool

Return completed results
```

### Randomness Seeding

Each worker seeds randomness with its `chunk_id` ([bgpy/simulation_framework/simulation.py269-281](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L269-L281)):

```
def _seed_random(self, seed_suffix: str = "") -> None:
    """Seeds randomness"""
    
    if self.python_hash_seed is not None:
        msg = (
            f"You've set the python_hash_seed to {self.python_hash_seed}, but "
            "the simulations aren't deterministic unless you also set the "
            "PYTHONHASHSEED in the env, such as with \n"
            f"export PYTHONHASHSEED={self.python_hash_seed}"
        )
        if os.environ.get("PYTHONHASHSEED") != str(self.python_hash_seed):
            raise RuntimeError(msg)
        random.seed(str(self.python_hash_seed) + seed_suffix)
```

This ensures each worker has different random selections while maintaining reproducibility when `PYTHONHASHSEED` is set.

**Sources:**

- [bgpy/simulation_framework/simulation.py269-371](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L269-L371)
- [bgpy/simulation_framework/simulation.py491-497](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L491-L497)

---

## Summary

The `Simulation` class provides a complete execution pipeline:

1. **Initialization:** Validates configuration, estimates RAM, sets up class references
2. **Graph Caching:** Downloads/caches CAIDA data via `ASGraphConstructor`
3. **Trial Execution:** Distributes trials across workers, each with independent `SimulationEngine`
4. **Engine Setup:**`Scenario` assigns policy classes and seeds announcements
5. **Propagation:**`SimulationEngine` executes Gao-Rexford propagation
6. **Hooks:** Scenarios inject custom logic via `pre_aggregation_hook` and `post_propagation_hook`
7. **Data Collection:**`ASGraphAnalyzer` analyzes outcomes, `GraphDataAggregator` aggregates metrics
8. **Output:** Results written to CSV/pickle, visualizations generated via `GraphFactory`

The architecture supports both single-process (with direct tqdm) and multi-process (with file-based progress tracking) execution modes, with careful attention to reproducibility through seed management and ASN reuse logic.