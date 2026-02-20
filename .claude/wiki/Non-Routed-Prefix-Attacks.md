# Non-Routed Prefix Attacks
Relevant source files
- [bgpy/simulation_engine/policies/custom_attackers/__init__.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/custom_attackers/__init__.py)
- [bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_prefix_hijack.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_prefix_hijack.py)
- [bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_hijack.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_hijack.py)
- [bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_prefix_hijack.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_prefix_hijack.py)
- [bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/__init__.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/__init__.py)
- [bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/first_asn_stripping_prefix_hijack.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/first_asn_stripping_prefix_hijack.py)
- [bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/forged_origin_prefix_hijack.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/forged_origin_prefix_hijack.py)
- [bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/superprefix_prefix_hijack.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/post_rov/superprefix_prefix_hijack.py)
- [bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/prefix_hijack.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/prefix_hijack.py)
- [bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/subprefix_hijack.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/subprefix_hijack.py)

## Purpose and Scope

This document describes non-routed prefix attacks, a category of BGP attacks that exploit Route Origin Authorizations (ROAs) with origin AS 0. These attacks target prefixes that have been explicitly marked as "should not be routed" in the RPKI system. This page covers the three non-routed attack scenario implementations in BGPy and their interaction with various security policies.

For information about basic prefix hijacks that work against unprotected BGP, see [Pre-ROV Attack Scenarios](/blcrdbob3/bgpy_pkg/7.1-pre-rov-attack-scenarios). For attacks designed to evade ROV through path manipulation, see [Post-ROV Attack Scenarios](/blcrdbob3/bgpy_pkg/7.2-post-rov-attack-scenarios). For details on the ROV policy and its variants, see [Route Origin Validation (ROV)](/blcrdbob3/bgpy_pkg/6.2-route-origin-validation-(rov)) and [ROV++ Policies](/blcrdbob3/bgpy_pkg/6.3-rov++-policies).

---

## AS 0 ROAs and Non-Routed Prefixes

### What are AS 0 ROAs?

AS 0 ROAs are a special type of Route Origin Authorization where the origin ASN is set to 0 (zero). According to RPKI standards, an AS 0 ROA indicates that a prefix should **never** be routed on the Internet. These are used to blackhole specific prefixes for various operational purposes:

- Preventing bogon prefixes from being announced
- Marking reserved or unallocated address space
- Explicitly disallowing routing of certain prefixes

### Validation Behavior

When a BGP router performing ROV encounters an announcement for a prefix covered by an AS 0 ROA, the announcement is considered **invalid by origin**, regardless of the actual origin ASN in the announcement. This is because no legitimate AS should be announcing a prefix marked as non-routed.
ScenarioROAAnnouncement OriginROV ResultNormal Hijack`1.2.0.0/16 → AS 1`AS 2Invalid by OriginNon-Routed Hijack`1.2.0.0/16 → AS 0`AS 2Invalid by OriginNon-Routed Hijack`1.2.0.0/16 → AS 0`AS 1Invalid by Origin
### Attack Opportunity

Non-routed prefix attacks exploit the fact that **basic ROV treats AS 0 ROAs the same as regular invalid-by-origin announcements**. If an attacker announces a non-routed prefix, standard ROV will reject it, but the attacker can still succeed against non-adopting ASes. More sophisticated attacks combine non-routed prefixes with superprefixes to bypass even some ROV deployments.

