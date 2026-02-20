# BGPy File Index

**NOTE**: Only add new files/features to the codebase. Do not edit existing files to preserve functionality. (See `PARAMETERS.md` for details.)

**WIKI FIRST**: Before exploring source files for any non-trivial task, consult `.claude/wiki/`. These are narrative deep-dives with diagrams and usage examples exported from DeepWiki. The section "DeepWiki Pages" below lists all available wiki files by topic. Do not read wiki files in their entirety; search or skim for the relevant section.

Complete reference of important files for understanding and extending the codebase.

## Entry Points & Package Metadata

| File | Purpose | How to Use |
|------|---------|-----------|
| `bgpy/__main__.py` | CLI entry point and example simulation | Reference for typical usage pattern; shows SubprefixHijack + ROV example |
| `bgpy/__init__.py` | Package initialization exposing core modules | Reference the public API structure |
| `pyproject.toml` | Project config, dependencies, build settings | Check version, Python requirement, tool configs (ruff, mypy, pytest) |

## Core Framework Classes

| File | Purpose | How to Use |
|------|---------|-----------|
| `bgpy/simulation_framework/simulation.py` | Main orchestrator for multi-trial simulations with adoption rates | Run end-to-end simulations; configure adoption percentages, output directories |
| `bgpy/simulation_framework/scenarios/scenario.py` | Single trial with attackers, victims, adopters, announcements, ROAs | Create new attack scenario types; understand attack/defense mechanics |
| `bgpy/simulation_framework/scenarios/scenario_config.py` | Configuration template for scenario type (frozen, reusable) | Configure which policies to test and how attackers/victims are selected |

## Simulation Engine Classes

| File | Purpose | How to Use |
|------|---------|-----------|
| `bgpy/simulation_engine/announcement.py` | Immutable BGP announcement with prefix, AS path, optional attributes | Understand announcement propagation; see `copy()` for efficient replication |
| `bgpy/simulation_engine/simulation_engines/simulation_engine.py` | Concrete engine that propagates announcements round-by-round | Run simulations; understand propagation by relationship type |
| `bgpy/simulation_engine/simulation_engines/base_simulation_engine.py` | Abstract base for simulation engines | Extend the simulator with alternate implementations |

## Policy Framework

| File | Purpose | How to Use |
|------|---------|-----------|
| `bgpy/simulation_engine/policies/policy.py` | Abstract base for all BGP security policies | Create new policies; implement `receive_ann()`, `process_incoming_anns()`, `propagate_to_*()` |
| `bgpy/simulation_engine/policies/bgp/bgp/bgp.py` | Standard BGP with Gao-Rexford route selection | Reference template for new policy implementations |
| `bgpy/simulation_engine/__init__.py` | Exports all policy implementations | See available policies: BGP, ROV, ASPA, BGPSec, BGPiSec, ROST, EdgeFilter, etc. |

## AS Graph & Topology

| File | Purpose | How to Use |
|------|---------|-----------|
| `bgpy/as_graphs/base/as_graph/as_graph.py` | Complete BGP topology with AS nodes, relationships, algorithms | Work with network topology; analyze cone sizes, relationships |
| `bgpy/as_graphs/base/as_graph/base_as.py` | Individual Autonomous System (AS) node | Understand AS-level properties, relationships, cones, ranks |
| `bgpy/as_graphs/base/as_graph_info.py` | Topology input data: links, peers, unlinked ASNs | Build custom AS graphs; parse topology data |
| `bgpy/as_graphs/caida_as_graph/caida_as_graph.py` | CAIDA topology implementation | Use real-world topology data from CAIDA |
| `bgpy/as_graphs/base/as_graph_constructor.py` | Pipeline: download → parse → build graph | Build custom AS graph sources; modify topology construction |
| `bgpy/as_graphs/__init__.py` | Exports ASGraph, AS, ASGraphCollector, CAIDAASGraph | Access topology-related classes |

## Data Structures & Utilities

