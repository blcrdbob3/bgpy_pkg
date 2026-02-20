# Running Your First Simulation
Relevant source files
- [.github/workflows/tests.yml](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/.github/workflows/tests.yml)
- [.pre-commit-config.yaml](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/.pre-commit-config.yaml)
- [LICENSE.txt](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/LICENSE.txt)
- [MANIFEST.in](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/MANIFEST.in)
- [README.md](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/README.md)
- [bgpy/__main__.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/__main__.py)
- [bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py)
- [bgpy/enums.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/enums.py)
- [bgpy/shared/enums.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/shared/enums.py)
- [bgpy/simulation_framework/scenarios/scenario.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py)
- [bgpy/simulation_framework/scenarios/scenario_config.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py)
- [bgpy/simulation_framework/simulation.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py)
- [pyproject.toml](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml)
- [requirements.txt](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/requirements.txt)
- [requirements_dev.txt](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/requirements_dev.txt)
- [setup.cfg](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/setup.cfg)
- [tox.ini](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/tox.ini)

This document provides a practical guide to running your first BGP security simulation using BGPy. It covers the minimal code required, explains key configuration parameters, and describes the execution flow. For installation instructions, see [Installation and Setup](/blcrdbob3/bgpy_pkg/2.1-installation-and-setup). For details on interpreting the output files and graphs, see [Understanding Simulation Output](/blcrdbob3/bgpy_pkg/2.3-understanding-simulation-output).

---

## Minimal Working Example

The simplest way to run a simulation is to create a Python script that instantiates a `Simulation` object and calls its `run()` method. Here is a complete example:

```
from pathlib import Path
from bgpy.shared.enums import SpecialPercentAdoptions
from bgpy.simulation_engine import ROV
from bgpy.simulation_framework import ScenarioConfig, Simulation, SubprefixHijack

# Create and configure the simulation
sim = Simulation(
    percent_adoptions=(
        SpecialPercentAdoptions.ONLY_ONE,
        0.1,
        0.2,
        0.5,
        0.8,
        0.99,
    ),
    scenario_configs=(
        ScenarioConfig(
            ScenarioCls=SubprefixHijack,
            AdoptPolicyCls=ROV,
        ),
    ),
    output_dir=Path("~/Desktop/my_simulation").expanduser(),
    num_trials=10,
    parse_cpus=4,
)

# Run the simulation
sim.run()
```

This example simulates a `SubprefixHijack` attack where various percentages of the network adopt the `ROV` (Route Origin Validation) security policy, running 10 independent trials across 4 CPU cores.

