# BGP Policy Reference
Relevant source files
- [bgpy/shared/exceptions.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/shared/exceptions.py)
- [bgpy/simulation_engine/ann_containers/ribs_in.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/ann_containers/ribs_in.py)
- [bgpy/simulation_engine/announcement.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/announcement.py)
- [bgpy/simulation_engine/policies/bgp/bgp/bgp.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/bgp.py)
- [bgpy/simulation_engine/policies/bgp/bgp/bgp.pyi](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/bgp.pyi)
- [bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py)
- [bgpy/simulation_engine/policies/bgp/bgp_full.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp_full.py)
- [bgpy/simulation_engine/policies/bgpsec/bgpsec.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgpsec/bgpsec.py)
- [bgpy/simulation_engine/policies/bgpsec/bgpsec_full.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgpsec/bgpsec_full.py)
- [bgpy/simulation_engine/policies/edge_filter/rov_edge_filter.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/edge_filter/rov_edge_filter.py)
- [bgpy/simulation_engine/policies/enforce_first_as/rov_enforce_first_as.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/enforce_first_as/rov_enforce_first_as.py)
- [bgpy/simulation_engine/policies/policy.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/policy.py)
- [bgpy/simulation_engine/policies/rov/peer_rov.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rov/peer_rov.py)
- [bgpy/simulation_engine/policies/rov/rov.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rov/rov.py)
- [bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py)
- [bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite_full.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite_full.py)
- [bgpy/simulation_engine/policies/rovpp/v2/base/rovpp_v2_lite.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v2/base/rovpp_v2_lite.py)
- [bgpy/simulation_engine/policies/rovpp/v2/base/rovpp_v2_lite_full.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v2/base/rovpp_v2_lite_full.py)
- [bgpy/simulation_engine/policies/rovpp/v2/improved/rovpp_v2_improved_lite_full.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v2/improved/rovpp_v2_improved_lite_full.py)
- [bgpy/tests/framework_tests/unit_tests/test_scenario.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/framework_tests/unit_tests/test_scenario.py)

## Purpose and Scope

This page provides a comprehensive reference for all BGP policy implementations in the BGPy simulation framework. A **policy** defines how an AS processes and propagates BGP announcements, including security mechanisms like Route Origin Validation (ROV), AS Path Attestation (ASPA), and BGPSec.

This page covers:

- The `Policy` abstract base class and policy architecture
- Core announcement processing and propagation mechanisms
- The Gao-Rexford routing decision process
- Overview of all implemented policy types and their inheritance hierarchy
- Policy selection guidelines

For detailed documentation of specific policy categories, see:

- Base BGP policies (BGP, BGPFull): [6.1](/blcrdbob3/bgpy_pkg/6.1-base-bgp-policies)
- ROV implementations: [6.2](/blcrdbob3/bgpy_pkg/6.2-route-origin-validation-(rov))
- ROV++ policies: [6.3](/blcrdbob3/bgpy_pkg/6.3-rov++-policies)
- ASPA policy family: [6.4](/blcrdbob3/bgpy_pkg/6.4-aspa-policy-family)
- Other security policies (BGPSec, PathEnd, etc.): [6.5](/blcrdbob3/bgpy_pkg/6.5-other-security-policies)

For information on attack scenarios that policies defend against, see [Attack Scenario Reference](/blcrdbob3/bgpy_pkg/7-attack-scenario-reference).

---

## Policy Architecture

### Policy Abstract Base Class