**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_prefix_hijack.py39-47](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_prefix_hijack.py#L39-L47)

---

## Non-Routed Attack Scenarios

### Scenario Class Hierarchy

```
Non-Routed Attack Variants

Scenario
(Base Class)

NonRoutedPrefixHijack

NonRoutedSuperprefixHijack

NonRoutedSuperprefixPrefixHijack
```

All non-routed attack scenarios extend the base `Scenario` class directly (not `VictimsPrefix`) because there is **no legitimate victim** in these attacks. The prefix is explicitly marked as non-routed, so there is no legitimate origin AS defending it.

**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_prefix_hijack.py14](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_prefix_hijack.py#L14-L14)[bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_hijack.py14](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_hijack.py#L14-L14)[bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_prefix_hijack.py14](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_prefix_hijack.py#L14-L14)

---

## NonRoutedPrefixHijack

### Overview

The `NonRoutedPrefixHijack` class implements the simplest non-routed attack where an attacker announces a prefix that has an AS 0 ROA. This attack tests how security policies handle announcements for prefixes that are explicitly marked as non-routed.

### Implementation

```
ROAs

Announcements

NonRoutedPrefixHijack

_get_announcements()

_get_roas()

Announcement
prefix=1.2.0.0/16
as_path=(attacker,)
timestamp=ATTACKER

ROA
prefix=1.2.0.0/16
origin=AS 0
```

**Key Characteristics:**
PropertyValueAttacker Announcements`Prefixes.PREFIX` (e.g., `1.2.0.0/16`)ROAs`ROA(1.2.0.0/16, origin=0)`Victim AnnouncementsNoneTimestamp`Timestamps.ATTACKER`
### Announcement Generation

The `_get_announcements()` method generates a single announcement per attacker:

```
For each attacker ASN:
    - Prefix: Prefixes.PREFIX.value (1.2.0.0/16)
    - AS Path: (attacker_asn,)
    - Timestamp: ATTACKER

```

**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_prefix_hijack.py17-37](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_prefix_hijack.py#L17-L37)

### ROA Generation

The `_get_roas()` method creates a single AS 0 ROA for the prefix:

```
ROA(ip_network(Prefixes.PREFIX.value), origin=0)
```

This marks `1.2.0.0/16` as non-routed, meaning no AS should legitimately announce it.

**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_prefix_hijack.py39-47](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_prefix_hijack.py#L39-L47)

### Expected Outcomes
PolicyExpected BehaviorBasic BGPAccepts the announcement (no ROA checking)ROVRejects as invalid by originROV++ V1Blackholes the announcementROV++ V2Blackholes and refuses to propagate
---

## NonRoutedSuperprefixHijack

### Overview

The `NonRoutedSuperprefixHijack` class implements a more sophisticated attack where the attacker announces a **superprefix** (e.g., `1.2.0.0/15`) while the non-routed ROA covers only a more specific prefix (e.g., `1.2.0.0/16`). This exploits the BGP longest-prefix-match behavior combined with RPKI validation.

### Attack Strategy

```
ROV Validation

Attacker Announcement

RPKI Database

Doesn't cover superprefix

ROA: 1.2.0.0/16 → AS 0
(Non-Routed)

Announcement
1.2.0.0/15 → Attacker
(Superprefix)

ROA Lookup for 1.2.0.0/15

No matching ROA
→ UNKNOWN

Basic ROV: ACCEPTS
(Unknown = Accept)
```

The key insight is that the superprefix (`1.2.0.0/15`) does **not** have a covering ROA, so its validation outcome is `UNKNOWN`. Basic ROV implementations accept announcements with unknown validation outcomes, allowing the attacker to succeed against ROV-adopting ASes.

### Implementation Details
PropertyValueAttacker Announcements`Prefixes.SUPERPREFIX` (e.g., `1.2.0.0/15`)ROAs`ROA(1.2.0.0/16, origin=0)`Victim AnnouncementsNoneValidation OutcomeUNKNOWN (no covering ROA for superprefix)
**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_hijack.py14-55](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_hijack.py#L14-L55)

### Code Structure

The scenario implements two key methods:

**`_get_announcements()`**[bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_hijack.py22-41](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_hijack.py#L22-L41):

```
For each attacker ASN:
    - Prefix: Prefixes.SUPERPREFIX.value (1.2.0.0/15)
    - AS Path: (attacker_asn,)
    - Timestamp: ATTACKER

```

**`_get_roas()`**[bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_hijack.py43-55](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_hijack.py#L43-L55):

```
ROA(ip_network(Prefixes.PREFIX.value), origin=0)
# ROA covers 1.2.0.0/16 (more specific than announced 1.2.0.0/15)
```

### Why This Works

The attack succeeds because:

1. The attacker announces `1.2.0.0/15` (superprefix)
2. RPKI validation looks for ROAs covering `1.2.0.0/15`
3. The only ROA is for `1.2.0.0/16` (more specific), which doesn't cover the announcement
4. Validation outcome: UNKNOWN
5. ROV policy accepts UNKNOWN announcements (default-allow behavior)
6. Traffic destined for `1.2.0.0/16` gets routed via the less-specific `1.2.0.0/15` announcement

---

## NonRoutedSuperprefixPrefixHijack

### Overview

The `NonRoutedSuperprefixPrefixHijack` class combines both strategies: the attacker announces **both** the non-routed prefix and its superprefix. This creates a multi-pronged attack that maximizes success against different policy configurations.

### Attack Structure

```
Outcomes

Validation Results

Attacker Announcements

RPKI Database

ROA: 1.2.0.0/16 → AS 0

Announcement #1
1.2.0.0/16 → Attacker

Announcement #2
1.2.0.0/15 → Attacker

1.2.0.0/16
INVALID by Origin

1.2.0.0/15
UNKNOWN

Basic BGP:
Accepts both

ROV:
Rejects prefix,
Accepts superprefix

ROV++:
Blackholes prefix,
Rejects superprefix
```

### Implementation

**Announcements**[bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_prefix_hijack.py22-50](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_prefix_hijack.py#L22-L50):

For each attacker ASN, two announcements are generated:
AnnouncementPrefixPurpose1`Prefixes.SUPERPREFIX` (`1.2.0.0/15`)Bypass ROV via unknown validation2`Prefixes.PREFIX` (`1.2.0.0/16`)Attack non-adopting ASes directly
**ROAs**[bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_prefix_hijack.py52-64](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_prefix_hijack.py#L52-L64):

```
ROA(ip_network(Prefixes.PREFIX.value), origin=0)
# Single ROA covering only the /16 prefix
```

### Attack Effectiveness

This combined attack maximizes coverage across different AS adoption scenarios:
Target AS TypeEffective AnnouncementReasonNon-adopting (Basic BGP)Prefix (`/16`)More specific, wins LPMROV-adoptingSuperprefix (`/15`)Unknown validation acceptedROV++ V1 adoptingNeitherBoth blackholed/rejectedROV++ V2 adoptingNeitherBoth blackholed and not propagated
**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_prefix_hijack.py1-64](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_prefix_hijack.py#L1-L64)

---

## Attack Mechanics and Policy Interactions

### Validation Flow for Non-Routed Attacks

```
Yes

No

Yes

No

Yes

No

Announcement Received
prefix P, origin A

ROA Lookup for prefix P

Covering
ROA exists?

ROA origin
matches A?

ROA origin
is AS 0?

Validation: VALID

Validation: INVALID

Validation: UNKNOWN

ROV: Accept
ROV++ V1: Accept
ROV++ V2: Accept

All policies: Accept

ROV: Reject
ROV++ V1: Blackhole
ROV++ V2: Blackhole + No Propagate
```

**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_prefix_hijack.py39-47](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_prefix_hijack.py#L39-L47)

### Policy Behavior Matrix
ScenarioAnnouncementROABasic BGPROVROV++ V1ROV++ V2NonRoutedPrefixHijack`1.2.0.0/16``1.2.0.0/16→0`✓ Accept✗ Reject◐ Blackhole◐ BlackholeNonRoutedSuperprefixHijack`1.2.0.0/15``1.2.0.0/16→0`✓ Accept✓ Accept (Unknown)✓ Accept (Unknown)✗ RejectNonRoutedSuperprefixPrefixHijack`1.2.0.0/16``1.2.0.0/15``1.2.0.0/16→0`✓ Accept both✗ Reject `/16`✓ Accept `/15`◐ Blackhole `/16`✓ Accept `/15`◐ Blackhole `/16`✗ Reject `/15`
**Legend:**

- ✓ Accept: Routes announcement normally
- ✗ Reject: Drops announcement completely
- ◐ Blackhole: Accepts but redirects traffic to null route

### ROV++ Enhanced Protections

The `ROV++` policies (see [ROV++ Policies](/blcrdbob3/bgpy_pkg/6.3-rov++-policies)) provide enhanced protection against non-routed prefix attacks:

**ROV++ V1:**

- Blackholes invalid-by-origin announcements (including AS 0 ROAs)
- Still vulnerable to superprefix attacks (unknown validation accepted)

**ROV++ V2:**

- Blackholes invalid-by-origin announcements
- Rejects unknown validation outcomes from certain AS relationships
- More resistant to superprefix attacks due to stricter propagation policies

**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_hijack.py14-20](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_hijack.py#L14-L20)

---

## File Organization

All non-routed attack scenarios are located in the `non_routed` subdirectory:

```
bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/
├── __init__.py
├── non_routed_prefix_hijack.py
├── non_routed_superprefix_hijack.py
└── non_routed_superprefix_prefix_hijack.py

```

### Common Patterns

All three scenarios share these implementation patterns:

1. **Direct Scenario Inheritance**: Extend `Scenario` directly (not `VictimsPrefix`)
2. **AS 0 ROAs**: Always use `ROA(prefix, origin=0)`
3. **No Victim**: No legitimate origin AS exists for non-routed prefixes
4. **Attacker Timestamps**: All announcements use `Timestamps.ATTACKER`

**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_prefix_hijack.py1-48](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_prefix_hijack.py#L1-L48)[bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_hijack.py1-56](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_hijack.py#L1-L56)[bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_prefix_hijack.py1-65](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_prefix_hijack.py#L1-L65)

---

## Usage in Simulations

### Scenario Configuration Example

To include non-routed attacks in a simulation:

```
from bgpy.simulation_framework import ScenarioConfig
from bgpy.simulation_framework.scenarios import (
    NonRoutedPrefixHijack,
    NonRoutedSuperprefixHijack,
    NonRoutedSuperprefixPrefixHijack
)
from bgpy.simulation_engine.policies import ROV, ROVPPV1, ROVPPV2

scenario_configs = [
    ScenarioConfig(
        ScenarioCls=NonRoutedPrefixHijack,
        AdoptPolicyCls=ROV,
        BasePolicyCls=BGP
    ),
    ScenarioConfig(
        ScenarioCls=NonRoutedSuperprefixHijack,
        AdoptPolicyCls=ROVPPV2,
        BasePolicyCls=BGP
    ),
]
```

### Interpretation of Results

When analyzing simulation outcomes for non-routed attacks:

1. **No Victim Success**: Non-routed attacks have no `VICTIM_SUCCESS` outcomes since there's no legitimate victim
2. **Attacker Success**: Indicates ASes that accepted/forwarded the non-routed announcement
3. **Disconnected**: ASes that rejected all announcements (desired outcome for security policies)

For details on outcome analysis, see [Outcome Analysis](/blcrdbob3/bgpy_pkg/8.1-outcome-analysis).

**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_prefix_hijack.py14](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_prefix_hijack.py#L14-L14)[bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_hijack.py14](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_hijack.py#L14-L14)

---

## Summary

Non-routed prefix attacks exploit AS 0 ROAs and represent a distinct category of BGP attacks where:

- No legitimate origin exists for the prefix
- Basic ROV rejects direct announcements but accepts superprefixes (unknown validation)
- ROV++ policies provide stronger protection through blackholing and selective propagation
- Combined attacks (prefix + superprefix) maximize attacker effectiveness across mixed adoption scenarios

These scenarios are critical for evaluating the effectiveness of security policies against deliberately blackholed address space and testing how different policies handle RPKI validation outcomes beyond simple valid/invalid dichotomies.

**Sources:**[bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_prefix_hijack.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_prefix_hijack.py)[bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_hijack.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_hijack.py)[bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_prefix_hijack.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/non_routed/non_routed_superprefix_prefix_hijack.py)