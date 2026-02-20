# Advanced Topics
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
- [scripts/two_multi_inheritance_ex.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/scripts/two_multi_inheritance_ex.py)
- [setup.cfg](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/setup.cfg)
- [tox.ini](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/tox.ini)

## Purpose and Scope

This page covers advanced usage patterns for extending BGPy with custom attack scenarios, security policies, and announcement/ROA management. These extension points allow researchers to implement novel BGP security mechanisms, model new attack vectors, and customize simulation behavior beyond the built-in policies and scenarios.

The three primary extension mechanisms are:

1. **Custom Scenarios** ([10.1](/blcrdbob3/bgpy_pkg/10.1-creating-custom-scenarios)) - Implementing new attack scenarios by extending `Scenario`
2. **Custom Policies** ([10.2](/blcrdbob3/bgpy_pkg/10.2-creating-custom-policies)) - Implementing new BGP security policies by extending `Policy`
3. **ROA and Announcement Management** ([10.3](/blcrdbob3/bgpy_pkg/10.3-roa-and-announcement-management)) - Controlling ROA generation and announcement preprocessing

For basic simulation setup and configuration, see [Getting Started](/blcrdbob3/bgpy_pkg/2-getting-started). For understanding the framework architecture, see [Core Concepts](/blcrdbob3/bgpy_pkg/3-core-concepts).

Sources: [bgpy/simulation_framework/scenarios/scenario.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py)[bgpy/simulation_framework/scenarios/scenario_config.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py)

---

## Extension Point Architecture

The BGPy framework provides three primary extension mechanisms that integrate with the simulation pipeline:

```
Configuration Layer

Extension Point 3: ROA Management

Extension Point 2: Custom Policies

Extension Point 1: Custom Scenarios

Core Simulation System

Simulation
Orchestrator

SimulationEngine
Propagation Engine

ASGraph
Network Topology

Scenario
Base Class

YourCustomScenario
extends Scenario

_get_announcements()
_get_roas()
_get_possible_attacker_asns()
post_propagation_hook()

Policy
Base Class

BGP
Basic Routing

YourCustomPolicy
extends Policy/BGP/ROV

_process_incoming_anns()
_valid_ann()
_copy_and_process()

Policy.roa_checker
ROAChecker Instance

_get_roas()
ROA Generation

_get_announcements()
Announcement Generation

ordered_prefix_subprefix_dict
Prefix Hierarchy

ScenarioConfig
ScenarioCls
AdoptPolicyCls
BasePolicyCls
```

**Key Integration Points**
Extension PointBase ClassConfigurationPrimary Use CaseCustom Scenarios`Scenario``ScenarioConfig.ScenarioCls`Model new attack vectors, route leaks, or operational scenariosCustom Policies`Policy`, `BGP`, `ROV``ScenarioConfig.AdoptPolicyCls` / `BasePolicyCls`Implement new BGP security mechanisms or validation logicROA ManagementMethods in `Scenario``ScenarioConfig.override_roas`Control RPKI validation behavior and prefix authorization
Sources: [bgpy/simulation_framework/simulation.py67-73](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L67-L73)[bgpy/simulation_framework/scenarios/scenario.py20-89](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L20-L89)[bgpy/simulation_framework/scenarios/scenario_config.py28-82](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L28-L82)

---

## Custom Scenario Development Overview

Custom scenarios define attack/defense test cases by controlling which ASes attack/defend, what announcements are generated, and what ROAs exist. The `Scenario` class provides the abstraction.

```
Key Methods to Override

Scenario Lifecycle

init()
Select attackers/victims
Generate announcements/ROAs

setup_engine()
Assign policies to ASes

Engine propagates
announcements

pre_aggregation_hook()
Pre-analysis modifications

post_propagation_hook()
Multi-round scenarios

_get_announcements()
Return tuple[Ann, ...]

_get_roas()
Return tuple[ROA, ...]

_get_possible_attacker_asns()
Return frozenset[int]

_get_possible_victim_asns()
Return frozenset[int]

get_policy_cls(as_obj)
Return Policy class
```

