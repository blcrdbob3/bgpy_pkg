# Attack Scenarios Overview
Relevant source files
- [.github/workflows/tests.yml](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/.github/workflows/tests.yml)
- [.pre-commit-config.yaml](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/.pre-commit-config.yaml)
- [LICENSE.txt](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/LICENSE.txt)
- [MANIFEST.in](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/MANIFEST.in)
- [README.md](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/README.md)
- [bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py)
- [bgpy/shared/enums.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/shared/enums.py)
- [bgpy/simulation_engine/__init__.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/__init__.py)
- [bgpy/simulation_engine/policies/__init__.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/__init__.py)
- [bgpy/simulation_engine/policies/aspa/__init__.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/__init__.py)
- [bgpy/simulation_engine/policies/aspa/aspawn.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/aspawn.py)
- [bgpy/simulation_engine/policies/aspa/aspawn_full.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/aspawn_full.py)
- [bgpy/simulation_engine/policies/aspa/asra.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/asra.py)
- [bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py)
- [bgpy/simulation_framework/scenarios/scenario.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py)
- [bgpy/simulation_framework/scenarios/scenario_config.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py)
- [bgpy/simulation_framework/simulation.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py)
- [pyproject.toml](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml)
- [requirements.txt](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/requirements.txt)
- [requirements_dev.txt](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/requirements_dev.txt)
- [scripts/aspawn_debug.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/scripts/aspawn_debug.py)
- [setup.cfg](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/setup.cfg)
- [tox.ini](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/tox.ini)

## Purpose and Scope

This document introduces the **attack scenario abstraction** in BGPy, which models various BGP security threats ranging from simple prefix hijacks to sophisticated path manipulation attacks. Scenarios define how attackers, victims, and security policy adopters interact during simulation trials.

For detailed implementation of specific attack types, see [Pre-ROV Attack Scenarios](/blcrdbob3/bgpy_pkg/7.1-pre-rov-attack-scenarios), [Post-ROV Attack Scenarios](/blcrdbob3/bgpy_pkg/7.2-post-rov-attack-scenarios), [Non-Routed Prefix Attacks](/blcrdbob3/bgpy_pkg/7.3-non-routed-prefix-attacks), and [Route Leak Scenarios](/blcrdbob3/bgpy_pkg/7.4-route-leak-scenarios). For information on configuring scenarios in simulations, see [Scenario Configuration](/blcrdbob3/bgpy_pkg/4.2-scenario-configuration). For guidance on creating custom scenarios, see [Creating Custom Scenarios](/blcrdbob3/bgpy_pkg/10.1-creating-custom-scenarios).

---

## Scenario Abstraction

### Core Classes

BGPy uses two complementary classes to model attack scenarios:
ClassMutabilityLifecyclePurpose`ScenarioConfig`Frozen (immutable)Reused across all trialsDefines scenario parameters and policy configuration`Scenario`MutableCreated per trialExecutes a single trial with randomized attackers/victims
**ScenarioConfig** is a frozen dataclass that specifies what type of attack to run, which security policies to test, and how many attackers/victims to select. It is created once and reused across all trials to ensure consistent configuration.

**Scenario** is instantiated for each trial and handles the random selection of specific attacker ASNs, victim ASNs, generation of malicious announcements, and setup of the simulation engine.

Sources: [bgpy/simulation_framework/scenarios/scenario_config.py28-81](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L28-L81)[bgpy/simulation_framework/scenarios/scenario.py20-96](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L20-L96)

---

### Scenario Lifecycle

```
Per Trial

Per Propagation Round

Next Round

ScenarioConfig
(frozen, reused)

Scenario.init()
Select attackers/victims/adopters

_get_announcements()
Generate attack announcements

_get_roas()
Generate RPKI ROAs

setup_engine()
Assign policies to ASes

pre_aggregation_hook()
Pre-analysis modifications

Engine.run()
BGP propagation

post_propagation_hook()
Multi-round attacks
```

**Scenario Lifecycle Explanation:**

