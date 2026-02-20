# Route Origin Validation (ROV)
Relevant source files
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

This page documents the Route Origin Validation (ROV) security policy implementation in BGPy. ROV is a BGP security mechanism that validates the origin ASN of route announcements using Route Origin Authorizations (ROAs) from the Resource Public Key Infrastructure (RPKI). This page covers the `ROV` and `PeerROV` policy classes, the ROA validation mechanism, and integration with the simulation framework.

For enhanced ROV variants that include blackholing mechanisms, see [ROV++ Policies](/blcrdbob3/bgpy_pkg/6.3-rov++-policies). For the base BGP policy that ROV extends, see [Base BGP Policies](/blcrdbob3/bgpy_pkg/6.1-base-bgp-policies). For details on how ROAs are generated for scenarios, see [ROA and Announcement Management](/blcrdbob3/bgpy_pkg/10.3-roa-and-announcement-management).

## ROV Policy Overview

ROV extends the basic BGP policy by filtering route announcements that are invalid according to RPKI ROAs. The framework implements two ROV variants:
Policy ClassDescriptionFiltering Scope`ROV`Standard Route Origin ValidationAll neighbors (providers, peers, customers)`PeerROV`ROV for peers onlyPeer relationships only
Both policies inherit from `BGP` and override the `_valid_ann` method to incorporate ROA validation checks into the announcement filtering process.