**Typical Override Pattern**

1. **Attacker/Victim Selection**: Override `_get_possible_attacker_asns()` or `_get_possible_victim_asns()` to constrain which ASes can participate
2. **Announcement Generation**: Override `_get_announcements()` to return attacker and victim announcements
3. **ROA Generation**: Override `_get_roas()` to control RPKI validation behavior
4. **Policy Assignment**: Override `get_policy_cls()` for per-AS policy customization
5. **Multi-Round Logic**: Override `post_propagation_hook()` for scenarios requiring multiple propagation rounds (e.g., route leaks)

**Configuration Integration**

Custom scenarios are specified in `ScenarioConfig.ScenarioCls` and can access configuration parameters via `self.scenario_config`:

- `scenario_config.num_attackers` / `scenario_config.num_victims`
- `scenario_config.AdoptPolicyCls` / `scenario_config.BasePolicyCls`
- `scenario_config.hardcoded_asn_cls_dict` for per-AS policy overrides
- `scenario_config.propagation_rounds` for multi-round scenarios

Detailed implementation guidance is provided in [Creating Custom Scenarios](/blcrdbob3/bgpy_pkg/10.1-creating-custom-scenarios).

Sources: [bgpy/simulation_framework/scenarios/scenario.py33-89](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L33-L89)[bgpy/simulation_framework/scenarios/scenario.py350-426](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L350-L426)[bgpy/simulation_framework/scenarios/scenario_config.py28-82](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L28-L82)

---

## Custom Policy Development Overview

Custom policies implement BGP routing and security logic by extending the `Policy` hierarchy. Most custom policies extend `BGP` (basic routing) or `ROV` (route origin validation) rather than the base `Policy` class.

```
Policy Assignment

Key Extension Methods

Policy Class Hierarchy

Policy
Abstract base
Defines interface

BGP
Basic Gao-Rexford routing
process_incoming_anns()
_valid_ann()

BGPFull
+RIBs +Withdrawals
ribs_in, ribs_out

ROV
+ROA validation
_valid_ann() checks ROAs

YourCustomPolicy
Override key methods

_process_incoming_anns()
Filter/modify announcements

_valid_ann(ann, recv_rel)
Validation logic

_copy_and_process(ann, recv_rel)
Announcement transformation

receive_ann(ann, recv_rel)
Main entry point

_process_outgoing_ann(ann, send_rel)
Outbound filtering

Scenario.get_policy_cls(as_obj)
Returns Policy class for AS

ScenarioConfig
AdoptPolicyCls
BasePolicyCls
AttackerBasePolicyCls

engine.setup(scenario)
Instantiate policies
```

**Common Policy Extension Patterns**
PatternBase ClassKey MethodsUse CasePath Validation`ROV` or `BGP``_valid_ann()`Reject announcements based on path attributes (e.g., ASPA)Announcement Transformation`BGP``_copy_and_process()`Modify announcements during propagation (e.g., add attributes)Selective Propagation`BGP``_process_outgoing_ann()`Control which announcements propagate to neighborsStateful Validation`BGP` or `ROV``_valid_ann()` + instance attributesUse local state for validation decisions
**Policy Assignment Flow**

1. `Simulation` creates `Scenario` with `ScenarioConfig`
2. `ScenarioConfig` specifies `AdoptPolicyCls`, `BasePolicyCls`, `AttackerBasePolicyCls`
3. `Scenario.setup_engine()` calls `engine.setup(scenario)`
4. `engine.setup()` iterates ASes, calls `scenario.get_policy_cls(as_obj)`
5. `get_policy_cls()` returns appropriate policy class based on AS role (attacker/victim/adopter)
6. Engine instantiates policy: `PolicyCls(as_obj)`

**Accessing ROA Checker**

All policies share a class-level `Policy.roa_checker` instance for RPKI validation:

