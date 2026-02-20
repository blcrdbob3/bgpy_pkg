# BGP Policies Overview
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

This page introduces the **Policy abstraction** in BGPy, which models how Autonomous Systems (ASes) process and propagate BGP announcements. Policies represent different BGP implementations ranging from basic BGP routing to advanced security mechanisms like ROV, ASPA, and BGPSec. This overview covers the policy architecture, core operations, and how policies integrate with the simulation framework.

For detailed implementation of specific policies, see [BGP Policy Reference](/blcrdbob3/bgpy_pkg/6-bgp-policy-reference). For information on how policies are assigned in simulations, see [Scenario Configuration](/blcrdbob3/bgpy_pkg/4.2-scenario-configuration). For the network topology that policies operate on, see [AS Graphs and Network Topology](/blcrdbob3/bgpy_pkg/3.2-as-graphs-and-network-topology).

---

## Policy Abstraction

The `Policy` class defines the abstract interface that all BGP implementations must satisfy. Each AS in the network is assigned a policy instance that determines how it handles announcements.

### The Policy Base Class

All policies inherit from `Policy`[bgpy/simulation_engine/policies/policy.py14](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/policy.py#L14-L14) which provides:
ComponentPurpose**Abstract Methods**`receive_ann()`, `process_incoming_anns()`, `propagate_to_providers()`, `propagate_to_customers()`, `propagate_to_peers()`**ROA Validation**`ann_is_valid_by_roa()`, `ann_is_invalid_by_roa()`, `ann_is_unknown_by_roa()`, `get_roa_outcome()`**Class Registry**`subclass_to_name_dict`, `name_to_subclass_dict` for policy lookup by name**ROA Checker**Shared `ROAChecker` instance for RPKI validation [bgpy/simulation_engine/policies/policy.py19](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/policy.py#L19-L19)
```
Policy Base Class

Policy (Abstract)
policy.py:14

Abstract Methods
receive_ann()
process_incoming_anns()
propagate_to_providers()
propagate_to_customers()
propagate_to_peers()

ROA Validation
ann_is_valid_by_roa()
ann_is_invalid_by_roa()
ann_is_unknown_by_roa()
get_roa_outcome()

ROAChecker
policy.py:19
Shared RPKI validator

Class Registry
subclass_to_name_dict
name_to_subclass_dict
```

**Sources:**[bgpy/simulation_engine/policies/policy.py1-167](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/policy.py#L1-L167)

### Policy Lifecycle in Simulation

Each policy instance is bound to an AS and participates in the announcement propagation rounds:

```
RecvQueue
LocalRIB
Policy Instance
AS Instance
SimulationEngine
RecvQueue
LocalRIB
Policy Instance
AS Instance
SimulationEngine
Round 0: Seed Announcements
Round N: Process from Providers
Propagate to Customers
seed_ann(announcement)
seed_ann(announcement)
add_ann(announcement)
process_incoming_anns(from_rel=PROVIDERS)
process_incoming_anns(from_rel=PROVIDERS)
get announcements
_valid_ann() for each ann
_get_best_ann_by_gao_rexford()
add_ann(best_ann)
propagate_to_customers()
propagate_to_customers()
get announcements
_process_outgoing_ann()
Send to neighbor AS
```

**Sources:**[bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py33-61](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py#L33-L61)[bgpy/simulation_engine/policies/bgp/bgp/propagate_funcs.py1-100](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/propagate_funcs.py#L1-L100)

---

## Policy Hierarchy

BGPy implements a hierarchy of policies, from basic BGP to advanced security mechanisms. The hierarchy follows a pattern where more advanced policies extend simpler ones.

### Policy Class Structure

```
Policy (Abstract)
policy.py

BGP
bgp/bgp/bgp.py

BGPFull
bgp/bgp_full.py

ROV
rov/rov.py

PeerROV
rov/peer_rov.py

ROVPPV1Lite
rovpp/v1/rovpp_v1_lite.py

ROVPPV2Lite
rovpp/v2/base/rovpp_v2_lite.py

ASPA
aspa/aspa.py

BGPSec
bgpsec/bgpsec.py

EdgeFilter
edge_filter/edge_filter.py

EnforceFirstAS
enforce_first_as/enforce_first_as.py

ROVEdgeFilter
edge_filter/rov_edge_filter.py

ROVEnforceFirstAS
enforce_first_as/rov_enforce_first_as.py
```

**Sources:**[bgpy/simulation_engine/policies/bgp/bgp/bgp.py43](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/bgp.py#L43-L43)[bgpy/simulation_engine/policies/bgp/bgp_full.py14](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp_full.py#L14-L14)[bgpy/simulation_engine/policies/rov/rov.py10](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rov/rov.py#L10-L10)[bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py12](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py#L12-L12)[bgpy/simulation_engine/policies/bgpsec/bgpsec.py12](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgpsec/bgpsec.py#L12-L12)

### Policy Categories
CategoryPoliciesPrimary Defense**Base Routing**`BGP`, `BGPFull`None - standard routing**Origin Validation**`ROV`, `PeerROV`Prefix hijacks with invalid origin**Enhanced Origin**`ROVPPV1Lite`, `ROVPPV2Lite`Subprefix hijacks via blackholing**Path Validation**`ASPA`, `ASRA`, `ASPAwN`Path manipulation attacks**Cryptographic**`BGPSec`, `BGPiSec`Forged path segments**Edge Filtering**`EdgeFilter`, `EnforceFirstAS`First-hop attacks
**Sources:**[bgpy/simulation_engine/policies/rov/rov.py10-28](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rov/rov.py#L10-L28)[bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py12-159](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py#L12-L159)[bgpy/simulation_engine/policies/bgpsec/bgpsec.py12-140](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgpsec/bgpsec.py#L12-L140)

---

## Core Policy Operations

Policies implement three main operations: receiving announcements, processing them, and propagating results.

### Processing Incoming Announcements

The `process_incoming_anns()` method is the core of policy logic:

```
Valid

Invalid

process_incoming_anns()
from_rel: Relationships
propagation_round: int

Iterate recv_q
Get ann_list for each prefix

Get current local_rib ann
for this prefix

For each new_ann:
_valid_ann(new_ann, from_rel)

_copy_and_process(new_ann)
Prepend AS to path
Set recv_relationship

Skip this announcement

_get_best_ann_by_gao_rexford()
Compare with current_ann

Update local_rib
if new best found

_reset_q()
Clear recv_q
```

**Implementation Details:**

The `BGP` class implements this at [bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py33-61](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py#L33-L61):

```
# Core loop: For each prefix with incoming announcements
for prefix, ann_list in self.recv_q.items():
    current_ann = self.local_rib.get(prefix)
    
    for new_ann in ann_list:
        # Validate (loop prevention, ROA validation for ROV policies)
        if self._valid_ann(new_ann, from_rel):
            # Process: prepend ASN, set relationships
            processed_ann = self._copy_and_process(new_ann, from_rel)
            # Select best via Gao-Rexford
            current_ann = self._get_best_ann_by_gao_rexford(current_ann, processed_ann)
    
    # Update local RIB if best changed
    if current_ann != original:
        self.local_rib.add_ann(current_ann)
```

**Sources:**[bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py33-61](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py#L33-L61)[bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py63-81](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py#L63-L81)

### Validation Logic (_valid_ann)

Each policy overrides `_valid_ann()` to implement specific filtering:
PolicyValidation LogicImplementation`BGP`Loop prevention only: `asn not in as_path and 0 not in as_path`[process_incoming_funcs.py83-93](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/process_incoming_funcs.py#L83-L93)`ROV`Reject if `ann_is_invalid_by_roa()`, else call `super()._valid_ann()`[rov.py15-28](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/rov.py#L15-L28)`PeerROV`Reject invalid ROAs only from peers[peer_rov.py15-32](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/peer_rov.py#L15-L32)`EnforceFirstAS`Check first ASN in path is neighbor[enforce_first_as.py1-27](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/enforce_first_as.py#L1-L27)`BGPSec`Verify cryptographic path (`bgpsec_as_path == as_path`)[bgpsec.py36-38](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpsec.py#L36-L38)
**Sources:**[bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py83-93](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py#L83-L93)[bgpy/simulation_engine/policies/rov/rov.py15-28](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rov/rov.py#L15-L28)[bgpy/simulation_engine/policies/rov/peer_rov.py15-32](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rov/peer_rov.py#L15-L32)

### Gao-Rexford Decision Process

All policies use Gao-Rexford routing to select the best announcement:

```
Tie

Winner

Tie

Winner

Tie

Winner

Current Ann vs New Ann

1. Local Preference
Customer > Peer > Provider
2. AS Path Length
Shorter path wins
3. Security Metric
(BGPSec only)
Valid > Invalid
4. Lowest Neighbor ASN
Deterministic tiebreaker

Return Winning Ann
```

The decision process is implemented at [bgpy/simulation_engine/policies/bgp/bgp/gao_rexford.py1-100](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/gao_rexford.py#L1-L100) with methods:

- `_get_best_ann_by_local_pref()` - Compare by recv_relationship
- `_get_best_ann_by_as_path()` - Compare path length
- `_get_best_ann_by_lowest_neighbor_asn_tiebreaker()` - Final tiebreaker

**Sources:**[bgpy/simulation_engine/policies/bgp/bgp/bgp.py83-89](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/bgp.py#L83-L89)[bgpy/simulation_engine/policies/bgpsec/bgpsec.py103-140](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgpsec/bgpsec.py#L103-L140)

### Propagation to Neighbors

Policies propagate announcements following valley-free routing:

```
Propagate To

LocalRIB

recv_relationship:
ORIGIN

recv_relationship:
CUSTOMERS

recv_relationship:
PEERS

recv_relationship:
PROVIDERS

Providers

Peers

Customers
```

Implementation at [bgpy/simulation_engine/policies/bgp/bgp/propagate_funcs.py1-100](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/propagate_funcs.py#L1-L100):

```
def propagate_to_providers(self):
    """Send announcements with recv_rel of ORIGIN or CUSTOMERS"""
    send_rels = {Relationships.ORIGIN, Relationships.CUSTOMERS}
    self._propagate(Relationships.PROVIDERS, send_rels)

def propagate_to_peers(self):
    """Send announcements with recv_rel of ORIGIN or CUSTOMERS"""
    send_rels = {Relationships.ORIGIN, Relationships.CUSTOMERS}
    self._propagate(Relationships.PEERS, send_rels)

def propagate_to_customers(self):
    """Send all announcements"""
    send_rels = set(Relationships)
    self._propagate(Relationships.CUSTOMERS, send_rels)
```

**Sources:**[bgpy/simulation_engine/policies/bgp/bgp/propagate_funcs.py1-100](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/propagate_funcs.py#L1-L100)

---

## Policy Data Structures

Policies maintain state using specialized containers:

### Core Data Structures

```
Used By

Policy State

LocalRIB
ann_containers/local_rib.py
prefix → Announcement
Current best route per prefix

RecvQueue
ann_containers/recv_queue.py
prefix → List[Announcement]
Incoming anns this round

RIBsIn
ann_containers/ribs_in.py
neighbor_asn → prefix → AnnInfo
Unprocessed anns from neighbors

RIBsOut
ann_containers/ribs_out.py
neighbor_asn → prefix → Announcement
Sent anns to neighbors

BGP
local_rib + recv_q

BGPFull
+ ribs_in + ribs_out
```
StructurePurposeKey Operations`LocalRIB`Stores current best announcement per prefix`add_ann()`, `get(prefix)`, `items()``RecvQueue`Buffers incoming announcements for processing`add_ann()`, `items()`, `get_ann_list(prefix)``RIBsIn`Tracks unprocessed announcements from each neighbor (BGPFull only)`add_unprocessed_ann()`, `get_ann_infos()`, `remove_entry()``RIBsOut`Records what was sent to each neighbor for withdrawals (BGPFull only)`add_ann()`, `get_ann()`, `remove_entry()`
**Sources:**[bgpy/simulation_engine/policies/bgp/bgp/bgp.py46-64](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/bgp.py#L46-L64)[bgpy/simulation_engine/policies/bgp/bgp_full.py17-27](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp_full.py#L17-L27)[bgpy/simulation_engine/ann_containers/ribs_in.py28-87](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/ann_containers/ribs_in.py#L28-L87)

---

## Policy Variants: Lite vs Full

Most security policies come in two variants:

### Lite vs Full Comparison

```
Examples

Full Policies

Lite Policies

Inherit from BGP
local_rib + recv_q only

Features:
✓ Core security logic
✓ Fast simulation
✗ No withdrawals
✗ No RIBs tracking

Inherit from BGPFull
+ ribs_in + ribs_out

Features:
✓ Core security logic
✓ Withdrawal support
✓ RIBs tracking
✗ Slower (more state)

ROVPPV1Lite

ROVPPV1LiteFull

BGPSec

BGPSecFull
```
AspectLiteFull**Base Class**`BGP` (or security variant)Multiple inheritance with `BGPFull`**State**`local_rib`, `recv_q`+ `ribs_in`, `ribs_out`**Withdrawals**Not supportedFull support via `withdraw_ann_from_neighbors()`**RIB Tracking**Only current best routeTracks all received and sent routes**Use Case**Most simulationsScenarios requiring withdrawals**Performance**FasterSlower due to additional bookkeeping
**Example:**`ROVPPV1LiteFull` at [bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite_full.py11](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite_full.py#L11-L11) uses multiple inheritance:

```
class ROVPPV1LiteFull(ROVPPV1Lite, ROVFull):
    """Combines ROV++ logic with BGPFull withdrawal support"""
```

**Sources:**[bgpy/simulation_engine/policies/bgp/bgp_full.py14-209](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp_full.py#L14-L209)[bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite_full.py11-37](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite_full.py#L11-L37)[bgpy/simulation_engine/policies/bgpsec/bgpsec_full.py6-9](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgpsec/bgpsec_full.py#L6-L9)

---

## Policy-Announcement Interaction

Policies interact with `Announcement` objects which carry both routing and security information:

### Announcement Attributes Used by Policies

```
Policy Usage

Announcement Fields

Core Attributes
prefix: str
as_path: tuple[int, ...]
next_hop_asn: int
recv_relationship: Relationships

Optional Attributes
withdraw: bool (BGPFull)
timestamp: int
seed_asn: int

Security Attributes
bgpsec_next_asn: int (BGPSec)
bgpsec_as_path: tuple (BGPSec)
only_to_customers: int (OTC)
rovpp_blackhole: bool (ROV++)

BGP:
prefix, as_path
next_hop_asn
recv_relationship

BGPFull:
+ withdraw

ROVPP:
+ rovpp_blackhole

BGPSec:
+ bgpsec_next_asn
+ bgpsec_as_path
```

**Key Announcement Operations:**

1. **Validation** - Policy checks announcement attributes:

```
def _valid_ann(self, ann: Ann, from_rel: Relationships) -> bool:
    # BGP: Loop prevention
    return self.as_.asn not in ann.as_path and 0 not in ann.as_path
```
2. **Processing** - Policy modifies announcement when accepting:

```
def _copy_and_process(self, ann: Ann, recv_relationship: Relationships) -> Ann:
    # Prepend ASN to path, set recv_relationship
    return ann.copy({
        "as_path": (self.as_.asn, *ann.as_path),
        "recv_relationship": recv_relationship
    })
```
3. **Propagation** - Policy modifies announcement when forwarding:

```
# BGPSec sets cryptographic fields
send_ann = ann.copy({
    "bgpsec_next_asn": neighbor.asn,
    "bgpsec_as_path": ann.bgpsec_as_path
})
```

**Sources:**[bgpy/simulation_engine/announcement.py10-143](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/announcement.py#L10-L143)[bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py95-116](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py#L95-L116)[bgpy/simulation_engine/policies/bgpsec/bgpsec.py40-62](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgpsec/bgpsec.py#L40-L62)

---

## ROA Integration

All security policies integrate with RPKI Route Origin Authorizations (ROAs) through the shared `ROAChecker`:

### ROA Validation Flow

```
ROAs
ROAChecker
Policy
ROAs
ROAChecker
Policy
ann_is_valid_by_roa(ann)
get_roa_outcome_w_prefix_str_cached(prefix, origin)
get_relevant_roas(prefix)
List[ROA]
Check prefix/origin match
ROAOutcome(validity)
ROAValidity.is_valid(outcome.validity)
```

### ROA Validation Methods
MethodReturnsPurpose`ann_is_valid_by_roa(ann)``bool`True if origin matches ROA`ann_is_invalid_by_roa(ann)``bool`True if origin mismatches ROA`ann_is_unknown_by_roa(ann)``bool`True if no ROA exists`ann_is_covered_by_roa(ann)``bool`True if any ROA exists`ann_is_roa_non_routed(ann)``bool`True if ROA has origin AS 0`get_roa_outcome(ann)``ROAOutcome`Full ROA validation result
**ROAOutcome Structure:**

- `validity`: `VALID`, `INVALID_ORIGIN`, `INVALID_LENGTH`, `INVALID_LENGTH_AND_ORIGIN`, `UNKNOWN`
- `routed_status`: `ROUTED`, `NON_ROUTED`

**Example Usage in ROV:**

```
def _valid_ann(self, ann: Ann, recv_rel: Relationships) -> bool:
    if self.ann_is_invalid_by_roa(ann):
        return False  # Drop invalid announcements
    else:
        return super()._valid_ann(ann, recv_rel)
```

**Sources:**[bgpy/simulation_engine/policies/policy.py99-154](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/policy.py#L99-L154)[bgpy/simulation_engine/policies/rov/rov.py15-28](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rov/rov.py#L15-L28)

---

## Policy Assignment in Simulations

Policies are assigned to ASes via `ScenarioConfig`:

```
scenario_config = ScenarioConfig(
    ScenarioCls=SubprefixHijack,
    BasePolicyCls=BGP,           # Non-adopting ASes
    AdoptPolicyCls=ROV,          # Adopting ASes
    percent_adoptions=[0.0, 0.1, 0.5, 1.0]
)
```

The simulation assigns policies based on:

1. **Default adopters** - Victims typically adopt the security policy
2. **Default non-adopters** - Attackers typically don't adopt
3. **Random adoption** - Other ASes randomly adopt based on `percent_adoptions`
4. **Override adoption** - Can specify exact ASNs via `override_adopting_asns`

For details on policy assignment mechanics, see [Scenario Configuration](/blcrdbob3/bgpy_pkg/4.2-scenario-configuration).

**Sources:**[bgpy/tests/framework_tests/unit_tests/test_scenario.py21-36](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/framework_tests/unit_tests/test_scenario.py#L21-L36)[bgpy/tests/framework_tests/unit_tests/test_scenario.py60-65](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/framework_tests/unit_tests/test_scenario.py#L60-L65)

---

## Advanced Policy Features

### Custom Propagation Logic (_policy_propagate)

Policies can override `_policy_propagate()` to implement custom propagation behavior:

```
def _policy_propagate(
    self,
    neighbor: AS,
    ann: Ann,
    propagate_to: Relationships,
    send_rels: set[Relationships]
) -> bool:
    """Return True if policy handled propagation, False otherwise"""
```

**Examples:**

- `ROVPPV1Lite`: Prevents blackhole announcement propagation [rovpp_v1_lite.py20-30](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/rovpp_v1_lite.py#L20-L30)
- `ROVPPV2Lite`: Allows blackholes only to customers from providers/peers [rovpp_v2_lite.py22-65](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/rovpp_v2_lite.py#L22-L65)
- `BGPSec`: Sets cryptographic path fields [bgpsec.py40-61](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpsec.py#L40-L61)

### Post-Processing Hooks

Scenarios can inject behavior via hooks:

- `post_propagation_hook()` - Called after each propagation round
- Used by `AccidentalRouteLeak` for two-round propagation

**Sources:**[bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py20-30](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py#L20-L30)[bgpy/simulation_engine/policies/bgpsec/bgpsec.py40-61](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgpsec/bgpsec.py#L40-L61)

---

## Summary

BGPy's policy system provides:

1. **Abstraction** - `Policy` base class defines common interface
2. **Hierarchy** - Policies build progressively from BGP to advanced security
3. **Flexibility** - Lite/Full variants balance functionality vs performance
4. **Integration** - ROA validation, announcement processing, Gao-Rexford routing
5. **Extensibility** - Override methods to implement custom security mechanisms

For implementation details of specific policies, see [BGP Policy Reference](/blcrdbob3/bgpy_pkg/6-bgp-policy-reference). For creating custom policies, see [Creating Custom Policies](/blcrdbob3/bgpy_pkg/10.2-creating-custom-policies).