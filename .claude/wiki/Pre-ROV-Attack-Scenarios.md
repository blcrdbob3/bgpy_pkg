# Pre-ROV Attack Scenarios
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

This document describes the **Pre-ROV Attack Scenarios** implemented in BGPy. These are attack scenarios that successfully compromise basic BGP routing without requiring sophisticated techniques to evade Route Origin Validation (ROV). Pre-ROV attacks exploit fundamental weaknesses in BGP's lack of origin authentication and prefix ownership verification.

For an overview of all attack scenario categories, see [Attack Scenarios Overview](/blcrdbob3/bgpy_pkg/3.4-attack-scenarios-overview). For attacks that specifically target ROV-enabled networks, see [Post-ROV Attack Scenarios](/blcrdbob3/bgpy_pkg/7.2-post-rov-attack-scenarios). For attacks exploiting non-routed prefixes with AS 0 ROAs, see [Non-Routed Prefix Attacks](/blcrdbob3/bgpy_pkg/7.3-non-routed-prefix-attacks).

The pre-ROV attack scenarios covered in this document are:

- **PrefixHijack**: Attacker announces the same prefix as the victim
- **SubprefixHijack**: Attacker announces a more specific subprefix of the victim's prefix

---

## Attack Scenario Class Hierarchy

Pre-ROV attack scenarios inherit from the `VictimsPrefix` base class, which provides common functionality for scenarios involving a victim announcing a legitimate prefix with corresponding ROAs.

```
_get_announcements()

_get_announcements()

Scenario
(Base Class)

VictimsPrefix
(scenarios/custom_scenarios/victims_prefix.py)

PrefixHijack
(scenarios/custom_scenarios/pre_rov/prefix_hijack.py)

SubprefixHijack
(scenarios/custom_scenarios/pre_rov/subprefix_hijack.py)

Returns victim prefix
+ attacker prefix

Returns victim prefix
+ attacker subprefix
```

**Sources:**