```
# In your custom policy's _valid_ann() method
roa_validity = Policy.roa_checker.get_validity(ann.prefix, ann.origin, ann.as_path)
```

Detailed implementation guidance is provided in [Creating Custom Policies](/blcrdbob3/bgpy_pkg/10.2-creating-custom-policies).

Sources: [bgpy/simulation_framework/scenarios/scenario.py358-373](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L358-L373)[bgpy/simulation_framework/scenarios/scenario_config.py41-45](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L41-L45)[bgpy/simulation_engine/policies/bgp/bgp.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp.py)

---

## ROA and Announcement Management Overview

ROAs (Route Origin Authorizations) and announcements are the fundamental data structures that control RPKI validation and BGP propagation. Custom scenarios manage these through specialized methods.

```
Override Options

Prefix Hierarchy Management

Announcement Generation Flow

ROA Generation Flow

Scenario._get_roas()
Override to return ROAs

_reset_and_add_roas_to_roa_checker()
Clear + populate Policy.roa_checker

Policy.roa_checker
ROAChecker instance
Shared across all policies

Scenario._get_announcements()
Override to return announcements

engine.setup(scenario)
Seeds initial announcements

engine.run()
Propagates announcements

ordered_prefix_subprefix_dict
Maps prefix -> subprefixes

_get_ordered_prefix_subprefix_dict()
Built from announcements + ROAs

ASGraphAnalyzer
Uses for data plane traceback

ScenarioConfig
override_announcements
override_roas

Scenario methods
_get_announcements()
_get_roas()
```

**ROA Management**

ROAs are stored in the shared `Policy.roa_checker` instance (a `ROAChecker` from the `roa-checker` package). The `Scenario` class manages ROA lifecycle:

1. `_get_roas()` returns `tuple[ROA, ...]`
2. `_reset_and_add_roas_to_roa_checker()` clears previous ROAs and inserts new ones
3. All policies access the same `Policy.roa_checker.get_validity()` for validation

**Announcement Management**

Announcements are generated per-scenario and seeded into the engine:

1. `_get_announcements()` returns `tuple[Announcement, ...]`
2. Typically includes victim announcements and attacker announcements
3. Engine seeds these via `engine.setup(scenario)`
4. Use `scenario_config.AnnCls` to specify custom announcement class

**Prefix Hierarchy**

The `ordered_prefix_subprefix_dict` maps each prefix to its subprefixes, sorted by specificity (most specific first). This is crucial for:

- **Data Plane Traceback**: Finding the most specific prefix match for route selection
- **ROV++ Blackholing**: Identifying which prefixes to blackhole based on ROA relationships
- **Superprefix/Subprefix Attacks**: Determining prefix containment relationships

Built automatically from all announcements and ROAs via `_get_ordered_prefix_subprefix_dict()`.

Detailed implementation guidance is provided in [ROA and Announcement Management](/blcrdbob3/bgpy_pkg/10.3-roa-and-announcement-management).

Sources: [bgpy/simulation_framework/scenarios/scenario.py73-88](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L73-L88)[bgpy/simulation_framework/scenarios/scenario.py379-402](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L379-L402)[bgpy/simulation_framework/scenarios/scenario.py431-458](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L431-L458)

---

## Integration Patterns

This section illustrates common patterns for integrating custom scenarios and policies.

### Pattern 1: Custom Scenario with Built-in Policy

Testing a new attack against existing defenses:

```
Configuration

Built-in Policies

Your Implementation

YourAttackScenario
extends Scenario
_get_announcements()
_get_roas()

ROV

ASPA

BGP

ScenarioConfig(
  ScenarioCls=YourAttackScenario,
  AdoptPolicyCls=ROV,
  BasePolicyCls=BGP
)

ScenarioConfig(
  ScenarioCls=YourAttackScenario,
  AdoptPolicyCls=ASPA,
  BasePolicyCls=BGP
)
```

**Example Workflow**:

