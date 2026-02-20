# Creating Custom Scenarios
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

This page guides developers through creating custom attack scenarios by extending BGPy's `Scenario` base class. Custom scenarios allow you to model new BGP security attacks, operational errors, or alternative routing behaviors. This document covers the scenario lifecycle, key extension points, and integration patterns.

For information about creating custom security policies that defend against attacks, see [Creating Custom Policies](/blcrdbob3/bgpy_pkg/10.2-creating-custom-policies). For details on announcement and ROA management, see [ROA and Announcement Management](/blcrdbob3/bgpy_pkg/10.3-roa-and-announcement-management).

---

## Scenario System Architecture

The following diagram shows how custom scenarios fit into the BGPy simulation pipeline:

```
Custom Scenario Methods

|inherits| BaseScenario
ScenarioConfig

User Code
Custom Scenario Definition

ScenarioConfig
dataclass

Scenario
Base Class

Custom Scenario
Extends Scenario

Simulation
Orchestrator

SimulationEngine
Propagation Engine

ASGraph
Network Topology

_get_announcements()

_get_roas()

pre_aggregation_hook()

post_propagation_hook()

_get_attacker_asns()

_get_victim_asns()
```

**Sources**: [bgpy/simulation_framework/scenarios/scenario.py1-487](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L1-L487)[bgpy/simulation_framework/simulation.py399-423](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L399-L423)

---

## Base Scenario Class Structure

The `Scenario` class [bgpy/simulation_framework/scenarios/scenario.py20-487](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L20-L487) provides the foundation for all attack scenarios. Each scenario instance represents a single trial with specific attacker/victim ASNs, announcements, and ROAs.

### Key Attributes
AttributeTypePurpose`scenario_config``ScenarioConfig`Immutable configuration defining policies and parameters`attacker_asns``frozenset[int]`ASNs performing the attack`victim_asns``frozenset[int]`ASNs being attacked`adopting_asns``frozenset[int]`ASNs adopting the defensive policy`announcements``tuple[Ann, ...]`BGP announcements seeded in the simulation`roas``tuple[ROA, ...]`RPKI Route Origin Authorizations`min_propagation_rounds``int`Minimum rounds required (default: 1)
**Sources**: [bgpy/simulation_framework/scenarios/scenario.py33-88](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L33-L88)

### Scenario Lifecycle

```
ASGraph
SimulationEngine
Custom Scenario
Simulation
ASGraph
SimulationEngine
Custom Scenario
Simulation
loop
[For each propagation round]
__init__(config, engine, ...)
_get_attacker_asns()
_get_victim_asns()
_get_adopting_asns()
_get_announcements()
_get_roas()
setup_engine(engine)
setup(self)
Set AS policy classes
Seed announcements
run(round, scenario)
Propagate announcements
pre_aggregation_hook()
post_propagation_hook()
```

