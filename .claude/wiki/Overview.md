# Overview
Relevant source files
- [.github/workflows/tests.yml](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/.github/workflows/tests.yml)
- [.pre-commit-config.yaml](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/.pre-commit-config.yaml)
- [LICENSE.txt](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/LICENSE.txt)
- [MANIFEST.in](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/MANIFEST.in)
- [README.md](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/README.md)
- [bgpy/__init__.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/__init__.py)
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

BGPy is a Python-based simulation framework for evaluating Border Gateway Protocol (BGP) security policies against various attack scenarios using real-world Internet topology data. The framework enables researchers and developers to model the propagation of BGP announcements across autonomous systems (ASes), test defensive policies (such as ROV, ASPA, BGPSec), and analyze attack success rates through statistical trials.

For step-by-step instructions on running simulations, see [Getting Started](/blcrdbob3/bgpy_pkg/2-getting-started). For detailed explanations of core abstractions, see [Core Concepts](/blcrdbob3/bgpy_pkg/3-core-concepts). For implementing custom policies or scenarios, see [Advanced Topics](/blcrdbob3/bgpy_pkg/10-advanced-topics).

## Core Capabilities

BGPy provides the following capabilities:
CapabilityDescriptionKey Classes**Topology Modeling**Constructs AS-level Internet graphs from CAIDA relationship data with ~90,000 ASes`CAIDAASGraphConstructor`, `ASGraph`**Policy Simulation**Implements 20+ BGP security policies including basic BGP, ROV, ASPA, ASRA, BGPSec`Policy` subclasses in `simulation_engine/policies/`**Attack Scenarios**Models prefix hijacks, route leaks, and policy-evasion attacks`Scenario` subclasses in `simulation_framework/scenarios/`**Statistical Analysis**Runs multiple trials with randomized attacker/victim selection and aggregates metrics`GraphDataAggregator`, `ASGraphAnalyzer`**Parallel Execution**Distributes trials across CPU cores for performance`Simulation._get_mp_results()`**Visualization**Generates publication-ready graphs with error bars and comparative analysis`GraphFactory`
Sources: [README.md1-39](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/README.md#L1-L39)[pyproject.toml1-95](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L1-L95)

## System Architecture

```
Data Sources

Output Layer

Analysis Layer

Policy Layer

Execution Layer

Orchestration Layer

Entry Layer

CLI Entry Point
bgpy.main.main()

Test Entry Point
pytest + EngineTester

Simulation
simulation.py

ScenarioConfig
Immutable trial configuration

SimulationEngine
Propagates announcements

Scenario
Trial-specific state

ASGraph
Network topology

Policy (abstract)
Decision logic

BGP
Base routing

ROV
Origin validation

ASPA
Path validation

ASGraphAnalyzer
Outcome classification

GraphDataAggregator
Statistical aggregation

GraphFactory
Visualization generation

CSV/Pickle/YAML
Persisted results

CAIDA AS Relationships
caida_as_graph_collector.py

ROAChecker
roa-checker library
```

**Figure 1: High-Level System Architecture**

The architecture follows a layered design where the `Simulation` class orchestrates execution, delegates announcement propagation to `SimulationEngine`, and collects metrics through `ASGraphAnalyzer`. Each layer is designed for extensibility through abstract base classes.

Sources: [bgpy/simulation_framework/simulation.py52-153](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L52-L153)[bgpy/__init__.py1-25](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/__init__.py#L1-L25)

## Core Components

### Simulation Orchestrator

The `Simulation` class ([simulation_framework/simulation.py52-605](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/simulation_framework/simulation.py#L52-L605)) serves as the main entry point for programmatic use. It manages:

- **Configuration**: Accepts `scenario_configs` (tuple of `ScenarioConfig` objects) and `percent_adoptions` (adoption rates to test)
- **Trial Management**: Runs `num_trials` independent trials with randomized attacker/victim selection
- **Multiprocessing**: Distributes work across `parse_cpus` cores using chunk-based parallelization
- **Data Aggregation**: Collects metrics via `GraphDataAggregator` and persists results

```
Simulation.init
Validate configuration
Cache CAIDA data

Simulation.run()
Main execution

Simulation._get_data()
Run all trials

GraphDataAggregator.write_data()
CSV + Pickle

Simulation._graph_data()
Generate visualizations
```

**Figure 2: Simulation Execution Flow**

Sources: [bgpy/simulation_framework/simulation.py52-267](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L52-L267)

### Network Topology

The `ASGraph` class represents the Internet topology as a directed graph where nodes are autonomous systems and edges represent business relationships:
Relationship TypeDirectionPropagation PriorityCustomer-ProviderBidirectionalCustomers: Highest (3)Peer-PeerBidirectionalPeers: Medium (2)Provider-CustomerBidirectionalProviders: Lowest (1)
The `CAIDAASGraphConstructor` ([as_graphs/caida_as_graph/caida_as_graph_constructor.py18-128](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/as_graphs/caida_as_graph/caida_as_graph_constructor.py#L18-L128)) downloads and parses CAIDA AS relationship files to construct the topology. The graph includes metadata such as:

- `propagation_ranks`: Topological ordering for deterministic propagation
- `customer_cone_size`: Number of downstream customers (used for random selection)
- `asn_groups`: AS categorization (stubs, multihomed, transit, input clique, IXPs)

Sources: [bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py41-77](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py#L41-L77)

### Policy Framework

Policies inherit from the `Policy` base class ([simulation_engine/policies/bgp/bgp.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/simulation_engine/policies/bgp/bgp.py)) and implement routing logic through these key methods:

- `process_incoming_anns()`: Receives announcements from neighbors
- `_policy_propagate()`: Selects best routes using the Gao-Rexford decision process
- `_copy_and_process()`: Prepends AS path and propagates to neighbors

The policy hierarchy enables incremental security enhancement:

```
Policy (abstract)
Base interface

BGP
Basic routing + Gao-Rexford

BGPFull
+ RIBs + Withdrawals

ROV
+ ROA validation

ASPA
+ Path validation

ASRA
+ Fake link detection
```

**Figure 3: Policy Inheritance Hierarchy**

Sources: [bgpy/simulation_engine/policies/bgp/bgp.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp.py)[bgpy/simulation_framework/scenarios/scenario_config.py28-81](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L28-L81)

### Scenario Configuration

A `ScenarioConfig` ([simulation_framework/scenarios/scenario_config.py28-81](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/simulation_framework/scenarios/scenario_config.py#L28-L81)) is an immutable configuration object that defines:

```
ScenarioConfig(
    ScenarioCls=SubprefixHijack,           # Attack type
    AdoptPolicyCls=ROV,                     # Defensive policy
    BasePolicyCls=BGP,                      # Non-adopting policy
    num_attackers=1,                        # Number of attackers
    num_victims=1,                          # Number of victims
    propagation_rounds=1,                   # Announcement rounds
    adoption_subcategory_attrs=(...)        # AS groups to adopt from
)
```

The `Scenario` class ([simulation_framework/scenarios/scenario.py20-487](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/simulation_framework/scenarios/scenario.py#L20-L487)) represents a single trial instantiation, selecting random attackers/victims from the AS graph and generating announcements.

Sources: [bgpy/simulation_framework/scenarios/scenario_config.py28-131](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L28-L131)[bgpy/simulation_framework/scenarios/scenario.py33-78](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L33-L78)

## Execution Pipeline

A complete simulation execution follows this sequence:

```
GraphFactory
"GraphDataAggregator"
"ASGraphAnalyzer"
AS
Scenario
"SimulationEngine"
"CAIDAASGraphConstructor"
Simulation
User
GraphFactory
"GraphDataAggregator"
"ASGraphAnalyzer"
AS
Scenario
"SimulationEngine"
"CAIDAASGraphConstructor"
Simulation
User
loop
[For each propagation_round]
loop
[For each trial]
__init__(scenario_configs, num_trials)
run()
ASGraph (cached)
run()
__init__(engine, scenario_config)
attacker_asns, victim_asns, announcements
setup_engine(engine)
Set policy classes
Seed announcements
run(scenario, propagation_round)
process_incoming_anns()
_policy_propagate()
Updated RIBs
Propagation complete
analyze(engine, scenario)
outcomes dict
aggregate_and_store_trial_data()
write_data(csv_path, pickle_path)
generate_graphs()
```

**Figure 4: Execution Sequence Diagram**

Sources: [bgpy/simulation_framework/simulation.py250-267](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L250-L267)[bgpy/simulation_framework/simulation.py377-439](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L377-L439)[bgpy/simulation_framework/simulation.py499-537](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L499-L537)

## Key Design Patterns

### Immutable Configuration

`ScenarioConfig` uses Python's `@dataclass(frozen=True)` to ensure configurations remain immutable across trials. This enables:

- Safe reuse across multiple trials and multiprocessing workers
- Hashability for dictionary keys in aggregation
- Clear separation between configuration (immutable) and state (mutable `Scenario` instances)

Sources: [bgpy/simulation_framework/scenarios/scenario_config.py28-29](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L28-L29)

### Multiprocessing Strategy

The framework distributes trials across CPU cores using chunk-based parallelization ([simulation.py309-359](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/simulation.py#L309-L359)):

1. Divide trials into chunks: `trials[i::cpus]` for CPU `i`
2. Each worker reconstructs the AS graph from cached TSV data (avoiding pickle issues with weakrefs)
3. Workers write progress to temporary files for tqdm monitoring
4. Main process aggregates results by summing `GraphDataAggregator` instances

Sources: [bgpy/simulation_framework/simulation.py309-371](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L309-L371)[bgpy/simulation_framework/simulation.py377-439](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L377-L439)

### Extensibility Through Inheritance

The framework provides abstract base classes for each layer:
ComponentBase ClassExtension PointPolicies`Policy``_policy_propagate()`, `process_incoming_anns()`Scenarios`Scenario``_get_announcements()`, `_get_roas()`Analyzers`BaseASGraphAnalyzer``analyze()`Graph Constructors`ASGraphConstructor``_get_as_graph_info()`
Sources: [bgpy/simulation_engine/policies/bgp/bgp.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp.py)[bgpy/simulation_framework/scenarios/scenario.py20-30](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L20-L30)

## Data Flow

The following diagram shows how data transforms from input to output:

```
CAIDA Relationships
serial-2.as-rel2.txt

ASGraphInfo
customer_provider_links
peer_links
ixp_asns

ASGraph
AS objects
Relationship edges

ScenarioConfig
Policy classes
Attack parameters

Scenario
attacker_asns
victim_asns
announcements

SimulationEngine
AS local RIBs

Outcomes Dict
{asn: {asn: outcome}}

TrialData
numerator, denominator

DataPointAggData
value, yerr

data.csv

data.pickle

graphs/*.png
```

**Figure 5: Data Transformation Pipeline**

Sources: [bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py41-77](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py#L41-L77)[bgpy/simulation_framework/graph_data_aggregator.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graph_data_aggregator.py)[bgpy/simulation_framework/as_graph_analyzers/as_graph_analyzer.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/as_graph_analyzers/as_graph_analyzer.py)

## Testing Framework

BGPy includes a comprehensive testing framework using `pytest` with:

- **EngineTester** ([tests/engine_tests/engine_tester.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/tests/engine_tests/engine_tester.py)): Runs deterministic simulations and compares against ground truth
- **Ground truth storage**: YAML files containing expected engine states and outcomes
- **Parallel test execution**: pytest-xdist for faster test runs
- **Continuous integration**: GitHub Actions testing across Python 3.10-3.14 and PyPy on Linux/macOS

For details on running tests, see [Testing and Development](/blcrdbob3/bgpy_pkg/9-testing-and-development).

Sources: [pyproject.toml108-119](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L108-L119)[tox.ini1-33](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/tox.ini#L1-L33)[.github/workflows/tests.yml1-29](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/.github/workflows/tests.yml#L1-L29)

## Installation and Dependencies

BGPy requires Python ≥3.10 and depends on:

- **beautifulsoup4**: Parsing CAIDA HTML pages for download links
- **matplotlib**: Graph generation
- **roa-checker**: RPKI ROA validation
- **rov-collector**: ROA data collection
- **yamlable**: YAML serialization of complex objects
- **psutil**: RAM validation
- **tqdm**: Progress bars

Installation: `pip install bgpy-pkg`

Development installation: `pip install bgpy-pkg[test]` (includes mypy, ruff, pytest-xdist)

Sources: [pyproject.toml57-94](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L57-L94)[requirements.txt1-15](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/requirements.txt#L1-L15)

## Entry Points

BGPy provides two primary entry points:

1. **CLI**: `bgpy` command (installed via entry point script at [pyproject.toml78-79](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L78-L79))

- Runs simulations from command line with `--num_trials` argument
- Entry point: [bgpy/__main__.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/__main__.py)
2. **Programmatic**: Import `bgpy.simulation_framework.Simulation` class

- Instantiate with custom configurations
- Call `.run()` to execute

For usage examples, see [Running Your First Simulation](/blcrdbob3/bgpy_pkg/2.2-running-your-first-simulation).

Sources: [pyproject.toml78-79](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L78-L79)[bgpy/simulation_framework/simulation.py39-50](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L39-L50)

## Version and Repository

- **Current Version**: 13.0.11
- **Repository**: [https://github.com/jfuruness/bgpy_pkg](https://github.com/jfuruness/bgpy_pkg)
- **Documentation**: [https://github.com/jfuruness/bgpy/wiki](https://github.com/jfuruness/bgpy/wiki)
- **License**: MIT

Sources: [pyproject.toml6-7](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L6-L7)[LICENSE.txt1-8](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/LICENSE.txt#L1-L8)