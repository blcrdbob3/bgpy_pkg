# Custom Attacker Policies
Relevant source files
- [bgpy/simulation_engine/__init__.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/__init__.py)
- [bgpy/simulation_engine/policies/__init__.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/__init__.py)
- [bgpy/simulation_engine/policies/aspa/__init__.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/__init__.py)
- [bgpy/simulation_engine/policies/aspa/aspawn.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/aspawn.py)
- [bgpy/simulation_engine/policies/aspa/aspawn_full.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/aspawn_full.py)
- [bgpy/simulation_engine/policies/aspa/asra.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/asra.py)
- [bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py)
- [scripts/aspawn_debug.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/scripts/aspawn_debug.py)

## Purpose and Scope

This document explains custom attacker policy implementations in BGPy, which are specialized policy classes that enable attackers to perform sophisticated path manipulation attacks against ASPA-based security policies. These policies modify normal BGP export behavior to allow attackers to propagate announcements that would otherwise be rejected by path validation mechanisms.

For information about the attack scenarios that use these policies, see [Attack Scenario Reference](/blcrdbob3/bgpy_pkg/7-attack-scenario-reference). For details on ASPA policy implementations being attacked, see [ASPA Policy Family](/blcrdbob3/bgpy_pkg/6.4-aspa-policy-family).

**Sources:**[bgpy/simulation_engine/policies/__init__.py16-19](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/__init__.py#L16-L19)[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py58-59](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L58-L59)

---

## Overview

Custom attacker policies are necessary when simulating attacks against path validation mechanisms like ASPA, ASRA, and ASPAwN. Unlike basic prefix hijacks where an attacker simply announces a malicious prefix, attacks against ASPA require the attacker to export announcements along specific AS paths that appear legitimate according to ASPA validation rules.

Normal ASPA-compliant policies restrict which paths an AS can export to its neighbors based on provider-customer relationships. Custom attacker policies remove these restrictions, allowing the attacker AS to export any announcement regardless of path validation results.

**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py187-223](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L187-L223)

---

## Architecture and Configuration

### Integration with ScenarioConfig

Custom attacker policies are configured through the `AttackerBasePolicyCls` parameter in `ScenarioConfig`. This is distinct from `AdoptPolicyCls` (the defensive policy being tested) and `BasePolicyCls` (the default policy for non-adopting ASes).

```
Custom Attacker Policies

AS Assignments

ScenarioConfig Parameters

AdoptPolicyCls
(Defensive Policy:
ASPA, ASRA, ASPAwN)

AttackerBasePolicyCls
(Attacker's Export Behavior)

BasePolicyCls
(Non-Adopter Policy:
typically BGP)

Victim AS
Announces legitimate prefix

Attacker AS
Announces malicious path

Adopting ASes
Run defensive policy

Non-Adopting ASes
Run base policy

ShortestPathPrefixASPAAttacker
Exports to all neighbors

FirstASNStrippingPrefixASPAAttacker
Exports with path manipulation
```

**Diagram: Custom Attacker Policy Configuration Flow**

**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py76](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L76-L76)[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py224-233](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L224-L233)

---

## Available Custom Attacker Policies

### ShortestPathPrefixASPAAttacker

The primary custom attacker policy for ASPA-based attacks. This policy allows the attacker to export announcements to all neighbors (customers, peers, and providers) regardless of ASPA validation results. This is required for the `ShortestPathPrefixHijack` scenario when targeting ASPA, ASRA, or ASPAwN policies.

**Key Characteristics:**

- Removes ASPA export restrictions
- Allows announcements with invalid AS paths to be propagated
- Required for shortest path export-all attacks against ASPA

