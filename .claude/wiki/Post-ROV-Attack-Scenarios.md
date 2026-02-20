# Post-ROV Attack Scenarios
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

## Purpose and Scope

This page documents attack scenarios that evade Route Origin Validation (ROV) through AS path manipulation. These attacks assume the defender has deployed ROV or more advanced path validation mechanisms, and the attacker adapts by forging paths rather than simply announcing false origins.

For attacks against basic BGP without security policies, see [Pre-ROV Attack Scenarios](/blcrdbob3/bgpy_pkg/7.1-pre-rov-attack-scenarios). For attacks exploiting non-routed prefixes with AS 0 ROAs, see [Non-Routed Prefix Attacks](/blcrdbob3/bgpy_pkg/7.3-non-routed-prefix-attacks). For information about the base scenario abstraction, see [Attack Scenarios Overview](/blcrdbob3/bgpy_pkg/3.4-attack-scenarios-overview).

---

## Attack Strategy Overview

Post-ROV attacks evade origin validation by manipulating the AS path to appear legitimate. The fundamental strategy is to append or prepend valid ASNs to the attacker's announcement, making it appear as though the announcement originated from a legitimate source or traversed a valid path.

### Post-ROV Attack Hierarchy

```
used by

VictimsPrefix
Base class with victim+ROAs

ForgedOriginPrefixHijack
Append victim ASN to path

ShortestPathPrefixHijack
Adapt to policy type

FirstASNStrippingPrefixHijack
Remove attacker from path

SuperprefixPrefixHijack
Announce prefix + superprefix
```

**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/__init__.py1-11](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/__init__.py#L1-L11)[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/forged_origin_prefix_hijack.py1-56](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/forged_origin_prefix_hijack.py#L1-L56)[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py1-571](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L1-L571)

---

## ForgedOriginPrefixHijack

`ForgedOriginPrefixHijack` is the simplest Post-ROV attack. The attacker announces a prefix with an AS path that includes the legitimate victim's ASN as the origin, bypassing ROV checks that only validate the origin AS.

### Attack Mechanism
ComponentValue**Prefix**`Prefixes.PREFIX.value` (same as victim)**AS Path**`(attacker_asn, victim_asn)`**Timestamp**`Timestamps.ATTACKER.value`**ROA**Valid for victim ASN (inherited from `VictimsPrefix`)
The attack creates announcements where the attacker prepends their ASN before the victim's ASN, making the origin validation pass while the attacker controls traffic routing.

### Implementation

```
Attacker Announcement

Victim Announcement

ROV validates origin

ROV validates origin

Chooses by
path length

Prefix: 1.2.0.0/16
Path: victim_asn
ROA: Valid

Prefix: 1.2.0.0/16
Path: attacker_asn, victim_asn
ROA: Valid origin

ROV Policy
Accepts both

Attacker wins
shorter path to attacker
```

**Code Reference:**

The announcement generation occurs in [bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/forged_origin_prefix_hijack.py35-55](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/forged_origin_prefix_hijack.py#L35-L55):

- Line 42: Retrieves victim ASN
- Lines 45-54: Creates announcements with `(attacker_asn, victim_asn)` path
- Lines 51-52: Sets `next_hop_asn` and `seed_asn` to attacker

**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/forged_origin_prefix_hijack.py1-56](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/forged_origin_prefix_hijack.py#L1-L56)

---

## ShortestPathPrefixHijack

`ShortestPathPrefixHijack` is an adaptive attack that constructs the shortest AS path allowed by the defending policy. The attack strategy varies based on which security policy is deployed, demonstrating sophisticated understanding of policy validation rules.

### Policy-Specific Attack Strategies

```
Line 101

Line 104

Line 107

Line 109

Line 111

Line 115

ShortestPathPrefixHijack
_get_shortest_path_attacker_anns

AdoptPolicyCls type?

pre_rov_policy_classes
BGP, BGPFull, etc.

rov_policy_classes
ROV, ROVFull, BGPSec, etc.

pathend_policy_classes
PathEnd, PathEndFull

aspa_policy_classes
ASPA, ASPAFull

asra_policy_classes
ASRA, ASPAwN, etc.

bgpisec_policy_classes
BGPiSec variants

_get_prefix_attacker_anns
Simple prefix hijack

_get_forged_origin_attacker_anns
Append victim ASN

_get_pathend_attack_anns
provider_asn, victim_asn

_get_aspa_attack_anns
Shortest valley-free path

post_propagation_hook
Copy real announcement
```

**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py94-124](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L94-L124)

### Attack Against PathEnd

PathEnd validates that the first two ASNs in the path have a valid relationship. The attack constructs a path containing:

1. A provider/peer/customer of the victim
2. The victim ASN

```
has provider

announces path:
attacker, provider, victim

PathEnd validates:
provider-victim relationship

victim_asn
Legitimate origin

first_provider
or peer/customer

attacker_asn

Forged Path

Passes validation
```

**Implementation details** at [bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py133-185](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L133-L185):

- Lines 144-152: Searches for provider of victim
- Lines 154-157: Falls back to peer if no provider
- Lines 159-163: Falls back to customer if needed
- Lines 176-184: Constructs announcement with `(attacker_asn, *shortest_valid_path)`

**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py133-185](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L133-L185)

