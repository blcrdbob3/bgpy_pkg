# Attack Scenario Reference
Relevant source files
- [bgpy/simulation_engine/__init__.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/__init__.py)
- [bgpy/simulation_engine/policies/__init__.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/__init__.py)
- [bgpy/simulation_engine/policies/aspa/__init__.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/__init__.py)
- [bgpy/simulation_engine/policies/aspa/aspawn.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/aspawn.py)
- [bgpy/simulation_engine/policies/aspa/aspawn_full.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/aspawn_full.py)
- [bgpy/simulation_engine/policies/aspa/asra.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/asra.py)
- [bgpy/simulation_engine/policies/custom_attackers/__init__.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/custom_attackers/__init__.py)
- [bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_prefix_hijack.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_prefix_hijack.py)
- [bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_hijack.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_hijack.py)
- [bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_prefix_hijack.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_prefix_hijack.py)
- [bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/__init__.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/__init__.py)
- [bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/first_asn_stripping_prefix_hijack.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/first_asn_stripping_prefix_hijack.py)
- [bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/forged_origin_prefix_hijack.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/forged_origin_prefix_hijack.py)
- [bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py)
- [bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/superprefix_prefix_hijack.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/superprefix_prefix_hijack.py)
- [bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/prefix_hijack.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/prefix_hijack.py)
- [bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/subprefix_hijack.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/subprefix_hijack.py)
- [scripts/aspawn_debug.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/scripts/aspawn_debug.py)

This page provides comprehensive documentation for all attack scenario implementations in BGPy. Attack scenarios define specific BGP security attacks (prefix hijacks, route leaks, etc.) by specifying the announcements, ROAs, and attack behavior. Each scenario class extends the base `Scenario` class and implements methods to generate attacker and victim announcements.

For information about BGP security policies that defend against these attacks, see [BGP Policy Reference](/blcrdbob3/bgpy_pkg/6-bgp-policy-reference). For guidance on implementing custom attack scenarios, see [Creating Custom Scenarios](/blcrdbob3/bgpy_pkg/10.1-creating-custom-scenarios).

## Attack Scenario Architecture

All attack scenarios inherit from the `Scenario` base class and implement specific attack behaviors by overriding key methods.

### Scenario Class Hierarchy

```
Non-Routed Attacks

Post-ROV Attacks

Pre-ROV Attacks

Scenario
(Abstract Base)

VictimsPrefix
Base for victim+ROA scenarios

PrefixHijack
Same prefix competition

SubprefixHijack
More specific prefix

ForgedOriginPrefixHijack
Append victim ASN

ShortestPathPrefixHijack
Policy-adaptive path manipulation

FirstASNStrippingPrefixHijack
Remove first ASN from path

SuperprefixPrefixHijack
Prefix + superprefix combo

NonRoutedPrefixHijack
AS 0 ROA exploitation

NonRoutedSuperprefixHijack
Superprefix with AS 0

NonRoutedSuperprefixPrefixHijack
Both prefix+superprefix

AccidentalRouteLeak
Two-round propagation
```

**Sources:**

