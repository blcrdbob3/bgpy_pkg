# Other Security Policies
Relevant source files
- [bgpy/shared/exceptions.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/shared/exceptions.py)
- [bgpy/simulation_engine/ann_containers/ann_container.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/ann_containers/ann_container.py)
- [bgpy/simulation_engine/ann_containers/ribs_in.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/ann_containers/ribs_in.py)
- [bgpy/simulation_engine/announcement.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/announcement.py)
- [bgpy/simulation_engine/policies/aspa/aspa.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/aspa.py)
- [bgpy/simulation_engine/policies/bgp/bgp/bgp.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/bgp.py)
- [bgpy/simulation_engine/policies/bgp/bgp/bgp.pyi](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/bgp.pyi)
- [bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/process_incoming_funcs.py)
- [bgpy/simulation_engine/policies/bgp/bgp/propagate_funcs.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/propagate_funcs.py)
- [bgpy/simulation_engine/policies/bgp/bgp_full.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp_full.py)
- [bgpy/simulation_engine/policies/bgpsec/bgpsec.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgpsec/bgpsec.py)
- [bgpy/simulation_engine/policies/bgpsec/bgpsec_full.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgpsec/bgpsec_full.py)
- [bgpy/simulation_engine/policies/path_end/path_end.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/path_end/path_end.py)
- [bgpy/simulation_engine/policies/rost/__init__.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rost/__init__.py)
- [bgpy/simulation_engine/policies/rost/rost_full.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rost/rost_full.py)
- [bgpy/simulation_engine/policies/rost/rost_trusted_repository.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rost/rost_trusted_repository.py)
- [bgpy/tests/engine_tests/engine_test_configs/internals/__init__.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/engine_test_configs/internals/__init__.py)
- [bgpy/tests/engine_tests/engine_test_configs/internals/internal_config_007.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/engine_test_configs/internals/internal_config_007.py)
- [bgpy/tests/engine_tests/engine_test_outputs/internal_config_007/engine_gt.yaml](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/engine_test_outputs/internal_config_007/engine_gt.yaml)
- [bgpy/tests/engine_tests/engine_test_outputs/internal_config_007/graph_data_gt.csv](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/engine_test_outputs/internal_config_007/graph_data_gt.csv)
- [bgpy/tests/engine_tests/engine_test_outputs/internal_config_007/graph_data_gt.pickle](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/engine_test_outputs/internal_config_007/graph_data_gt.pickle)
- [bgpy/tests/engine_tests/engine_test_outputs/internal_config_007/outcomes_gt.yaml](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/engine_test_outputs/internal_config_007/outcomes_gt.yaml)
- [bgpy/utils/engine_runner/diagram.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/diagram.py)

## Purpose and Scope

This page documents BGP security policies that don't fit into the main policy families covered in previous sections. These include:

- **PathEnd**: Path-end validation to detect fake provider attacks
- **BGPSec**: Cryptographic path validation using digital signatures
- **RoST**: Route origin and path validation using a trusted repository

For information about base BGP routing (BGP, BGPFull), see [Base BGP Policies](/blcrdbob3/bgpy_pkg/6.1-base-bgp-policies). For ROV and ROV++ policies, see [Route Origin Validation](/blcrdbob3/bgpy_pkg/6.2-route-origin-validation-(rov)) and [ROV++ Policies](/blcrdbob3/bgpy_pkg/6.3-rov++-policies). For ASPA-based policies, see [ASPA Policy Family](/blcrdbob3/bgpy_pkg/6.4-aspa-policy-family).

---

## Policy Hierarchy

All policies documented on this page extend from either `ROV` or `BGPFull`, inheriting their base functionality while adding specialized security mechanisms.

```
Policy
(Abstract Base)

BGP
Basic Routing

BGPFull
+RIBs +Withdrawals

ROV
Route Origin Validation

BGPFullIgnoreInvalid

PathEnd
Path-End Validation

BGPSec
Cryptographic Paths

BGPSecFull
BGPSec +Full RIBs

RoSTFull
Trusted Repository
```