All policies in BGPy inherit from the `Policy` abstract base class defined in [bgpy/simulation_engine/policies/policy.py14-167](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/policy.py#L14-L167) This class establishes the core interface that all policies must implement:

**Key Components:**
ComponentTypeDescription`name``str`Human-readable policy name (class attribute)`roa_checker``ROAChecker`Global RPKI validator (class attribute, shared across all policies)`subclass_to_name_dict``dict`Registry mapping policy classes to names`name_to_subclass_dict``dict`Registry mapping names to policy classes
**Abstract Methods Required:**

```
receive_ann(ann: Announcement) -> None
process_incoming_anns(from_rel: Relationships, propagation_round: int, ...) -> None
propagate_to_providers() -> None
propagate_to_customers() -> None
propagate_to_peers() -> None
```

**ROA Validation Methods:**

The `Policy` base class provides built-in methods for RPKI validation [bgpy/simulation_engine/policies/policy.py99-154](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/policy.py#L99-L154):

- `get_roa_outcome(ann)` - Returns `ROAOutcome` for an announcement
- `ann_is_invalid_by_roa(ann)` - Returns `True` if announcement is ROA-invalid
- `ann_is_valid_by_roa(ann)` - Returns `True` if announcement is ROA-valid
- `ann_is_unknown_by_roa(ann)` - Returns `True` if no ROA covers the announcement
- `ann_is_roa_non_routed(ann)` - Returns `True` if ROA marks prefix as non-routed

Sources: [bgpy/simulation_engine/policies/policy.py1-167](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/policy.py#L1-L167)

---

### Policy Registration and Inheritance

Policies automatically register themselves using Python's `__init_subclass__` hook [bgpy/simulation_engine/policies/policy.py21-40](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/policy.py#L21-L40) Each policy must define a unique `name` class attribute:

```
class MyPolicy(BGP):
    name = "My Custom Policy"  # Registers policy with this name
```

This enables:

1. YAML serialization of policies by name
2. Dynamic policy lookup via `Policy.name_to_subclass_dict`
3. Automatic validation that policy names are unique

Sources: [bgpy/simulation_engine/policies/policy.py21-40](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/policy.py#L21-L40)

---

## Core Data Structures

### Announcement Container Types

Policies maintain several data structures for managing BGP announcements:
ContainerClassPurposeUsed ByLocal RIB`LocalRIB`Stores best route per prefixAll policiesReceive Queue`RecvQueue`Buffers incoming announcements per roundAll policiesRIBsIn`RIBsIn`Stores unprocessed announcements from each neighborBGPFull and subclassesRIBsOut`RIBsOut`Tracks announcements sent to each neighborBGPFull and subclasses
**LocalRIB**[bgpy/simulation_engine/policies/bgp/bgp/bgp.py60](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/bgp.py#L60-L60): Maps prefix → best announcement currently selected by the AS.

**RecvQueue**[bgpy/simulation_engine/policies/bgp/bgp/bgp.py61](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/bgp.py#L61-L61): Maps prefix → list of announcements received this round, cleared after processing.

**RIBsIn**[bgpy/simulation_engine/ann_containers/ribs_in.py28-87](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/ann_containers/ribs_in.py#L28-L87): Maps neighbor_asn → {prefix → `AnnInfo`}, where `AnnInfo` stores the unprocessed announcement and receive relationship [bgpy/simulation_engine/ann_containers/ribs_in.py13-26](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/ann_containers/ribs_in.py#L13-L26)

**RIBsOut**[bgpy/simulation_engine/policies/bgp/bgp_full.py26](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp_full.py#L26-L26): Maps neighbor_asn → {prefix → announcement}, tracking what was sent to each neighbor for withdrawal handling.

### Announcement Structure

The `Announcement` dataclass [bgpy/simulation_engine/announcement.py10-143](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/announcement.py#L10-L143) contains:

**Core Fields:**

- `prefix` - IP prefix (e.g., "1.2.0.0/16")
- `as_path` - Tuple of ASNs in path
- `next_hop_asn` - Next hop for data plane traffic
- `seed_asn` - Original AS that seeded this announcement
- `recv_relationship` - Relationship type from which announcement was received
- `timestamp` - Used for tie-breaking (victim=0, attacker=1)

**Optional Fields (policy-specific):**

- `withdraw` - Boolean for withdrawal announcements (BGPFull)
- `bgpsec_next_asn`, `bgpsec_as_path` - BGPSec validation fields
- `only_to_customers` - RFC 9234 OTC attribute
- `rovpp_blackhole` - ROV++ blackhole marker

Sources: [bgpy/simulation_engine/announcement.py1-143](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/announcement.py#L1-L143)[bgpy/simulation_engine/policies/bgp/bgp/bgp.py46-64](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/bgp.py#L46-L64)[bgpy/simulation_engine/ann_containers/ribs_in.py1-87](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/ann_containers/ribs_in.py#L1-L87)

---

## Announcement Processing Pipeline

### Overview

The announcement processing pipeline consists of three phases executed in sequence for each relationship type (providers → peers → customers):

```
receive_ann()

recv_q

process_incoming_anns()

_valid_ann()

_copy_and_process()

_get_best_ann_by_gao_rexford()

local_rib

propagate_to_X()

_policy_propagate()

_process_outgoing_ann()

neighbor.receive_ann()
```

Sources: [bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py1-123](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py#L1-L123)

### Phase 1: Receiving Announcements

Announcements arrive via `receive_ann(ann)`[bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py27-30](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py#L27-L30) which adds them to the receive queue:

```
def receive_ann(self, ann: "Ann") -> None:
    self.recv_q.add_ann(ann)
```

The `recv_q` buffers announcements until `process_incoming_anns()` is called [bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py33-61](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py#L33-L61)

Sources: [bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py27-30](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py#L27-L30)

### Phase 2: Processing Incoming Announcements

The `process_incoming_anns(from_rel, propagation_round, scenario)` method [bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py33-61](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py#L33-L61) processes all announcements in `recv_q`:

**For each prefix:**

1. Get current announcement from `local_rib`
2. For each new announcement:

- Call `_valid_ann()` to check validity (loops, ROA, etc.)
- Call `_copy_and_process()` to prepend AS to path
- Call `_get_best_ann_by_gao_rexford()` to compare with current best
3. If best announcement changed, update `local_rib`
4. Clear `recv_q` if `reset_q=True`

**BGPFull Extensions**[bgpy/simulation_engine/policies/bgp/bgp_full.py32-81](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp_full.py#L32-L81):

- Adds announcements to `ribs_in`[bgpy/simulation_engine/policies/bgp/bgp_full.py82-96](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp_full.py#L82-L96)
- Handles withdrawal announcements [bgpy/simulation_engine/policies/bgp/bgp_full.py58-66](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp_full.py#L58-L66)
- Withdraws replaced announcements from neighbors [bgpy/simulation_engine/policies/bgp/bgp_full.py67-78](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp_full.py#L67-L78)

Sources: [bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py33-61](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py#L33-L61)[bgpy/simulation_engine/policies/bgp/bgp_full.py32-122](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp_full.py#L32-L122)

### Phase 3: Announcement Validation

The `_valid_ann(ann, recv_relationship)` method [bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py83-93](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py#L83-L93) determines if an announcement should be accepted:

**Base BGP Validation:**

```
def _valid_ann(self, ann: "Ann", recv_relationship: "Relationships") -> bool:
    # BGP Loop Prevention + no AS 0
    return self.as_.asn not in ann.as_path and 0 not in ann.as_path
```

**ROV Extension**[bgpy/simulation_engine/policies/rov/rov.py15-28](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rov/rov.py#L15-L28):

```
def _valid_ann(self, ann: "Ann", recv_rel: "Relationships") -> bool:
    if self.ann_is_invalid_by_roa(ann):
        return False
    return super()._valid_ann(ann, recv_rel)
```

**PeerROV Extension**[bgpy/simulation_engine/policies/rov/peer_rov.py15-32](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rov/peer_rov.py#L15-L32):

```
def _valid_ann(self, ann: "Ann", recv_rel: "Relationships") -> bool:
    # Only filter ROA-invalid from peers
    if self.ann_is_invalid_by_roa(ann) and ann.recv_relationship == Relationships.PEERS:
        return False
    return super()._valid_ann(ann, recv_rel)
```

Sources: [bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py83-93](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py#L83-L93)[bgpy/simulation_engine/policies/rov/rov.py1-29](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rov/rov.py#L1-L29)[bgpy/simulation_engine/policies/rov/peer_rov.py1-33](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rov/peer_rov.py#L1-L33)

### Phase 4: Announcement Processing

The `_copy_and_process(ann, recv_relationship)` method [bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py95-116](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py#L95-L116) creates a processed copy of the announcement:

**Base BGP Processing:**

1. Prepend AS to `as_path`: `(self.as_.asn, *ann.as_path)`
2. Set `recv_relationship` to the relationship type
3. Clear `seed_asn` to `None`

**BGPSec Extension**[bgpy/simulation_engine/policies/bgpsec/bgpsec.py64-88](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgpsec/bgpsec.py#L64-L88):

- Validates BGPSec path via `bgpsec_valid(ann, self.as_.asn)`
- Prepends ASN to `bgpsec_as_path` if valid, otherwise clears it

Sources: [bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py95-116](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py#L95-L116)[bgpy/simulation_engine/policies/bgpsec/bgpsec.py64-88](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgpsec/bgpsec.py#L64-L88)

---

## Gao-Rexford Decision Process

### Decision Process Hierarchy

The `_get_best_ann_by_gao_rexford(current_ann, new_ann)` method [bgpy/simulation_engine/policies/bgp/bgp/gao_rexford.py] implements the BGP route selection algorithm. Announcements are compared using a hierarchy of tie-breaking rules:

```
Equal

Winner

Equal

Winner

Equal

Winner

Compare Announcements

1. Local Preference
_get_best_ann_by_local_pref()
2. AS Path Length
_get_best_ann_by_as_path()

Return Winner

3. Security Metric
(BGPSec only)

Return Winner

4. Lowest Neighbor ASN
_get_best_ann_by_lowest_neighbor_asn_tiebreaker()

Return Winner

Return Winner
```

### Step 1: Local Preference by Relationship

Local preference is determined by the relationship from which the announcement was received:
RelationshipLocal PrefRoute Type`ORIGIN`4AS originates this prefix`CUSTOMERS`3Received from customer`PEERS`2Received from peer`PROVIDERS`1Received from provider
This implements valley-free routing: customer routes are preferred over peer routes, which are preferred over provider routes.

Sources: [bgpy/simulation_engine/policies/bgp/bgp/gao_rexford.py]

### Step 2: AS Path Length

If local preference is equal, prefer the announcement with the shorter AS path length:

```
def _get_best_ann_by_as_path(self, current_ann: "Ann", new_ann: "Ann") -> "Ann | None":
    if len(current_ann.as_path) < len(new_ann.as_path):
        return current_ann
    elif len(new_ann.as_path) < len(current_ann.as_path):
        return new_ann
    else:
        return None  # Equal, continue to next tiebreaker
```

Sources: [bgpy/simulation_engine/policies/bgp/bgp/gao_rexford.py]

### Step 3: Security Metrics (BGPSec Only)

BGPSec policies insert an additional tie-breaking step after AS path length [bgpy/simulation_engine/policies/bgpsec/bgpsec.py90-139](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgpsec/bgpsec.py#L90-L139) The `_get_best_ann_by_bgpsec()` method prefers announcements with valid BGPSec signatures:

```
def _get_best_ann_by_bgpsec(self, current_ann: "Ann", new_ann: "Ann") -> "Ann | None":
    current_valid = self.bgpsec_valid(current_ann, self.as_.asn)
    new_valid = self.bgpsec_valid(new_ann, self.as_.asn)
    
    if current_valid and not new_valid:
        return current_ann
    elif not current_valid and new_valid:
        return new_ann
    else:
        return None  # Both valid or both invalid
```

This implements "security third" preference as surveyed in "A Survey of Interdomain Routing Policies".

Sources: [bgpy/simulation_engine/policies/bgpsec/bgpsec.py90-139](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgpsec/bgpsec.py#L90-L139)

### Step 4: Lowest Neighbor ASN Tiebreaker

If all previous steps are equal, break ties by selecting the announcement from the neighbor with the lowest ASN:

```
def _get_best_ann_by_lowest_neighbor_asn_tiebreaker(
    self, current_ann: "Ann", new_ann: "Ann"
) -> "Ann":
    # As path is [this_as, neighbor, ...]
    if current_ann.as_path[1] < new_ann.as_path[1]:
        return current_ann
    else:
        return new_ann
```

Sources: [bgpy/simulation_engine/policies/bgp/bgp/gao_rexford.py]

---

## Propagation Mechanisms

### Valley-Free Routing

BGP policies implement valley-free routing through three propagation methods called in sequence by the simulation engine:

1. **`propagate_to_providers()`** - Propagate routes learned from customers or originated locally
2. **`propagate_to_peers()`** - Propagate routes learned from customers or originated locally
3. **`propagate_to_customers()`** - Propagate all routes regardless of source

The internal `_propagate(propagate_to, send_rels)` method [bgpy/simulation_engine/policies/bgp/bgp/propagate_funcs.py] implements the logic:

```
def _propagate(self, propagate_to: Relationships, send_rels: set[Relationships]):
    for prefix, ann in self.local_rib.items():
        if ann.recv_relationship in send_rels:
            for neighbor in self._get_neighbors(propagate_to):
                # Policy-specific handling
                if not self._policy_propagate(neighbor, ann, propagate_to, send_rels):
                    self._process_outgoing_ann(neighbor, ann, propagate_to, send_rels)
```

**Send Relationships:**
Propagating ToSend RelationsLogicProviders`{ORIGIN, CUSTOMERS}`Only send customer routes upPeers`{ORIGIN, CUSTOMERS}`Only send customer routes acrossCustomers`{ORIGIN, CUSTOMERS, PEERS, PROVIDERS}`Send all routes down
Sources: [bgpy/simulation_engine/policies/bgp/bgp/propagate_funcs.py]

### Policy-Specific Propagation Hooks

The `_policy_propagate(neighbor, ann, propagate_to, send_rels)` method allows policies to customize propagation behavior [bgpy/simulation_engine/policies/bgp/bgp/propagate_funcs.py]:

**Return Values:**

- `True` - Policy handled propagation (don't call `_process_outgoing_ann`)
- `False` - Use default propagation behavior

**ROV++V1 Implementation**[bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py20-30](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py#L20-L30):

```
def _policy_propagate(self, neighbor, ann, propagate_to, send_rels) -> bool:
    # Don't propagate blackholes
    return ann.rovpp_blackhole
```

**ROV++V2 Implementation**[bgpy/simulation_engine/policies/rovpp/v2/base/rovpp_v2_lite.py22-65](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v2/base/rovpp_v2_lite.py#L22-L65):

```
def _policy_propagate(self, neighbor, ann, propagate_to, send_rels) -> bool:
    if ann.rovpp_blackhole:
        # Only send blackholes to customers if from peer/provider
        if self._send_competing_hijack_allowed(ann, propagate_to):
            self._process_outgoing_ann(neighbor, ann, propagate_to, send_rels)
        return True
    return False
```

**BGPSec Implementation**[bgpy/simulation_engine/policies/bgpsec/bgpsec.py40-61](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgpsec/bgpsec.py#L40-L61):

```
def _policy_propagate(self, neighbor, ann, propagate_to, send_rels) -> bool:
    # Set BGPSec fields based on neighbor policy
    if isinstance(neighbor.policy, BGPSec):
        send_ann = ann.copy({"bgpsec_next_asn": neighbor.asn, "bgpsec_as_path": ann.bgpsec_as_path})
    else:
        send_ann = ann.copy({"bgpsec_next_asn": None, "bgpsec_as_path": ()})
    self._process_outgoing_ann(neighbor, send_ann, propagate_to, send_rels)
    return True
```

Sources: [bgpy/simulation_engine/policies/bgp/bgp/propagate_funcs.py], [bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py20-30](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py#L20-L30)[bgpy/simulation_engine/policies/rovpp/v2/base/rovpp_v2_lite.py22-65](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v2/base/rovpp_v2_lite.py#L22-L65)[bgpy/simulation_engine/policies/bgpsec/bgpsec.py40-61](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgpsec/bgpsec.py#L40-L61)

---

## Policy Class Hierarchy

### Complete Policy Inheritance Tree

```
Policy
(Abstract Base)

BGP
bgp/bgp/bgp.py

BGPFull
bgp/bgp_full.py
+RIBsIn +RIBsOut +Withdrawals

ROV
rov/rov.py
+ROA Validation

ROVFull
rov/rov_full.py

PeerROV
rov/peer_rov.py
ROV for Peers Only

ROVPPV1Lite
rovpp/v1/rovpp_v1_lite.py
+Blackholing

ROVPPV1LiteFull
rovpp/v1/rovpp_v1_lite_full.py

ROVPPV2Lite
rovpp/v2/base/rovpp_v2_lite.py
+Selective Propagation

ROVPPV2LiteFull
rovpp/v2/base/rovpp_v2_lite_full.py

BGPSec
bgpsec/bgpsec.py
+Path Signatures

BGPSecFull
bgpsec/bgpsec_full.py

EnforceFirstAS
enforce_first_as/enforce_first_as.py

ROVEnforceFirstAS
enforce_first_as/rov_enforce_first_as.py

EdgeFilter
edge_filter/edge_filter.py

ROVEdgeFilter
edge_filter/rov_edge_filter.py
```

Sources: [bgpy/simulation_engine/policies/policy.py14-167](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/policy.py#L14-L167)[bgpy/simulation_engine/policies/bgp/bgp/bgp.py43-125](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/bgp.py#L43-L125)[bgpy/simulation_engine/policies/bgp/bgp_full.py14-306](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp_full.py#L14-L306)[bgpy/simulation_engine/policies/rov/rov.py1-29](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rov/rov.py#L1-L29)[bgpy/simulation_engine/policies/rov/peer_rov.py1-33](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rov/peer_rov.py#L1-L33)[bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py1-159](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py#L1-L159)[bgpy/simulation_engine/policies/rovpp/v2/base/rovpp_v2_lite.py1-66](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v2/base/rovpp_v2_lite.py#L1-L66)[bgpy/simulation_engine/policies/bgpsec/bgpsec.py1-140](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgpsec/bgpsec.py#L1-L140)

---

## Policy Categories Overview

### Base BGP Policies
PolicyFileKey Features`BGP`[bgpy/simulation_engine/policies/bgp/bgp/bgp.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/bgp.py)Basic BGP routing with Gao-Rexford, no security`BGPFull`[bgpy/simulation_engine/policies/bgp/bgp_full.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp_full.py)Adds RIBsIn, RIBsOut, withdrawal handling
**Use Cases:**

- `BGP` - Baseline simulations, lightweight scenarios
- `BGPFull` - Scenarios requiring withdrawal tracking (e.g., route leak recovery)

**Details:** See [Base BGP Policies](/blcrdbob3/bgpy_pkg/6.1-base-bgp-policies)

Sources: [bgpy/simulation_engine/policies/bgp/bgp/bgp.py43-125](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/bgp.py#L43-L125)[bgpy/simulation_engine/policies/bgp/bgp_full.py14-306](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp_full.py#L14-L306)

### Route Origin Validation (ROV)
PolicyFileDefense Mechanism`ROV`[bgpy/simulation_engine/policies/rov/rov.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rov/rov.py)Filters ROA-invalid announcements from all neighbors`PeerROV`[bgpy/simulation_engine/policies/rov/peer_rov.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rov/peer_rov.py)Filters ROA-invalid only from peers (real-world common)`ROVFull`[bgpy/simulation_engine/policies/rov/rov_full.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rov/rov_full.py)ROV + withdrawals + RIBs
**Defense Against:**

- Prefix hijacks with incorrect origin AS
- Subprefix hijacks (when max-length configured)

**Does NOT Defend Against:**

- Attacks with forged origin matching ROA
- Path manipulation attacks
- Non-routed prefix attacks (without ROV++)

**Details:** See [Route Origin Validation](/blcrdbob3/bgpy_pkg/6.2-route-origin-validation-(rov))

Sources: [bgpy/simulation_engine/policies/rov/rov.py1-29](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rov/rov.py#L1-L29)[bgpy/simulation_engine/policies/rov/peer_rov.py1-33](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rov/peer_rov.py#L1-L33)

### ROV++ Policies
PolicyFileAdditional Defense`ROVPPV1Lite`[bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py)Blackholes for non-routed prefixes + invalid subprefixes`ROVPPV2Lite`[bgpy/simulation_engine/policies/rovpp/v2/base/rovpp_v2_lite.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v2/base/rovpp_v2_lite.py)V1 + selective blackhole propagation to customers`ROVPPV1LiteFull`[bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite_full.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite_full.py)V1 + withdrawals + RIBs`ROVPPV2LiteFull`[bgpy/simulation_engine/policies/rovpp/v2/base/rovpp_v2_lite_full.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v2/base/rovpp_v2_lite_full.py)V2 + withdrawals + RIBs
**Key Mechanism:** When an AS receives an ROA-invalid subprefix from a neighbor, it creates a "blackhole" announcement for that subprefix with the AS itself as origin. This prevents traffic from following the invalid path.

**ROV++V1 Behavior**[bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py20-30](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py#L20-L30):

- Blackholes are NOT propagated to any neighbors
- Local protection only

**ROV++V2 Behavior**[bgpy/simulation_engine/policies/rovpp/v2/base/rovpp_v2_lite.py22-65](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v2/base/rovpp_v2_lite.py#L22-L65):

- Blackholes propagated to customers if received from peer/provider
- Provides downstream protection

**Defense Against:**

- Non-routed prefix superprefix attacks (AS 0 ROAs)
- Subprefix hijacks with invalid origin
- Some path manipulation attacks

**Details:** See [ROV++ Policies](/blcrdbob3/bgpy_pkg/6.3-rov++-policies)

Sources: [bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py1-159](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py#L1-L159)[bgpy/simulation_engine/policies/rovpp/v2/base/rovpp_v2_lite.py1-66](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v2/base/rovpp_v2_lite.py#L1-L66)

### ASPA Policy Family

The ASPA (AS Path Attestation) family validates the AS path relationships using ASPA objects that specify authorized provider-to-customer relationships.
PolicyDefense Mechanism`ASPA`Validates AS path against ASPA records`ASRA`ASPA + detects fake links in path`ASPAwN`ASPA + validates neighbor relationships
**Defense Against:**

- Path manipulation attacks (shortest path, forged origin)
- First ASN stripping attacks
- Path forgery

**Requires:**

- ASPA records specifying provider-customer relationships
- Often combined with Enforce-First-AS

**Details:** See [ASPA Policy Family](/blcrdbob3/bgpy_pkg/6.4-aspa-policy-family)

Note: ASPA policy implementations not shown in provided files but referenced in system diagrams.

### Other Security Policies
PolicyFileMechanism`BGPSec`[bgpy/simulation_engine/policies/bgpsec/bgpsec.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgpsec/bgpsec.py)Cryptographic path signatures, security-third preference`BGPSecFull`[bgpy/simulation_engine/policies/bgpsec/bgpsec_full.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgpsec/bgpsec_full.py)BGPSec + withdrawals + RIBs`EnforceFirstAS`[bgpy/simulation_engine/policies/enforce_first_as/](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/enforce_first_as/)Validates first ASN is a neighbor`EdgeFilter`[bgpy/simulation_engine/policies/edge_filter/](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/edge_filter/)Edge ASes filter paths with unauthorized ASNs`PathEnd`Not in provided filesPath-end validation`BGP-iSec`Not in provided filesTransitive security attributes
**BGPSec Features:**

- Maintains `bgpsec_as_path` with cryptographic signatures
- Validates via `bgpsec_valid(ann, asn)` - checks `bgpsec_next_asn == asn` and `bgpsec_as_path == as_path`
- Clears BGPSec fields when propagating to non-BGPSec neighbors
- Adds security as third tie-breaker in Gao-Rexford

**Details:** See [Other Security Policies](/blcrdbob3/bgpy_pkg/6.5-other-security-policies)

Sources: [bgpy/simulation_engine/policies/bgpsec/bgpsec.py1-140](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgpsec/bgpsec.py#L1-L140)[bgpy/simulation_engine/policies/bgpsec/bgpsec_full.py1-10](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgpsec/bgpsec_full.py#L1-L10)

---

## Policy Selection Guide

### By Attack Scenario
Attack TypeMinimum DefenseStrong DefenseStrongest Defense**Prefix Hijack**`ROV``ROV++V2``BGPSec`**Subprefix Hijack**`ROV` (w/ max-length)`ROV++V2``BGPSec`**Forged Origin Prefix Hijack**`ASPA``ASRA``BGPSec`**Shortest Path Hijack**`ASPA``ASRA``BGPSec`**First ASN Stripping**`EnforceFirstAS``ASPA` + `EnforceFirstAS``BGPSec`**Non-Routed Prefix Attacks**`ROV++V1``ROV++V2``BGPSec`**Route Leaks**`ROV++V2``ASPA``BGPSec`
### By Deployment Complexity

**Easy to Deploy (Real-world Ready):**

- `ROV` - Only requires RPKI ROA database
- `PeerROV` - Common real-world partial deployment
- `EnforceFirstAS` - Simple neighbor validation

**Moderate Complexity:**

- `ROV++V1`, `ROV++V2` - Requires ROA database + local blackhole logic
- `ASPA` family - Requires ASPA records + validation logic

**High Complexity (Research/Future):**

- `BGPSec` - Requires cryptographic infrastructure, significant overhead
- `PathEnd` - Requires path-end validation infrastructure
- `BGP-iSec` - Requires transitive attribute support

### By Performance Requirements

**Lightweight (use for large-scale simulations):**

- `BGP` - Minimal overhead, no RIBs
- `ROV` - Adds only ROA lookup per announcement
- `PeerROV` - Even lighter, fewer ROA lookups

**Moderate (standard simulations):**

- `BGPFull` - Adds RIBsIn/RIBsOut tracking
- `ROV++V1/V2` - Adds blackhole creation logic
- `ROVFull` - Full RIBs + ROA validation

**Heavy (detailed analysis):**

- `BGPSec` - Cryptographic signature tracking
- `ASPA` family - Complex path validation

### Combining Policies for Scenarios

For simulation studies, typical combinations include:

**Baseline Study:**

- `BasePolicyCls=BGP`
- `AdoptPolicyCls=ROV`

**Advanced Security Study:**

- `BasePolicyCls=ROV`
- `AdoptPolicyCls=ROVPPV2Lite` or `ASPA`

**Withdrawal Analysis:**

- `BasePolicyCls=BGPFull`
- `AdoptPolicyCls=ROVFull` or `ROVPPV2LiteFull`

Configure via `ScenarioConfig` [bgpy/simulation_framework]:

```
ScenarioConfig(
    ScenarioCls=SubprefixHijack,
    BasePolicyCls=BGP,           # Non-adopting ASes use this
    AdoptPolicyCls=ROV,          # Adopting ASes use this
    AnnCls=Announcement
)
```

Sources: [bgpy/tests/framework_tests/unit_tests/test_scenario.py20-36](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/framework_tests/unit_tests/test_scenario.py#L20-L36)

---

## Extending Policies

To create custom policies, subclass an existing policy and override specific methods:

**Example: Custom Validation Policy**

```
class MyCustomROV(ROV):
    name = "My Custom ROV"
    
    def _valid_ann(self, ann: "Ann", recv_rel: "Relationships") -> bool:
        # Add custom validation logic
        if self.my_custom_check(ann):
            return super()._valid_ann(ann, recv_rel)
        return False
```

**Common Extension Points:**

- `_valid_ann()` - Customize announcement validation
- `_copy_and_process()` - Modify announcement processing
- `_policy_propagate()` - Customize propagation behavior
- `_get_best_ann_by_gao_rexford()` - Modify route selection

For complete guide, see [Creating Custom Policies](/blcrdbob3/bgpy_pkg/10.2-creating-custom-policies).

Sources: [bgpy/simulation_engine/policies/policy.py14-167](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/policy.py#L14-L167)

---

## Summary

BGPy's policy system provides a flexible, extensible framework for simulating BGP security mechanisms. The key design principles are:

1. **Layered Inheritance** - Policies build on each other (BGP → ROV → ROV++ → etc.)
2. **Pluggable Validation** - Override `_valid_ann()` to add security checks
3. **Customizable Propagation** - Override `_policy_propagate()` for custom routing behavior
4. **Multiple Implementations** - "Lite" versions for speed, "Full" versions for detailed analysis

The policy abstraction allows researchers to:

- Compare security mechanisms fairly under identical conditions
- Study partial deployment scenarios by mixing policy types
- Prototype new security proposals by extending existing policies
- Analyze real-world deployment challenges

For implementation details of specific policy categories, see the subsections:

- [Base BGP Policies](/blcrdbob3/bgpy_pkg/6.1-base-bgp-policies)
- [Route Origin Validation](/blcrdbob3/bgpy_pkg/6.2-route-origin-validation-(rov))
- [ROV++ Policies](/blcrdbob3/bgpy_pkg/6.3-rov++-policies)
- [ASPA Policy Family](/blcrdbob3/bgpy_pkg/6.4-aspa-policy-family)
- [Other Security Policies](/blcrdbob3/bgpy_pkg/6.5-other-security-policies)