1. **Initialization** (`__init__`): Randomly selects attacker ASNs, victim ASNs, and adopting ASNs from the AS graph based on configuration parameters
2. **Announcement Generation** (`_get_announcements`): Creates malicious BGP announcements specific to the attack type
3. **ROA Generation** (`_get_roas`): Creates RPKI Route Origin Authorization records for validation
4. **Engine Setup** (`setup_engine`): Assigns policy classes to each AS based on whether they are attackers, victims, adopters, or base ASes
5. **Propagation Hooks**: Execute custom logic before aggregation (`pre_aggregation_hook`) or after propagation (`post_propagation_hook`)

Sources: [bgpy/simulation_framework/scenarios/scenario.py33-96](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L33-L96)[bgpy/simulation_framework/simulation.py499-537](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L499-L537)

---

## Attack Taxonomy

BGPy models four main categories of BGP attacks, organized by the security policies they target:

```
Route Leak

AccidentalRouteLeak
Two-round propagation

Non-Routed Attacks
(Exploit AS 0 ROAs)

NonRoutedPrefixHijack
Hijack non-routed prefix

NonRoutedSuperprefixHijack
Hijack non-routed superprefix

Post-ROV Attacks
(Evade Origin Validation)

ForgedOriginPrefixHijack
Forge victim as origin

ShortestPathPrefixHijack
Path manipulation

FirstASNStrippingPrefixHijack
Strip first ASN

Pre-ROV Attacks
(Against Basic BGP)

PrefixHijack
Announce victim's prefix

SubprefixHijack
Announce more-specific prefix

BGP Policy

ROV Policy
```

**Attack Category Summary:**
CategoryTarget PoliciesAttack VectorExample Scenarios**Pre-ROV**BGP, OnlyToCustomers, EdgeFilterNo origin validationPrefixHijack, SubprefixHijack**Post-ROV**ROV, PeerROV, ROV++, BGPSecPath manipulation, forged originsForgedOriginPrefixHijack, ShortestPathPrefixHijack**Non-Routed**ROV, ROV++AS 0 ROAs for unallocated spaceNonRoutedPrefixHijack, NonRoutedSuperprefixHijack**Route Leak**All policiesValley-free violationAccidentalRouteLeak
Sources: [bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py474-570](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L474-L570)

---

### Pre-ROV Attacks

Pre-ROV attacks are effective against basic BGP without origin validation. These attacks work by announcing prefixes with the attacker as the origin.

**PrefixHijack**: The attacker announces the exact prefix owned by the victim with the attacker's ASN as the origin. Success depends on AS path length and routing preferences.

**SubprefixHijack**: The attacker announces a more-specific subprefix of the victim's prefix. Due to longest-prefix matching, this attracts more traffic than the victim's legitimate announcement, even if the attacker's path is longer.

Sources: For detailed implementations, see [Pre-ROV Attack Scenarios](/blcrdbob3/bgpy_pkg/7.1-pre-rov-attack-scenarios).

---

### Post-ROV Attacks

Post-ROV attacks evade Route Origin Validation by manipulating AS paths while maintaining valid origins or exploiting validation gaps.

**ForgedOriginPrefixHijack**: The attacker appends the victim's ASN to their AS path, making it appear the announcement originated from the victim. ROV sees a valid origin, but traffic is routed to the attacker.

**ShortestPathPrefixHijack**: An adaptive attack that finds the shortest path that evades a given security policy:

- Against **ROV**: Uses forged origin
- Against **PathEnd**: Includes victim + one provider in path
- Against **ASPA**: Finds shortest valley-free path ending in non-adopter
- Against **BGP-iSec**: Uses actual announcements from local RIBs (requires two propagation rounds)

**FirstASNStrippingPrefixHijack**: The attacker strips the first ASN from announcements received from providers, making routes appear shorter and evading some path validation mechanisms.

Sources: [bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py73-469](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L73-L469)

---

### Non-Routed Prefix Attacks

Non-routed prefix attacks exploit ROAs with origin AS 0, which indicate that a prefix should not be routed on the Internet. Attackers announce these prefixes, and ROV policies must decide how to handle them.

**NonRoutedPrefixHijack**: Hijack a prefix with AS 0 in its ROA.

**NonRoutedSuperprefixHijack**: Hijack a superprefix of a legitimately routed prefix, where the superprefix has AS 0 in its ROA.

These attacks test whether policies properly blackhole non-routed prefixes vs. allowing them as "unknown" validation status.