### Attack Against ASPA

ASPA validates that each AS pair in the path represents a valid provider-customer relationship. The attack finds the shortest valley-free path from the victim to a non-adopting AS, ensuring all ASPA validations pass.

#### Valley-Free Path Discovery Algorithm

The algorithm searches in priority order:

1. **Provider cone**: BFS through provider relationships
2. **Peer cone**: Breadth-first through peers of visited providers
3. **Customer cone**: Propagation-rank-based traversal through customer relationships

```
Yes

No, continue

All peers adopting

None found

_find_shortest_valley_free_non_adopting_path
root_asn=victim

BFS through providers
Lines 258-267

Iterate visited ASes
Check peers
Lines 272-278

Propagation rank order
Lines 325-342

Is AS non-adopting?

Return AS path

Warning: full adoption
```

**Key algorithmic features:**
PhaseRelationshipsData StructureTerminationPhase 1Providers`deque` BFS queueFirst non-adopter foundPhase 2PeersOrdered dict iterationFirst non-adopter foundPhase 3CustomersPropagation ranksShortest path among non-adopters
**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py235-360](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L235-L360)

#### ASPA Attack Requirements

When attacking ASPA policies, the attacker must use `ShortestPathPrefixASPAAttacker` as their base policy class. This custom attacker policy exports the malicious announcement to all neighbors (customers, peers, and providers) rather than following valley-free routing.

**Validation logic** at [bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py224-233](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L224-L233):

- Line 227: Checks `AttackerBasePolicyCls == RequiredASPAAttackerCls`
- Lines 228-233: Raises `ValueError` with import instructions if incorrect

**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py187-233](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L187-L233)

### Attack Against BGP-iSec

BGP-iSec uses transitive cryptographic attributes that cannot be forged from theoretical paths. The attacker must copy an actual announcement from a real AS's local RIB. This attack uses a two-round propagation mechanism.

#### Two-Round Propagation Mechanism

```
Propagation Round 1
post_propagation_hook
Propagation Round 0
Scenario Setup
Propagation Round 1
post_propagation_hook
Propagation Round 0
Scenario Setup
Seed victim announcement only
Propagate victim announcement
propagation_round == 0
Search all AS local RIBs
Find best announcement to copy
Prefer no OTC attribute
Prefer shorter paths
Prepend attacker ASN
self.announcements = victim + attacker
self.setup_engine clear graph
engine.ready_to_run_round = 1
Propagate both announcements
```

**Implementation details** at [bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py362-468](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L362-L468):

1. **Round 0 validation** (lines 412-416): Ensures `propagation_rounds >= 2`
2. **Best announcement selection** (lines 421-436):

- Line 424: Searches non-`BGPiSecTransitive` ASes
- Lines 428-430: Prefers announcements without `only_to_customers` flag
- Line 434: Prefers shorter AS paths
3. **Fallback handling** (lines 437-445): Uses victim's announcement if none found
4. **Attack announcement creation** (lines 449-461): Prepends attacker ASN to best announcement
5. **Engine reset** (lines 463-466): Clears graph and reseeds for second propagation

**Why this approach is more efficient than traditional two-round propagation:**

Traditional approach (not used):

