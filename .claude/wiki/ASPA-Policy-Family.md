# ASPA Policy Family
Relevant source files
- [bgpy/simulation_engine/__init__.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/__init__.py)
- [bgpy/simulation_engine/ann_containers/ann_container.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/ann_containers/ann_container.py)
- [bgpy/simulation_engine/policies/__init__.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/__init__.py)
- [bgpy/simulation_engine/policies/aspa/__init__.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/__init__.py)
- [bgpy/simulation_engine/policies/aspa/aspa.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/aspa.py)
- [bgpy/simulation_engine/policies/aspa/aspawn.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/aspawn.py)
- [bgpy/simulation_engine/policies/aspa/aspawn_full.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/aspawn_full.py)
- [bgpy/simulation_engine/policies/aspa/asra.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/asra.py)
- [bgpy/simulation_engine/policies/bgp/bgp/propagate_funcs.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/propagate_funcs.py)
- [bgpy/simulation_engine/policies/path_end/path_end.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/path_end/path_end.py)
- [bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py)
- [bgpy/utils/engine_runner/diagram.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/diagram.py)
- [scripts/aspawn_debug.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/scripts/aspawn_debug.py)

## Purpose and Scope

This document describes the ASPA (Autonomous System Provider Authorization) policy family in BGPy, which implements path validation mechanisms to detect route leaks and path manipulation attacks. The ASPA family consists of three main policies—`ASPA`, `ASRA`, and `ASPAwN`—each with progressively stricter validation rules. These policies extend ROV (see [Route Origin Validation](/blcrdbob3/bgpy_pkg/6.2-route-origin-validation-(rov))) by validating the entire AS path rather than just the origin.

For basic BGP policies and ROV, see [Route Origin Validation](/blcrdbob3/bgpy_pkg/6.2-route-origin-validation-(rov)). For attack scenarios that target ASPA policies, see [Post-ROV Attack Scenarios](/blcrdbob3/bgpy_pkg/7.2-post-rov-attack-scenarios) and [Custom Attacker Policies](/blcrdbob3/bgpy_pkg/7.5-custom-attacker-policies).

## Overview

The ASPA policy family validates AS paths by checking whether each hop in the path represents a legitimate business relationship. All ASPA policies inherit from `ROV` and add path validation on top of origin validation.
PolicyBase ClassValidation MechanismKey Feature`ASPA``ROV`Up-ramp and down-ramp checksProvider authorization`ASRA``ASPA`ASPA + fake link detectionDetects fabricated links`ASPAwN``ASPA`ASPA + neighbor checksValidates all neighbors in path
**Full Variants**: Each policy has a corresponding "Full" version (`ASPAFull`, `ASRAFull`, `ASPAwNFull`) that includes RIBs In/Out and withdrawal support, inheriting from `ROVFull`.