Sources: For detailed implementations, see [Non-Routed Prefix Attacks](/blcrdbob3/bgpy_pkg/7.3-non-routed-prefix-attacks).

---

### Route Leak Scenarios

**AccidentalRouteLeak** models operational errors where an AS violates valley-free routing by re-announcing provider routes to other providers or peers. This scenario uses a two-round propagation:

1. **Round 1**: Legitimate announcements propagate normally
2. **Round 2**: The attacker leaks announcements from their local RIB to providers/peers (via `post_propagation_hook`)

Route leaks are particularly effective because the attacker may have a shorter path than the legitimate route, causing widespread traffic hijacking.

Sources: For detailed implementation, see [Route Leak Scenarios](/blcrdbob3/bgpy_pkg/7.4-route-leak-scenarios).

---

## Scenario Components

### ASN Selection

Scenarios randomly select specific ASNs for attackers, victims, and policy adopters from AS graph subcategories:

```
AS Graph asn_groups

Scenario.get*_asns()

ScenarioConfig Attributes

num_attackers

attacker_subcategory_attr
(e.g., STUBS_OR_MH)

num_victims

victim_subcategory_attr

adoption_subcategory_attrs
(tuple of subcategories)

_get_attacker_asns()

_get_victim_asns()

_get_adopting_asns()

stub_or_multihomed

etc

input_clique

attacker_asns
(frozenset)

victim_asns
(frozenset)

adopting_asns
(frozenset)
```

**ASN Selection Logic:**
ASN TypeMethodSelection CriteriaAttackers`_get_attacker_asns()`Random sample from `attacker_subcategory_attr` (default: stubs/multihomed)Victims`_get_victim_asns()`Random sample from `victim_subcategory_attr`, excluding attackersAdopters`_get_adopting_asns()`Random sample across `adoption_subcategory_attrs` based on `percent_adoption`
The scenario reuses attackers/victims across different `percent_adoption` values within the same trial for comparability. Adopters are reused across different `ScenarioConfig` objects if adoption subcategories match.

Sources: [bgpy/simulation_framework/scenarios/scenario.py101-301](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L101-L301)[bgpy/simulation_framework/simulation.py389-430](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L389-L430)

---

### Announcement and ROA Generation

Each scenario type overrides `_get_announcements()` and `_get_roas()` to create attack-specific BGP announcements and RPKI Route Origin Authorizations:

```
PrefixHijack Example

Base Scenario Class

_get_announcements()
Returns: tuple[Ann, ...]

_get_roas()
Returns: tuple[ROA, ...]

Victim Announcement:
prefix=1.2.0.0/16
as_path=(victim_asn,)
timestamp=VICTIM

Attacker Announcement:
prefix=1.2.0.0/16
as_path=(attacker_asn,)
timestamp=ATTACKER

ROA:
prefix=1.2.0.0/16
origin=victim_asn
max_length=24

Policy.roa_checker
(Global ROAChecker)
```

**Key Announcement Attributes:**

- **prefix**: IP prefix being announced (from `Prefixes` enum)
- **as_path**: Sequence of ASNs in reverse order (origin last)
- **timestamp**: `VICTIM` (0) or `ATTACKER` (1) to control tie-breaking
- **seed_asn**: AS that originates this announcement
- **next_hop_asn**: Next hop for data plane routing

ROAs are inserted into the global `Policy.roa_checker` singleton, which all ROV-based policies query during announcement validation.

Sources: [bgpy/simulation_framework/scenarios/scenario.py378-402](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L378-L402)

---

### Policy Assignment

The `get_policy_cls()` method determines which policy class each AS should use based on scenario configuration:

```
Yes

No

Yes

No

Yes

No

Yes

No

Scenario.get_policy_cls(as_obj)

asn in
attacker_asns?

asn in
victim_asns
(default adopters)?

asn in
hardcoded_asn_cls_dict?

asn in
adopting_asns?

AttackerBasePolicyCls
(if set)

AdoptPolicyCls

hardcoded_asn_cls_dict[asn]

BasePolicyCls

hardcoded_base_asn_cls_dict[asn]
(if set, else BasePolicyCls)
```

**Policy Assignment Priority:**