| File | Purpose | How to Use |
|------|---------|-----------|
| `bgpy/simulation_engine/ann_containers/local_rib.py` | Best routes per prefix (Routing Information Base) | Understand how ASes store best route selections |
| `bgpy/shared/enums.py` | Core enums: Relationships, Outcomes, ROAValidity, ASGroups | Reference for enum constants throughout codebase |
| `bgpy/shared/constants.py` | Logging configuration and cache directories | Configure logging; manage CAIDA download cache |
| `bgpy/utils/utils.py` | ROV adoption utilities: `get_real_world_rov_asn_cls_dict()` | Use real-world ROV deployment statistics |
| `bgpy/shared/__init__.py` | Exports constants, enums, exceptions | Access shared utilities |

## Test Infrastructure

| File | Purpose | How to Use |
|------|---------|-----------|
| `bgpy/tests/conftest.py` | Pytest config: CAIDA caching, test aggregation | Configure test behavior; understand test setup |
| `bgpy/tests/engine_tests/test_engine.py` | Parametrized system tests (31+ configurations) | Run engine validation tests; see test validation patterns |
| `bgpy/tests/engine_tests/utils/engine_tester.py` | Individual test runner with diagram comparison | Debug specific engine behavior; validate announcements |
| `bgpy/tests/engine_tests/engine_test_configs/examples/` | 100+ predefined test scenarios | Reference test configurations; use as templates |

## Scenario Implementations

| File | Purpose | How to Use |
|------|---------|-----------|
| `bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/prefix_hijack.py` | Example: attacker and victim announce same prefix | Template for new attack scenarios |
| `bgpy/simulation_framework/scenarios/custom_scenarios/valid_prefix.py` | Baseline: only victim announces (control case) | Reference minimal scenario implementation |

## Module Exports

| File | Purpose | How to Use |
|------|---------|-----------|
| `bgpy/simulation_framework/__init__.py` | Exports scenarios, Simulation class, graphing | Access high-level framework API |

---

## DeepWiki Pages (.claude/wiki/)

Exported documentation from deepwiki.com/blcrdbob3/bgpy_pkg. Read these for narrative explanations, diagrams, and usage examples. Do not read in their entirety; search or skim for the relevant section.

### Getting Started
| File | Topic |
|------|-------|
| `wiki/Overview.md` | Project overview, capabilities, architecture summary |
| `wiki/Getting-Started.md` | Getting started index |
| `wiki/Installation-and-Setup.md` | Python version requirements, Graphviz, RAM, troubleshooting |
| `wiki/Running-Your-First-Simulation.md` | Minimal working example, key parameters |
| `wiki/Understanding-Simulation-Output.md` | CSV data, pickle files, PNG visualizations |

### Core Concepts
| File | Topic |
|------|-------|
| `wiki/Core-Concepts.md` | Core concepts index |
| `wiki/Simulation-Framework-Architecture.md` | Layered architecture overview |
| `wiki/AS-Graphs-and-Network-Topology.md` | AS relationships, topology representation |
| `wiki/BGP-Policies-Overview.md` | Policy hierarchy and selection model |
| `wiki/Attack-Scenarios-Overview.md` | Hijack types and scenario structure |

### Simulation Framework
| File | Topic |
|------|-------|
| `wiki/Simulation-Framework-Deep-Dive.md` | Framework deep-dive index |
| `wiki/Simulation-Class-and-Execution-Pipeline.md` | Simulation class, trial loop, adoption percentages |
| `wiki/Scenario-Configuration.md` | ScenarioConfig fields, attacker/victim selection |
| `wiki/Multi-Processing-and-Performance.md` | multiprocessing.Pool usage, parse_cpus, memory tips |

### AS Graph System
| File | Topic |
|------|-------|
| `wiki/AS-Graph-System.md` | AS graph system index |
| `wiki/AS-Graph-Structure-and-Properties.md` | ASGraph internals, cones, propagation ranks |
| `wiki/CAIDA-Data-and-Graph-Construction.md` | CAIDA download pipeline, TSV parsing, caching |
| `wiki/AS-Groups-and-Categorization.md` | ASGroups enum, stubs, multihomed, transit, etc. |