- Keep full graph state from round 0
- Attacker modifies local RIB
- Propagate again with full graph (expensive withdrawals)
- Requires `BGPFull` policy (much slower)

Current approach:

- Clear graph after finding best announcement
- Reseed with both announcements
- Single propagation with empty graph
- Works with simple `BGP` policy (much faster)

**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py362-468](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L362-L468)

### Policy Class Classifications

The `ShortestPathPrefixHijack` class maintains frozen sets categorizing policy classes by their validation mechanisms:
PropertyPolicy ClassesAttack Strategy`pre_rov_policy_classes``BGP`, `BGPFull`, `OnlyToCustomers`, `EdgeFilter`, `EnforceFirstAS`Simple prefix hijack`rov_policy_classes``ROV`, `ROVFull`, `PeerROV`, `BGPSec`, `ROVPPV1Lite`, `ROVPPV2Lite`, `ProviderConeID`Forged origin`pathend_policy_classes``PathEnd`, `PathEndFull`Provider-victim path`aspa_policy_classes``ASPA`, `ASPAFull`Shortest valley-free to non-adopter`asra_policy_classes``ASRA`, `ASRAFull`, `ASPAwN`, `ASPAwNFull`Same as ASPA but no custom attacker required`bgpisec_policy_classes``BGPiSecTransitive`, `BGPiSecTransitiveOnlyToCustomers`, `BGPiSec`, and `Full` variantsCopy real announcement
**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py474-570](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L474-L570)

---

## FirstASNStrippingPrefixHijack

`FirstASNStrippingPrefixHijack` extends `ShortestPathPrefixHijack` by removing the attacker's ASN from the forged path. This makes the attack stealthier by making it appear as though the announcement originated directly from the second AS in the path.

### Attack Mechanism

```
FirstASNStrippingPrefixHijack

ShortestPathPrefixHijack

Strip attacker_asn

appears to originate
from AS1

Path: attacker, AS1, AS2, victim

Path: AS1, AS2, victim

More stealthy
Harder to trace
```

