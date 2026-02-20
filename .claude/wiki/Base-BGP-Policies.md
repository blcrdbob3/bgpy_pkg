# Base BGP Policies
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

## Purpose and Scope

This document covers the base BGP policy implementations in BGPy: the `BGP` and `BGPFull` classes. These form the foundation of all BGP routing behavior in the simulation framework. The `BGP` class implements standard BGP route selection and propagation using the Gao-Rexford decision process, while `BGPFull` extends it with comprehensive RIB management and explicit withdrawal handling.

For security-enhanced policies built on top of these base classes (ROV, ASPA, BGPSec, etc.), see sections [6.2](/blcrdbob3/bgpy_pkg/6.2-route-origin-validation-(rov)), [6.3](/blcrdbob3/bgpy_pkg/6.3-rov++-policies), [6.4](/blcrdbob3/bgpy_pkg/6.4-aspa-policy-family), and [6.5](/blcrdbob3/bgpy_pkg/6.5-other-security-policies). For general policy architecture concepts, see [3.3](/blcrdbob3/bgpy_pkg/3.3-bgp-policies-overview).

---

## Policy Class Hierarchy

The base BGP policies follow an inheritance hierarchy that progressively adds functionality:

```
Policy
(Abstract Base)

BGP
bgp/bgp.py

BGPFull
bgp_full.py

LocalRIB
Route Table

RecvQueue
Incoming Announcements

RIBsIn
Per-Neighbor Input RIBs

RIBsOut
Per-Neighbor Output RIBs
```

