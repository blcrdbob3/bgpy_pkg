# Getting Started
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

This page provides a practical guide to installing BGPy, running your first simulation, and understanding the basic workflow. By the end of this guide, you will have executed a complete simulation comparing BGP and ROV defense policies against a subprefix hijack attack.

For detailed installation instructions, see [Installation and Setup](/blcrdbob3/bgpy_pkg/2.1-installation-and-setup). For a step-by-step walkthrough of simulation parameters, see [Running Your First Simulation](/blcrdbob3/bgpy_pkg/2.2-running-your-first-simulation). For comprehensive documentation on output formats, see [Understanding Simulation Output](/blcrdbob3/bgpy_pkg/2.3-understanding-simulation-output).

---

## Prerequisites

BGPy requires Python 3.10 or higher and supports both CPython and PyPy implementations. The package has been tested on Linux, macOS (Intel and ARM), and is distributed via PyPI.

### System Requirements
RequirementSpecificationNotes**Python Version**>= 3.10Supports 3.10, 3.11, 3.12, 3.13, 3.14**Python Implementation**CPython or PyPyPyPy 3.11 recommended for performance**Operating System**Linux, macOSWindows not currently supported**RAM**~1-2GB per CPU coreDepends on graph configuration**External Tools**Graphviz (optional)Required only for AS graph visualizations
**Sources:**[pyproject.toml5-56](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L5-L56)[pyproject.toml40-56](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L40-L56)

### Core Dependencies

BGPy automatically installs the following key dependencies:

- **roa-checker** (~3.0): RPKI ROA validation library
- **rov-collector** (~1.0): Real-world ROV data collection
- **matplotlib** (3.10.8): Graph generation
- **tqdm** (4.67.1): Progress tracking
- **PyYAML** (6.0.3): Configuration and result serialization
- **requests-cache** (1.2.1): Caching for CAIDA data downloads