- [bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/prefix_hijack.py13-14](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/prefix_hijack.py#L13-L14)
- [bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/subprefix_hijack.py13-14](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/subprefix_hijack.py#L13-L14)
- [bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/forged_origin_prefix_hijack.py13-14](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/forged_origin_prefix_hijack.py#L13-L14)
- [bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py73-74](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L73-L74)
- [bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/first_asn_stripping_prefix_hijack.py17-18](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/first_asn_stripping_prefix_hijack.py#L17-L18)

### Key Scenario Methods

All scenarios implement or override these core methods:
MethodPurposeReturn Type`_get_announcements()`Generate announcements for attacker(s) and victim(s)`tuple[Ann, ...]``_get_roas()`Generate ROAs for prefix validation`tuple[ROA, ...]``post_propagation_hook()`Optional: modify state between propagation rounds`None``setup_engine()`Seed announcements into the simulation engine`None`
**Sources:**

- [bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/prefix_hijack.py16-31](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/prefix_hijack.py#L16-L31)
- [bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_prefix_hijack.py39-47](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_prefix_hijack.py#L39-L47)
- [bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py362-468](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L362-L468)

### Announcement Generation Flow

```
Announcement Creation

Yes

No

Scenario Initialization

Select Attacker/Victim ASNs
_get_attacker_asns()
_get_victim_asns()

_get_announcements(engine)

Victim Announcements
super()._get_announcements()

Attacker Announcements
scenario-specific logic

Combine Announcements
victim_anns + attacker_anns

_get_roas(announcements, engine)

setup_engine(engine)
Seed announcements into AS graph

SimulationEngine.run()
Propagate through network

post_propagation_hook()
defined?

Modify announcements
or AS states

Second propagation round

Analysis Phase
```

**Sources:**

- [bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/prefix_hijack.py16-31](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/prefix_hijack.py#L16-L31)
- [bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/forged_origin_prefix_hijack.py19-33](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/forged_origin_prefix_hijack.py#L19-L33)
- [bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py78-92](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L78-L92)

## Pre-ROV Attack Scenarios

Pre-ROV attacks are basic BGP hijacks that succeed against standard BGP without security extensions. These attacks are easily defeated by ROV (Route Origin Validation).

### PrefixHijack

The simplest attack where the attacker announces the same prefix as the victim, competing based on AS path length and Gao-Rexford routing policies.

**Announcements:**

- **Victim:**`Announcement(prefix=PREFIX, as_path=(victim_asn,))`
- **Attacker:**`Announcement(prefix=PREFIX, as_path=(attacker_asn,))`

**ROA:**`ROA(prefix=PREFIX, origin=victim_asn)`

**ROA Validation:**

- Victim announcement: `VALID` (origin matches ROA)
- Attacker announcement: `INVALID_BY_ORIGIN` (origin doesn't match ROA)

**Effectiveness:**

- Succeeds against: `BGP`, `BGPFull`, basic policies
- Defeated by: `ROV`, `PeerROV`, `ASPA`, `BGPSec`, all ROV-based policies

**Sources:**

- [bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/prefix_hijack.py13-49](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/prefix_hijack.py#L13-L49)

### SubprefixHijack

The attacker announces a more specific (longer) prefix, which is preferred by BGP's longest-prefix-match rule.

**Announcements:**

- **Victim:**`Announcement(prefix=PREFIX, as_path=(victim_asn,))`
- **Attacker:**`Announcement(prefix=SUBPREFIX, as_path=(attacker_asn,))`

**ROA:**`ROA(prefix=PREFIX, origin=victim_asn)`

**ROA Validation:**

- Victim announcement: `VALID`
- Attacker announcement: `INVALID_BY_LENGTH` and `INVALID_BY_ORIGIN`

**Effectiveness:**

- Succeeds against: `BGP`, `BGPFull`
- Defeated by: `ROV`, `PeerROV`, all ROV-based policies

**Note:** Subprefix hijacks are particularly dangerous because they don't require the attacker to have a shorter AS path—the more specific prefix always wins.

**Sources:**

- [bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/subprefix_hijack.py13-54](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/subprefix_hijack.py#L13-L54)

## Post-ROV Attack Scenarios

Post-ROV attacks are sophisticated path manipulation techniques designed to evade Route Origin Validation and more advanced security policies.

### ForgedOriginPrefixHijack

The attacker appends the victim's ASN to the AS path, making the announcement appear to originate from the legitimate source.

**Announcements:**

- **Victim:**`Announcement(prefix=PREFIX, as_path=(victim_asn,))`
- **Attacker:**`Announcement(prefix=PREFIX, as_path=(attacker_asn, victim_asn), next_hop_asn=attacker_asn, seed_asn=attacker_asn)`

**ROA:**`ROA(prefix=PREFIX, origin=victim_asn)`

**ROA Validation:**

- Victim announcement: `VALID`
- Attacker announcement: `VALID` (origin is victim_asn, which matches ROA)

**Effectiveness:**

- Succeeds against: `BGP`, `BGPFull`, `ROV`, `PeerROV`, `BGPSec`, `ROVPP` variants
- Defeated by: `ASPA`, `ASRA`, `PathEnd`, `BGP-iSec` (these validate AS path relationships)

**Sources:**

- [bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/forged_origin_prefix_hijack.py13-56](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/forged_origin_prefix_hijack.py#L13-L56)

### ShortestPathPrefixHijack

An adaptive attack that constructs the shortest valid path that evades the deployed security policy. The attack strategy changes based on `AdoptPolicyCls`:

```
ShortestPathPrefixHijack
_get_shortest_path_attacker_anns()

scenario_config
.AdoptPolicyCls

pre_rov_policy_classes
BGP, BGPFull, etc.

_get_prefix_attacker_anns()
Simple prefix hijack

rov_policy_classes
ROV, PeerROV, ROVPP, etc.

_get_forged_origin_attacker_anns()
Append victim ASN

pathend_policy_classes
PathEnd, PathEndFull

_get_pathend_attack_anns()
as_path = (provider_asn, victim_asn)

aspa_policy_classes
ASPA, ASPAFull

_get_aspa_attack_anns()
Find shortest valley-free
non-adopting path

asra_policy_classes
ASRA, ASPAwN

Same as ASPA
but no custom attacker policy

bgpisec_policy_classes
BGPiSecTransitive, etc.

post_propagation_hook()
Find shortest actual announcement
in non-adopter's local RIB
```

**Policy-Specific Attack Strategies:**

#### Against Pre-ROV Policies (BGP, BGPFull)

Uses simple `PrefixHijack` strategy.

#### Against ROV Policies (ROV, PeerROV, ROVPP)

Uses `ForgedOriginPrefixHijack` strategy (append victim ASN).

#### Against PathEnd Policies

Constructs a 2-hop path: `(first_provider_of_victim, victim_asn)`. PathEnd only validates the last two hops, so this path appears valid.

**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py133-185](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L133-L185)

#### Against ASPA Policies

Uses `_find_shortest_valley_free_non_adopting_path()` to construct the shortest path ending in a non-ASPA adopter. This requires using `ShortestPathPrefixASPAAttacker` as the attacker policy, which exports all announcements to customers (bypassing ASPA's provider validation).

**Algorithm:**

1. BFS through provider relationships from victim
2. Check peer relationships
3. If needed, use propagation ranks to explore customer relationships
4. Return shortest path ending in non-adopter

**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py187-360](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L187-L360)

#### Against ASRA/ASPAwN Policies

Same as ASPA but doesn't require custom attacker policy (can use `BGP` attacker policy).

**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py111-114](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L111-L114)

#### Against BGP-iSec Policies

Unlike other attacks that construct *plausible* paths, BGP-iSec attacks must use *actual* announcements due to transitive cryptographic attributes. The attack uses `post_propagation_hook()`:

1. After first propagation round, search all non-BGP-iSec ASes' local RIBs
2. Find announcement with shortest AS path, preferring those without OTC (Only-To-Customers) attributes
3. Clear the graph and seed attacker's announcement with prepended ASN
4. Propagate again

**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py362-468](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L362-L468)

**Effectiveness:**

- The attack adapts to any policy, finding the shortest evasion path
- Requires `ShortestPathPrefixASPAAttacker` when attacking ASPA
- Against BGP-iSec, requires 2 propagation rounds

**Sources:**

- [bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py73-571](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L73-L571)
- [bgpy/simulation_engine/__init__.py56-57](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/__init__.py#L56-L57)

### FirstASNStrippingPrefixHijack

Extends `ShortestPathPrefixHijack` by removing the attacker's ASN from the AS path, making detection harder.

**Announcements:**

- **Victim:**`Announcement(prefix=PREFIX, as_path=(victim_asn,))`
- **Attacker:** Same as `ShortestPathPrefixHijack` but with first ASN removed from `as_path`

**Example against ASPA:**

- ShortestPath would announce: `as_path=(attacker_asn, provider1, provider2, victim_asn)`
- FirstASNStripping announces: `as_path=(provider1, provider2, victim_asn)`

**Effectiveness:**

- More evasive than `ShortestPathPrefixHijack` when path length > 1
- Requires `FirstASNStrippingPrefixASPAAttacker` when attacking ASPA
- If path length = 1, behaves identically to `ShortestPathPrefixHijack`

**Sources:**

- [bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/first_asn_stripping_prefix_hijack.py17-56](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/first_asn_stripping_prefix_hijack.py#L17-L56)
- [bgpy/simulation_engine/policies/custom_attackers/__init__.py1-6](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/custom_attackers/__init__.py#L1-L6)

### SuperprefixPrefixHijack

The attacker announces both the exact prefix (invalid by ROA) and a superprefix (ROA unknown), exploiting ASes that accept unknown ROA statuses.

**Announcements:**

- **Victim:**`Announcement(prefix=PREFIX, as_path=(victim_asn,))`
- **Attacker:**
- `Announcement(prefix=PREFIX, as_path=(attacker_asn,))`
- `Announcement(prefix=SUPERPREFIX, as_path=(attacker_asn,))`

**ROA:**`ROA(prefix=PREFIX, origin=victim_asn)`

**ROA Validation:**

- Victim PREFIX: `VALID`
- Attacker PREFIX: `INVALID_BY_ORIGIN`
- Attacker SUPERPREFIX: `UNKNOWN` (no covering ROA)

**Effectiveness:**

- Succeeds against ASes that accept `UNKNOWN` ROA status
- The superprefix may be preferred in some cases due to longest-prefix-match trade-offs
- Defeated by policies that reject both `INVALID` and `UNKNOWN` ROAs

**Sources:**

- [bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/superprefix_prefix_hijack.py13-48](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/superprefix_prefix_hijack.py#L13-L48)

## Non-Routed Prefix Attacks

Non-routed prefix attacks exploit ROAs with origin AS 0, which indicate that a prefix should not be routed. These attacks test how policies handle such "do not route" ROAs.

### Attack Mechanism Diagram

```
Policy Handling

ROA Validation

origin=attacker_asn
ROA origin=0

ROA(prefix=PREFIX, origin=0)
Indicates non-routed prefix

Attacker Announcement
prefix=PREFIX
as_path=(attacker_asn,)

Origin matches
ROA origin?

Result: INVALID_BY_ORIGIN

ROV Policy

ROV++ Policy

Rejects INVALID

Blackholes prefix
and neighbors
```

**Sources:**

- [bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_prefix_hijack.py39-47](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_prefix_hijack.py#L39-L47)

### NonRoutedPrefixHijack

The attacker announces a prefix that has a ROA with AS 0 origin.

**Announcements:**

- **Attacker:**`Announcement(prefix=PREFIX, as_path=(attacker_asn,))`

**ROA:**`ROA(prefix=PREFIX, origin=0)`

**ROA Validation:**

- Attacker announcement: `INVALID_BY_ORIGIN` (attacker_asn ≠ 0)

**Effectiveness:**

- Tests whether policies properly handle AS 0 ROAs
- `ROV` rejects the announcement
- `ROV++V1` and `ROV++V2` blackhole the prefix and neighboring prefixes

**Sources:**

- [bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_prefix_hijack.py14-48](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_prefix_hijack.py#L14-L48)

### NonRoutedSuperprefixHijack

The attacker announces a superprefix (ROA unknown) to hijack a non-routed prefix.

**Announcements:**

- **Attacker:**`Announcement(prefix=SUPERPREFIX, as_path=(attacker_asn,))`

**ROA:**`ROA(prefix=PREFIX, origin=0)`

**ROA Validation:**

- Attacker SUPERPREFIX: `UNKNOWN` (no covering ROA for SUPERPREFIX)

**Effectiveness:**

- Tests whether policies propagate AS 0 ROA information to covering prefixes
- Basic `ROV` accepts the announcement (ROA unknown)
- `ROV++` variants may blackhole based on implementation

**Sources:**

- [bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_hijack.py14-56](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_hijack.py#L14-L56)

### NonRoutedSuperprefixPrefixHijack

Combines both attacks: the attacker announces both the exact prefix and a superprefix.

**Announcements:**

- **Attacker:**
- `Announcement(prefix=SUPERPREFIX, as_path=(attacker_asn,))`
- `Announcement(prefix=PREFIX, as_path=(attacker_asn,))`

**ROA:**`ROA(prefix=PREFIX, origin=0)`

**ROA Validation:**

- Attacker PREFIX: `INVALID_BY_ORIGIN`
- Attacker SUPERPREFIX: `UNKNOWN`

**Effectiveness:**

- Comprehensive test of AS 0 ROA handling
- Tests both exact-match and covering-prefix scenarios
- Some ASes may prefer the more specific PREFIX despite being invalid

**Sources:**

- [bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_prefix_hijack.py14-64](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_prefix_hijack.py#L14-L64)

## Custom Attacker Policies

Certain attack scenarios require specialized attacker policies that deviate from standard BGP export behavior. These policies are assigned to attacker ASes via `ScenarioConfig.AttackerBasePolicyCls`.

### ShortestPathPrefixASPAAttacker

Required when using `ShortestPathPrefixHijack` against ASPA-based policies (`ASPA`, `ASPAFull`).

**Behavior:**

- Extends `ASPA` policy
- **Exports announcements to customers even if they fail ASPA validation**
- This allows the attacker to send the shortest-path announcement through ASPA's provider-customer validation

**Usage:**

```
from bgpy.simulation_engine import ShortestPathPrefixASPAAttacker
from bgpy.simulation_framework import ScenarioConfig, ShortestPathPrefixHijack
from bgpy.simulation_engine import ASPA

scenario_config = ScenarioConfig(
    ScenarioCls=ShortestPathPrefixHijack,
    AdoptPolicyCls=ASPA,
    AttackerBasePolicyCls=ShortestPathPrefixASPAAttacker  # Required
)
```

**Validation:**
The scenario will raise `ValueError` if `AttackerBasePolicyCls` is not set correctly:

**Sources:**

- [bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py224-233](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L224-L233)
- [bgpy/simulation_engine/__init__.py56](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/__init__.py#L56-L56)

### FirstASNStrippingPrefixASPAAttacker

Required when using `FirstASNStrippingPrefixHijack` against ASPA-based policies.

**Behavior:**

- Extends `ShortestPathPrefixASPAAttacker`
- Exports announcements to customers even if ASPA validation fails
- Used in conjunction with first-ASN-stripping attack

**Usage:**

```
from bgpy.simulation_engine import FirstASNStrippingPrefixASPAAttacker
from bgpy.simulation_framework import ScenarioConfig, FirstASNStrippingPrefixHijack
from bgpy.simulation_engine import ASPA

scenario_config = ScenarioConfig(
    ScenarioCls=FirstASNStrippingPrefixHijack,
    AdoptPolicyCls=ASPA,
    AttackerBasePolicyCls=FirstASNStrippingPrefixASPAAttacker  # Required
)
```

**Sources:**

- [bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/first_asn_stripping_prefix_hijack.py20](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/first_asn_stripping_prefix_hijack.py#L20-L20)
- [bgpy/simulation_engine/policies/custom_attackers/__init__.py1-6](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/custom_attackers/__init__.py#L1-L6)

## Scenario Configuration Summary

This table summarizes all attack scenarios, their target policies, and required configurations:
ScenarioTarget PoliciesCustom Attacker Policy RequiredMulti-RoundKey Method`PrefixHijack`BGP, BGPFullNoNo`_get_prefix_attacker_anns()``SubprefixHijack`BGP, BGPFullNoNo`_get_subprefix_attacker_anns()``ForgedOriginPrefixHijack`ROV, PeerROV, BGPSecNoNo`_get_forged_origin_attacker_anns()``ShortestPathPrefixHijack` (vs BGP)BGP, BGPFullNoNoUses `PrefixHijack` strategy`ShortestPathPrefixHijack` (vs ROV)ROV, PeerROV, ROVPPNoNoUses `ForgedOriginPrefixHijack` strategy`ShortestPathPrefixHijack` (vs PathEnd)PathEndNoNo`_get_pathend_attack_anns()``ShortestPathPrefixHijack` (vs ASPA)ASPAYes (`ShortestPathPrefixASPAAttacker`)No`_get_aspa_attack_anns()``ShortestPathPrefixHijack` (vs ASRA)ASRA, ASPAwNNoNo`_get_aspa_attack_anns()``ShortestPathPrefixHijack` (vs BGP-iSec)BGP-iSec variantsNoYes (2 rounds)`post_propagation_hook()``FirstASNStrippingPrefixHijack` (vs ASPA)ASPAYes (`FirstASNStrippingPrefixASPAAttacker`)NoExtends ShortestPath`SuperprefixPrefixHijack`ROV variantsNoNoAnnounces PREFIX + SUPERPREFIX`NonRoutedPrefixHijack`ROV, ROVPPNoNoROA with AS 0`NonRoutedSuperprefixHijack`ROV, ROVPPNoNoSuperprefix with AS 0 ROA`NonRoutedSuperprefixPrefixHijack`ROV, ROVPPNoNoBoth prefixes with AS 0 ROA`AccidentalRouteLeak`AllNoYes (2 rounds)`post_propagation_hook()`
**Sources:**

- [bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py73-571](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L73-L571)
- [bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/__init__.py1-11](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/__init__.py#L1-L11)
- [bgpy/simulation_engine/__init__.py1-119](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/__init__.py#L1-L119)