**Implementation** at [bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/first_asn_stripping_prefix_hijack.py41-56](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/first_asn_stripping_prefix_hijack.py#L41-L56):

- Line 46: Calls `_get_shortest_path_attacker_anns()` from parent class
- Lines 48-55: Strips first ASN from each announcement if path length > 1
- Line 51: Uses `ann.copy({"as_path": ann.as_path[1:]})` to remove attacker

### Required Attacker Policy

Like the parent class when attacking ASPA, this scenario requires `FirstASNStrippingPrefixASPAAttacker` as the attacker policy when targeting ASPA-based defenses. This custom policy is needed because the attacker's ASN does not appear in the AS path, requiring special export behavior.

**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/first_asn_stripping_prefix_hijack.py1-57](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/first_asn_stripping_prefix_hijack.py#L1-L57)

---

## SuperprefixPrefixHijack

`SuperprefixPrefixHijack` announces both a specific prefix (matching the victim's) and a less-specific superprefix. This creates two attack vectors simultaneously, exploiting longest-prefix-match routing.

### Dual Announcement Strategy

```
Invalid by origin

Unknown no ROA

Accepts victim + super

Victim Announcement
Prefix: 1.2.0.0/16
Path: victim_asn
ROA: Valid

Attacker Prefix Ann
Prefix: 1.2.0.0/16
Path: attacker_asn
ROA: Invalid origin

Attacker Superprefix Ann
Prefix: 1.0.0.0/8
Path: attacker_asn
ROA: Unknown

ROV Decision

Mixed routing:
Some ASes to victim
Some ASes to attacker
```

### Announcement Details
AnnouncementPrefixAS PathROA StatusVictim`Prefixes.PREFIX.value``(victim_asn,)`ValidAttacker prefix`Prefixes.PREFIX.value``(attacker_asn,)`Invalid by originAttacker superprefix`Prefixes.SUPERPREFIX.value``(attacker_asn,)`Unknown (no ROA)
The attack succeeds when:

1. ROV-adopting ASes reject the attacker's prefix announcement (invalid origin)
2. ROV-adopting ASes accept the attacker's superprefix (unknown, no ROA)
3. ASes closer to the attacker prefer the superprefix due to shorter path
4. Traffic to addresses not explicitly covered by victim flows to attacker

**Implementation** at [bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/superprefix_prefix_hijack.py22-48](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/superprefix_prefix_hijack.py#L22-L48):

- Lines 33-38: Creates prefix announcement (invalid by ROV)
- Lines 40-45: Creates superprefix announcement (unknown by ROV)

**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/superprefix_prefix_hijack.py1-49](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/superprefix_prefix_hijack.py#L1-L49)

---

## Custom Attacker Policies

Post-ROV attacks against ASPA-family policies require custom attacker policies because standard valley-free routing would prevent the attacker from exporting malicious announcements in all necessary directions.

### ShortestPathPrefixASPAAttacker

This policy allows the attacker to export the forged announcement to all neighbors (customers, peers, and providers), violating valley-free routing to maximize attack propagation.

```
ASPA Attacker Export

Export to all

Forged announcement
needs wide propagation

customers, peers, providers

Standard BGP Export

Export to all

Export only to

Export only to

Receive from customer

customers, peers, providers

Receive from peer

customers

Receive from provider

customers
```

The custom policy is defined in [bgpy/simulation_engine/policies/custom_attackers/shortest_path_prefix_aspa_attacker.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/custom_attackers/shortest_path_prefix_aspa_attacker.py) and must be explicitly specified in the `ScenarioConfig.AttackerBasePolicyCls` when using `ShortestPathPrefixHijack` against ASPA policies.

**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py76-77](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L76-L77)[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py224-233](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L224-L233)

### FirstASNStrippingPrefixASPAAttacker

This policy extends the export-all behavior for scenarios where the attacker's ASN is stripped from the path. It's required when using `FirstASNStrippingPrefixHijack` against ASPA policies.

**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/first_asn_stripping_prefix_hijack.py20](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/first_asn_stripping_prefix_hijack.py#L20-L20)[bgpy/simulation_engine/policies/custom_attackers/__init__.py1-6](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/custom_attackers/__init__.py#L1-L6)

---

## Implementation Patterns

### Common Base Class Pattern

All Post-ROV attack scenarios extend `VictimsPrefix`, which provides:

- Victim ASN selection from available ASes
- Legitimate prefix announcement generation
- ROA creation with victim as authorized origin
- Attacker ASN selection

```
VictimsPrefix
victim_asns, attacker_asns
_get_announcements creates victim anns
_get_roas creates valid ROAs

ForgedOriginPrefixHijack
Overrides _get_announcements
Adds victim+attacker anns

ShortestPathPrefixHijack
Overrides _get_announcements
Adapts to policy type

FirstASNStrippingPrefixHijack
Extends ShortestPath
Strips attacker from path

SuperprefixPrefixHijack
Overrides _get_announcements
Adds prefix + superprefix
```

**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/forged_origin_prefix_hijack.py4-6](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/forged_origin_prefix_hijack.py#L4-L6)[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py60-63](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L60-L63)

### Mixin Pattern for Code Reuse

`ShortestPathPrefixHijack` reuses attack methods from simpler scenarios using a mixin pattern:

**Code at**[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py126-131](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L126-L131):

```
_get_prefix_attacker_anns = PrefixHijack._get_prefix_attacker_anns
_get_forged_origin_attacker_anns = ForgedOriginPrefixHijack._get_forged_origin_attacker_anns
```

This allows `ShortestPathPrefixHijack` to delegate to simpler attack implementations when facing weaker policies, avoiding code duplication.

**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py60-65](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L60-L65)[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py126-131](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L126-L131)

### Hook-Based Two-Round Attacks

For attacks requiring multiple propagation rounds (e.g., BGP-iSec attack), scenarios use the `post_propagation_hook` mechanism:

1. Scenario sets `propagation_rounds >= 2` in configuration
2. Round 0: Propagates legitimate announcements only
3. Hook executes after round 0, analyzes graph state, modifies announcements
4. Hook calls `self.setup_engine(engine)` to reset graph
5. Hook sets `engine.ready_to_run_round = 1`
6. Round 1: Propagates modified announcements

This pattern avoids the computational expense of propagating in a full graph and avoids requiring `BGPFull` policies.

**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py362-468](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L362-L468)