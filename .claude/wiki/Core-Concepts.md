# Core Concepts
Relevant source files
- [.github/workflows/tests.yml](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/.github/workflows/tests.yml)
- [.pre-commit-config.yaml](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/.pre-commit-config.yaml)
- [LICENSE.txt](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/LICENSE.txt)
- [MANIFEST.in](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/MANIFEST.in)
- [README.md](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/README.md)
- [bgpy/as_graphs/base/as_graph/as_graph.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py)
- [bgpy/as_graphs/base/as_graph/base_as.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/base_as.py)
- [bgpy/as_graphs/base/as_graph/cone_funcs.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/cone_funcs.py)
- [bgpy/as_graphs/base/as_graph/customer_cone_funcs.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/customer_cone_funcs.py)
- [bgpy/as_graphs/base/as_graph/graph_building_funcs.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/graph_building_funcs.py)
- [bgpy/as_graphs/base/as_graph_collector.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph_collector.py)
- [bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py)
- [bgpy/shared/enums.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/shared/enums.py)
- [bgpy/simulation_framework/scenarios/scenario.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py)
- [bgpy/simulation_framework/scenarios/scenario_config.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py)
- [bgpy/simulation_framework/simulation.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py)
- [bgpy/utils/engine_runner/engine_run_config.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/engine_run_config.py)
- [bgpy/utils/engine_runner/engine_runner.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/engine_runner.py)
- [pyproject.toml](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml)
- [requirements.txt](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/requirements.txt)
- [requirements_dev.txt](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/requirements_dev.txt)
- [setup.cfg](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/setup.cfg)
- [tox.ini](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/tox.ini)

## Purpose and Scope

This page introduces the four fundamental building blocks of BGPy: **Simulations**, **AS Graphs**, **Policies**, and **Scenarios**. Understanding these concepts and how they interact is essential for using BGPy effectively. Each concept is introduced briefly here with references to detailed documentation in child pages.

For information about installation and running your first simulation, see [Getting Started](/blcrdbob3/bgpy_pkg/2-getting-started). For detailed implementation guidance, see sections [3.1](/blcrdbob3/bgpy_pkg/3.1-simulation-framework-architecture) through [3.4](/blcrdbob3/bgpy_pkg/3.4-attack-scenarios-overview).

---

## The Four Core Abstractions

BGPy's architecture is built around four key abstractions that work together to model BGP security:
AbstractionPrimary ClassPurposeDetails**Simulation**`Simulation`Orchestrates execution of multiple trials across different adoption percentages[Section 3.1](/blcrdbob3/bgpy_pkg/3.1-simulation-framework-architecture)**AS Graph**`ASGraph`Represents the Internet topology with AS relationships[Section 3.2](/blcrdbob3/bgpy_pkg/3.2-as-graphs-and-network-topology)**Policy**`Policy` (BGP, ROV, ASPA, etc.)Defines how an AS processes and propagates BGP announcements[Section 3.3](/blcrdbob3/bgpy_pkg/3.3-bgp-policies-overview)**Scenario**`Scenario`Configures attack/defense conditions for a trial[Section 3.4](/blcrdbob3/bgpy_pkg/3.4-attack-scenarios-overview)
---

## Component Relationships

The following diagram shows how the four core abstractions relate to each other in BGPy's architecture:

```
creates

configures with

instantiates

runs multiple trials with

contains many

has one

configured by

assigns policies to

operates on

propagates on

specifies

Simulation
(simulation.py)

ASGraph
(as_graph.py)

AS
(base_as.py)

Policy
(BGP, ROV, ASPA, etc.)

Scenario
(scenario.py)

ScenarioConfig
(scenario_config.py)

SimulationEngine
(simulation_engine.py)
```

**Sources:**[bgpy/simulation_framework/simulation.py52-605](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L52-L605)[bgpy/as_graphs/base/as_graph/as_graph.py38-305](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L38-L305)[bgpy/simulation_framework/scenarios/scenario.py20-487](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L20-L487)

---

## Data Flow Through the System

The following diagram illustrates how data flows from configuration to results:

```
Output

Analysis

Trial Execution

Simulation Setup

Configuration

percent_adoptions
(0.1, 0.5, 0.8, etc.)

scenario_configs
(ScenarioConfig tuples)

num_trials
(statistical runs)

CAIDA Data
(AS relationships)

ASGraph
(Internet topology)

SimulationEngine
(propagation engine)

Scenario
(attack configuration)

Policy Assignment
(AdoptPolicyCls/BasePolicyCls)

Propagation Rounds
(providers→peers→customers)

ASGraphAnalyzer
(outcome determination)

GraphDataAggregator
(metric collection)

CSV Files
(metrics)

YAML Files
(engine state)

PNG Graphs
(visualizations)
```

