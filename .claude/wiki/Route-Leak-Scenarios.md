# Route Leak Scenarios
Relevant source files
- [bgpy/simulation_engine/policies/bgp/bgp/gao_rexford.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/gao_rexford.py)
- [bgpy/simulation_engine/policies/custom_attackers/first_asn_stripping_prefix_aspa_attacker.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/custom_attackers/first_asn_stripping_prefix_aspa_attacker.py)
- [bgpy/simulation_engine/policies/custom_attackers/shortest_path_prefix_aspa_attacker.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/custom_attackers/shortest_path_prefix_aspa_attacker.py)
- [bgpy/simulation_engine/simulation_engines/base_simulation_engine.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/simulation_engines/base_simulation_engine.py)
- [bgpy/simulation_engine/simulation_engines/simulation_engine.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/simulation_engines/simulation_engine.py)
- [bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py)
- [bgpy/simulation_framework/scenarios/custom_scenarios/victims_prefix.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/victims_prefix.py)

## Purpose and Scope

This document describes the route leak attack scenario implementation in BGPy, specifically the `AccidentalRouteLeak` class. Route leaks simulate operational errors where an AS incorrectly exports routes learned from providers or peers to other providers or peers, violating valley-free routing policies. This page covers the two-round propagation mechanism, attacker/victim selection constraints, and how route leaks differ from other attack scenarios.

For information about other attack types, see [Attack Scenarios Overview](/blcrdbob3/bgpy_pkg/3.4-attack-scenarios-overview), [Pre-ROV Attack Scenarios](/blcrdbob3/bgpy_pkg/7.1-pre-rov-attack-scenarios), [Post-ROV Attack Scenarios](/blcrdbob3/bgpy_pkg/7.2-post-rov-attack-scenarios), and [Non-Routed Prefix Attacks](/blcrdbob3/bgpy_pkg/7.3-non-routed-prefix-attacks).

---

## Route Leak Concept

A route leak occurs when an AS advertises a route to a neighbor from whom it should not advertise that route according to valley-free routing policies. The most common form is when an AS learns a route from a provider or peer and then incorrectly advertises it to other providers or peers, effectively treating the route as if it came from a customer.

In BGPy, route leaks are modeled as operational errors rather than malicious attacks. The leaking AS receives a legitimate prefix announcement, and then re-announces it as if it originated the prefix or received it from a customer, causing it to be exported to all neighbor relationships.