**Sources:**[bgpy/simulation_engine/policies/rov/rov.py1-29](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rov/rov.py#L1-L29)[bgpy/simulation_engine/policies/rov/peer_rov.py1-33](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rov/peer_rov.py#L1-L33)

## ROV Class Hierarchy

```
Policy.roa_checker

class var

Policy
(Abstract Base)

BGP
process_incoming_anns
valid_ann
propagate_to*

ROV
name='ROV'
_valid_ann

PeerROV
name='PeerROV'
_valid_ann

ROVFull
(not shown)

ROV++ Variants
ROVPPV1Lite
ROVPPV2Lite
(see page 6.3)

ROAChecker
get_roa_outcome_w_prefix_str_cached
get_relevant_roas
```

**Diagram: ROV Policy Class Hierarchy**

This diagram shows how ROV policies extend the base BGP policy and share access to the global `ROAChecker` instance. All policies inherit ROA validation methods from the `Policy` base class.

**Sources:**[bgpy/simulation_engine/policies/rov/rov.py10-28](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rov/rov.py#L10-L28)[bgpy/simulation_engine/policies/rov/peer_rov.py10-32](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rov/peer_rov.py#L10-L32)[bgpy/simulation_engine/policies/policy.py14-167](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/policy.py#L14-L167)

## ROV Implementation

### Standard ROV

The `ROV` class implements full Route Origin Validation by rejecting all announcements that are invalid according to ROAs, regardless of the neighbor relationship.

```
Invalid

Valid or Unknown

Pass BGP checks

Fail BGP checks

Announcement
prefix, origin, as_path

_valid_ann
(ann, recv_rel)

ann_is_invalid_by_roa
(ann)

super()._valid_ann
(ann, recv_rel)

Accept
Return True

Reject
Return False
```

**Diagram: ROV Announcement Validation Flow**

The validation process first checks ROA validity. If the announcement is invalid by ROA, it is immediately rejected. Otherwise, standard BGP validation checks (loop detection, path validation, etc.) are applied.

**Sources:**[bgpy/simulation_engine/policies/rov/rov.py15-28](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rov/rov.py#L15-L28)

#### Code Implementation

The `ROV._valid_ann` method override is straightforward:

[bgpy/simulation_engine/policies/rov/rov.py15-28](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rov/rov.py#L15-L28)

The method leverages the `ann_is_invalid_by_roa` helper method inherited from the `Policy` base class to determine ROA validity.

### PeerROV

The `PeerROV` class implements a more selective variant of ROV that only filters invalid announcements received from peer relationships. This reflects real-world deployment patterns where operators may be more cautious about filtering routes from customers or providers.

[bgpy/simulation_engine/policies/rov/peer_rov.py15-32](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rov/peer_rov.py#L15-L32)

The key difference is the additional check: `ann.recv_relationship == Relationships.PEERS`. Invalid announcements from customers or providers are still processed using standard BGP validation.

**Sources:**[bgpy/simulation_engine/policies/rov/peer_rov.py1-33](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rov/peer_rov.py#L1-L33)

## ROA Validation Mechanism

### ROAChecker Class

All policies in BGPy share a single global `ROAChecker` instance defined as a class variable on the `Policy` base class:

[bgpy/simulation_engine/policies/policy.py18-19](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/policy.py#L18-L19)

The `ROAChecker` is provided by the external `roa_checker` library and simulates a globally available RPKI validator (similar to Routinator or FORT Validator in real deployments).

### ROA Validation Methods

The `Policy` base class provides several methods for ROA validation:
MethodReturn TypePurpose`get_roa_outcome(ann)``ROAOutcome`Returns full ROA outcome with validity and routing status`ann_is_invalid_by_roa(ann)``bool`True if announcement is ROA-invalid`ann_is_valid_by_roa(ann)``bool`True if announcement is ROA-valid`ann_is_unknown_by_roa(ann)``bool`True if no ROA covers the prefix`ann_is_covered_by_roa(ann)``bool`True if any ROA covers the prefix`ann_is_roa_non_routed(ann)``bool`True if covered by a non-routed ROA (origin AS 0)
**Sources:**[bgpy/simulation_engine/policies/policy.py99-154](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/policy.py#L99-L154)

### ROA Validation States

```
Announcement
(prefix, origin)

roa_checker.get_roa_outcome_w_prefix_str_cached
(prefix, origin)

VALID
Prefix and origin match ROA
ann_is_valid_by_roa = True

INVALID
Covered by ROA but origin/length mismatch
ann_is_invalid_by_roa = True

UNKNOWN
No ROA covers prefix
ann_is_unknown_by_roa = True

Accepted by ROV
(passes ROV check)

Rejected by ROV
(fails ROV check)

Accepted by ROV
(passes ROV check)
```

**Diagram: ROA Validation States and Outcomes**

An announcement can be in one of three ROA validity states. Only announcements in the INVALID state are rejected by ROV. Valid and Unknown announcements both pass the ROV check.

**Sources:**[bgpy/simulation_engine/policies/policy.py104-133](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/policy.py#L104-L133)

### Cached Validation

The `ROAChecker` uses a cached validation method `get_roa_outcome_w_prefix_str_cached` to avoid redundant lookups during simulation. This is critical for performance since the same prefix-origin pairs are validated repeatedly across the AS graph.

[bgpy/simulation_engine/policies/policy.py99-102](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/policy.py#L99-L102)

**Sources:**[bgpy/simulation_engine/policies/policy.py99-154](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/policy.py#L99-L154)

## Integration with Scenarios

### ROA Generation

Scenarios generate ROAs during initialization by calling `Scenario._add_roa_info_to_anns`. ROAs are stored globally in the `ROAChecker` instance and remain available throughout the simulation.

The test file demonstrates ROA usage:

[bgpy/tests/framework_tests/unit_tests/test_scenario.py279-324](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/framework_tests/unit_tests/test_scenario.py#L279-L324)

In this example:

- A ROA is created for prefix `1.2.0.0/16` with origin `victim`
- The victim's announcement for `1.2.0.0/16` is validated as `VALID`
- The attacker's announcement for the more specific `1.2.0.0/24` is validated as `INVALID` (wrong origin)

**Sources:**[bgpy/tests/framework_tests/unit_tests/test_scenario.py279-324](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/framework_tests/unit_tests/test_scenario.py#L279-L324)

### Announcement Validation Example

```
ROV Processing

Scenario Setup

Generate ROAs
ROA(1.2.0.0/16, origin=victim)

Generate Announcements
Victim: 1.2.0.0/16
Attacker: 1.2.0.0/24

Announcement
prefix=1.2.0.0/16
origin=victim

Announcement
prefix=1.2.0.0/24
origin=attacker

ROV._valid_ann
ann_is_invalid_by_roa

ROV._valid_ann
ann_is_invalid_by_roa

VALID
Exact match

INVALID_ORIGIN
Wrong origin for subprefix

Accepted
Propagated

Rejected
Dropped
```

**Diagram: ROA Validation in Subprefix Hijack Scenario**

This shows how ROV handles a typical subprefix hijack attack. The victim's legitimate announcement passes validation, while the attacker's more specific announcement is rejected due to origin mismatch.

**Sources:**[bgpy/tests/framework_tests/unit_tests/test_scenario.py286-324](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/framework_tests/unit_tests/test_scenario.py#L286-L324)

## ROV Extensions and Variants

Several other policies in the framework build upon ROV:
Policy ClassDescriptionReference`ROVEnforceFirstAS`ROV + First-AS enforcement[bgpy/simulation_engine/policies/enforce_first_as/rov_enforce_first_as.py1-27](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/enforce_first_as/rov_enforce_first_as.py#L1-L27)`ROVEdgeFilter`ROV + Edge AS filtering[bgpy/simulation_engine/policies/edge_filter/rov_edge_filter.py1-23](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/edge_filter/rov_edge_filter.py#L1-L23)`ROVPPV1Lite`ROV + blackholing (V1)See [ROV++ Policies](/blcrdbob3/bgpy_pkg/6.3-rov++-policies)`ROVPPV2Lite`ROV + selective propagation (V2)See [ROV++ Policies](/blcrdbob3/bgpy_pkg/6.3-rov++-policies)
These variants extend ROV by adding additional validation checks while preserving the core ROA validation logic.

**Sources:**[bgpy/simulation_engine/policies/enforce_first_as/rov_enforce_first_as.py1-27](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/enforce_first_as/rov_enforce_first_as.py#L1-L27)[bgpy/simulation_engine/policies/edge_filter/rov_edge_filter.py1-23](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/edge_filter/rov_edge_filter.py#L1-L23)

## Non-Routed ROAs

ROV also supports non-routed ROAs (ROAs with origin AS 0), which are used to explicitly mark prefixes as not meant for routing. The `Policy.ann_is_roa_non_routed` method checks for this condition:

[bgpy/simulation_engine/policies/policy.py139-153](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/policy.py#L139-L153)

Non-routed ROAs are particularly important for ROV++ policies, which create blackhole announcements for these prefixes. See [ROV++ Policies](/blcrdbob3/bgpy_pkg/6.3-rov++-policies) for details.

**Sources:**[bgpy/simulation_engine/policies/policy.py139-153](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/policy.py#L139-L153)[bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py70-89](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py#L70-L89)

## Key Characteristics

### Deployment Semantics

- **Standard ROV**: Filters invalid announcements from all neighbors
- **PeerROV**: Filters invalid announcements only from peers, reflecting conservative real-world deployment patterns
- **Invalid-by-default**: Unknown (not covered by any ROA) announcements are treated as valid, following IETF RFC 6811 semantics

### Performance Considerations

- Uses cached ROA lookups via `get_roa_outcome_w_prefix_str_cached`
- Global `ROAChecker` instance shared across all ASes avoids redundant ROA storage
- Validation occurs during the `_valid_ann` check before announcements enter the local RIB

### Limitations

- Does not protect against path manipulation attacks (see [ASPA Policy Family](/blcrdbob3/bgpy_pkg/6.4-aspa-policy-family))
- Cannot detect forged origin attacks where the attacker uses the legitimate origin ASN
- Requires ROA coverage for prefixes to be effective (unknown prefixes pass validation)

**Sources:**[bgpy/simulation_engine/policies/rov/rov.py1-29](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rov/rov.py#L1-L29)[bgpy/simulation_engine/policies/rov/peer_rov.py1-33](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rov/peer_rov.py#L1-L33)[bgpy/simulation_engine/policies/policy.py99-154](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/policy.py#L99-L154)