**Sources:**[bgpy/simulation_framework/simulation.py250-267](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L250-L267)[bgpy/simulation_framework/simulation.py377-439](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L377-L439)

---

## Simulation: The Orchestrator

The `Simulation` class is the top-level entry point that coordinates all other components. It manages:

- **Multi-trial execution**: Runs statistical trials with randomized attacker/victim selection
- **Adoption sweeps**: Tests different adoption percentages (e.g., 10%, 50%, 80%)
- **Parallelization**: Distributes work across CPU cores for performance
- **Data aggregation**: Collects and stores metrics across all trials

**Key Configuration:**

```
Simulation(
    percent_adoptions=(0.1, 0.2, 0.5, 0.8),  # Adoption rates to test
    scenario_configs=(...),                    # Attack/defense configurations
    num_trials=100,                            # Statistical repetitions
    parse_cpus=8,                              # Parallel workers
)
```

The `Simulation` class creates an `ASGraph` from CAIDA data, instantiates a `SimulationEngine`, and runs each `Scenario` multiple times to gather statistically significant results.

**Detailed documentation:**[Simulation Framework Architecture](/blcrdbob3/bgpy_pkg/3.1-simulation-framework-architecture)

**Sources:**[bgpy/simulation_framework/simulation.py52-167](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L52-L167)

---

## AS Graph: The Network Topology

The `ASGraph` represents the Internet's AS-level topology with business relationships:
Relationship TypeDescriptionEconomic Incentive**Customer-Provider**Customer pays provider for transitProvider prioritizes customer routes**Peer-Peer**Settlement-free exchangeNeither pays, limited routing**IXP**Internet Exchange PointMulti-party peering facility
**Key Properties:**