**Sources:**[bgpy/simulation_engine/__init__.py56](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/__init__.py#L56-L56)[bgpy/simulation_engine/policies/__init__.py16-18](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/__init__.py#L16-L18)[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py58](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L58-L58)

### FirstASNStrippingPrefixASPAAttacker

Specialized attacker policy for first-ASN stripping attacks. This allows attackers to remove the first ASN from an announcement's path and re-export it, which can evade certain ASPA validation checks.

**Key Characteristics:**

- Enables path manipulation attacks
- Removes first ASN from path during export
- Used in conjunction with `FirstASNStrippingPrefixHijack` scenario

**Sources:**[bgpy/simulation_engine/__init__.py39](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/__init__.py#L39-L39)[bgpy/simulation_engine/policies/__init__.py17](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/__init__.py#L17-L17)

---

## Policy Requirements by Attack Scenario

The following table shows which custom attacker policies are required for different attack scenarios against ASPA-based defensive policies:
Attack ScenarioTarget PoliciesRequired Attacker PolicyValidation`ShortestPathPrefixHijack`ASPA, ASPAFull`ShortestPathPrefixASPAAttacker`Mandatory`ShortestPathPrefixHijack`ASRA, ASRAFull, ASPAwN, ASPAwNFull`ShortestPathPrefixASPAAttacker`Recommended`FirstASNStrippingPrefixHijack`ASPA, ASPAFull, ASRA, ASRAFull, ASPAwN, ASPAwNFull`FirstASNStrippingPrefixASPAAttacker`MandatoryOther scenariosBGP, ROV, PathEnd, BGPSec, etc.Not requiredN/A
**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py101-124](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L101-L124)[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py532-550](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L532-L550)

---

## Usage Example

### Basic Configuration

```
from bgpy.simulation_engine import ASPA, ShortestPathPrefixASPAAttacker
from bgpy.simulation_framework import ScenarioConfig, ShortestPathPrefixHijack

# Correct configuration for ASPA attack
config = ScenarioConfig(
    ScenarioCls=ShortestPathPrefixHijack,
    AdoptPolicyCls=ASPA,
    AttackerBasePolicyCls=ShortestPathPrefixASPAAttacker  # Custom attacker policy
)
```

### What Happens Without Custom Attacker Policy

If `AttackerBasePolicyCls` is not set correctly, the scenario will raise a validation error:

```
# Incorrect configuration - will raise ValueError
config = ScenarioConfig(
    ScenarioCls=ShortestPathPrefixHijack,
    AdoptPolicyCls=ASPA,
    # AttackerBasePolicyCls defaults to BGP, which cannot export the attack path
)
# Raises: "For a shortest path export all attack against ASPA,
#          scenario_config.AttackerAdoptPolicyCls must be set to
#          ASPAShortestPathPrefixAttacker..."
```

**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py224-233](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L224-L233)

---

## Validation Mechanism

### Required Attacker Class Validation

The `ShortestPathPrefixHijack` scenario enforces the use of `ShortestPathPrefixASPAAttacker` when attacking ASPA policies through the `_validate_required_aspa_attacker_cls` method:

```
True

False

Yes

No

_get_aspa_attack_anns() called

require_aspa_attacker_cls
parameter?

_validate_required_aspa_attacker_cls()

Skip validation

AttackerBasePolicyCls ==
ShortestPathPrefixASPAAttacker?

Continue with attack

Raise ValueError
with detailed message

Generate attack announcements
with shortest valid path
```

**Diagram: Attacker Policy Validation Flow**

**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py187-223](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L187-L223)[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py224-233](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L224-L233)

### When Validation is Applied
Policy TargetValidation RequiredReasonASPA, ASPAFullYes (enforced)These policies strictly validate provider relationshipsASRA, ASRAFull, ASPAwN, ASPAwNFullNo (bypassed)These policies have additional checks that may not require custom attackerPathEnd, BGPSec, ROVN/ADifferent attack mechanisms used
**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py109-114](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L109-L114)

---

## Attack Path Construction

### Shortest Valley-Free Path Algorithm

Custom attacker policies enable the attacker to export announcements along the shortest valley-free non-adopting path. The `ShortestPathPrefixHijack` scenario uses `_find_shortest_valley_free_non_adopting_path()` to construct this path:

```
Yes

No

Yes

No

Yes

No

Start at Victim AS
(root_asn)

Phase 1: BFS through
provider relationships

Found non-adopting
AS?

Return path
via providers

Phase 2: Check peer
relationships of visited ASes

Found non-adopting
peer?

Return path
via providers + peer

Phase 3: Reverse propagation
through customer relationships

Iterate through ASes
in propagation rank order

Build paths via
customer relationships

Found non-adopting
customer?

Return shortest
customer path

Warn: Full adoption
return empty path
```

**Diagram: Shortest Path Discovery Algorithm**

This algorithm ensures the attacker finds the shortest path that:

1. Originates from the victim AS
2. Follows valley-free routing (up-ramp via providers, optional peer hop, down-ramp via customers)
3. Terminates at a non-adopting AS (which will accept the invalid announcement)

**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py235-360](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L235-L360)

---

## Technical Implementation Details

### Export Behavior Modification

Custom attacker policies fundamentally alter announcement export behavior. While normal ASPA policies reject announcements that fail validation checks, custom attacker policies:

1. **Disable Path Validation**: Remove checks that would prevent export of invalid paths
2. **Override Export Rules**: Allow export to all neighbor types (customers, peers, providers)
3. **Maintain Announcement Properties**: Preserve transitive attributes like OTC (Only-To-Customers) flags

### Path Construction for ASPA Attacks

When generating attack announcements against ASPA, the attacker prepends its ASN to the shortest valid path:

```
Shortest Valid Path: [Provider_N, Provider_N-1, ..., Provider_1, Victim_ASN]
Attacker Path:      [Attacker_ASN, Provider_N, Provider_N-1, ..., Provider_1, Victim_ASN]

```

The attacker then uses `ShortestPathPrefixASPAAttacker` to export this announcement to all neighbors, including customers. Normally ASPA would reject this export as a route leak, but the custom policy bypasses this check.

**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py206-222](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L206-L222)

---

## Interaction with Other ASPA Variants

### ASRA (ASPA with Route leak detection and fake link detection Algorithm)

When attacking ASRA policies, the `require_aspa_attacker_cls` parameter is set to `False`, allowing more flexibility:

**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py111-114](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L111-L114)[bgpy/simulation_engine/policies/aspa/asra.py1-126](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/asra.py#L1-L126)

### ASPAwN (ASPA with Neighbor validation)

ASPAwN adds neighbor checks at every AS in the path. The custom attacker policy remains necessary to export the attack path, but the path construction algorithm must account for the additional neighbor validation:

**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py542-550](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L542-L550)[bgpy/simulation_engine/policies/aspa/aspawn.py1-51](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/aspawn.py#L1-L51)

---

## Related Scenario Configurations

The table below shows how different scenarios interact with custom attacker policies:
Scenario ClassASPA Attack MethodCustom Attacker Required`PrefixHijack`N/A - targets pre-ROV policiesNo`ForgedOriginPrefixHijack`Forged origin + ROV evasionNo`ShortestPathPrefixHijack`Shortest valid path + export-all**Yes**`FirstASNStrippingPrefixHijack`Path manipulation**Yes**`AccidentalRouteLeak`Two-round propagationNo
**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py73-124](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L73-L124)

---

## Key Takeaways

1. **Custom attacker policies enable sophisticated attacks**: They allow attackers to bypass export restrictions in path validation mechanisms
2. **Required for ASPA attacks**: `ShortestPathPrefixASPAAttacker` must be explicitly configured when attacking ASPA-based policies
3. **Validation prevents misconfiguration**: The framework automatically validates that correct attacker policies are used
4. **Import from simulation_engine**: Both custom attacker classes are available at the top level:

```
from bgpy.simulation_engine import (
    ShortestPathPrefixASPAAttacker,
    FirstASNStrippingPrefixASPAAttacker
)
```
5. **Path construction is complex**: The shortest valid path algorithm uses multi-phase BFS/propagation to find optimal attack paths

**Sources:**[bgpy/simulation_engine/__init__.py1-119](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/__init__.py#L1-L119)[bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py187-360](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/shortest_path_prefix_hijack.py#L187-L360)