# Creating Custom Policies
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
- [scripts/two_multi_inheritance_ex.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/scripts/two_multi_inheritance_ex.py)

This page provides a comprehensive guide for implementing custom BGP security policies in BGPy. It covers the abstract `Policy` base class, required methods, inheritance patterns, and best practices for extending existing policies.

For information about the built-in policies available in BGPy, see [BGP Policy Reference](/blcrdbob3/bgpy_pkg/6-bgp-policy-reference). For details on how policies are assigned during simulation execution, see [Simulation Class and Execution Pipeline](/blcrdbob3/bgpy_pkg/4.1-simulation-class-and-execution-pipeline).

---

## Policy Base Class Architecture

All BGP policies in BGPy inherit from the abstract `Policy` base class, which defines the interface for announcement processing, propagation, and ROA validation.

```
Policy
(Abstract Base Class)
bgpy/simulation_engine/policies/policy.py

BGP
Basic Routing

BGPFull
+RIBs +Withdrawals

ROV
Route Origin Validation

PeerROV
Peer-only ROV

ROVPPV1Lite
+Blackholing

ROVPPV2Lite
+Selective Propagation

ROVEnforceFirstAS
+First ASN Check

ROVEdgeFilter
+Edge Filtering
```

**Sources:**[bgpy/simulation_engine/policies/policy.py1-167](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/policy.py#L1-L167)[bgpy/simulation_engine/policies/rov/rov.py1-29](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rov/rov.py#L1-L29)[bgpy/simulation_engine/policies/rov/peer_rov.py1-33](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rov/peer_rov.py#L1-L33)

---

## Required Abstract Methods

The `Policy` class requires implementation of several abstract methods. The table below categorizes them by functionality:
CategoryMethodPurposeSignature**Receiving**`receive_ann`Accept incoming announcements`(ann: Ann) -> None`**Processing**`process_incoming_anns`Process all announcements from a relationship`(from_rel: Relationships, propagation_round: int, scenario: Scenario, reset_q: bool) -> None`**Propagation**`propagate_to_providers`Send announcements to provider ASes`() -> None`**Propagation**`propagate_to_customers`Send announcements to customer ASes`() -> None`**Propagation**`propagate_to_peers`Send announcements to peer ASes`() -> None`**Serialization**`__to_yaml_dict__`Convert policy to YAML dict`() -> dict[Any, Any]`**Serialization**`__from_yaml_dict__`Reconstruct policy from YAML`(dct, yaml_tag) -> Policy`
**Sources:**[bgpy/simulation_engine/policies/policy.py51-167](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/policy.py#L51-L167)

---

## Automatic Policy Registration

When you define a new policy class, the `__init_subclass__` method automatically registers it with a unique name. This enables YAML serialization and policy lookup by name.

```
Define Policy Class
class MyPolicy(ROV):
name = 'MyPolicy'

init_subclass
Automatic Registration

name_to_subclass_dict
{'MyPolicy': MyPolicy}

subclass_to_name_dict
{MyPolicy: 'MyPolicy'}

YamlAble Decoration
yaml_tag='MyPolicy'
```

**Key requirements:**

- Every policy **must** define a `name` class attribute
- Names **must** be unique across all policies
- The `__init_subclass__` method validates uniqueness at class definition time

**Sources:**[bgpy/simulation_engine/policies/policy.py21-40](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/policy.py#L21-L40)

---

## Creating a Simple Custom Policy

The most common pattern for creating a custom policy is to extend an existing policy (typically `BGP` or `ROV`) and override the `_valid_ann` method to customize announcement validation logic.

### Example: ROV Policy Implementation

The `ROV` policy demonstrates the simplest extension pattern:

```
ROV Policy Logic

Invalid

Valid/Unknown

Announcement Received

_valid_ann()
Check Validity

ann_is_invalid_by_roa()?

Return False
Reject Announcement

super()._valid_ann()
Standard BGP Checks

Return BGP Result
Accept if Valid
```

The implementation overrides only `_valid_ann` to add ROA validation:

```
# From bgpy/simulation_engine/policies/rov/rov.py
class ROV(BGP):
    name: str = "ROV"
    
    def _valid_ann(self, ann: "Ann", recv_rel: "Relationships") -> bool:
        # Reject invalid-by-ROA announcements
        if self.ann_is_invalid_by_roa(ann):
            return False
        # Use standard BGP validation for everything else
        else:
            return super()._valid_ann(ann, recv_rel)
```

**Sources:**[bgpy/simulation_engine/policies/rov/rov.py10-29](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rov/rov.py#L10-L29)

---

## Relationship-Specific Filtering

Some policies apply security policies selectively based on the relationship with the neighbor. The `PeerROV` policy demonstrates this pattern:

```
PeerROV Decision Logic

Yes

No

Yes

No

_valid_ann()
called

Invalid by ROA?

From Peer?

super()._valid_ann()
Standard BGP Logic

Return False
Reject
```

This pattern checks both ROA validity **and** the receiving relationship:
ConditionActionInvalid by ROA **AND** from peerRejectInvalid by ROA **AND** from provider/customerDelegate to standard BGPValid/Unknown by ROADelegate to standard BGP
**Sources:**[bgpy/simulation_engine/policies/rov/peer_rov.py10-33](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rov/peer_rov.py#L10-L33)

---

## Multiple Inheritance Patterns

More complex policies can inherit from multiple parent classes to combine behaviors. Python's Method Resolution Order (MRO) determines which method is called when multiple parents define the same method.

```
BGPSimplePolicy
Base Methods

BGP
Full Implementation

ASPASimplePolicy
Path Validation

ASPA
Combines ASPA + BGP

MRO: ASPA → ASPASimple → BGP → BGPSimple
Left-to-right, depth-first
```

### Example: Combining Two Security Mechanisms

The `ROVEnforceFirstAS` policy combines ROV with first-ASN validation:

```
# From bgpy/simulation_engine/policies/enforce_first_as/rov_enforce_first_as.py
class ROVEnforceFirstAS(EnforceFirstAS):
    name: str = "ROV + Enforce-First-AS"
    
    def _valid_ann(self, ann: "Ann", from_rel: "Relationships") -> bool:
        # First check ROV
        if self.ann_is_invalid_by_roa(ann):
            return False
        # Then delegate to EnforceFirstAS logic
        return super()._valid_ann(ann, from_rel)
```

**Inheritance chain:**`ROVEnforceFirstAS` → `EnforceFirstAS` → `ROV` → `BGP`

**Sources:**[bgpy/simulation_engine/policies/enforce_first_as/rov_enforce_first_as.py10-27](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/enforce_first_as/rov_enforce_first_as.py#L10-L27)[scripts/two_multi_inheritance_ex.py1-22](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/scripts/two_multi_inheritance_ex.py#L1-L22)

---

## Advanced Pattern: Overriding Propagation Logic

Some policies need to modify announcement propagation behavior. The `ROVPPV1Lite` policy demonstrates how to control which announcements are propagated.

```
ROV++V1 Lite Propagation

True

False

_policy_propagate()
called for each announcement

ann.rovpp_blackhole?

Return True
Policy handled propagation

Return False
Continue normal propagation
```

### Key Methods to Override
MethodPurposeWhen to Override`_policy_propagate`Control announcement propagationWhen you need to selectively block or modify propagation`process_incoming_anns`Custom processing before local RIB insertionWhen you need to add announcements (e.g., blackholes) or perform complex validation`_valid_ann`Announcement acceptance logicMost common override point for simple filtering
**Sources:**[bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py20-159](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py#L20-L159)

---

## ROA Validation Helper Methods

The `Policy` base class provides several helper methods for ROA validation. These methods interact with the global `ROAChecker` instance (`Policy.roa_checker`).
MethodReturn TypeDescription`ann_is_invalid_by_roa(ann)``bool`True if ROA marks announcement as invalid`ann_is_valid_by_roa(ann)``bool`True if ROA marks announcement as valid`ann_is_unknown_by_roa(ann)``bool`True if no ROA covers the announcement`ann_is_covered_by_roa(ann)``bool`True if any ROA exists for the prefix`ann_is_roa_non_routed(ann)``bool`True if ROA has origin AS 0 (non-routed)`get_roa_outcome(ann)``ROAOutcome`Full ROA outcome with validity and routing status
```
ann_is_invalid_by_roa()

ann_is_valid_by_roa()

get_roa_outcome()

get_roa_outcome_w_prefix_str_cached()

Policy Instance

Policy.roa_checker
(Global ROAChecker)

ROA Database
(from Scenario)
```

**Important:** The `roa_checker` is a **class variable** shared across all policy instances. ROAs are loaded into it at scenario initialization.

**Sources:**[bgpy/simulation_engine/policies/policy.py99-154](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/policy.py#L99-L154)

---

## Modifying Local RIB During Processing

Advanced policies may need to inject additional announcements into the local RIB during processing. The `ROVPPV1Lite` policy demonstrates this pattern for blackhole announcements.

```
ROV++V1 Blackhole Injection

process_incoming_anns()

super().process_incoming_anns()
Standard BGP Processing

_add_blackholes()
Inject Blackhole Announcements

_get_non_routed_blackholes_to_add()
Create blackholes for AS 0 ROAs

_get_routed_blackholes_to_add()
Create blackholes for invalid subprefixes

_add_blackholes_tolocal_rib()
Insert into local_rib

_recount_holes()
Update hole counts
```

### Pattern: Calling Super Before Custom Logic

The standard pattern for extending `process_incoming_anns` is:

1. Call `super().process_incoming_anns()` with `reset_q=False` to perform standard processing
2. Add your custom announcements to the local RIB
3. Perform any post-processing (e.g., recomputing metrics)
4. Call `self._reset_q(reset_q)` to optionally clear the receive queue

**Sources:**[bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py32-159](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite.py#L32-L159)

---

## Conditional Propagation Logic

Some policies need to propagate announcements differently based on their properties. The `ROVPPV2Lite` policy demonstrates conditional propagation for blackhole announcements.

```
ROV++V2 Blackhole Propagation Rules

Yes

No

Yes

No

Yes

No

Yes

No

Blackhole?

_send_competing_hijack_allowed()?

Return False
Continue normal

Received from
peer/provider/origin?

Sending to
customers?

Return True
Policy handled

Subprefix or
non-routed?

_process_outgoing_ann()
Send Announcement
```

**Key insight:** The return value of `_policy_propagate` indicates whether the policy has handled propagation:

- `True` = Policy handled propagation (don't continue with normal logic)
- `False` = Continue with normal propagation logic

**Sources:**[bgpy/simulation_engine/policies/rovpp/v2/base/rovpp_v2_lite.py22-66](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v2/base/rovpp_v2_lite.py#L22-L66)

---

## Policy with Full RIB Support

Policies can also be extended to support full RIB tracking (RIBsIn, RIBsOut, withdrawals). This is done through multiple inheritance with `BGPFull`.

```
ROVPPV1Lite
Blackhole Logic

ROVFull
RIBs + Withdrawals

ROVPPV1LiteFull
Combined: Blackholes + RIBs
```

### Example: Adapting Blackhole Logic for Full RIBs

When combining with `BGPFull`, some methods may need slight modifications to handle withdrawals:

```
# From bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite_full.py
class ROVPPV1LiteFull(ROVPPV1Lite, ROVFull):
    name: str = "ROV++V1 Lite Full"
    
    def _add_blackholes_tolocal_rib(self, blackholes: tuple["Ann", ...]) -> None:
        # Modified logic to handle withdrawal scenarios
        for blackhole in blackholes:
            existing_ann = self.local_rib.get(blackhole.prefix)
            if existing_ann is None:
                self.local_rib.add_ann(blackhole)
            elif self.ann_is_invalid_by_roa(existing_ann):
                # Would need withdrawal handling here
                raise NotImplementedError("Need to handle withdrawals...")
```

**Sources:**[bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite_full.py1-37](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v1/rovpp_v1_lite_full.py#L1-L37)[bgpy/simulation_engine/policies/rovpp/v2/base/rovpp_v2_lite_full.py1-14](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rovpp/v2/base/rovpp_v2_lite_full.py#L1-L14)

---

## Testing Custom Policies

Custom policies should be tested using the `EngineTester` framework with ground truth comparisons. The test structure typically:

1. Creates a `ScenarioConfig` specifying your custom policy
2. Instantiates the scenario with the custom policy
3. Runs simulation and compares against ground truth

### Example Test Structure

```
# Pattern from bgpy/tests/framework_tests/unit_tests/test_scenario.py
def test_custom_policy(engine):
    scenario_config = ScenarioConfig(
        ScenarioCls=SubprefixHijack,
        BasePolicyCls=BGP,
        AdoptPolicyCls=MyCustomPolicy,  # Your custom policy here
        num_attackers=1,
        num_victims=1,
    )
    
    scenario = SubprefixHijack(scenario_config=scenario_config, engine=engine)
    # Run assertions or comparisons
```

### Key Testing Considerations
AspectRecommendation**Attackers/Victims**Use `override_attacker_asns` and `override_victim_asns` for reproducibility**Announcements**Use `override_announcements` to test specific attack patterns**ROAs**Use `override_roas` to test ROA interaction**Multiple Scenarios**Test your policy against various attack scenarios (prefix hijack, subprefix, etc.)
**Sources:**[bgpy/tests/framework_tests/unit_tests/test_scenario.py1-385](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/framework_tests/unit_tests/test_scenario.py#L1-L385)

---

## Complete Policy Checklist

When creating a custom policy, ensure you:

- Define a unique `name` class attribute
- Inherit from appropriate base class(es) - typically `BGP`, `ROV`, or another existing policy
- Override only the methods you need to customize
- Call `super()` appropriately to leverage parent class logic
- Handle ROA validation using provided helper methods if applicable
- Test with multiple attack scenarios
- Document the security mechanism your policy implements
- Consider whether `BGPFull` support is needed for your use case

**Sources:**[bgpy/simulation_engine/policies/policy.py14-167](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/policy.py#L14-L167)[bgpy/simulation_engine/policies/rov/rov.py10-29](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rov/rov.py#L10-L29)