- Implement attack logic in `_get_announcements()`
- Generate appropriate ROAs in `_get_roas()`
- Test against multiple policies by creating multiple `ScenarioConfig` instances
- Framework handles policy assignment and metric aggregation

Sources: [bgpy/simulation_framework/scenarios/scenario_config.py28-82](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L28-L82)

---

### Pattern 2: Custom Policy with Built-in Scenarios

Testing a new defense against known attacks:

```
Configuration

Your Implementation

Built-in Scenarios

PrefixHijack

SubprefixHijack

NonRoutedPrefixHijack

YourDefensePolicy
extends ROV
_valid_ann()
_process_incoming_anns()

ScenarioConfig(
  ScenarioCls=PrefixHijack,
  AdoptPolicyCls=YourDefensePolicy,
  BasePolicyCls=BGP
)

ScenarioConfig(
  ScenarioCls=SubprefixHijack,
  AdoptPolicyCls=YourDefensePolicy,
  BasePolicyCls=BGP
)
```

**Example Workflow**:

- Extend `ROV` or `BGP` to inherit base functionality
- Override `_valid_ann()` for validation logic
- Override `_process_incoming_anns()` for announcement filtering
- Test against multiple attack scenarios via different `ScenarioConfig` instances

Sources: [bgpy/simulation_framework/scenarios/scenario_config.py28-82](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L28-L82)

---

### Pattern 3: Custom Attacker Policy

Some attacks require custom attacker behavior (e.g., ASPA evasion):

```
Your Implementation

Policy Assignment Logic

Scenario Configuration

Yes

No

Yes

No

ScenarioConfig
AttackerBasePolicyCls=YourAttackerPolicy

Scenario.get_policy_cls(as_obj)

asn in
attacker_asns?

Return AttackerBasePolicyCls

asn in
adopting_asns?

Return AdoptPolicyCls

Return BasePolicyCls

YourAttackerPolicy
Custom attacker logic
```

**Example Usage**:

```
ScenarioConfig(
    ScenarioCls=ShortestPathPrefixHijack,
    AdoptPolicyCls=ASPA,
    BasePolicyCls=BGP,
    AttackerBasePolicyCls=ASPAShortestPathAttacker  # Custom attacker
)
```

The scenario automatically assigns `AttackerBasePolicyCls` to attacker ASes via `get_policy_cls()`.

Sources: [bgpy/simulation_framework/scenarios/scenario.py358-373](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L358-L373)[bgpy/simulation_framework/scenarios/scenario_config.py44-45](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L44-L45)[bgpy/simulation_framework/scenarios/scenario_config.py135-144](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L135-L144)

---

### Pattern 4: Per-AS Policy Customization

Fine-grained control over individual AS policies:

```
Policy Assignment Logic

Configuration

Yes

No

Yes

No

Yes

No

Yes

No

ScenarioConfig
hardcoded_asn_cls_dict=frozendict({
  1234: PolicyA,
  5678: PolicyB
})
hardcoded_base_asn_cls_dict=frozendict({
  9999: PolicyC
})

get_policy_cls(as_obj)

Attacker?

In hardcoded_
asn_cls_dict?

In adopting_asns?

In hardcoded_base_
asn_cls_dict?

AttackerBasePolicyCls

hardcoded_asn_cls_dict[asn]

AdoptPolicyCls

hardcoded_base_asn_cls_dict[asn]

BasePolicyCls
```

**Use Cases**:

- Model specific ASes (e.g., Tier-1 providers) with unique policies
- Create heterogeneous deployment scenarios
- Test partial deployment with specific AS configurations

**Important**: Use `frozendict` for `hardcoded_asn_cls_dict` to ensure `ScenarioConfig` remains hashable.

Sources: [bgpy/simulation_framework/scenarios/scenario.py358-373](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L358-L373)[bgpy/simulation_framework/scenarios/scenario_config.py59-68](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L59-L68)

---

### Pattern 5: Multi-Round Propagation

Some scenarios require multiple propagation rounds (e.g., route leaks):