**Sources:**[bgpy/__main__.py1-34](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/__main__.py#L1-L34)

---

## Core Components

### Simulation Class

The `Simulation` class is the main orchestrator that coordinates all aspects of running a BGP security simulation. It handles:

- Downloading and caching CAIDA AS relationship data
- Constructing the AS graph representing the Internet topology
- Running multiple trials with different adoption percentages
- Collecting and aggregating metrics
- Generating output files and visualizations

**Sources:**[bgpy/simulation_framework/simulation.py52-605](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L52-L605)

### ScenarioConfig

A `ScenarioConfig` is an immutable configuration object that defines a single attack/defense scenario. It specifies:
ParameterTypeDescription`ScenarioCls``type[Scenario]`The attack scenario class (e.g., `SubprefixHijack`)`AdoptPolicyCls``type[Policy]`The security policy being evaluated (e.g., `ROV`)`BasePolicyCls``type[Policy]`The baseline policy for non-adopting ASes (default: `BGP`)`num_attackers``int`Number of attacker ASes (default: 1)`num_victims``int`Number of victim ASes (default: 1)`propagation_rounds``int`Number of BGP propagation rounds (auto-calculated if not set)
**Sources:**[bgpy/simulation_framework/scenarios/scenario_config.py28-243](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L28-L243)

### Relationship Between Components

```
instantiates

creates tuple of

defines

defines

defines

contains tuple

creates for each trial

creates

creates

uses config from

selects attacker/victim ASNs

assigns policies to ASes

propagates announcements through

User Script

Simulation
(simulation.py)

ScenarioConfig
(scenario_config.py)

Scenario Instance
(scenario.py)

SimulationEngine
(simulation_engine)

ASGraph
(as_graphs)

ScenarioCls
(e.g. SubprefixHijack)

AdoptPolicyCls
(e.g. ROV)

BasePolicyCls
(e.g. BGP)
```

**Sources:**[bgpy/simulation_framework/simulation.py52-109](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L52-L109)[bgpy/simulation_framework/scenarios/scenario_config.py28-82](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L28-L82)[bgpy/simulation_framework/scenarios/scenario.py20-89](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L20-L89)

---

## Key Configuration Parameters

### percent_adoptions

The `percent_adoptions` parameter controls what fraction of the network adopts the security policy specified in `AdoptPolicyCls`. It accepts a tuple of values, where each value represents a data point on the adoption curve:

```
percent_adoptions=(
    SpecialPercentAdoptions.ONLY_ONE,  # Only 1 AS adopts
    0.1,                                # 10% adoption
    0.5,                                # 50% adoption
    0.99,                               # 99% adoption
    SpecialPercentAdoptions.ALL_BUT_ONE, # All but 1 AS adopts
)
```

The simulation runs trials at each adoption percentage, allowing you to see how effectiveness changes with deployment.

**Sources:**[bgpy/simulation_framework/simulation.py59-66](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L59-L66)[bgpy/shared/enums.py111-123](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/shared/enums.py#L111-L123)

### num_trials

The `num_trials` parameter specifies how many independent simulation runs to perform for each adoption percentage. Higher trial counts reduce variance and produce more statistically reliable results. Each trial randomly selects different attacker and victim ASes.

```
num_trials=100  # Run 100 independent trials
```

**Sources:**[bgpy/simulation_framework/simulation.py74-121](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L74-L121)

### parse_cpus

The `parse_cpus` parameter controls parallel execution. BGPy uses Python's `multiprocessing.Pool` to distribute trials across CPU cores:

```
parse_cpus=8  # Use 8 CPU cores
```

If `parse_cpus > 1`, trials are divided into chunks and processed in parallel. If `parse_cpus == 1`, trials run sequentially with a progress bar. The default is `max(cpu_count() - 1, 1)`.

**Sources:**[bgpy/simulation_framework/simulation.py76-123](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L76-L123)[bgpy/simulation_framework/simulation.py286-348](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L286-L348)

### output_dir

Specifies where simulation results are written. The directory will contain:

- `data.csv` - Human-readable metrics
- `data.pickle` - Python-serialized data structures
- `graphs/` - Generated visualization plots
- YAML files (if requested)

```
output_dir=Path("~/Desktop/my_simulation").expanduser()
```

**Sources:**[bgpy/simulation_framework/simulation.py75-133](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L75-L133)[bgpy/simulation_framework/simulation.py573-605](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L573-L605)

---

## Execution Flow

When you call `sim.run()`, the following sequence occurs:

```
Yes

No

next propagation_round

next scenario_config

next percent_adoption

next trial

sim.run() called

Download & Cache CAIDA Data
(ASGraphConstructor)

Divide trials into chunks
(one per CPU)

parse_cpus > 1?

Single Process Execution
(with tqdm progress bar)

Multi-Process Execution
(Pool.apply_async)

For each chunk:
_run_chunk()

Reconstruct AS Graph
(from cached TSV)

For each trial in chunk

For each percent_adoption

For each scenario_config

Create Scenario instance
(select attackers/victims)

Setup Engine
(assign policies to ASes)

For each propagation_round

engine.run()
(propagate announcements)

ASGraphAnalyzer.analyze()
(determine outcomes)

GraphDataAggregator
(collect metrics)

scenario.post_propagation_hook()

Combine results from all chunks

Write data.csv

Write data.pickle

GraphFactory.generate_graphs()

Simulation Complete
```

**Sources:**[bgpy/simulation_framework/simulation.py250-268](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L250-L268)[bgpy/simulation_framework/simulation.py377-439](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L377-L439)[bgpy/simulation_framework/simulation.py499-567](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L499-L567)

### Detailed Execution Steps

#### 1. Initialization Phase

During `Simulation.__init__()`, the system:

- Validates RAM requirements based on CPU count and AS graph configuration
- Seeds random number generators (if `python_hash_seed` is set)
- Creates the output directory structure
- Validates `ScenarioConfig` objects for consistency

**Sources:**[bgpy/simulation_framework/simulation.py55-160](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L55-L160)[bgpy/simulation_framework/simulation.py176-248](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L176-L248)

#### 2. Graph Construction

The `ASGraphConstructor` downloads CAIDA AS relationship data and constructs the AS graph:

```
CAIDAASGraphCollector
downloads .as-rel file

Parse relationships
(customers, providers, peers)

Extract metadata
(input clique, IXPs)

CAIDAASGraph constructor
(compute ranks, cones)

Cache to TSV
(for multiprocessing)
```

**Sources:**[bgpy/simulation_framework/simulation.py257-258](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L257-L258)[bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py1-128](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py#L1-L128)

#### 3. Trial Execution

For each trial, the system:

1. **Creates a Scenario instance** - Randomly selects attacker and victim ASes from appropriate subcategories (e.g., stub ASes)
2. **Assigns policies** - Each AS is assigned either `AdoptPolicyCls` or `BasePolicyCls` based on adoption percentage
3. **Seeds announcements** - The scenario generates initial BGP announcements from attackers and victims
4. **Runs propagation** - The `SimulationEngine` propagates announcements through the network following valley-free routing rules
5. **Analyzes outcomes** - The `ASGraphAnalyzer` traces paths to determine whether each AS routes to the attacker or victim
6. **Aggregates data** - The `GraphDataAggregator` collects metrics for later visualization

**Sources:**[bgpy/simulation_framework/simulation.py393-439](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L393-L439)[bgpy/simulation_framework/scenarios/scenario.py33-89](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L33-L89)[bgpy/simulation_framework/simulation.py499-567](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L499-L567)

#### 4. Multiprocessing Strategy

When `parse_cpus > 1`, trials are divided into chunks:

```
# Example: 100 trials with 4 CPUs
# Chunk 0: trials [0, 4, 8, 12, ..., 96]
# Chunk 1: trials [1, 5, 9, 13, ..., 97]
# Chunk 2: trials [2, 6, 10, 14, ..., 98]
# Chunk 3: trials [3, 7, 11, 15, ..., 99]
```

Each worker process:

- Reconstructs the AS graph from cached TSV data (avoiding pickle serialization issues with weakrefs)
- Runs its assigned trials
- Writes progress to temporary files for the main process to monitor
- Returns a `GraphDataAggregator` with collected metrics

**Sources:**[bgpy/simulation_framework/simulation.py309-372](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L309-L372)[bgpy/simulation_framework/simulation.py461-474](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L461-L474)

---

## Command-Line Execution

BGPy includes a command-line entry point. After installation, you can run the default simulation:

```
bgpy
```

This executes the `main()` function defined in `bgpy/__main__.py`, which runs a pre-configured simulation with `SubprefixHijack` and `ROV`.

You can also create a custom Python script and run it directly:

```
python my_simulation.py
```

**Sources:**[bgpy/__main__.py1-35](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/__main__.py#L1-L35)[pyproject.toml78-79](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L78-L79)

---

## Common Parameter Patterns

### Quick Testing

For rapid iteration during development:

```
sim = Simulation(
    percent_adoptions=(0.5,),  # Single adoption level
    scenario_configs=(ScenarioConfig(SubprefixHijack, ROV),),
    num_trials=2,              # Minimal trials
    parse_cpus=1,              # Single process for easier debugging
)
```

### Production Runs

For publication-quality results:

```
sim = Simulation(
    percent_adoptions=(
        SpecialPercentAdoptions.ONLY_ONE,
        0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,
        SpecialPercentAdoptions.ALL_BUT_ONE,
    ),
    scenario_configs=(...),
    num_trials=100,            # High trial count for statistical confidence
    parse_cpus=16,             # Maximum parallelism
)
```

### Comparing Multiple Policies

To compare different security policies against the same attack:

```
from bgpy.simulation_engine import ROV, ASPA, BGPSec

sim = Simulation(
    scenario_configs=(
        ScenarioConfig(SubprefixHijack, ROV),
        ScenarioConfig(SubprefixHijack, ASPA),
        ScenarioConfig(SubprefixHijack, BGPSec),
    ),
    # ...other parameters
)
```

Each `ScenarioConfig` will be executed across all adoption percentages and trials, allowing direct comparison.

**Sources:**[bgpy/simulation_framework/simulation.py124-127](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L124-L127)[bgpy/simulation_framework/scenarios/scenario_config.py28-82](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L28-L82)

---

## Parameter Reference Table
ParameterTypeDefaultDescription`sim_name``str | None``"bgpy_sims"`Name used in default output directory path`percent_adoptions``tuple[float | SpecialPercentAdoptions, ...]``(ONLY_ONE, 0.1, 0.2, 0.5, 0.8, 0.99)`Adoption percentages to simulate`scenario_configs``tuple[ScenarioConfig, ...]``(SubprefixHijack + ROV,)`Attack/defense scenarios to evaluate`num_trials``int``1`Number of independent trials per adoption percentage`output_dir``Path | None``~/Desktop/sims/{sim_name}`Where to write results`parse_cpus``int``max(cpu_count()-1, 1)`Number of parallel processes`python_hash_seed``int | None``None`Random seed for reproducibility (requires `PYTHONHASHSEED` env var)`data_plane_tracking``bool``True`Track data plane outcomes (actual traffic paths)`control_plane_tracking``bool``False`Track control plane outcomes (BGP announcements)
**Sources:**[bgpy/simulation_framework/simulation.py55-152](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L55-L152)

---

## Next Steps

After running your first simulation, you'll have output files in the `output_dir`. To understand what these files contain and how to interpret the generated graphs, proceed to [Understanding Simulation Output](/blcrdbob3/bgpy_pkg/2.3-understanding-simulation-output).

For deeper customization:

- To modify attack scenarios: see [Attack Scenario Reference](/blcrdbob3/bgpy_pkg/7-attack-scenario-reference)
- To implement custom security policies: see [Creating Custom Policies](/blcrdbob3/bgpy_pkg/10.2-creating-custom-policies)
- To adjust AS graph construction: see [CAIDA Data and Graph Construction](/blcrdbob3/bgpy_pkg/5.2-caida-data-and-graph-construction)

**Sources:**[bgpy/simulation_framework/simulation.py250-268](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L250-L268)[bgpy/simulation_framework/simulation.py573-605](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L573-L605)