- [bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/prefix_hijack.py1-50](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/prefix_hijack.py#L1-L50)
- [bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/subprefix_hijack.py1-55](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/subprefix_hijack.py#L1-L55)

---

## PrefixHijack Attack

The `PrefixHijack` class implements a basic prefix hijacking attack where the attacker announces the exact same prefix as the victim, competing for routing traffic.

### Attack Mechanism

In a prefix hijack:

1. **Victim** announces a legitimate prefix (e.g., `1.0.0.0/24`)
2. **Attacker** announces the same prefix (`1.0.0.0/24`) with its own AS number as the origin
3. ASes without ROV choose between the announcements based on BGP path selection (typically preferring shorter AS paths or customer routes)

### Implementation Details

The `PrefixHijack` class overrides two key methods:
MethodPurposeReturns`_get_announcements()`Generates all announcements for the scenario`tuple[Ann, ...]` containing victim and attacker announcements`_get_prefix_attacker_anns()`Helper to generate attacker's announcements`tuple[Ann, ...]` with same prefix as victim
**Key Code Structure:**

```
For each attacker_asn

PrefixHijack._get_announcements()

super()._get_announcements()
(from VictimsPrefix)

_get_prefix_attacker_anns()

Concatenate:
victim_anns + attacker_anns

Return tuple[Ann, ...]

Create AnnCls
prefix=PREFIX
as_path=(attacker_asn,)
timestamp=ATTACKER
```

The attacker announcements are generated in [`_get_prefix_attacker_anns()`](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/`_get_prefix_attacker_anns()`):

- **Prefix**: `Prefixes.PREFIX.value` (same as victim)
- **AS Path**: `(attacker_asn,)` (single-hop path)
- **Timestamp**: `Timestamps.ATTACKER.value` (marks as attacker announcement)

### ROA Status

Against ROV-enabled ASes:

- **Victim announcement**: Valid by ROA (correct origin)
- **Attacker announcement**: Invalid by ROA (incorrect origin)

ROV-enabled ASes will reject the attacker's announcement, making this attack ineffective against networks with ROV deployed.

**Sources:**

- [bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/prefix_hijack.py13-49](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/prefix_hijack.py#L13-L49)

---

## SubprefixHijack Attack

The `SubprefixHijack` class implements a more sophisticated attack where the attacker announces a more specific (longer prefix) subprefix of the victim's announced prefix.

### Attack Mechanism

In a subprefix hijack:

1. **Victim** announces a broad prefix (e.g., `1.0.0.0/24`)
2. **Attacker** announces a more specific subprefix (e.g., `1.0.0.0/25`)
3. Due to BGP's longest-prefix-match routing, the attacker's more specific prefix is preferred even by ROV-enabled ASes if they lack a ROA covering the subprefix

### Why This Attack is More Effective

The subprefix hijack exploits two BGP behaviors:

1. **Longest Prefix Match**: Routers always prefer more specific prefixes
2. **ROA Coverage Gaps**: If the victim's ROA only covers `/24` but not `/25`, the attacker's `/25` announcement has "Unknown" ROA status (not Invalid)

AnnouncementPrefixOriginROA StatusVictim`1.0.0.0/24`Victim ASNValidAttacker`1.0.0.0/25`Attacker ASNInvalid by ROA origin
However, even with Invalid ROA status, the more specific prefix often wins due to prefix length preference in routing.

### Implementation Details

Similar structure to `PrefixHijack`, but with a different prefix for the attacker:

```
SubprefixHijack._get_announcements()

super()._get_announcements()
(from VictimsPrefix)

_get_subprefix_attacker_anns()

Announcement:
prefix=PREFIX (e.g., /24)
as_path=(victim_asn,)

For each attacker_asn

Create AnnCls:
prefix=SUBPREFIX (e.g., /25)
as_path=(attacker_asn,)
timestamp=ATTACKER

Concatenate:
victim_anns + attacker_anns

Return tuple[Ann, ...]
```

The key difference is in [`_get_subprefix_attacker_anns()`](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/`_get_subprefix_attacker_anns()`):

- **Prefix**: `Prefixes.SUBPREFIX.value` (more specific than victim's `Prefixes.PREFIX.value`)
- **AS Path**: `(attacker_asn,)` (single-hop path)
- **Timestamp**: `Timestamps.ATTACKER.value`

### Attack Success Conditions

This attack succeeds even against some ROV-enabled ASes because:

- The more specific prefix length takes precedence in routing decisions
- ROV policies may vary in how they handle announcements that are Invalid by origin but more specific

**Sources:**

- [bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/subprefix_hijack.py13-54](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/subprefix_hijack.py#L13-L54)

---

## Announcement Generation Architecture

Both pre-ROV attacks follow a consistent announcement generation pattern that integrates with the simulation engine.

```
AS Graph Seeding

Announcement Creation

Scenario Instance

Simulation Engine

BaseSimulationEngine

setup()
Initialize scenario

PrefixHijack or
SubprefixHijack

_get_announcements()

VictimsPrefix._get_announcements()

_get_prefix_attacker_anns()
or
_get_subprefix_attacker_anns()

scenario_config.AnnCls

Victim Announcements:
prefix=PREFIX
origin=victim_asn

Attacker Announcements:
prefix=PREFIX or SUBPREFIX
origin=attacker_asn

Seed announcements
into AS local RIBs

Begin BGP propagation
```

### Announcement Attributes

Each announcement created by these scenarios includes:
AttributeDescriptionSet By`prefix`IP prefix being announced`Prefixes` enum value`as_path`Sequence of AS numbers in the pathTuple starting with origin ASN`timestamp`When the announcement was made`Timestamps.VICTIM` or `Timestamps.ATTACKER``seed_asn`(implicit) ASN where announcement originatesDefaults to first ASN in `as_path``next_hop_asn`(implicit) Next hop for the announcementDefaults to first ASN in `as_path`
The `scenario_config.AnnCls` is typically the `Announcement` class but can be customized for specific scenarios (e.g., ASPA-specific announcement types).

**Sources:**

- [bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/prefix_hijack.py16-49](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/prefix_hijack.py#L16-L49)
- [bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/subprefix_hijack.py21-54](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/subprefix_hijack.py#L21-L54)

---

## Attack Scenario Comparison

### Feature Matrix
FeaturePrefixHijackSubprefixHijack**Attacker Prefix**Same as victimMore specific than victim**ROA Status (Attacker)**Invalid by originInvalid by origin and length**Effective Against Basic BGP**✓ Yes✓ Yes**Effective Against ROV**✗ No⚠️ Partial (depends on policy)**Requires Path Manipulation**✗ No✗ No**Attack Sophistication**LowLow-Medium
### Code Structure Comparison

Both classes follow an identical structure with only the announcement generation differing:

```
SubprefixHijack

_get_announcements()

super() call

_get_subprefix_attacker_anns()

Prefixes.SUBPREFIX

PrefixHijack

_get_announcements()

super() call

_get_prefix_attacker_anns()

Prefixes.PREFIX
```

The only implementation difference is the prefix used in attacker announcements:

- `PrefixHijack`: Uses `Prefixes.PREFIX.value` (line 44 of [prefix_hijack.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/prefix_hijack.py))
- `SubprefixHijack`: Uses `Prefixes.SUBPREFIX.value` (line 49 of [subprefix_hijack.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/subprefix_hijack.py))

**Sources:**

- [bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/prefix_hijack.py13-49](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/prefix_hijack.py#L13-L49)
- [bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/subprefix_hijack.py13-54](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/subprefix_hijack.py#L13-L54)

---

## Usage in Simulations

Pre-ROV attack scenarios are specified in simulation configuration via `ScenarioConfig` objects. See [Scenario Configuration](/blcrdbob3/bgpy_pkg/4.2-scenario-configuration) for details on configuring scenarios in simulations.

### Typical Simulation Setup

```
# Example configuration (conceptual)
scenario_configs = [
    ScenarioConfig(
        ScenarioCls=PrefixHijack,
        AdoptPolicyCls=ROV,
        BasePolicyCls=BGP,
        num_attackers=1,
        num_victims=1
    ),
    ScenarioConfig(
        ScenarioCls=SubprefixHijack,
        AdoptPolicyCls=ROV,
        BasePolicyCls=BGP,
        num_attackers=1,
        num_victims=1
    )
]
```

These scenarios are particularly useful for:

1. **Baseline measurements**: Establishing attack success rates against basic BGP
2. **ROV effectiveness testing**: Measuring how ROV deployment reduces attack success
3. **Policy comparison**: Comparing ROV with more advanced policies like ASPA or BGPSec

**Sources:**

- [bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/prefix_hijack.py1-50](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/prefix_hijack.py#L1-L50)
- [bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/subprefix_hijack.py1-55](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/pre_rov/subprefix_hijack.py#L1-L55)