Sources: [bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py1-205](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py#L1-L205)

---

## AccidentalRouteLeak Class Architecture

```
Key Methods

Key Attributes

Inheritance Hierarchy

Scenario
(Base Class)

VictimsPrefix
announcements: victim prefix only
roas: victim ROAs

AccidentalRouteLeak
min_propagation_rounds: 2
post_propagation_hook
customer cone tracking

min_propagation_rounds = 2
Requires two propagation rounds

_attackers_customer_cones_asns
Set of ASNs in attacker's cone

warning_as_groups
STUBS, STUBS_OR_MH, ALL_WOUT_IXPS

post_propagation_hook()
Line 71-132
Modifies announcements after round 0

_get_attacker_asns()
Line 134-165
Stores customer cones

_get_possible_victim_asns()
Line 167-181
Excludes customer cone

validate_attacker_subcategory()
Line 48-66
Warns for stub attackers

_untracked_asns property
Line 196-204
Excludes customer cone
```

The `AccidentalRouteLeak` class extends `VictimsPrefix`, which only seeds the victim's legitimate prefix announcement without any attacker-originated announcements. The leaker behavior is implemented through the `post_propagation_hook` mechanism rather than seeding malicious announcements.

Sources: [bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py21-46](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py#L21-L46)[bgpy/simulation_framework/scenarios/custom_scenarios/victims_prefix.py14-57](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/victims_prefix.py#L14-L57)

---

## Two-Round Propagation Mechanism

### Propagation Flow Diagram

```
"AS Graph"
"SimulationEngine"
"AccidentalRouteLeak"
"Simulation Orchestrator"
"AS Graph"
"SimulationEngine"
"AccidentalRouteLeak"
"Simulation Orchestrator"
Setup Phase
ready_to_run_round = 0
Round 0: Normal Propagation
Leaker receives victim's announcement
Hook Execution
Copy announcement with
recv_relationship=ORIGIN
seed_asn=attacker_asn
timestamp=ATTACKER
ready_to_run_round = 1
Round 1: Leak Propagation
Leaked announcement propagates
to all relationships
setup_engine(engine)
seed victim announcements
run(propagation_round=0)
_propagate_to_providers()
_propagate_to_peers()
_propagate_to_customers()
post_propagation_hook(round=0)
Get leaker's local_rib
self.announcements += leak_anns
setup_engine(engine) [clears graph]
run(propagation_round=1)
_propagate_to_providers()
_propagate_to_peers()
_propagate_to_customers()
```

Sources: [bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py71-132](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py#L71-L132)[bgpy/simulation_engine/simulation_engines/simulation_engine.py61-144](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/simulation_engines/simulation_engine.py#L61-L144)

### Hook Implementation Details

The `post_propagation_hook` method implements the leak mechanism through the following steps:
StepActionCode Reference**1. Check Round**Only executes logic on round 0[Line 108](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/Line 108)**2. Extract Leaker's Routes**Gets announcements from attacker's `local_rib`[Lines 112-118](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/Lines 112-118)**3. Create Leak Announcements**Copies announcements with modified attributes[Lines 119-127](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/Lines 119-127)**4. Update Scenario**Appends leak announcements to scenario[Line 128](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/Line 128)**5. Reset Graph**Calls `setup_engine()` to clear graph state[Line 129](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/Line 129)**6. Enable Round 1**Sets `ready_to_run_round = 1`[Line 130](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/Line 130)
The key modification is setting `recv_relationship=Relationships.ORIGIN` on the leaked announcement. This makes the leaker treat the route as if it originated locally or came from a customer, causing it to be exported to all neighbor types (providers, peers, and customers) according to valley-free routing rules.

Sources: [bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py108-132](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py#L108-L132)

### Optimization Rationale

The implementation includes extensive comments explaining why the two-round approach is more efficient than alternatives:

**Old Approach (Avoided):**

- Modify leaker's local RIB after round 0
- Require `BGPFull` policy (supports withdrawals and RIB management)
- Propagate again on an already-full graph
- Very slow due to `BGPFull` overhead and full-graph propagation

**Current Approach (Implemented):**

- Extract leak announcements after round 0
- Clear the graph completely
- Seed only leak announcements (no victim announcements)
- Propagate on empty graph with basic `BGP` policy
- Treats propagation rounds as atomic, avoiding need for withdrawals

This optimization reduces simulation time significantly while producing equivalent results.

Sources: [bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py78-105](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py#L78-L105)

---

## Attacker Selection and Validation

### Attacker Subcategory Constraints

Route leaks require the leaker to have upstream providers or peers from which to receive routes. Stub ASes (ASes with only provider relationships) cannot perform meaningful route leaks because they have no other providers or peers to leak to.

The `validate_attacker_subcategory` method warns if stub ASes are selected as attackers:

```
# Conceptual illustration (not actual code)
if attacker_subcategory in [STUBS, STUBS_OR_MH, ALL_WOUT_IXPS]:
    warnings.warn("Route leaks can't leak from stubs", RuntimeWarning)
```

Users can override this by setting `override_attacker_asns=True` in the scenario config or by selecting a different attacker subcategory like `ASGroups.MULTIHOMED`.

Sources: [bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py48-66](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py#L48-L66)[Lines 184-193](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/Lines 184-193)

### Customer Cone Tracking

The `_get_attacker_asns` method stores the customer cones of all selected attackers in `_attackers_customer_cones_asns`:

```
_get_attacker_asns()

super()._get_attacker_asns()

For each attacker:
_get_cone_size_helper()

Store in _attackers_customer_cones_asns

Used in:
• _get_possible_victim_asns
• _untracked_asns
```

The `_get_cone_size_helper` function recursively computes all ASes in the customer cone by following customer relationships downward from the attacker.

Sources: [bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py134-165](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py#L134-L165)[Line 69](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/Line 69)

---

## Victim Selection Constraints

### Excluding Customer Cone

The `_get_possible_victim_asns` method overrides the parent class to exclude the attacker's customer cone from possible victims:

```
# Conceptual illustration
possible_victims = super()._get_possible_victim_asns(engine, percent_adoption)
possible_victims = possible_victims - attackers_customer_cones_asns
return possible_victims
```

**Rationale:** If a victim is in the attacker's customer cone, the attacker already has a customer-provider path to the victim. Advertising the victim's prefix to other providers/peers is not a "leak" in this case—it's normal valley-free routing behavior. True route leaks only affect ASes outside the attacker's customer cone.

Sources: [bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py167-181](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py#L167-L181)

### Edge Case: Disconnection

The implementation notes a rare edge case where the selected attacker cannot reach the victim due to network disconnection (occurs ~0.1% of the time in CAIDA topology). In theory, valid attackers could be pre-computed by analyzing provider cones and peer relationships, but this is not implemented due to:

1. Performance cost of computing valid attacker set
2. Extreme rarity of the disconnection case
3. Disconnection being a valid simulation outcome

Sources: [bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py140-149](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py#L140-L149)

---

## Untracked ASNs and Metrics

The `_untracked_asns` property excludes the attacker's customer cone from metric tracking:

```
@property
def _untracked_asns(self) -> frozenset[int]:
    return super()._untracked_asns | self._attackers_customer_cones_asns
```

**Rationale:** ASes in the attacker's customer cone receive routes through normal valley-free routing (as the attacker is their provider), not through the route leak. Including them in success metrics would misrepresent the impact of the leak itself.

This ensures that metrics like "attacker success" and "victim success" only count ASes that could be affected by the leak to providers/peers, not ASes that would naturally receive routes from the attacker anyway.

Sources: [bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py196-204](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py#L196-L204)

---

## Integration with Simulation Engine

### Ready-to-Run State Management

The `ready_to_run_round` attribute in `BaseSimulationEngine` controls which propagation round can be executed:
StateMeaningSet By`-1`Not initializedConstructor`0`Ready to run round 0`setup()` method`1`Ready to run round 1`post_propagation_hook()``N`Ready to run round NAfter running round N-1
The `SimulationEngine.run()` method validates this state before propagation:

```
# From SimulationEngine.run()
if self.ready_to_run_round != propagation_round:
    raise RuntimeError(f"Engine not set up to run for {propagation_round} round")
```

After successful propagation, the engine increments `ready_to_run_round` to allow the next round.

Sources: [bgpy/simulation_engine/simulation_engines/simulation_engine.py61-74](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/simulation_engines/simulation_engine.py#L61-L74)[bgpy/simulation_engine/simulation_engines/base_simulation_engine.py37-47](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/simulation_engines/base_simulation_engine.py#L37-L47)

### Hook Invocation Points

The simulation orchestrator calls `post_propagation_hook` after each propagation round. For `AccidentalRouteLeak`, the hook:

- Executes custom logic only on round 0
- Raises `NotImplementedError` if called on rounds > 1
- Returns immediately without action on round 1 (since the check fails)

This design allows scenarios to control their own multi-round behavior while maintaining a simple orchestrator loop.

Sources: [bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py71-132](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py#L71-L132)

---

## Comparison with Other Multi-Round Scenarios

### Route Leak vs. Path Manipulation Attacks
AspectAccidentalRouteLeakASPA Attackers (e.g., ShortestPathPrefixASPAAttacker)**Rounds Required**2 (victim propagation, then leak)1 (single propagation with modified announcements)**Hook Used**`post_propagation_hook`None (uses `_policy_propagate` override)**Announcement Source**Copies victim's announcementCreates attacker announcement at seed time**Graph State**Cleared between roundsNot cleared**Policy Override**No custom policy neededCustom attacker policy required**Mechanism**Modifies `recv_relationship`Modifies `as_path` to customers only
Path manipulation attacks like those using `ShortestPathPrefixASPAAttacker` modify announcements during propagation without needing multiple rounds. They override `_policy_propagate` to send different announcements to different neighbor types (e.g., origin hijacks to customers, normal announcements to others).

Sources: [bgpy/simulation_engine/policies/custom_attackers/shortest_path_prefix_aspa_attacker.py41-64](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/custom_attackers/shortest_path_prefix_aspa_attacker.py#L41-L64)[bgpy/simulation_engine/policies/custom_attackers/first_asn_stripping_prefix_aspa_attacker.py42-64](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/custom_attackers/first_asn_stripping_prefix_aspa_attacker.py#L42-L64)

---

## Key Classes and Methods Reference

### AccidentalRouteLeak Class
MemberTypeDescription`min_propagation_rounds``int`Class attribute set to `2``_attackers_customer_cones_asns``set[int]`Set of ASNs in attacker customer cones`__init__()`MethodRequires engine parameter, stores customer cones`post_propagation_hook()`MethodImplements leak on round 0, resets graph`_get_attacker_asns()`MethodComputes and stores customer cones`_get_possible_victim_asns()`MethodExcludes customer cone from victims`validate_attacker_subcategory()`MethodWarns for stub attackers`warning_as_groups`PropertyReturns stub-related AS groups`_untracked_asns`PropertyReturns untracked ASNs including customer cone
Sources: [bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py21-205](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py#L21-L205)

### Related Base Classes

**VictimsPrefix**[bgpy/simulation_framework/scenarios/custom_scenarios/victims_prefix.py14-57](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/victims_prefix.py#L14-L57):

- `_get_announcements()`: Returns victim prefix announcements only
- `_get_roas()`: Returns ROAs for victim prefix

**BaseSimulationEngine**[bgpy/simulation_engine/simulation_engines/base_simulation_engine.py14-99](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/simulation_engines/base_simulation_engine.py#L14-L99):

- `ready_to_run_round`: State tracking for propagation rounds
- `setup()`: Abstract method for scenario initialization
- `run()`: Abstract method for propagation execution

**SimulationEngine**[bgpy/simulation_engine/simulation_engines/simulation_engine.py13-161](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/simulation_engines/simulation_engine.py#L13-L161):

- `setup()`: Sets AS classes and seeds announcements
- `run()`: Validates ready state and calls `_propagate()`
- `_propagate()`: Orchestrates provider, peer, customer propagation

---

## Usage Example

```
# Conceptual example (not executable code)
from bgpy.simulation_framework import Simulation, ScenarioConfig
from bgpy.simulation_framework.scenarios import AccidentalRouteLeak
from bgpy.shared.enums import ASGroups

# Configure route leak with multihomed attackers
scenario_config = ScenarioConfig(
    ScenarioCls=AccidentalRouteLeak,
    attacker_subcategory_attr=ASGroups.MULTIHOMED.value,  # Avoid stub warning
    num_attackers=1,
    num_victims=1,
)

# Run simulation
sim = Simulation(
    scenario_configs=[scenario_config],
    percent_adoptions=[0.5],
    num_trials=10,
)
sim.run()
```

The simulation will:

1. Select a multihomed AS as the leaker
2. Select a victim outside the leaker's customer cone
3. Run round 0 to propagate victim's legitimate prefix
4. Execute hook to create leaked announcement
5. Clear graph and run round 1 to propagate leaked prefix
6. Analyze outcomes excluding leaker's customer cone

Sources: [bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py26-45](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/accidental_route_leak.py#L26-L45)