### BGP Policy Reference
| File | Topic |
|------|-------|
| `wiki/BGP-Policy-Reference.md` | Policy reference index |
| `wiki/Base-BGP-Policies.md` | BGP and Gao-Rexford rules |
| `wiki/Route-Origin-Validation-(ROV).md` | ROV, PeerROV, ROA validation logic |
| `wiki/ROV++-Policies.md` | ROV++ policy family |
| `wiki/ASPA-Policy-Family.md` | ASPA, ASPAwN, ASRA policies |
| `wiki/Other-Security-Policies.md` | BGPSec, BGPiSec, PathEnd, PeerlockLite, EdgeFilter, etc. |

### Attack Scenario Reference
| File | Topic |
|------|-------|
| `wiki/Attack-Scenario-Reference.md` | Scenario reference index |
| `wiki/Pre-ROV-Attack-Scenarios.md` | PrefixHijack, SubprefixHijack, SuperprefixPrefixHijack |
| `wiki/Post-ROV-Attack-Scenarios.md` | ForgedOriginPrefixHijack and post-ROV variants |
| `wiki/Non-Routed-Prefix-Attacks.md` | NonRoutedPrefixHijack scenarios |
| `wiki/Route-Leak-Scenarios.md` | AccidentalRouteLeak and related scenarios |
| `wiki/Custom-Attacker-Policies.md` | Writing policies for attacker ASes |

### Analysis and Visualization
| File | Topic |
|------|-------|
| `wiki/Analysis-and-Visualization.md` | Analysis index |
| `wiki/Outcome-Analysis.md` | ASGraphAnalyzer, outcome classification |
| `wiki/Data-Aggregation.md` | GraphDataAggregator, CSV output format |
| `wiki/Graph-Generation.md` | GraphFactory, matplotlib line plots |
| `wiki/Diagram-Generation.md` | Graphviz AS-graph diagrams for engine tests |

### Testing and Development
| File | Topic |
|------|-------|
| `wiki/Testing-and-Development.md` | Testing index |
| `wiki/Test-Framework-Architecture.md` | Test layout, conftest, fixtures, parametrization |
| `wiki/Ground-Truth-Management.md` | Ground-truth YAML/CSV files, --overwrite flag |
| `wiki/Development-Practices.md` | ruff, mypy, pre-commit, tox workflow |

### Advanced Topics
| File | Topic |
|------|-------|
| `wiki/Advanced-Topics.md` | Advanced topics index |
| `wiki/Creating-Custom-Scenarios.md` | Subclassing Scenario, overriding _get_announcements/_get_roas |
| `wiki/Creating-Custom-Policies.md` | Subclassing Policy, auto-registration, propagation hooks |
| `wiki/ROA-and-Announcement-Management.md` | ROA construction, Announcement fields, RPKI validation |

---

## Quick Reference by Task

**I want to... | Start here**
- Run a simulation → `bgpy/simulation_framework/simulation.py` or `bgpy/__main__.py`
- Create a new policy → `bgpy/simulation_engine/policies/policy.py` + look at `bgp.py` as template
- Create a new attack scenario → `bgpy/simulation_framework/scenarios/scenario.py` + look at `prefix_hijack.py`
- Use custom topology → `bgpy/as_graphs/base/as_graph/as_graph.py` or `as_graph_info.py`
- Understand announcement flow → `bgpy/simulation_engine/announcement.py` + `simulation_engine.py`
- Work with real-world data → `bgpy/as_graphs/caida_as_graph/caida_as_graph.py` or `bgpy/utils/utils.py`
- Debug tests → `bgpy/tests/engine_tests/test_engine.py` or `engine_tester.py`
- Understand routing rules → `bgpy/simulation_engine/policies/bgp/bgp/bgp.py`