**Sources:**[bgpy/simulation_engine/policies/path_end/path_end.py1-35](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/path_end/path_end.py#L1-L35)[bgpy/simulation_engine/policies/bgpsec/bgpsec.py1-140](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgpsec/bgpsec.py#L1-L140)[bgpy/simulation_engine/policies/bgpsec/bgpsec_full.py1-10](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgpsec/bgpsec_full.py#L1-L10)[bgpy/simulation_engine/policies/rost/rost_full.py1-79](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rost/rost_full.py#L1-L79)

---

## PathEnd Policy

### Overview

`PathEnd` detects **fake provider attacks** where an attacker forges an AS path by inserting itself between a legitimate origin and a fake provider AS. PathEnd validates that the second-to-last AS in a path is actually a neighbor of the origin AS.

### Implementation Details

The `PathEnd` class extends `ROV` and overrides the `_valid_ann()` method to add path-end validation.

**Key Method: `_valid_ann()`**

[bgpy/simulation_engine/policies/path_end/path_end.py15-34](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/path_end/path_end.py#L15-L34)

```
No

Yes

No

Yes

Yes

No

_valid_ann() called

Is origin AS
deploying PathEnd?

Path length > 1?

Get origin AS object
from as_graph.as_dict

Is as_path[-2]
a real neighbor
of origin?

Call super()._valid_ann()
(ROV validation)

Return False
(Fake provider detected)
```

### Validation Logic

1. **Extract origin ASN**: `origin_asn = ann.origin` (returns `ann.as_path[-1]`)
2. **Check if origin deploys PathEnd**: Look up origin in `as_graph.as_dict` and verify `isinstance(origin_as_obj.policy, PathEnd)`
3. **Validate path length**: Only check paths with `len(ann.as_path) > 1`
4. **Verify second-to-last AS**: Iterate through origin's neighbors to confirm `ann.as_path[-2]` matches a real neighbor's ASN
5. **Fall back to ROV**: If valid or origin doesn't deploy PathEnd, defer to `super()._valid_ann()` for ROV checks

**Sources:**[bgpy/simulation_engine/policies/path_end/path_end.py1-35](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/path_end/path_end.py#L1-L35)

---

## BGPSec Policy Family

### Overview

BGPSec provides **cryptographic path validation** by maintaining a separate signed AS path (`bgpsec_as_path`) alongside the regular AS path. Each AS digitally signs the path, and receiving ASes can verify the entire chain of signatures.

### Class Structure
ClassExtendsRIBs SupportWithdrawalsPurpose`BGPSec``ROV`NoNoBasic BGPSec with cryptographic validation`BGPSecFull``BGPSec`, `BGPFull`Yes (RIBsIn, RIBsOut)YesBGPSec with full RIB management
### Announcement Attributes

BGPSec uses two additional announcement attributes defined in [bgpy/simulation_engine/announcement.py38-43](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/announcement.py#L38-L43):

- **`bgpsec_next_asn`**: The next AS that should receive the control plane announcement (opposite direction of `next_hop_asn`)
- **`bgpsec_as_path`**: The cryptographically signed AS path (empty tuple if invalid)

### BGPSec Validation Flow

```
Propagation Phase

Yes

No

_policy_propagate(neighbor, ann)

Is neighbor
BGPSec?

next_asn = neighbor.asn
path = ann.bgpsec_as_path

next_asn = None
path = ()

ann.copy({'bgpsec_next_asn': next_asn,
'bgpsec_as_path': path})

Processing Phase

Valid

Invalid

_copy_and_process(ann, recv_rel)

bgpsec_valid(ann, self.asn)

bgpsec_as_path =
(self.asn, *ann.bgpsec_as_path)

bgpsec_as_path = ()

super()._copy_and_process()
with bgpsec_as_path

Seeding Phase

Yes

No

seed_ann(ann)

Is as_path == (self.asn,)?

ann = ann.copy({'bgpsec_as_path': ann.as_path})

super().seed_ann(ann)
```

### Key Methods

**1. Validation Method**

[bgpy/simulation_engine/policies/bgpsec/bgpsec.py35-38](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgpsec/bgpsec.py#L35-L38)

The static method `bgpsec_valid(ann, asn)` returns `True` if:

- `ann.bgpsec_next_asn == asn` (announcement was intended for this AS)
- `ann.bgpsec_as_path == ann.as_path` (signed path matches announced path)

**2. Seeding Method**

[bgpy/simulation_engine/policies/bgpsec/bgpsec.py27-33](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgpsec/bgpsec.py#L27-L33)

When seeding an announcement at an origin AS (where `ann.as_path == (self.as_.asn,)`), initializes `bgpsec_as_path` to match the AS path.

**3. Processing Method**

[bgpy/simulation_engine/policies/bgpsec/bgpsec.py64-88](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgpsec/bgpsec.py#L64-L88)

When processing incoming announcements, `_copy_and_process()`:

- Validates the announcement using `bgpsec_valid()`
- If valid: prepends `self.as_.asn` to `bgpsec_as_path`
- If invalid: clears `bgpsec_as_path` to empty tuple

**4. Propagation Method**

[bgpy/simulation_engine/policies/bgpsec/bgpsec.py40-61](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgpsec/bgpsec.py#L40-L61)

`_policy_propagate()` customizes announcement propagation:

- If sending to a `BGPSec` neighbor: sets `bgpsec_next_asn` and maintains `bgpsec_as_path`
- If sending to a non-BGPSec neighbor: clears both fields (downgrades to regular BGP)

### Gao-Rexford Preference

BGPSec overrides `_get_best_ann_by_gao_rexford()` to implement "security third" preference ordering:

1. **Local preference** (by relationship: ORIGIN > CUSTOMERS > PEERS > PROVIDERS)
2. **AS path length** (shorter is better)
3. **BGPSec validity** (valid paths preferred over invalid)
4. **Lowest neighbor ASN** (tiebreaker)

[bgpy/simulation_engine/policies/bgpsec/bgpsec.py103-139](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgpsec/bgpsec.py#L103-L139)

This ordering reflects survey results from "A Survey of Interdomain Routing Policies" where the majority of users prefer security as the third criteria.

**Sources:**[bgpy/simulation_engine/policies/bgpsec/bgpsec.py1-140](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgpsec/bgpsec.py#L1-L140)[bgpy/simulation_engine/policies/bgpsec/bgpsec_full.py1-10](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgpsec/bgpsec_full.py#L1-L10)[bgpy/simulation_engine/announcement.py38-43](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/announcement.py#L38-L43)

---

## RoST Policy

### Overview

`RoSTFull` (Route origin and path validation using Signed Tokens) implements a **trusted repository** mechanism that tracks announcement withdrawals across the network. When an AS receives a withdrawal, it stores this information in a trie structure and uses it to suppress or unsuppress announcements in subsequent propagation rounds.

### Architecture

```
Trie Structure

RoSTTrustedRepository (Singleton)

RoSTFull Policy

RoSTFull
(extends BGPFullIgnoreInvalid)

withdraw_ann_from_neighbors()

process_incoming_anns()

add_recv_q_to_rost_trusted_repository()

remove_anns_from_recv_q_that_should_be_withdrawn()

add_suppressed_withdrawals_back_to_recv_q()

rost_trusted_repository
(class variable)

_withdrawal_as_path_root
(RoSTTrustedRepoNode)

add_ann(ann)

seen_withdrawal(ribs_in_ann, checking_asn)

RoSTTrustedRepoNode

as_path_branches: dict[int, Node]

end_of_as_path_prefixes:
set[(prefix, as_path)]
```

### RoSTTrustedRepository Trie Structure

The repository uses a **reversed AS path trie** where paths are traversed from origin to first hop. This allows efficient checking of whether a withdrawal has been seen for any prefix along a given path.

**Example Trie After Multiple Withdrawals:**

```
Root
├── ASN 777 (origin)
│   └── ASN 4
│       └── ASN 666
│           ├── end_prefixes: {("1.2.0.0/16", (777, 4, 666))}
│           └── ASN 3
│               └── end_prefixes: {("1.2.0.0/16", (777, 4, 666, 3))}
└── ASN 999 (origin)
    └── ASN 123
        └── end_prefixes: {("2.3.0.0/16", (999, 123))}

```

**Key Methods:**
MethodPurposeLocation`add_ann(ann)`Add withdrawal to trie or remove it if `ann.withdraw == False`[rost_trusted_repository.py46-68](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/rost_trusted_repository.py#L46-L68)`seen_withdrawal(ribs_in_ann, checking_asn)`Check if withdrawal exists for this announcement[rost_trusted_repository.py70-83](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/rost_trusted_repository.py#L70-L83)`clear()`Reset the entire repository[rost_trusted_repository.py43-44](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/rost_trusted_repository.py#L43-L44)
### RoSTFull Processing Flow

```
ribs_in
RoSTTrustedRepository
recv_q
RoSTFull AS
Neighbor
ribs_in
RoSTTrustedRepository
recv_q
RoSTFull AS
Neighbor
process_incoming_anns() called
loop
[For each announcement/withdrawal]
Remove suppressed anns from recv_q
alt
[Withdrawal seen]
loop
[For each non-withdrawal ann]
Add suppressed withdrawals back
alt
[Not in recv_q]
loop
[For each ribs_in ann]
Iterate over incoming anns
Get ann
Process ann with _copy_and_process()
add_ann(processed_ann)
Iterate over anns
Get ann
seen_withdrawal(ann, self.asn)?
True/False
Remove ann from recv_q
Iterate over stored anns
Get ann
Is withdrawal in recv_q?
seen_withdrawal(ann, self.asn)?
True
Add withdrawal for this ann
super().process_incoming_anns()
```

### Processing Phase Methods

**1. Adding Received Announcements to Repository**

[bgpy/simulation_engine/policies/rost/rost_full.py38-44](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rost/rost_full.py#L38-L44)

`add_recv_q_to_rost_trusted_repository()` iterates through `recv_q` and adds all announcements (both regular and withdrawals) to the repository. Announcements are processed first to ensure they have the correct `recv_relationship`.

**2. Removing Suppressed Announcements**

[bgpy/simulation_engine/policies/rost/rost_full.py46-57](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rost/rost_full.py#L46-L57)

`remove_anns_from_recv_q_that_should_be_withdrawn()` filters `recv_q` to remove any non-withdrawal announcements that have a corresponding withdrawal in the repository.

**3. Re-adding Suppressed Withdrawals**

[bgpy/simulation_engine/policies/rost/rost_full.py59-78](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rost/rost_full.py#L59-L78)

`add_suppressed_withdrawals_back_to_recv_q()` checks `ribs_in` for announcements that:

- Don't have a withdrawal currently in `recv_q`
- Have been withdrawn according to the repository

For these announcements, it creates and adds withdrawal announcements to `recv_q`.

### Withdrawal Handling

When an AS using `RoSTFull` withdraws an announcement:

[bgpy/simulation_engine/policies/rost/rost_full.py24-28](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rost/rost_full.py#L24-L28)

```
def withdraw_ann_from_neighbors(self, withdraw_ann: Ann) -> None:
    """Adds withdrawals you create to RoST Trusted Repo"""
    self.rost_trusted_repository.add_ann(withdraw_ann)
    super().withdraw_ann_from_neighbors(withdraw_ann)
```

This ensures that locally-generated withdrawals are also tracked in the repository before being propagated to neighbors.

### Singleton Repository

The `RoSTTrustedRepository` is a **class variable** shared across all `RoSTFull` instances:

[bgpy/simulation_engine/policies/rost/rost_full.py18](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rost/rost_full.py#L18-L18)

```
rost_trusted_repository = RoSTTrustedRepository()
```

This singleton pattern means all RoST-deploying ASes share the same withdrawal information, simulating a globally-distributed trusted repository. The repository is cleared at the start of each simulation trial:

[bgpy/simulation_engine/policies/rost/rost_full.py20-22](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rost/rost_full.py#L20-L22)

**Sources:**[bgpy/simulation_engine/policies/rost/rost_full.py1-79](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rost/rost_full.py#L1-L79)[bgpy/simulation_engine/policies/rost/rost_trusted_repository.py1-84](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rost/rost_trusted_repository.py#L1-L84)

---

## Policy Comparison Table
FeaturePathEndBGPSecBGPSecFullRoSTFull**Extends**ROVROVBGPSec + BGPFullBGPFullIgnoreInvalid**Primary Defense**Fake provider attacksPath forgeryPath forgery + full RIBsWithdrawal suppression attacks**Validation Mechanism**Check origin's neighborsCryptographic signaturesCryptographic signaturesTrusted withdrawal repository**Additional Attributes**None`bgpsec_as_path`, `bgpsec_next_asn``bgpsec_as_path`, `bgpsec_next_asn`None**RIBsIn/RIBsOut Support**NoNoYesYes**Withdrawal Support**NoNoYesYes**Computational Cost**LowHigh (signature validation)HighMedium (trie traversal)**Deployment Requirement**Origin must deployAll ASes on path must deployAll ASes on path must deployPartial deployment effective**Key Override**`_valid_ann()``_valid_ann()`, `_copy_and_process()`, `_policy_propagate()`, `_get_best_ann_by_gao_rexford()`Inherits from BGPSec`process_incoming_anns()`, `withdraw_ann_from_neighbors()`
### When to Use Each Policy

- **PathEnd**: Lightweight protection against fake provider attacks when origin AS deploys the policy
- **BGPSec**: Maximum security against path manipulation when full deployment is feasible
- **BGPSecFull**: BGPSec security in simulations requiring detailed RIB tracking and withdrawal modeling
- **RoSTFull**: Protection against withdrawal suppression attacks and route flap damping manipulation

**Sources:**[bgpy/simulation_engine/policies/path_end/path_end.py1-35](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/path_end/path_end.py#L1-L35)[bgpy/simulation_engine/policies/bgpsec/bgpsec.py1-140](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgpsec/bgpsec.py#L1-L140)[bgpy/simulation_engine/policies/bgpsec/bgpsec_full.py1-10](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgpsec/bgpsec_full.py#L1-L10)[bgpy/simulation_engine/policies/rost/rost_full.py1-79](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/rost/rost_full.py#L1-L79)

---

## Testing Examples

The test suite includes scenarios that validate these policies. For example, `internal_config_007` tests RoSTFull behavior:

[bgpy/tests/engine_tests/engine_test_configs/internals/internal_config_007.py1-94](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/engine_test_configs/internals/internal_config_007.py#L1-L94)

This test configures a network where:

- Some ASes deploy `RoSTFull`
- Others deploy `BGPFullIgnoreInvalid` or `BGPFullSuppressWithdrawals`
- The scenario uses a `WithdrawalValidPrefixScenario` that withdraws a valid prefix after the first propagation round
- Tests verify that RoST-deploying ASes correctly suppress announcements with routing loops after processing withdrawals

**Sources:**[bgpy/tests/engine_tests/engine_test_configs/internals/internal_config_007.py1-94](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/engine_test_configs/internals/internal_config_007.py#L1-L94)[bgpy/tests/engine_tests/engine_test_outputs/internal_config_007/engine_gt.yaml1-561](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/engine_test_outputs/internal_config_007/engine_gt.yaml#L1-L561)