**Sources:**[bgpy/simulation_engine/policies/bgp/bgp/bgp.py43-64](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/bgp.py#L43-L64)[bgpy/simulation_engine/policies/bgp/bgp_full.py14-26](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp_full.py#L14-L26)

---

## Announcement Data Structure

All route information is represented by the `Announcement` class, an immutable dataclass that holds BGP path attributes:

### Core Fields
FieldTypeDescription`prefix``str`The IP prefix being announced`as_path``tuple[int, ...]`Sequence of ASNs the announcement has traversed`next_hop_asn``int`Next hop for data plane forwarding`seed_asn``int | None`Origin AS that first announced this prefix`recv_relationship``Relationships`Relationship type through which announcement was received`timestamp``int`Timestamp for tie-breaking (default: 0)
### Optional Fields

The `Announcement` class includes optional fields used by specific policy variants:
FieldTypeUsed By`withdraw``bool``BGPFull` for explicit route withdrawals`bgpsec_next_asn``int | None``BGPSec` for cryptographic path validation`bgpsec_as_path``tuple[int, ...]``BGPSec` for secure AS path`only_to_customers``int | None`RFC 9234 OTC attribute`rovpp_blackhole``bool``ROV++` for blackhole signaling
The immutable design ensures announcements cannot be accidentally modified during propagation. New announcements are created using the `copy()` method with updated attributes.

**Sources:**[bgpy/simulation_engine/announcement.py10-73](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/announcement.py#L10-L73)

---

## Announcement Processing Pipeline

The following diagram shows how announcements flow through the BGP policy from reception to propagation:

```
Valid

Invalid

receive_ann()
Add to recv_q

process_incoming_anns()
Process by relationship

_valid_ann()
Loop prevention check

_copy_and_process()
Prepend ASN, set recv_relationship

_get_best_ann_by_gao_rexford()
Route selection

local_rib.add_ann()
Store best route

propagate_to_customers()
propagate_to_peers()
propagate_to_providers()

_process_outgoing_ann()
Send to neighbors

Drop
```

**Sources:**[bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py27-61](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py#L27-L61)[bgpy/simulation_engine/policies/bgp/bgp/propagate_funcs.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/propagate_funcs.py)

---

## BGP Base Class

The `BGP` class implements standard BGP routing behavior with valley-free routing and Gao-Rexford route selection.

### Initialization

```
BGP(
    local_rib: LocalRIB | None = None,
    recv_q: RecvQueue | None = None,
    as_: AS | None = None
)
```

Each `BGP` policy instance maintains:

- **`local_rib`**: The Local Routing Information Base storing the best route per prefix
- **`recv_q`**: A receive queue for incoming announcements, organized by prefix
- **`as_`**: A weak reference to the AS that owns this policy

**Sources:**[bgpy/simulation_engine/policies/bgp/bgp/bgp.py46-63](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/bgp.py#L46-L63)

### Key Methods

#### Receiving Announcements

**`receive_ann(ann: Announcement)`**

Adds an incoming announcement to the receive queue. Announcements accumulate in `recv_q` until `process_incoming_anns()` is called during a propagation round.

**Sources:**[bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py27-30](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py#L27-L30)

#### Processing Announcements

**`process_incoming_anns(from_rel: Relationships, propagation_round: int, scenario: Scenario, reset_q: bool = True)`**

Processes all announcements in the receive queue that came from a specific relationship type. For each prefix:

1. Retrieves the current best announcement from `local_rib`
2. Iterates through all new announcements for that prefix
3. Validates each announcement using `_valid_ann()`
4. Processes valid announcements with `_copy_and_process()`
5. Compares against current best using `_get_best_ann_by_gao_rexford()`
6. Updates `local_rib` if a new best route is found

**Sources:**[bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py33-60](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py#L33-L60)

#### Validation

**`_valid_ann(ann: Announcement, recv_relationship: Relationships) -> bool`**

Validates announcements using BGP loop prevention:

- Rejects announcements containing the AS's own ASN in the path
- Rejects announcements containing AS 0 in the path

**Sources:**[bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py83-92](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py#L83-L92)

#### Processing

**`_copy_and_process(ann: Announcement, recv_relationship: Relationships, overwrite_default_kwargs: dict | None = None) -> Announcement`**

Creates a processed copy of an announcement by:

- Prepending the AS's ASN to the `as_path`
- Setting the `recv_relationship` to reflect how it was received
- Clearing the `seed_asn` (since it's no longer the origin)

**Sources:**[bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py95-115](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py#L95-L115)

#### Propagation

The BGP class includes three main propagation methods that implement valley-free routing:

- **`propagate_to_providers()`**: Propagates only customer-learned routes
- **`propagate_to_peers()`**: Propagates only customer-learned routes
- **`propagate_to_customers()`**: Propagates routes learned from any relationship

These methods internally call `_propagate()` which iterates through announcements in `local_rib` and determines whether to send each announcement to neighbors based on the Gao-Rexford export rules.

**Sources:**[bgpy/simulation_engine/policies/bgp/bgp/propagate_funcs.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/propagate_funcs.py)

---

## Gao-Rexford Decision Process

The `_get_best_ann_by_gao_rexford()` method implements BGP route selection following the Gao-Rexford model, which prioritizes economic relationships:

```
Tie

Winner

Tie

Winner

Compare current_ann vs new_ann

_get_best_ann_by_local_pref()
Prefer customer routes over
peer routes over provider routes

_get_best_ann_by_as_path()
Prefer shorter AS path

_get_best_ann_by_lowest_neighbor_asn_tiebreaker()
Prefer lower neighbor ASN

Return best announcement
```

### Decision Steps

1. **Local Preference**: Routes are ranked by relationship:

- Customer routes (highest preference)
- Peer routes (medium preference)
- Provider routes (lowest preference)
2. **AS Path Length**: Shorter paths are preferred (fewer hops)
3. **Tiebreaker**: If all else is equal, prefer announcements from the neighbor with the lower ASN

This ordering ensures ASes prefer routes that maximize revenue (customer routes) and minimize costs (shorter paths, avoiding provider transit when possible).

**Sources:**[bgpy/simulation_engine/policies/bgp/bgp/gao_rexford.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/gao_rexford.py)

---

## BGPFull Class

`BGPFull` extends `BGP` with comprehensive RIB management and explicit withdrawal handling, matching real-world BGP implementations more closely.

### Additional Data Structures

```
BGPFull(
    ribs_in: RIBsIn | None = None,
    ribs_out: RIBsOut | None = None,
    *args, **kwargs
)
```

- **`ribs_in`**: Stores unprocessed announcements received from each neighbor, organized as `{neighbor_asn: {prefix: AnnInfo}}`
- **`ribs_out`**: Tracks which announcements were sent to each neighbor, organized as `{neighbor_asn: {prefix: Announcement}}`

**Sources:**[bgpy/simulation_engine/policies/bgp/bgp_full.py17-26](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp_full.py#L17-L26)

### Enhanced Processing

The `process_incoming_anns()` method in `BGPFull` differs from `BGP` by:

1. **Maintaining RIBsIn**: Stores or removes announcements in `ribs_in` based on whether they are withdrawals
2. **Handling Withdrawals**: Explicitly removes withdrawn routes from `local_rib` and finds the next best route from `ribs_in`
3. **Validating Withdrawals**: Ensures no implicit withdrawals occur (routes can only be replaced after explicit withdrawal)
4. **Propagating Withdrawals**: When the best route changes, withdraws the old route from neighbors using `withdraw_ann_from_neighbors()`

**Sources:**[bgpy/simulation_engine/policies/bgp/bgp_full.py32-80](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp_full.py#L32-L80)

### Withdrawal Processing

The following diagram shows how `BGPFull` handles route withdrawals:

```
Match

No match

Found

None

Receive withdrawal
withdraw=True

Remove from ribs_in

Check if withdrawal matches
current local_rib entry

Remove from local_rib

_get_and_process_best_ribs_in_ann()
Find next best route in ribs_in

Update local_rib with new best

withdraw_ann_from_neighbors()
Propagate withdrawal

Check ribs_out for
which neighbors received route

Send withdrawal to
affected neighbors

Keep local_rib unchanged

Prefix removed from local_rib
```

**Sources:**[bgpy/simulation_engine/policies/bgp/bgp_full.py97-121](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp_full.py#L97-L121)[bgpy/simulation_engine/policies/bgp/bgp_full.py123-157](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp_full.py#L123-L157)

### RIBsIn Management

The `RIBsIn` container stores unprocessed announcements along with their receive relationships:

```
@dataclass
class AnnInfo:
    unprocessed_ann: Announcement
    recv_relationship: Relationships
```

Key methods:

- **`add_unprocessed_ann(ann, recv_relationship)`**: Stores an announcement from a neighbor
- **`get_ann_infos(prefix)`**: Returns all `AnnInfo` objects for a given prefix
- **`remove_entry(neighbor_asn, prefix)`**: Removes an entry during withdrawal processing

This structure allows `BGPFull` to re-evaluate route selection when withdrawals occur by examining all available routes in `ribs_in`.

**Sources:**[bgpy/simulation_engine/ann_containers/ribs_in.py13-73](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/ann_containers/ribs_in.py#L13-L73)

---

## Data Structures

### LocalRIB

The `LocalRIB` container stores the best route for each prefix. It extends `AnnContainer` and provides:

- **`add_ann(ann)`**: Stores announcement keyed by prefix
- **`get(prefix)`**: Retrieves the best announcement for a prefix
- **`pop(prefix)`**: Removes and returns an announcement

**Sources:**[bgpy/simulation_engine/ann_containers/local_rib.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/ann_containers/local_rib.py)

### RecvQueue

The `RecvQueue` organizes incoming announcements by prefix before processing:

- Structured as `{prefix: [Announcement, ...]}`
- Accumulates announcements from all neighbors during a propagation round
- Cleared after `process_incoming_anns()` completes

**Sources:**[bgpy/simulation_engine/ann_containers/recv_queue.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/ann_containers/recv_queue.py)

### RIBsOut

The `RIBsOut` container tracks which announcements were sent to which neighbors:

- Structured as `{neighbor_asn: {prefix: Announcement}}`
- Used during withdrawal processing to determine which neighbors need to receive withdrawal messages
- Updated when announcements are sent via `_process_outgoing_ann()`

**Sources:**[bgpy/simulation_engine/ann_containers/ribs_out.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/ann_containers/ribs_out.py)

---

## Validation and Error Handling

`BGPFull` includes strict validation to catch protocol violations and development errors:

### Validation Methods
MethodPurposeError Condition`only_one_withdrawal_per_prefix_per_neighbor()`Ensures at most one withdrawal per prefix from each neighborMultiple withdrawals from same neighbor for same prefix`only_one_ann_per_prefix_per_neighbor()`Ensures at most one announcement per prefix from each neighborMultiple announcements from same neighbor for same prefix`no_implicit_withdrawals()`Ensures routes are explicitly withdrawn before replacementNew announcement overwrites existing `ribs_in` entry without withdrawal
These validations are wrapped in assertions that can be disabled with `python -O` for production performance, but are enabled by default to catch bugs during development.

**Sources:**[bgpy/simulation_engine/policies/bgp/bgp_full.py227-262](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp_full.py#L227-L262)

---

## Class Method Reference

### BGP Core Methods
MethodParametersReturnsDescription`seed_ann()``ann: Announcement``None`Seeds an announcement at origin AS`receive_ann()``ann: Announcement``None`Receives announcement into `recv_q``process_incoming_anns()``from_rel: Relationships, propagation_round: int, scenario: Scenario``None`Processes announcements from a specific relationship type`propagate_to_providers()`None`None`Propagates customer routes to providers`propagate_to_peers()`None`None`Propagates customer routes to peers`propagate_to_customers()`None`None`Propagates all routes to customers
**Sources:**[bgpy/simulation_engine/policies/bgp/bgp/bgp.pyi41-82](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/bgp.pyi#L41-L82)

### BGPFull Additional Methods
MethodParametersReturnsDescription`withdraw_ann_from_neighbors()``withdraw_ann: Announcement``None`Propagates withdrawal to all neighbors that received the route`_process_new_ann_in_ribs_in()``unprocessed_ann: Announcement, prefix: str, from_rel: Relationships``None`Adds or removes announcement from `ribs_in``_remove_from_local_rib_and_get_new_best_ann()``new_ann: Announcement, local_rib_ann: Announcement | None``Announcement | None`Handles withdrawal and finds replacement route`_get_and_process_best_ribs_in_ann()``prefix: str``Announcement | None`Selects best route from `ribs_in` after withdrawal
**Sources:**[bgpy/simulation_engine/policies/bgp/bgp_full.py82-169](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp_full.py#L82-L169)

---

## YAML Serialization

Both `BGP` and `BGPFull` support YAML serialization for test fixtures and simulation state persistence:

```
# BGP serialization
def __to_yaml_dict__(self) -> dict:
    return {"local_rib": self.local_rib, "recv_q": self.recv_q}

# BGPFull serialization  
def __to_yaml_dict__(self) -> dict:
    as_dict = super().__to_yaml_dict__()
    as_dict.update({"ribs_in": self.ribs_in, "ribs_out": self.ribs_out})
    return as_dict
```

This enables:

- Ground truth storage for regression testing
- Simulation state snapshots
- Debugging of routing state across propagation rounds

**Sources:**[bgpy/simulation_engine/policies/bgp/bgp/bgp.py115-124](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/bgp.py#L115-L124)[bgpy/simulation_engine/policies/bgp/bgp_full.py203-208](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp_full.py#L203-L208)