Sources: [bgpy/simulation_engine/policies/aspa/__init__.py1-15](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/__init__.py#L1-L15)[bgpy/simulation_engine/__init__.py1-119](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/__init__.py#L1-L119)

## Policy Class Hierarchy

```
Policy
(Abstract Base)

BGP
(Basic Routing)

ROV
(Origin Validation)

ROVFull
(+Withdrawals & RIBs)

ASPA
bgpy.simulation_engine.policies.aspa.aspa

ASPAFull
bgpy.simulation_engine.policies.aspa.aspa_full

ASRA
bgpy.simulation_engine.policies.aspa.asra

ASRAFull
bgpy.simulation_engine.policies.aspa.asra_full

ASPAwN
bgpy.simulation_engine.policies.aspa.aspawn

ASPAwNFull
bgpy.simulation_engine.policies.aspa.aspawn_full
```

Sources: [bgpy/simulation_engine/policies/aspa/__init__.py1-15](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/__init__.py#L1-L15)[bgpy/simulation_engine/policies/aspa/aspa.py1-146](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/aspa.py#L1-L146)

## ASPA Policy

### Purpose

`ASPA` implements AS Path Attestation based on the ASPA RFC V18 proposal. It validates that each AS-to-AS hop in a path represents a legitimate provider-customer or peer relationship, preventing route leaks where an AS advertises a route it should not propagate.

Sources: [bgpy/simulation_engine/policies/aspa/aspa.py10-25](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/aspa.py#L10-L25)

### Validation Algorithm

The `ASPA` policy performs different validation checks depending on the relationship from which an announcement is received:

```
False

True

CUSTOMERS/PEERS

PROVIDERS

False

True

False

True

_valid_ann()

_next_hop_valid()
Check next_hop_asn == as_path[0]

from_rel type?

_upstream_check()
From customer/peer

_downstream_check()
From provider

_get_max_up_ramp_length()
Find max contiguous provider chain
from origin

_get_max_down_ramp_length()
Find max contiguous provider chain
from receiver

max_up_ramp >= N?

max_up_ramp +
max_down_ramp >= N?

super()._valid_ann()
ROV validation

Return False
```

Sources: [bgpy/simulation_engine/policies/aspa/aspa.py27-146](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/aspa.py#L27-L146)

### Core Validation Methods

#### Next Hop Validation

[bgpy/simulation_engine/policies/aspa/aspa.py45-51](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/aspa.py#L45-L51)

```
def _next_hop_valid(self, ann: "Ann") -> bool:
    """Ensures the next hop is the first ASN in the AS-Path"""
    return ann.next_hop_asn == ann.as_path[0]
```

This prevents an AS from advertising an announcement with a manipulated next hop ASN. For route server deployments, this behavior would need modification.

#### Upstream Check (From Customers/Peers)

[bgpy/simulation_engine/policies/aspa/aspa.py53-68](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/aspa.py#L53-L68)

When receiving from customers or peers, ASPA verifies that the entire path consists of valid provider-customer relationships from the origin up. The `max_up_ramp` represents the longest contiguous chain of provider relationships starting from the origin.

**Algorithm**:

1. If path length is 1, delegate to ROV
2. Calculate `max_up_ramp` by traversing from origin and checking each hop
3. If `max_up_ramp < N` (path length), the announcement is invalid
4. Otherwise, delegate to ROV for origin validation

#### Downstream Check (From Providers)

[bgpy/simulation_engine/policies/aspa/aspa.py89-100](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/aspa.py#L89-L100)

When receiving from providers, ASPA allows for a "valley-free" path that goes up through providers then down through customers. Both `max_up_ramp` and `max_down_ramp` are calculated.

**Algorithm**:

1. Calculate `max_up_ramp` and `max_down_ramp`
2. If `max_up_ramp + max_down_ramp < N`, the path is invalid
3. Otherwise, delegate to ROV

#### Up-Ramp and Down-Ramp Calculation

[bgpy/simulation_engine/policies/aspa/aspa.py70-124](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/aspa.py#L70-L124)

The **up-ramp** is the contiguous chain of provider relationships starting from the origin (the announcement traverses "up" the hierarchy). The **down-ramp** is the contiguous chain starting from the receiver side (traversing "down" the hierarchy).

```
Example AS Path with ASPA Validation

provider_check(1,2)

provider_check(2,3)

provider_check(3,4)

provider_check(4,5)

Origin AS
(AS 1)

Provider 1
(AS 2)

Provider 2
(AS 3)

Provider 3
(AS 4)

Receiver
(AS 5)

Up-ramp: Contiguous provider chain from origin
Down-ramp: Contiguous provider chain from receiver
Path reversed for analysis: [1, 2, 3, 4, 5]
```

The path is reversed for analysis, and ASPA iterates through checking `provider_check(AS[i], AS[i+1])` to find where the provider chain breaks.

Sources: [bgpy/simulation_engine/policies/aspa/aspa.py70-124](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/aspa.py#L70-L124)

#### Provider Check

[bgpy/simulation_engine/policies/aspa/aspa.py126-146](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/aspa.py#L126-L146)

The `_provider_check(asn1, asn2)` method is the core primitive:

**Logic**:

- If `asn1` deploys ASPA (i.e., `isinstance(as_obj.policy, ASPA)`):

- Return `False` if `asn2` not in `asn1.provider_asns` ("Not Provider+")
- Return `True` if `asn2` is in `asn1.provider_asns` ("Provider+")
- If `asn1` does not deploy ASPA:

- Return `True` ("No Attestation")

This implements the RFC's "authorized()" function and handles cases where ASes don't exist in the graph.

Sources: [bgpy/simulation_engine/policies/aspa/aspa.py126-146](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/aspa.py#L126-L146)

## ASRA Policy

### Purpose

`ASRA` extends `ASPA` with additional fake link detection capabilities using ASRA records. It implements "Algorithm B" from the ASRA draft, which detects when an AS forges a link to another AS in the path.

Sources: [bgpy/simulation_engine/policies/aspa/asra.py1-126](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/asra.py#L1-L126)

### Fake Link Detection Algorithm

```
False

True

False

True

True

False

All hops checked

_valid_ann()

super()._valid_ann()
(ASPA validation)

ASPA result?

from_rel ==
PROVIDERS?

_get_min_up_ramp_length()
Find first non-provider hop

For i in range(min_up_ramp, N-1)

_is_fake_link(path[i], path[i+1])

Fake link
detected?

Return False

Return True
```

Sources: [bgpy/simulation_engine/policies/aspa/asra.py16-64](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/asra.py#L16-L64)

### Min Up-Ramp Calculation

[bgpy/simulation_engine/policies/aspa/asra.py66-90](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/asra.py#L66-L90)

The `min_up_ramp` identifies where the continuous provider chain from the origin ends. It differs from ASPA's `max_up_ramp` in that it stops at the first failure or non-ASPA AS:

**Algorithm**:

1. Start from origin (index 0 in reversed path)
2. For each hop `i → i+1`:

- If `AS[i]` doesn't deploy ASPA: return `i`
- If `AS[i+1]` not in `AS[i].provider_asns`: return `i`
3. If all hops pass: return path length

### Fake Link Detection

[bgpy/simulation_engine/policies/aspa/asra.py92-126](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/asra.py#L92-L126)

The `_is_fake_link(asn1, asn2)` method checks two conditions:

1. **ASPA condition**: `asn1` deploys ASPA and does NOT list `asn2` as a provider
2. **ASRA condition**: `asn1` deploys ASRA and does NOT list `asn2` as a neighbor

**Both conditions must be true** to declare a fake link. This means:

- If only ASPA records say "not a provider" → not fake
- If only ASRA records say "not a neighbor" → not fake
- If both records say "not authorized" → fake link detected

The neighbor check uses `asn1_obj.neighbor_asns`, which includes providers, peers, and customers.

Sources: [bgpy/simulation_engine/policies/aspa/asra.py92-126](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/asra.py#L92-L126)

## ASPAwN Policy

### Purpose

`ASPAwN` (ASPA with Neighbors) was originally developed independently and later confirmed to be equivalent to ASRA Algorithm B. It validates that every AS in the path only appears adjacent to its declared neighbors.

Sources: [bgpy/simulation_engine/policies/aspa/aspawn.py1-51](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/aspawn.py#L1-L51)

### Validation Algorithm

[bgpy/simulation_engine/policies/aspa/aspawn.py33-50](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/aspawn.py#L33-L50)

The algorithm is simpler than ASRA but has the same effect:

```
False

True

False

True

False

True

All ASes checked

_valid_ann()

For each ASN in as_path

AS deploys
ASPAwN?

Check if previous ASN
in neighbor_asns

Valid?

Check if next ASN
in neighbor_asns

Valid?

super()._valid_ann()
(ASPA validation)

Return False
```

**Key differences from ASRA**:

- Checks every ASPA-deploying AS in the path, not just after `min_up_ramp`
- Uses a single neighbor check rather than separate ASPA/ASRA record checks
- Simpler implementation with equivalent security properties

Sources: [bgpy/simulation_engine/policies/aspa/aspawn.py33-50](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/aspawn.py#L33-L50)

### Neighbor Sets

The `neighbor_asns` attribute on AS objects includes:

- `provider_asns`: All providers of the AS
- `peer_asns`: All peers of the AS
- `customer_asns`: All customers of the AS

This is computed during AS graph construction and used for efficient neighbor lookups.

## Full Policy Variants

### ASPAFull

[bgpy/simulation_engine/policies/aspa/aspa_full.py1-10](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/aspa_full.py#L1-L10)

Extends both `ASPA` and `ROVFull` to add:

- **RIBs In/Out**: Separate tracking of received and sent announcements
- **Withdrawal support**: Proper handling of route withdrawals
- **State management**: Required for scenarios with multiple propagation rounds

### ASRAFull and ASPAwNFull

[bgpy/simulation_engine/policies/aspa/asra_full.py1-10](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/asra_full.py#L1-L10)[bgpy/simulation_engine/policies/aspa/aspawn_full.py1-10](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/aspawn_full.py#L1-L10)

Similar extensions of `ASRA` and `ASPAwN` with full RIB and withdrawal support. Used primarily in:

- `AccidentalRouteLeak` scenarios (requires two propagation rounds)
- Testing frameworks that need to verify intermediate state
- Advanced simulations with dynamic route changes

## Attack Considerations

### Shortest Path Attacks

[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py187-222](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L187-L222)

The `ShortestPathPrefixHijack` scenario implements attacks against ASPA policies by finding the shortest valley-free path through non-adopting ASes:

**Attack Strategy**:

1. Use `_find_shortest_valley_free_non_adopting_path()` to find shortest path
2. Start from victim AS and use BFS through provider relationships
3. Extend search to peer relationships if needed
4. Use propagation rank ordering as fallback for customer relationships
5. Attacker forges announcement with this path

The search prioritizes:

- **Providers first**: Shortest up-ramp through non-adopters
- **Peers second**: Lateral movement to non-adopters
- **Customers last**: Down-ramp to non-adopters (rare case)

Sources: [bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py235-360](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L235-L360)

### Custom Attacker Policies

[bgpy/simulation_engine/policies/__init__.py16-19](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/__init__.py#L16-L19)[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py76](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L76-L76)

Special attacker policy classes exist for ASPA-specific attacks:

- `ShortestPathPrefixASPAAttacker`: Exports all routes to customers regardless of validation
- `FirstASNStrippingPrefixASPAAttacker`: Strips first ASN from path before forwarding

These policies allow attackers to bypass ASPA validation by modifying normal BGP behavior. They must be explicitly specified in `ScenarioConfig.AttackerBasePolicyCls`.

### Policy Classification for Attack Scenarios

[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py532-549](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L532-L549)

Attack scenarios classify policies into groups to determine attack strategy:
Policy GroupClassesAttack Type`aspa_policy_classes``ASPA`, `ASPAFull`Shortest valley-free path through non-adopters`asra_policy_classes``ASRA`, `ASRAFull`, `ASPAwN`, `ASPAwNFull`Same as ASPA (no custom attacker required)
The ASRA variants don't require custom attacker policies because the shortest path attack naturally evades fake link detection by only using legitimate links.

Sources: [bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py532-570](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L532-L570)

## Implementation Details

### Performance Optimizations

[bgpy/simulation_engine/policies/aspa/aspa.py15-20](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/aspa.py#L15-L20)

Several performance considerations in the ASPA implementation:

- Caching of provider checks was tested but showed negligible impact
- Path reversals kept for RFC compliance despite 5% performance cost
- Early termination in validation checks when invalid path detected
- Provider check ordering prioritizes most common case (from providers)

### Path Reversal

ASPA validation requires analyzing paths from origin to receiver, but BGP announcements store paths in receiver-to-origin order. The implementation reverses paths using `ann.as_path[::-1]` for analysis, then reverses back for return values.

### Edge Cases

[bgpy/simulation_engine/policies/aspa/aspa.py136-145](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/aspa.py#L136-L145)

The `_provider_check()` method handles:

- ASes that don't exist in the graph (returns `True`)
- ASes that don't deploy ASPA (returns `True`, "No Attestation")
- Empty provider sets (returns `False` if AS deploys ASPA)

Sources: [bgpy/simulation_engine/policies/aspa/aspa.py1-146](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/aspa.py#L1-L146)[bgpy/simulation_engine/policies/aspa/asra.py1-126](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/asra.py#L1-L126)[bgpy/simulation_engine/policies/aspa/aspawn.py1-51](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/aspawn.py#L1-L51)