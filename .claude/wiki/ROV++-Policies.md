# ROV++ Policies
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

This document describes the ROV++ (Route Origin Validation Plus Plus) policy implementations in BGPy. ROV++ extends basic ROV by adding blackhole announcements to defend against prefix and subprefix hijacks that evade ROV. Two main variants are implemented: ROV++V1 and ROV++V2, each with "Lite" and "Full" versions.

For basic Route Origin Validation without blackholing mechanisms, see [Route Origin Validation (ROV)](/blcrdbob3/bgpy_pkg/6.2-route-origin-validation-(rov)). For information on other security policies like ASPA and BGPSec, see [ASPA Policy Family](/blcrdbob3/bgpy_pkg/6.4-aspa-policy-family) and [Other Security Policies](/blcrdbob3/bgpy_pkg/6.5-other-security-policies).

---

## Overview

ROV++ enhances standard ROV by creating and propagating **blackhole announcements** to defend against hijacks. The key innovation is that ROV++ ASes proactively advertise more-specific prefixes with special blackhole flags to prevent attackers from attracting traffic, even when the attacker's announcement appears valid by ROV.

The policy family includes:

- **ROVPPV1Lite**: Adds blackholes to local RIB but does not propagate them
- **ROVPPV2Lite**: Adds blackholes and selectively propagates them to customers
- **ROVPPV2ImprovedLite**: Enhanced variant of V2 with optimized logic
- **Full variants**: Extended versions with withdrawal support and RIBs In/Out