**Sources**: [bgpy/simulation_framework/scenarios/scenario.py33-88](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L33-L88)[bgpy/simulation_framework/simulation.py414-437](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L414-L437)[bgpy/simulation_engine/simulation_engines/simulation_engine.py20-56](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/simulation_engines/simulation_engine.py#L20-L56)

---

## Creating a Basic Scenario

### Step 1: Define Your Scenario Class

Create a new class extending `Scenario` and override `_get_announcements()`:

```
from bgpy.simulation_framework.scenarios import Scenario
from bgpy.shared.enums import Prefixes, Relationships, Timestamps

class MyCustomHijack(Scenario):
    """Describe your attack scenario"""
    
    def _get_announcements(
        self,
        *,
        engine: Optional["BaseSimulationEngine"] = None,
    ) -> tuple["Ann", ...]:
        """Generate announcements for your attack"""
        
        anns = []
        
        # Victim announces legitimate prefix
        for victim_asn in self.victim_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.PREFIX.value,
                    as_path=(victim_asn,),
                    timestamp=Timestamps.VICTIM.value,
                    seed_asn=victim_asn,
                    recv_relationship=Relationships.ORIGIN,
                )
            )
        
        # Attacker announces hijacked prefix
        for attacker_asn in self.attacker_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.PREFIX.value,  # Same prefix
                    as_path=(attacker_asn,),
                    timestamp=Timestamps.ATTACKER.value,
                    seed_asn=attacker_asn,
                    recv_relationship=Relationships.ORIGIN,
                )
            )
        
        return tuple(anns)
```

**Sources**: [bgpy/simulation_framework/scenarios/scenario.py379-389](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L379-L389)[bgpy/simulation_framework/scenarios/custom_scenarios/victims_prefix.py21-44](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/victims_prefix.py#L21-L44)

### Step 2: Define ROAs (Optional)

Override `_get_roas()` to generate RPKI ROAs:

```
from roa_checker import ROA
from ipaddress import ip_network

class MyCustomHijack(Scenario):
    # ... previous code ...
    
    def _get_roas(
        self,
        *,
        announcements: tuple["Ann", ...] = (),
        engine: Optional["BaseSimulationEngine"] = None,
    ) -> tuple[ROA, ...]:
        """Generate ROAs authorizing victim's prefix"""
        
        return tuple([
            ROA(ip_network(Prefixes.PREFIX.value), victim_asn)
            for victim_asn in self.victim_asns
        ])
```

**Sources**: [bgpy/simulation_framework/scenarios/scenario.py391-402](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L391-L402)[bgpy/simulation_framework/scenarios/custom_scenarios/victims_prefix.py46-56](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/victims_prefix.py#L46-L56)

### Step 3: Create ScenarioConfig

Define the configuration specifying policies and parameters:

```
from bgpy.simulation_framework.scenarios import ScenarioConfig
from bgpy.simulation_engine import BGP, ROV

config = ScenarioConfig(
    ScenarioCls=MyCustomHijack,
    BasePolicyCls=BGP,           # Non-adopting ASes use BGP
    AdoptPolicyCls=ROV,          # Adopting ASes use ROV
    num_attackers=1,
    num_victims=1,
)
```

**Sources**: [bgpy/simulation_framework/scenarios/scenario_config.py28-81](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L28-L81)

### Step 4: Use in Simulation

Pass your scenario config to the `Simulation` class:

```
from bgpy.simulation_framework import Simulation

sim = Simulation(
    scenario_configs=(config,),
    num_trials=100,
)
sim.run()
```

**Sources**: [bgpy/simulation_framework/simulation.py52-153](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L52-L153)

---

## Advanced Scenario Features

### Multi-Round Propagation

Some scenarios require multiple propagation rounds. Set `min_propagation_rounds` and use hooks to control behavior between rounds:

```
Round 1

Round 0

Setup Engine

Propagate

pre_aggregation_hook

post_propagation_hook

Propagate

pre_aggregation_hook

post_propagation_hook
```

Example from `AccidentalRouteLeak`:

```
class AccidentalRouteLeak(VictimsPrefix):
    min_propagation_rounds: int = 2  # Requires 2 rounds
    
    def post_propagation_hook(
        self,
        engine: "BaseSimulationEngine",
        percent_adopt: float | SpecialPercentAdoptions,
        trial: int,
        propagation_round: int,
    ) -> None:
        """After round 0, modify announcements to cause leak"""
        
        if propagation_round == 0:
            # Extract legitimate announcement from attacker's RIB
            announcements: list[Ann] = list(self.announcements)
            
            for attacker_asn in self.attacker_asns:
                for _prefix, ann in engine.as_graph.as_dict[
                    attacker_asn
                ].policy.local_rib.items():
                    # Re-announce as if received from customer
                    announcements.append(
                        ann.copy({
                            "recv_relationship": Relationships.ORIGIN,
                            "seed_asn": attacker_asn,
                            "timestamp": Timestamps.ATTACKER.value,
                        })
                    )
            
            # Update announcements and reset engine
            self.announcements = tuple(announcements)
            self.setup_engine(engine)
            engine.ready_to_run_round = 1
```

**Sources**: [bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py21-133](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py#L21-L133)[bgpy/simulation_framework/scenarios/scenario.py416-425](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L416-L425)

### Hook Methods

The `Scenario` class provides two hook methods:
HookWhen CalledUse Cases`pre_aggregation_hook()`After propagation, before metric collectionValidate state, log debug info`post_propagation_hook()`After metric collectionModify announcements, trigger second round
**Sources**: [bgpy/simulation_framework/scenarios/scenario.py404-425](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L404-L425)[bgpy/simulation_framework/simulation.py514-537](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L514-L537)

---

## Customizing Attacker/Victim Selection

### Custom Attacker Selection

Override `_get_possible_attacker_asns()` to restrict which ASes can attack:

```
from bgpy.shared.enums import ASGroups

class MyScenario(Scenario):
    def _get_possible_attacker_asns(
        self,
        engine: BaseSimulationEngine,
        percent_adoption: float | SpecialPercentAdoptions,
    ) -> frozenset[int]:
        """Only allow multihomed ASes to attack"""
        
        possible_asns = engine.as_graph.asn_groups[
            ASGroups.MULTIHOMED.value
        ]
        return possible_asns
```

The base implementation uses `attacker_subcategory_attr` from `ScenarioConfig`:

```
config = ScenarioConfig(
    ScenarioCls=MyScenario,
    attacker_subcategory_attr=ASGroups.MULTIHOMED.value,  # Control via config
    # ...
)
```

**Sources**: [bgpy/simulation_framework/scenarios/scenario.py168-181](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L168-L181)[bgpy/simulation_framework/scenarios/scenario_config.py54-56](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L54-L56)

### Custom Victim Selection

Similarly, override `_get_possible_victim_asns()`:

```
class MyScenario(Scenario):
    def _get_possible_victim_asns(
        self,
        engine: BaseSimulationEngine,
        percent_adoption: float | SpecialPercentAdoptions,
    ) -> frozenset[int]:
        """Customize victim selection logic"""
        
        possible_asns = super()._get_possible_victim_asns(engine, percent_adoption)
        
        # Example: Exclude certain ASes
        possible_asns = possible_asns - self.custom_excluded_asns
        
        return possible_asns
```

The `AccidentalRouteLeak` scenario excludes attackers' customer cones from victim selection:

**Sources**: [bgpy/simulation_framework/scenarios/scenario.py222-237](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L222-L237)[bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py167-181](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py#L167-L181)

---

## Custom Attacker Policies

For scenarios where attackers need special routing behaviors (e.g., path manipulation), define a custom attacker policy and reference it in `ScenarioConfig`:

### Attacker Policy Class Hierarchy

```
Custom Methods

Policy
Abstract Base

BGP
Basic Routing

CustomAttackerPolicy
Extends BGP

process_incoming_anns()

_policy_propagate()
```

### Example: ShortestPathPrefixASPAAttacker

This attacker sends origin hijacks to customers when using ASPA:

```
from bgpy.simulation_engine.policies.bgp import BGP
from bgpy.shared.enums import Relationships

class ShortestPathPrefixASPAAttacker(BGP):
    def _policy_propagate(
        self: "BGP",
        neighbor: "AS",
        ann: "Ann",
        propagate_to: Relationships,
        send_rels: set[Relationships],
    ) -> bool:
        """Use origin hijack for customers to evade ASPA"""
        
        if (
            propagate_to == Relationships.CUSTOMERS
            and ann.recv_relationship == Relationships.ORIGIN
            and len(ann.as_path) > 1
        ):
            # Send forged-origin announcement to customers
            new_ann = ann.copy({
                "as_path": (self.as_.asn, ann.origin),
                "seed_asn": None,
            })
            self._process_outgoing_ann(neighbor, new_ann, propagate_to, send_rels)
            return True
        else:
            return False
```

**Sources**: [bgpy/simulation_engine/policies/custom_attackers/shortest_path_prefix_aspa_attacker.py1-65](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/custom_attackers/shortest_path_prefix_aspa_attacker.py#L1-L65)

### Linking Attacker Policy to Scenario

Use `AttackerBasePolicyCls` in `ScenarioConfig`:

```
from bgpy.simulation_framework.scenarios import ScenarioConfig

config = ScenarioConfig(
    ScenarioCls=ShortestPathPrefixHijack,
    BasePolicyCls=BGP,
    AdoptPolicyCls=ASPA,
    AttackerBasePolicyCls=ShortestPathPrefixASPAAttacker,
)
```

Or set it automatically in `ScenarioConfig.__post_init__()` for ASPA-specific scenarios:

**Sources**: [bgpy/simulation_framework/scenarios/scenario_config.py135-144](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L135-L144)[bgpy/simulation_framework/scenarios/scenario.py358-373](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L358-L373)

---

## Complete Example: Custom Subprefix Hijack

Here's a complete custom scenario implementing a subprefix hijack with validation:

```
from typing import Optional
from ipaddress import ip_network
from roa_checker import ROA

from bgpy.simulation_framework.scenarios import Scenario, ScenarioConfig
from bgpy.simulation_engine import Announcement as Ann, BGP, ROV
from bgpy.shared.enums import Prefixes, Relationships, Timestamps

class MySubprefixHijack(Scenario):
    """Attacker announces more specific subprefix"""
    
    def _get_announcements(
        self,
        *,
        engine: Optional["BaseSimulationEngine"] = None,
    ) -> tuple["Ann", ...]:
        """Generate victim prefix and attacker subprefix"""
        
        anns = []
        
        # Victim announces /16
        for victim_asn in self.victim_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.PREFIX.value,  # "1.2.0.0/16"
                    as_path=(victim_asn,),
                    timestamp=Timestamps.VICTIM.value,
                    seed_asn=victim_asn,
                    recv_relationship=Relationships.ORIGIN,
                )
            )
        
        # Attacker announces /24 (more specific)
        for attacker_asn in self.attacker_asns:
            anns.append(
                self.scenario_config.AnnCls(
                    prefix=Prefixes.SUBPREFIX.value,  # "1.2.3.0/24"
                    as_path=(attacker_asn,),
                    timestamp=Timestamps.ATTACKER.value,
                    seed_asn=attacker_asn,
                    recv_relationship=Relationships.ORIGIN,
                )
            )
        
        return tuple(anns)
    
    def _get_roas(
        self,
        *,
        announcements: tuple["Ann", ...] = (),
        engine: Optional["BaseSimulationEngine"] = None,
    ) -> tuple[ROA, ...]:
        """Generate ROA for victim's prefix"""
        
        return tuple([
            ROA(ip_network(Prefixes.PREFIX.value), victim_asn)
            for victim_asn in self.victim_asns
        ])

# Configuration
my_config = ScenarioConfig(
    ScenarioCls=MySubprefixHijack,
    BasePolicyCls=BGP,
    AdoptPolicyCls=ROV,
    num_attackers=1,
    num_victims=1,
)

# Use in simulation
from bgpy.simulation_framework import Simulation

sim = Simulation(
    scenario_configs=(my_config,),
    num_trials=100,
)
sim.run()
```

**Sources**: [bgpy/simulation_framework/scenarios/scenario.py379-402](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L379-L402)[bgpy/simulation_framework/scenarios/custom_scenarios/victims_prefix.py14-56](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/victims_prefix.py#L14-L56)

---

## ScenarioConfig Advanced Options

The `ScenarioConfig` dataclass provides fine-grained control over scenario behavior:
ParameterTypePurpose`propagation_rounds``int`Number of propagation rounds (defaults to `min_propagation_rounds`)`AnnCls``type[Ann]`Custom announcement class`adoption_subcategory_attrs``tuple[str, ...]`AS groups to randomly adopt policy from`hardcoded_asn_cls_dict``frozendict[int, type[Policy]]`Force specific ASes to use specific policies`hardcoded_base_asn_cls_dict``frozendict[int, type[Policy]]`Fallback policies for non-adopting ASes`override_attacker_asns``frozenset[int] | None`Manually specify attackers (for testing/YAML)`override_victim_asns``frozenset[int] | None`Manually specify victims (for testing/YAML)`override_announcements``tuple[Ann, ...] | None`Manually specify announcements (for testing/YAML)`scenario_label``str`Custom label for graphs (defaults to `AdoptPolicyCls.name`)
**Sources**: [bgpy/simulation_framework/scenarios/scenario_config.py28-81](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L28-L81)

### Example: Hardcoded Policies

Force specific ASes to always use certain policies:

```
from frozendict import frozendict

config = ScenarioConfig(
    ScenarioCls=MyScenario,
    BasePolicyCls=BGP,
    AdoptPolicyCls=ROV,
    hardcoded_asn_cls_dict=frozendict({
        1234: ASPA,  # AS 1234 always uses ASPA
        5678: BGPSec,  # AS 5678 always uses BGPSec
    }),
)
```

**Sources**: [bgpy/simulation_framework/scenarios/scenario_config.py61-68](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L61-L68)[bgpy/simulation_framework/scenarios/scenario.py366-367](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L366-L367)

---

## Integration Points with Simulation Pipeline

The following diagram shows how custom scenarios integrate with the broader simulation system:

```
User Code

ScenarioConfig

Custom Scenario Instance

Simulation._run_chunk()

scenario.get_policy_cls()

scenario.setup_engine()

engine.run()

scenario.pre_aggregation_hook()

ASGraphAnalyzer.analyze()

scenario.post_propagation_hook()
```

**Sources**: [bgpy/simulation_framework/simulation.py377-439](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L377-L439)[bgpy/simulation_framework/simulation.py499-537](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L499-L537)

### Policy Assignment Flow

When `setup_engine()` is called, the scenario controls which policy each AS uses:

```
Yes

No

Yes

No

Yes

No

Yes

No

scenario.setup_engine(engine)

scenario.get_policy_cls(as_obj)

as_obj.asn in
attacker_asns?

as_obj.asn in
_default_adopters?

as_obj.asn in
hardcoded_asn_cls_dict?

as_obj.asn in
adopting_asns?

Return AttackerBasePolicyCls

Return AdoptPolicyCls

Return hardcoded policy

Return BasePolicyCls
```

**Sources**: [bgpy/simulation_framework/scenarios/scenario.py358-373](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L358-L373)[bgpy/simulation_engine/simulation_engines/simulation_engine.py27-42](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/simulation_engines/simulation_engine.py#L27-L42)

---

## Best Practices

### 1. Inherit from Existing Scenarios

If your scenario is similar to an existing one, inherit from it:

```
from bgpy.simulation_framework.scenarios import VictimsPrefix

class MyScenario(VictimsPrefix):  # Inherits victim prefix logic
    def _get_announcements(self, *, engine=None):
        # Start with victim announcements
        anns = list(super()._get_announcements(engine=engine))
        
        # Add attacker announcements
        for attacker_asn in self.attacker_asns:
            anns.append(...)
        
        return tuple(anns)
```

**Sources**: [bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py21-46](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py#L21-L46)

### 2. Validate Configuration in `__init__()`

Add validation for scenario-specific requirements:

```
class AccidentalRouteLeak(VictimsPrefix):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validate_attacker_subcategory()
    
    def validate_attacker_subcategory(self) -> None:
        if self.scenario_config.attacker_subcategory_attr in self.warning_as_groups:
            warnings.warn(
                "Route leaks don't work from stub ASes",
                RuntimeWarning,
            )
```

**Sources**: [bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py26-66](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py#L26-L66)

### 3. Document `min_propagation_rounds`

If your scenario requires multiple rounds, document why:

```
class AccidentalRouteLeak(VictimsPrefix):
    """Accidental route leak scenario
    
    Requires 2 propagation rounds:
    - Round 0: Victim announces legitimate prefix
    - Round 1: Attacker leaks the prefix after receiving it
    """
    min_propagation_rounds: int = 2
```

**Sources**: [bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py21-24](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py#L21-L24)

### 4. Use `untracked_asns` Property

Exclude ASes from metric tracking that shouldn't be measured:

```
class AccidentalRouteLeak(VictimsPrefix):
    @property
    def untracked_asns(self) -> frozenset[int]:
        """Exclude attacker's customers from metrics"""
        return super().untracked_asns | self._attackers_customer_cones_asns
```

**Sources**: [bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py195-204](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py#L195-L204)[bgpy/simulation_framework/scenarios/scenario.py323-344](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L323-L344)

---

## Testing Custom Scenarios

Custom scenarios should be tested using BGPy's test framework. See [Test Framework Architecture](/blcrdbob3/bgpy_pkg/9.1-test-framework-architecture) for details on writing tests.

Basic test structure:

```
def test_my_custom_scenario():
    from bgpy.tests.engine_tests.utils import EngineTestConfig
    
    config = EngineTestConfig(
        ScenarioCls=MyCustomHijack,
        AdoptPolicyCls=ROV,
        override_attacker_asns=frozenset([666]),
        override_victim_asns=frozenset([777]),
    )
    
    # Run test using framework
    # ...
```

**Sources**: [bgpy/simulation_framework/scenarios/scenario_config.py70-74](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L70-L74)