1. **Attackers** → `AttackerBasePolicyCls` (if specified) for custom attacker behavior
2. **Victims** → `AdoptPolicyCls` (victims always adopt the defense)
3. **Hardcoded ASNs** → `hardcoded_asn_cls_dict[asn]` for specific AS overrides
4. **Adopters** → `AdoptPolicyCls` (randomly selected based on `percent_adoption`)
5. **Non-adopters** → `hardcoded_base_asn_cls_dict[asn]` or `BasePolicyCls`

Sources: [bgpy/simulation_framework/scenarios/scenario.py358-373](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L358-L373)

---

## Extensibility: Hook Methods

Scenarios can inject custom behavior at specific points in the simulation lifecycle using hook methods:

### pre_aggregation_hook

Called immediately after propagation but before outcome analysis. Useful for:

- Validating intermediate state
- Logging specific announcement properties
- Modifying announcements before analysis (rare)

```
def pre_aggregation_hook(
    self,
    engine: BaseSimulationEngine,
    percent_adopt: float | SpecialPercentAdoptions,
    trial: int,
    propagation_round: int,
) -> None:
    pass  # Override in subclasses
```

Sources: [bgpy/simulation_framework/scenarios/scenario.py404-414](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L404-L414)

---

### post_propagation_hook

Called after propagation and outcome aggregation. Enables multi-round attacks by modifying announcements between rounds. Used by:

**AccidentalRouteLeak**: After round 1, leaks provider announcements to providers/peers in round 2.

**ShortestPathPrefixHijack against BGP-iSec**: After round 1, examines local RIBs to find best announcement to manipulate, then clears the graph and seeds manipulated announcements for round 2.

```
def post_propagation_hook(
    self,
    engine: BaseSimulationEngine,
    percent_adopt: float | SpecialPercentAdoptions,
    trial: int,
    propagation_round: int,
) -> None:
    pass  # Override in subclasses
```

Sources: [bgpy/simulation_framework/scenarios/scenario.py416-425](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L416-L425)[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py362-468](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L362-L468)

---

## Custom Attacker Policies

Some attacks require the attacker to deploy a modified BGP policy that deviates from normal routing behavior. BGPy supports this through `AttackerBasePolicyCls`:

### ShortestPathPrefixASPAAttacker

When attacking ASPA, the attacker must:

1. Send forged-origin announcements to **customers only** (not providers/peers)
2. This evades ASPA's provider validation since customers don't check their providers' attestations

The `ScenarioConfig` automatically sets `AttackerBasePolicyCls=ShortestPathPrefixASPAAttacker` when `AdoptPolicyCls` is `ASPA` (but not `ASRA` or `ASPAwN`, which have stronger validation).

### FirstASNStrippingPrefixASPAAttacker

Strips the first ASN from received announcements before propagating, making paths appear shorter and potentially evading path validation.

**Custom Attacker Policy Assignment:**

```
Yes

No

ScenarioConfig

post_init()

AdoptPolicyCls
is ASPA?
(not ASRA/ASPAwN)

getattr(ScenarioCls,
'RequiredASPAAttackerCls')

Set AttackerBasePolicyCls

AttackerBasePolicyCls
remains None or manual
```

Sources: [bgpy/simulation_framework/scenarios/scenario_config.py135-144](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L135-L144)[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py76-233](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L76-L233)

---

## Integration with Simulation Pipeline

Scenarios integrate with the broader simulation framework as follows:

```
Per Trial Loop

Per Propagation Round

Next Round

Simulation Class

scenario = ScenarioCls(
scenario_config,
percent_adoption,
engine,
...)

scenario.setup_engine(engine)

engine.run(scenario)

scenario.pre_aggregation_hook()

ASGraphAnalyzer.analyze()

GraphDataAggregator.aggregate()

scenario.post_propagation_hook()
```

The `Simulation` class creates a new `Scenario` instance for each combination of trial, percent_adoption, and scenario_config. The scenario sets up the engine with policies and seed announcements, then the engine propagates BGP messages. After each round, outcomes are analyzed and aggregated.

Sources: [bgpy/simulation_framework/simulation.py377-437](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L377-L437)[bgpy/simulation_framework/simulation.py499-537](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L499-L537)