Sources: [bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py1-159](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py#L1-L159)[bgpy/simulation_engine/policies/rovpp/v2/base/rovpp_v2_lite.py1-66](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v2/base/rovpp_v2_lite.py#L1-L66)

---

## Class Hierarchy

```
Policy
(Abstract Base)

BGP
Basic BGP routing

ROV
Route Origin Validation

ROVFull
+Withdrawals +RIBs

ROVPPV1Lite
+Blackholing, no propagation

ROVPPV1LiteFull
+Withdrawals

ROVPPV2Lite
+Selective blackhole propagation

ROVPPV2LiteFull
+Withdrawals

ROVPPV2ImprovedLite
Enhanced propagation logic

ROVPPV2ImprovedLiteFull
+Withdrawals
```

Sources: [bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py12-18](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py#L12-L18)[bgpy/simulation_engine/policies/rovpp/v2/base/rovpp_v2_lite.py13-20](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v2/base/rovpp_v2_lite.py#L13-L20)[bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite_full.py11-18](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite_full.py#L11-L18)

---

## ROV++V1 Lite

### Core Mechanism

`ROVPPV1Lite` extends `ROV` by adding blackhole announcements to defend against two attack types:

1. **Non-routed prefix attacks**: Attackers exploit ROAs with origin AS 0
2. **Subprefix hijacks**: Attackers announce more-specific prefixes with invalid origins

The policy creates special announcements marked with `rovpp_blackhole=True` and adds them to the local RIB. These blackholes are **not propagated** to neighbors in V1.

Sources: [bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py12-18](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py#L12-L18)

### Blackhole Processing Pipeline

```
process_incoming_anns
from_rel, propagation_round

super().process_incoming_anns()
Standard ROV processing

_add_blackholes()
Generate and insert blackholes

_get_non_routed_blackholes_to_add()
For each ROA with origin=0

_get_routed_blackholes_to_add()
For invalid subprefixes

_add_blackholes_tolocal_rib()
Insert into local_rib

_recount_holes()
Update hole counts

_reset_q()
Clear recv_q
```

Sources: [bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py32-56](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py#L32-L56)

### Processing Incoming Announcements

The `process_incoming_anns` method overrides the base `ROV` implementation to inject blackhole generation logic:
StepMethodPurpose1`super().process_incoming_anns()`Standard ROV validation and local RIB updates2`_add_blackholes()`Generate and insert blackhole announcements3`_recount_holes()`Update hole tracking (single-round only)4`_reset_q()`Clear received announcement queue
Sources: [bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py32-55](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py#L32-L55)

### Non-Routed Blackholes

Non-routed blackholes defend against attacks exploiting ROAs with origin AS 0. The `_get_non_routed_blackholes_to_add` method creates blackhole announcements for all non-routed prefixes:

```
Yes

No

scenario.roas
All ROA objects

roa.is_non_routed?

Create blackhole announcement
prefix=roa.prefix
next_hop_asn=self.as_.asn
as_path=(self.as_.asn,)
rovpp_blackhole=True

Return tuple of blackholes
```

Key attributes of non-routed blackholes:

- `prefix`: The non-routed prefix from the ROA
- `next_hop_asn`: Self (the AS creating the blackhole)
- `as_path`: Only contains self
- `recv_relationship`: `Relationships.ORIGIN`
- `rovpp_blackhole`: `True`
- `seed_asn`: `None`
- `timestamp`: `Timestamps.VICTIM.value`

Sources: [bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py70-89](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py#L70-L89)

### Routed Subprefix Blackholes

Routed blackholes defend against subprefix hijacks where an attacker announces a more-specific prefix with an invalid origin. The policy identifies these by checking:

1. Announcements in the local RIB (valid prefixes)
2. Invalid subprefixes received from the same neighbor
3. Subprefix relationships defined in `scenario.ordered_prefix_subprefix_dict`

The `_invalid_subprefixes_from_same_neighbor` method yields invalid subprefixes matching these criteria:

```
Yes

No

Yes

No

ann: Announcement in local_rib

ann.recv_relationship
== ORIGIN?

Return empty

For subprefix in
scenario.ordered_prefix_subprefix_dict[ann.prefix]

For sub_ann in
self.recv_q.get_ann_list(subprefix)

1. Invalid by ROA?
2. Same neighbor?
(sub_ann.as_path[0] == ann.as_path[1])

yield sub_ann
```

The blackhole is created by copying and processing the invalid subprefix announcement with:

- `next_hop_asn` set to self
- `rovpp_blackhole` set to `True`

Sources: [bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py91-132](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py#L91-L132)

### Blackhole Insertion

The `_add_blackholes_tolocal_rib` method adds blackholes to the local RIB with specific rules:
ConditionActionNo existing announcement for prefixInsert blackholeExisting announcement is invalid by ROAInsert blackhole (overwrites invalid)Existing announcement is valid by ROADo not insert (preserve valid)
This ensures valid announcements are never overwritten by blackholes.

Sources: [bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py134-141](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py#L134-L141)

### Propagation Behavior in V1

The `_policy_propagate` method prevents blackhole propagation in V1:

```
def _policy_propagate(
    self,
    neighbor: "AS",
    ann: "Ann",
    propagate_to: Relationships,
    send_rels: set[Relationships],
) -> bool:
    """Only propagate announcements that aren't blackholes"""
    
    # Policy handled this ann for propagation (and did nothing if blackhole)
    return ann.rovpp_blackhole
```

The method returns `True` if the announcement is a blackhole, indicating the policy handled it (by not propagating it). This prevents blackholes from being sent to neighbors.

Sources: [bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py20-30](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py#L20-L30)

---

## ROV++V2 Lite

### Enhanced Propagation

`ROVPPV2Lite` extends `ROVPPV1Lite` by adding **selective blackhole propagation**. Unlike V1, which keeps blackholes local, V2 propagates blackholes to customers under specific conditions.

Sources: [bgpy/simulation_engine/policies/rovpp/v2/base/rovpp_v2_lite.py13-20](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v2/base/rovpp_v2_lite.py#L13-L20)

### Propagation Decision Logic

```
Yes

No

Yes

No

Yes

No

Yes

No

_policy_propagate()
neighbor, ann, propagate_to

ann.rovpp_blackhole?

_send_competing_hijack_allowed()
Check propagation conditions

ann.recv_relationship in
[PEERS, PROVIDERS, ORIGIN]?

propagate_to == CUSTOMERS?

Subprefix OR non-routed?
(not INVALID_LENGTH or non-routed)

_process_outgoing_ann()
Send to neighbor

return True
(policy handled)

return False
(standard processing)
```

Sources: [bgpy/simulation_engine/policies/rovpp/v2/base/rovpp_v2_lite.py22-41](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v2/base/rovpp_v2_lite.py#L22-L41)

### Propagation Conditions

The `_send_competing_hijack_allowed` method determines when a blackhole can be propagated. All three conditions must be satisfied:
ConditionCheckRationale**Direction**`recv_relationship in [PEERS, PROVIDERS, ORIGIN]`Only propagate blackholes learned from peers/providers/origin**Target**`propagate_to == CUSTOMERS`Only send blackholes to customers (valley-free)**Type**Subprefix OR non-routedDon't propagate prefix-level blackholes; check via `ROAValidity.INVALID_LENGTH` or `ann_is_roa_non_routed()`
The type check uses a complex condition:

```
self.get_roa_outcome(ann).validity not in (
    ROAValidity.INVALID_LENGTH,
    ROAValidity.INVALID_LENGTH_AND_ORIGIN,
) or not self.ann_is_roa_non_routed(ann)
```

This evaluates to `True` when:

- The announcement is **not** invalid by length (indicating it's a subprefix), OR
- The announcement is **not** non-routed

Sources: [bgpy/simulation_engine/policies/rovpp/v2/base/rovpp_v2_lite.py43-65](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v2/base/rovpp_v2_lite.py#L43-L65)

### V1 vs V2 Comparison
FeatureROVPPV1LiteROVPPV2Lite**Blackhole creation**✓ Non-routed + subprefix✓ Non-routed + subprefix**Blackhole insertion in local RIB**✓ Yes✓ Yes**Blackhole propagation**✗ None✓ Selective to customers**Propagation source**N/APeer/Provider/Origin only**Propagation target**N/ACustomers only**Propagation types**N/ASubprefix + non-routed only
---

## Full Variants

### ROV++V1 Lite Full

`ROVPPV1LiteFull` extends `ROVPPV1Lite` and mixes in `ROVFull` to add support for withdrawals and RIBs In/Out. The key difference is in blackhole insertion:

The `_add_blackholes_tolocal_rib` override adds a check for the case where an invalid announcement exists in the local RIB:

```
def _add_blackholes_tolocal_rib(self, blackholes: tuple["Ann", ...]) -> None:
    """Adds all blackholes to the local RIB"""
    
    for blackhole in blackholes:
        existing_ann = self.local_rib.get(blackhole.prefix)
        # Don't overwrite valid existing announcements
        if existing_ann is None:
            self.local_rib.add_ann(blackhole)
        elif self.ann_is_invalid_by_roa(existing_ann):
            # Withdrawal handling not implemented
            raise NotImplementedError(
                "Need to handle withdrawals for this"
                " if you need this feature, please email jfuruness@gmail.com"
            )
```

This raises a `NotImplementedError` because proper withdrawal handling for replacing invalid announcements with blackholes is not yet implemented.

Sources: [bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite_full.py11-36](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite_full.py#L11-L36)

### ROV++V2 Lite Full

`ROVPPV2LiteFull` combines `ROVPPV2Lite` and `ROVFull` through multiple inheritance:

```
class ROVPPV2LiteFull(ROVPPV2Lite, ROVFull):
    """An Policy that deploys ROV++V2 Lite as defined in the ROV++ paper, and
    has withdrawals, ribs in and out
    
    ROV++ Improved Deployable Defense against BGP Hijacking
    """
    
    name: str = "ROV++V2 Lite Full"
```

This variant inherits all V2 propagation logic while gaining withdrawal and RIB management capabilities from `ROVFull`.

Sources: [bgpy/simulation_engine/policies/rovpp/v2/base/rovpp_v2_lite_full.py1-13](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v2/base/rovpp_v2_lite_full.py#L1-L13)

### ROV++V2 Improved Variants

The "Improved" variants (`ROVPPV2ImprovedLite` and `ROVPPV2ImprovedLiteFull`) provide enhanced implementations with optimized propagation logic. These extend the base V2 policies:

```
class ROVPPV2ImprovedLiteFull(ROVPPV2ImprovedLite, ROVFull):
    """Full version of ROVPPV2ImprovedLite"""
    
    name: str = "ROV++V2i Lite Full"
```

Sources: [bgpy/simulation_engine/policies/rovpp/v2/improved/rovpp_v2_improved_lite_full.py1-10](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v2/improved/rovpp_v2_improved_lite_full.py#L1-L10)

---

## Implementation Details

### Multi-Round Limitations

ROV++V1 Lite includes a limitation for multi-round scenarios in the `_recount_holes` method:

```
def _recount_holes(self, propagation_round: int) -> None:
    # It's possible that we had a previously valid prefix
    # Then later recieved a subprefix that was invalid
    # Or there was previously an invalid subprefix
    # But later that invalid subprefix was removed
    # So we must recount the holes of each ann in local RIB
    # NOTE June 22 2024: I think doing this may require the use of the RIBsIn
    # because you could recieve a subprefix hijack round 1, and round 2 receive
    # the valid prefix from the same neighbor
    # not going to implement because of that, and because I don't think there's
    # a need to, because as far as I know there aren't any two round attacks
    # against ROV++. If someone comes up with one let me know and I can try to
    # help out, email at jfuruness@gmail.com.
    # NOTE: Additionally, we don't account for withdrawals at all...
    if propagation_round != 0:
        raise NotImplementedError("TODO: support ROV++ for multiple rounds")
```

This means ROV++ policies currently only support single-round propagation scenarios.

Sources: [bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py143-158](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py#L143-L158)

### ROA Checker Integration

All ROV++ policies inherit ROA validation methods from the `Policy` base class through `ROV`:
MethodPurposeReturns`ann_is_invalid_by_roa(ann)`Check if announcement is invalid`bool``ann_is_valid_by_roa(ann)`Check if announcement is valid`bool``ann_is_unknown_by_roa(ann)`Check if announcement is unknown`bool``ann_is_roa_non_routed(ann)`Check if ROA is non-routed (origin=0)`bool``get_roa_outcome(ann)`Get full ROA validation outcome`ROAOutcome`
These methods utilize the global `roa_checker` instance at `Policy.roa_checker`.

Sources: [bgpy/simulation_engine/policies/policy.py99-153](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/policy.py#L99-L153)[bgpy/simulation_engine/policies/rov/rov.py1-28](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rov/rov.py#L1-L28)

### Scenario Integration

ROV++ policies interact with scenario objects to access:

- `scenario.roas`: List of ROA objects for blackhole generation
- `scenario.ordered_prefix_subprefix_dict`: Mapping of prefixes to their subprefixes for identifying hijacks
- `scenario.scenario_config.AnnCls`: Announcement class for creating blackhole announcements

The `process_incoming_anns` method receives the `scenario` parameter to enable this integration.

Sources: [bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py32-56](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py#L32-L56)[bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py70-89](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py#L70-L89)

---

## Usage Summary

```
Yes

No

Scenario
(e.g., SubprefixHijack)

ScenarioConfig
AdoptPolicyCls

AS instance

ROV++ Policy
(V1 or V2 variant)

SimulationEngine

process_incoming_anns()

Blackhole generation
+ Local RIB insertion

Selective propagation
(V2 only)

Is V2?

End
```

To use ROV++ policies in a simulation:

1. Import the desired policy class (e.g., `ROVPPV1Lite`, `ROVPPV2Lite`)
2. Set it as `AdoptPolicyCls` in `ScenarioConfig`
3. Configure the scenario with appropriate ROAs and attack announcements
4. Run the simulation - the policy will automatically generate and manage blackholes

Sources: All ROV++ policy files