```
Configuration

Round 1: Secondary Propagation

Round 0: Initial Propagation

setup_engine()
Seed victim anns

engine.run(round=0)

post_propagation_hook()
Modify announcements

engine.run(round=1)
Propagate modified anns

post_propagation_hook()
Cleanup if needed

ScenarioConfig
propagation_rounds=2
```

**Example Implementation Pattern**:

```
class YourMultiRoundScenario(Scenario):
    min_propagation_rounds = 2
    
    def post_propagation_hook(
        self, 
        engine: BaseSimulationEngine,
        propagation_round: int,
        **kwargs
    ) -> None:
        if propagation_round == 0:
            # Modify announcements after first round
            for as_obj in engine:
                # Access as_obj._local_rib
                # Add/modify announcements
                pass
```

The `Simulation` class automatically calls `engine.run()` for each propagation round specified in `ScenarioConfig.propagation_rounds`.

Sources: [bgpy/simulation_framework/simulation.py414-423](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L414-L423)[bgpy/simulation_framework/scenarios/scenario.py416-425](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L416-L425)[bgpy/simulation_framework/scenarios/scenario_config.py94-117](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L94-L117)

---

## Testing Custom Implementations

Custom scenarios and policies should be tested using the BGPy test framework (see [Testing and Development](/blcrdbob3/bgpy_pkg/9-testing-and-development)):

**Key Testing Practices**:

1. **Use `EngineTester`**: Extends `EngineRunner` with ground truth comparison ([9.1](/blcrdbob3/bgpy_pkg/9.1-test-framework-architecture))
2. **Generate Ground Truth**: Run with `--overwrite` flag to create baseline YAML files ([9.2](/blcrdbob3/bgpy_pkg/9.2-ground-truth-management))
3. **Verify Outcomes**: Test framework compares `engine_gt.yaml`, `outcomes_gt.yaml`, `metrics_gt.csv`
4. **Small AS Graphs**: Use minimal topologies for unit tests (faster, easier to debug)
5. **Multiple Scenarios**: Test custom policies against multiple attack scenarios
6. **Edge Cases**: Test with `ONLY_ONE` and `ALL_BUT_ONE` adoption levels

**Example Test Structure**:

```
def test_your_custom_policy():
    engine_tester = EngineTester(
        BaseASGraphConstructor=YourTestGraphConstructor,
        scenario_config=ScenarioConfig(
            ScenarioCls=PrefixHijack,
            AdoptPolicyCls=YourCustomPolicy,
            BasePolicyCls=BGP,
        ),
        # ... other config
    )
    engine_tester.run()
```

Sources: [bgpy/tests/engine_tests/engine_test_configs/engine_tester.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/engine_test_configs/engine_tester.py)

---

## Summary

BGPy provides three primary extension points for advanced usage:
Extension PointImplementationConfigurationTestingCustom ScenariosExtend `Scenario`, override `_get_announcements()`, `_get_roas()``ScenarioConfig.ScenarioCls``EngineTester` with test AS graphCustom PoliciesExtend `Policy`/`BGP`/`ROV`, override `_valid_ann()`, `_process_incoming_anns()``ScenarioConfig.AdoptPolicyCls`Multiple scenario configsROA ManagementOverride `_get_roas()` in scenario, access `Policy.roa_checker``ScenarioConfig.override_roas`Validate with ROV policies
For detailed implementation guidance:

- **Custom Scenarios**: See [Creating Custom Scenarios](/blcrdbob3/bgpy_pkg/10.1-creating-custom-scenarios)
- **Custom Policies**: See [Creating Custom Policies](/blcrdbob3/bgpy_pkg/10.2-creating-custom-policies)
- **ROA/Announcement Management**: See [ROA and Announcement Management](/blcrdbob3/bgpy_pkg/10.3-roa-and-announcement-management)

Sources: [bgpy/simulation_framework/scenarios/scenario.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py)[bgpy/simulation_framework/scenarios/scenario_config.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py)[bgpy/simulation_framework/simulation.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py)