**Sources:**[pyproject.toml57-72](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L57-L72)[requirements.txt1-14](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/requirements.txt#L1-L14)

---

## Installation

Install BGPy using pip:

```
pip install bgpy_pkg
```

For development with testing tools:

```
pip install bgpy_pkg[test]
```

Verify installation by checking the CLI is available:

```
bgpy --help
```

**Sources:**[pyproject.toml1-6](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L1-L6)[pyproject.toml78-79](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L78-L79)

---

## Minimal Working Example

The simplest way to run a simulation is to use the `Simulation` class directly. Here is a complete example that simulates a subprefix hijack with ROV defense:

```
from pathlib import Path
from bgpy.simulation_framework import Simulation, ScenarioConfig, SubprefixHijack
from bgpy.simulation_engine import ROV, BGP
from bgpy.shared.enums import SpecialPercentAdoptions

sim = Simulation(
    percent_adoptions=(
        SpecialPercentAdoptions.ONLY_ONE,
        0.5,
        0.99,
    ),
    scenario_configs=(
        ScenarioConfig(
            ScenarioCls=SubprefixHijack,
            AdoptPolicyCls=ROV,
            BasePolicyCls=BGP,
        ),
    ),
    output_dir=Path("~/Desktop/my_first_sim").expanduser(),
    num_trials=5,
    parse_cpus=2,
)
sim.run()
```

This code will:

1. Download CAIDA AS relationship data (cached after first run)
2. Run 5 independent trials of a subprefix hijack scenario
3. Test ROV adoption at 1 AS, 50%, and 99% deployment
4. Generate CSV/pickle data files and PNG graphs
5. Save all results to `~/Desktop/my_first_sim`

**Sources:**[bgpy/__main__.py8-31](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/__main__.py#L8-L31)

---

## Core Simulation Workflow

```
Outputs

Execution Pipeline

Simulation Class (simulation.py)

User Code

Instantiate Simulation
(scenario_configs, percent_adoptions, num_trials)

Call sim.run()

init
- Validate parameters
- Check RAM availability
- Create output_dir

run()
- Cache CAIDA data
- Execute trials
- Aggregate results
- Generate graphs

ASGraphConstructor
Build topology from CAIDA

SimulationEngine
Propagate BGP announcements

ASGraphAnalyzer
Compute outcomes per AS

GraphDataAggregator
Aggregate across trials

GraphFactory
Generate PNG visualizations

CSV: data.csv
Human-readable metrics

Pickle: data.pickle
Python objects for analysis

PNG Graphs
graphs/*.png
```

**Diagram: High-level simulation execution flow from user code through core classes to output artifacts**

The `Simulation` class ([bgpy/simulation_framework/simulation.py52-605](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L52-L605)) serves as the main orchestrator. It coordinates the following components:

- **ASGraphConstructor**: Downloads and parses CAIDA AS relationship data
- **SimulationEngine**: Executes BGP propagation rounds following Gao-Rexford routing
- **ASGraphAnalyzer**: Determines per-AS outcomes (attacker success, victim success, disconnected)
- **GraphDataAggregator**: Aggregates statistics across multiple trials
- **GraphFactory**: Produces publication-ready visualizations

**Sources:**[bgpy/simulation_framework/simulation.py52-268](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L52-L268)

---

## Key Simulation Parameters

Understanding the `Simulation.__init__()` parameters is essential for configuring your experiments:
ParameterTypeDefaultPurpose`percent_adoptions``tuple[float | SpecialPercentAdoptions, ...]``(ONLY_ONE, 0.1, 0.2, 0.5, 0.8, 0.99)`Fraction of ASes adopting the defense policy`scenario_configs``tuple[ScenarioConfig, ...]``(ScenarioConfig(...),)`Attack/defense scenario combinations to test`num_trials``int``1`Number of independent trials (for statistical confidence)`parse_cpus``int``max(cpu_count() - 1, 1)`Number of parallel processes`output_dir``Path | None``~/Desktop/sims/{sim_name}`Where to write results
**Sources:**[bgpy/simulation_framework/simulation.py55-109](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L55-L109)

### SpecialPercentAdoptions

BGPy provides two special adoption values for edge cases:

- **`SpecialPercentAdoptions.ONLY_ONE`**: Exactly 1 AS adopts (useful for testing minimal deployment)
- **`SpecialPercentAdoptions.ALL_BUT_ONE`**: All except 1 AS adopts (useful for testing near-complete deployment)

**Sources:**[bgpy/shared/enums.py111-123](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/shared/enums.py#L111-L123)

### ScenarioConfig Structure

```
ScenarioConfig (scenario_config.py)

ScenarioConfig

ScenarioCls: type[Scenario]
(e.g., SubprefixHijack)

AdoptPolicyCls: type[Policy]
(e.g., ROV)

BasePolicyCls: type[Policy]
(e.g., BGP)

num_attackers: int = 1

num_victims: int = 1

adoption_subcategory_attrs
(STUBS_OR_MH, ETC, INPUT_CLIQUE)
```

**Diagram: ScenarioConfig dataclass structure defining attack scenarios and policy assignments**

A `ScenarioConfig` ([bgpy/simulation_framework/scenarios/scenario_config.py28-243](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L28-L243)) encapsulates:

- **Attack type**: Via `ScenarioCls` (e.g., `SubprefixHijack`, `PrefixHijack`)
- **Defense policy**: Via `AdoptPolicyCls` (e.g., `ROV`, `ASPA`, `BGPSec`)
- **Baseline policy**: Via `BasePolicyCls` (typically `BGP`)
- **Attacker/victim counts**: Number of malicious/target ASes
- **Adoption distribution**: Which AS categories participate in the defense

**Sources:**[bgpy/simulation_framework/scenarios/scenario_config.py28-81](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L28-L81)

---

## Trial Execution Internals

Each trial represents one independent simulation with randomly selected attackers, victims, and adopting ASes:

```
GraphDataAggregator
ASGraphAnalyzer
SimulationEngine
Scenario
Simulation
GraphDataAggregator
ASGraphAnalyzer
SimulationEngine
Scenario
Simulation
loop
[For each propagation_round]
Initialize with percent_adoption
Select random attacker/victim ASNs
Select random adopting ASNs
Generate announcements & ROAs
setup(scenario)
Assign Policy classes to ASes
Seed initial announcements
run(propagation_round, scenario)
Propagate: Providers → Peers → Customers
post_propagation_hook()
analyze()
Traceback via next_hop_asn
Classify outcomes per AS
outcomes dict
aggregate_and_store_trial_data()
Update running statistics
```

**Diagram: Sequence of method calls during a single trial execution**

Within `Simulation._run_chunk()` ([bgpy/simulation_framework/simulation.py377-439](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L377-L439)), the system:

1. **Scenario Initialization**: Creates a `Scenario` instance that randomly selects attacker/victim ASNs and determines which ASes adopt the defense policy based on `percent_adoption`
2. **Engine Setup**: The `Scenario.setup_engine()` method assigns `Policy` classes (e.g., `ROV`, `BGP`) to each AS and seeds initial announcements
3. **Propagation**: `SimulationEngine.run()` executes BGP propagation following valley-free routing (providers first, then peers, then customers)
4. **Analysis**: `ASGraphAnalyzer.analyze()` performs traceback to determine which prefix each AS ultimately routes to
5. **Aggregation**: `GraphDataAggregator.aggregate_and_store_trial_data()` collects per-trial statistics for later averaging

**Sources:**[bgpy/simulation_framework/simulation.py377-567](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L377-L567)[bgpy/simulation_framework/scenarios/scenario.py33-89](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L33-L89)

---

## Understanding Output Files

After `sim.run()` completes, the `output_dir` contains:

```
output_dir/
├── data.csv           # Human-readable CSV with all metrics
├── data.pickle        # Python objects for programmatic analysis
└── graphs/
    ├── {scenario}_data_plane_attacker_success.png
    ├── {scenario}_data_plane_victim_success.png
    ├── {scenario}_control_plane_attacker_success.png
    └── ... (multiple graph variants)

```

### CSV Format (data.csv)

The CSV contains one row per (trial, percent_adoption, scenario_config, AS_group, outcome, plane) combination. Key columns include:

- `percent_adopt`: Adoption percentage (0.0 to 1.0 or special values)
- `scenario_label`: Name of the policy being evaluated (e.g., "ROV")
- `as_group`: AS category (stub, multihomed, transit, input_clique, etc.)
- `outcome`: Classification (attacker_success, victim_success, disconnected)
- `plane`: data_plane or control_plane
- `value`: Fraction of ASes in this category with this outcome (0.0 to 1.0)

**Sources:**[bgpy/simulation_framework/graph_data_aggregator.py1-300](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graph_data_aggregator.py#L1-L300) (inferred from aggregator structure)

### Pickle Format (data.pickle)

The pickle file contains a `GraphDataAggregator` instance with:

- `data_point_info`: Dictionary mapping `DataPointKey` → `DataPointAggData`
- `DataPointKey`: Tuple of (propagation_round, percent_adopt, scenario_config, graph_category)
- `DataPointAggData`: Contains `value` (mean) and `yerr` (standard error) across trials

This format is intended for programmatic analysis and custom graph generation.

**Sources:**[bgpy/simulation_framework/graph_data_aggregator.py1-300](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graph_data_aggregator.py#L1-L300) (inferred)

### Graph Format (graphs/*.png)

Generated PNG files show adoption percentage (x-axis) vs. outcome fraction (y-axis) for different AS groups. Graphs are separated by:

- **Plane**: data_plane (actual traffic paths) vs. control_plane (BGP announcements)
- **AS Group**: stub, multihomed, transit, input_clique, etc.
- **Outcome**: attacker_success, victim_success, disconnected
- **Adoption Status**: adopting vs. non-adopting ASes

**Sources:**[bgpy/simulation_framework/graphing/graph_factory.py1-400](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/graph_factory.py#L1-L400) (inferred from factory structure)

For detailed documentation on interpreting these outputs, see [Understanding Simulation Output](/blcrdbob3/bgpy_pkg/2.3-understanding-simulation-output).

---

## Multiprocessing Behavior

When `parse_cpus > 1`, BGPy distributes trials across CPU cores using Python's `multiprocessing.Pool`:

```
Worker Process 2

Worker Process 1

Worker Process 0

Main Process

Simulation.run()

_get_mp_results()
Create Pool

_get_chunks(parse_cpus)
Split trials[i::cpus]

_run_chunk(chunk_id=0, trials=[0, 3, 6, ...])

Reconstruct ASGraph from TSV

Execute trials 0, 3, 6, ...

Write progress to 0.txt

Return GraphDataAggregator

_run_chunk(chunk_id=1, trials=[1, 4, 7, ...])

Reconstruct ASGraph from TSV

Execute trials 1, 4, 7, ...

Write progress to 1.txt

Return GraphDataAggregator

_run_chunk(chunk_id=2, trials=[2, 5, 8, ...])

Reconstruct ASGraph from TSV

Execute trials 2, 5, 8, ...

Write progress to 2.txt

Return GraphDataAggregator

Main Process
Read progress files for tqdm

Aggregate results
sum(GraphDataAggregators)
```

**Diagram: Multiprocessing architecture showing trial distribution and progress tracking**

Key implementation details:

- **Chunk Distribution**: Trials are distributed round-robin (`trials[i::cpus]`) to ensure even workload
- **AS Graph Reconstruction**: Each worker rebuilds the graph from cached TSV data (pickle serialization fails due to weakrefs)
- **Progress Tracking**: Workers write completion counts to temporary files (`{chunk_id}.txt`) that the main process reads for the tqdm progress bar
- **Result Aggregation**: `GraphDataAggregator` instances are summed using `__add__` to combine statistics

**Sources:**[bgpy/simulation_framework/simulation.py308-372](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L308-L372)[bgpy/simulation_framework/simulation.py461-474](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L461-L474)

---

## RAM Considerations

BGPy validates available RAM before execution to prevent out-of-memory crashes:
ConfigurationRAM per CoreNo cone storage~0.9 GBCustomer cone size only~1.6 GBBoth customer & provider cones~2.3 GB
The validation check occurs in `Simulation._validate_ram()` and warns if expected usage exceeds 90% of available RAM.

**Sources:**[bgpy/simulation_framework/simulation.py215-248](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L215-L248)

---

## Next Steps

You now understand how to run a basic simulation and interpret the outputs. To dive deeper:

- **[Installation and Setup](/blcrdbob3/bgpy_pkg/2.1-installation-and-setup)**: Detailed environment configuration and PyPy setup
- **[Running Your First Simulation](/blcrdbob3/bgpy_pkg/2.2-running-your-first-simulation)**: Parameter explanations and common configuration patterns
- **[Understanding Simulation Output](/blcrdbob3/bgpy_pkg/2.3-understanding-simulation-output)**: Comprehensive guide to CSV/pickle formats and graph interpretation

For advanced usage:

- **[Core Concepts](/blcrdbob3/bgpy_pkg/3-core-concepts)**: Understand AS graphs, policies, scenarios, and the simulation framework
- **[BGP Policy Reference](/blcrdbob3/bgpy_pkg/6-bgp-policy-reference)**: Explore the 20+ security policies (ROV, ASPA, BGPSec, etc.)
- **[Attack Scenario Reference](/blcrdbob3/bgpy_pkg/7-attack-scenario-reference)**: Learn about prefix hijacks, route leaks, and evasion techniques
- **[Creating Custom Scenarios](/blcrdbob3/bgpy_pkg/10.1-creating-custom-scenarios)**: Implement your own attack types
- **[Creating Custom Policies](/blcrdbob3/bgpy_pkg/10.2-creating-custom-policies)**: Build new security mechanisms

**Sources:**[README.md28-38](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/README.md#L28-L38) (table of contents structure)