- **AS objects**: Individual autonomous systems ([bgpy/as_graphs/base/as_graph/base_as.py14-212](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/base_as.py#L14-L212))
- **Relationships**: Customers, providers, peers stored as tuples
- **Metadata**: Customer cone sizes, propagation ranks, AS classifications
- **Groups**: Pre-computed sets of stubs, multihomed, transit, input clique ASes

```
as_dict[666]

as_dict[777]

as_dict[888]

provider

peer

ASGraph
(frozendict[int, AS])

AS(asn=666)
customers=(...)
providers=(...)
peers=(...)

AS(asn=777)
Policy=ROV()

AS(asn=888)
Policy=BGP()
```

The graph uses CAIDA's AS Relationships dataset to build a realistic topology with ~70,000 ASes and their business relationships.

**Detailed documentation:**[AS Graphs and Network Topology](/blcrdbob3/bgpy_pkg/3.2-as-graphs-and-network-topology)

**Sources:**[bgpy/as_graphs/base/as_graph/as_graph.py38-305](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L38-L305)[bgpy/as_graphs/base/as_graph/base_as.py14-212](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/base_as.py#L14-L212)

---

## Policy: Announcement Processing Logic

The `Policy` class hierarchy defines how ASes process BGP announcements. Each AS in the graph has exactly one policy instance that controls its behavior.

**Policy Hierarchy:**

```
Policy
(abstract base)

BGP
(basic routing)

BGPFull
(+RIBs +withdrawals)

ROV
(Route Origin Validation)

ASPA
(AS Path Attestation)

ASRA
(ASPA + fake link detection)

BGPSec
(cryptographic paths)
```

**Core Policy Methods:**
MethodPurposeCalled By`_process_incoming_anns()`Filters and validates announcementsEngine during propagation`_policy_propagate()`Determines which announcements to send to neighborsEngine during propagation`process_withdrawals()`Handles route withdrawals (BGPFull only)Engine during propagation
**Detailed documentation:**[BGP Policies Overview](/blcrdbob3/bgpy_pkg/3.3-bgp-policies-overview)

**Sources:**[bgpy/simulation_engine/policies/bgp/bgp.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp.py) (imported via simulation_framework), [bgpy/simulation_framework/scenarios/scenario_config.py9-17](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L9-L17)

---

## Scenario: Attack and Defense Configuration

A `Scenario` encapsulates a single attack/defense configuration for one trial. It specifies:

- **Attack type**: Which scenario class to instantiate (e.g., `PrefixHijack`, `SubprefixHijack`)
- **Participants**: Which ASes are attackers, victims, and adopters
- **Policies**: Which security policy adopting ASes use
- **Announcements**: What BGP announcements to inject
- **ROAs**: What RPKI Route Origin Authorizations exist

**Key Components:**

```
Runtime State

Configuration

ScenarioConfig
(immutable)

Scenario
(single trial)

ScenarioCls
(PrefixHijack)

AdoptPolicyCls
(ROV)

BasePolicyCls
(BGP)

num_attackers=1

num_victims=1

attacker_asns
(frozenset)

victim_asns
(frozenset)

adopting_asns
(frozenset)

announcements
(tuple)

roas
(tuple)
```

**Scenario Lifecycle:**

1. **Initialization**: Select random attackers, victims, and adopters based on `ScenarioConfig`
2. **Engine Setup**: Assign policies to ASes via `setup_engine()`
3. **Propagation**: Engine runs, scenarios can hook in via `pre_aggregation_hook()` and `post_propagation_hook()`

**Detailed documentation:**[Attack Scenarios Overview](/blcrdbob3/bgpy_pkg/3.4-attack-scenarios-overview)

**Sources:**[bgpy/simulation_framework/scenarios/scenario.py20-487](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L20-L487)[bgpy/simulation_framework/scenarios/scenario_config.py28-243](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L28-L243)

---

## Execution Model

The following diagram shows how the four concepts work together during a single trial:

```
AS (with Policy)
SimulationEngine
ASGraph
Scenario
ScenarioConfig
Simulation
AS (with Policy)
SimulationEngine
ASGraph
Scenario
ScenarioConfig
Simulation
Initialize with configs
loop
[For each propagation round]
loop
[For each trial]
Create from CAIDA data
Instantiate with ASGraph
Read config
Instantiate with random ASNs
Select attackers/victims/adopters
Generate announcements & ROAs
setup_engine()
Assign policies (AdoptPolicyCls or BasePolicyCls)
Seed initial announcements
Process announcements (Policy logic)
Apply Gao-Rexford, ROV, ASPA, etc.
Propagate to neighbors
Return final state
Analyze outcomes
Aggregate metrics
Write CSV, YAML, graphs
```

**Sources:**[bgpy/simulation_framework/simulation.py377-567](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L377-L567)[bgpy/simulation_framework/scenarios/scenario.py350-357](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L350-L357)

---

## Code Entity Mapping

The following table maps natural language concepts to their concrete implementations:
ConceptPrimary ClassFile LocationKey Methods/AttributesSimulation orchestrator`Simulation`[bgpy/simulation_framework/simulation.py52](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L52-L52)`run()`, `_run_chunk()`, `_single_engine_run()`Network topology`ASGraph`[bgpy/as_graphs/base/as_graph/as_graph.py38](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L38-L38)`as_dict`, `propagation_ranks`, `as_groups`Individual AS`AS`[bgpy/as_graphs/base/as_graph/base_as.py14](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/base_as.py#L14-L14)`asn`, `customers`, `providers`, `peers`, `policy`Routing behavior`Policy` subclasses[bgpy/simulation_engine/policies/](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/)`_process_incoming_anns()`, `_policy_propagate()`Attack configuration`Scenario` subclasses[bgpy/simulation_framework/scenarios/](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/)`setup_engine()`, `_get_announcements()`, `_get_roas()`Immutable config`ScenarioConfig`[bgpy/simulation_framework/scenarios/scenario_config.py28](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L28-L28)`ScenarioCls`, `AdoptPolicyCls`, `BasePolicyCls`Propagation engine`SimulationEngine`[bgpy/simulation_engine/](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/)`setup()`, `run()`, `propagate()`
**Sources:** All files listed in table above

---

## Next Steps

- **[Simulation Framework Architecture](/blcrdbob3/bgpy_pkg/3.1-simulation-framework-architecture)**: Deep dive into how `Simulation` orchestrates execution
- **[AS Graphs and Network Topology](/blcrdbob3/bgpy_pkg/3.2-as-graphs-and-network-topology)**: Detailed explanation of `ASGraph` structure and properties
- **[BGP Policies Overview](/blcrdbob3/bgpy_pkg/3.3-bgp-policies-overview)**: Complete policy hierarchy and implementation details
- **[Attack Scenarios Overview](/blcrdbob3/bgpy_pkg/3.4-attack-scenarios-overview)**: Taxonomy of attack scenarios and how to use them

For practical usage, see [Running Your First Simulation](/blcrdbob3/bgpy_pkg/2.2-running-your-first-simulation).

**Sources:**[Table of contents structure from provided context](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/Table of contents structure from provided context)