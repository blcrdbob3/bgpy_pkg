# Scenario Configuration
Relevant source files
- [.github/workflows/tests.yml](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/.github/workflows/tests.yml)
- [.pre-commit-config.yaml](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/.pre-commit-config.yaml)
- [LICENSE.txt](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/LICENSE.txt)
- [MANIFEST.in](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/MANIFEST.in)
- [README.md](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/README.md)
- [bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py)
- [bgpy/shared/enums.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/shared/enums.py)
- [bgpy/simulation_framework/scenarios/scenario.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py)
- [bgpy/simulation_framework/scenarios/scenario_config.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py)
- [bgpy/simulation_framework/simulation.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py)
- [pyproject.toml](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml)
- [requirements.txt](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/requirements.txt)
- [requirements_dev.txt](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/requirements_dev.txt)
- [setup.cfg](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/setup.cfg)
- [tox.ini](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/tox.ini)

## Purpose and Scope

This page documents the configuration system for BGP simulation scenarios in BGPy. It explains the `ScenarioConfig` dataclass, the `percent_adoptions` parameter, and how to configure simulation parameters that control attack scenarios, policy adoption, and network behavior.

For information about the overall simulation execution flow, see [Simulation Class and Execution Pipeline](/blcrdbob3/bgpy_pkg/4.1-simulation-class-and-execution-pipeline). For details about implementing custom attack scenarios, see [Creating Custom Scenarios](/blcrdbob3/bgpy_pkg/10.1-creating-custom-scenarios). For the catalog of available attack scenarios, see [Attack Scenario Reference](/blcrdbob3/bgpy_pkg/7-attack-scenario-reference).

---

## ScenarioConfig Overview

The `ScenarioConfig` is an immutable, frozen dataclass that contains all parameters needed to set up and run a BGP attack scenario. It is reused across multiple trials to ensure consistency and is the central configuration object passed to the `Simulation` class.

```
Scenario Layer

Simulation Layer

Configuration Layer

scenario_configs:
tuple[ScenarioConfig]

for each scenario_config

stores as
.scenario_config

reads policy classes from

ScenarioConfig
(frozen dataclass)

Simulation
init

_run_chunk

Scenario
init

setup_engine

get_policy_cls
```

**Sources:**[bgpy/simulation_framework/scenarios/scenario_config.py28-81](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L28-L81)[bgpy/simulation_framework/simulation.py67-73](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L67-L73)[bgpy/simulation_framework/scenarios/scenario.py33-56](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L33-L56)

### Key Properties
PropertyDescription**Immutable**Frozen dataclass ensures configuration cannot change during execution**Reusable**Same config used across multiple trials for consistency**Hashable**Can be used as dictionary key for data aggregation**Serializable**Supports YAML serialization for reproducible tests
**Sources:**[bgpy/simulation_framework/scenarios/scenario_config.py28](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L28-L28)

---

## Core Configuration Parameters

### Scenario Class Selection

The `ScenarioCls` parameter specifies which attack scenario to simulate.

```
from bgpy.simulation_framework import ScenarioConfig, SubprefixHijack
from bgpy.simulation_engine import ROV, BGP

config = ScenarioConfig(
    ScenarioCls=SubprefixHijack,
    AdoptPolicyCls=ROV,
    BasePolicyCls=BGP,
)
```

**Parameter Details:**
ParameterTypeDescription`ScenarioCls``type[Scenario]`The attack scenario class (e.g., `PrefixHijack`, `SubprefixHijack`)
During initialization, the `Scenario` validates that the config's `ScenarioCls` matches the instantiated scenario class:

**Sources:**[bgpy/simulation_framework/scenarios/scenario_config.py35](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L35-L35)[bgpy/simulation_framework/scenarios/scenario.py48-53](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L48-L53)

### Policy Class Configuration

Three policy class parameters control the security posture of different AS groups:

```
Policy Assignment Logic

Yes

No

Yes

No

Yes

No

Yes

No

AS Object

get_policy_cls

AS in
attacker_asns?

AttackerBasePolicyCls

AS in
_default_adopters
(victims)?

AdoptPolicyCls

AS in
hardcoded_asn_cls_dict?

Hardcoded Policy

AS in
adopting_asns?

BasePolicyCls
```

**Sources:**[bgpy/simulation_framework/scenarios/scenario.py358-373](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L358-L373)
ParameterTypeDefaultDescription`BasePolicyCls``type[Policy]``BGP`Policy for non-adopting ASes`AdoptPolicyCls``type[Policy]``BGP`*Policy for adopting ASes (victims always adopt)`AttackerBasePolicyCls``type[Policy]``None`Optional policy override for attackers
*If not specified, defaults to `BasePolicyCls` in `__post_init__`.

**Important Validation:** If `AdoptPolicyCls` inherits from `BGPFull` (supports withdrawals), then `BasePolicyCls` must also inherit from `BGPFull` to prevent mixing withdrawal-aware and non-withdrawal-aware policies:

**Sources:**[bgpy/simulation_framework/scenarios/scenario_config.py41-43](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L41-L43)[bgpy/simulation_framework/simulation.py196-204](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L196-L204)

### Propagation Rounds

The `propagation_rounds` parameter controls how many times the simulation engine runs BGP propagation.

```
config = ScenarioConfig(
    ScenarioCls=AccidentalRouteLeak,
    propagation_rounds=2,  # Route leak needs two rounds
    # ...
)
```
ParameterTypeDescription`propagation_rounds``int`Number of propagation rounds (defaults to `ScenarioCls.min_propagation_rounds`)
If not specified, `propagation_rounds` defaults to the scenario's `min_propagation_rounds` value in `__post_init__`. The configuration validates that the specified rounds meet the minimum requirement:

**Sources:**[bgpy/simulation_framework/scenarios/scenario_config.py37](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L37-L37)[bgpy/simulation_framework/scenarios/scenario_config.py94-117](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L94-L117)

---

## Attack and Victim Configuration

### Basic Parameters

```
config = ScenarioConfig(
    ScenarioCls=PrefixHijack,
    num_attackers=3,
    num_victims=1,
    attacker_subcategory_attr=ASGroups.STUBS_OR_MH.value,
    victim_subcategory_attr=ASGroups.STUBS_OR_MH.value,
    # ...
)
```
ParameterTypeDefaultDescription`num_attackers``int``1`Number of attacker ASes`num_victims``int``1`Number of victim ASes`attacker_subcategory_attr``str``ASGroups.STUBS_OR_MH.value`AS group from which to select attackers`victim_subcategory_attr``str``ASGroups.STUBS_OR_MH.value`AS group from which to select victims
The subcategory attributes reference AS groups defined in the `ASGraph`. Common values include:
AS GroupDescription`ASGroups.STUBS_OR_MH.value`Stub or multihomed ASes`ASGroups.INPUT_CLIQUE.value`Top-tier ISPs`ASGroups.ETC.value`Transit ASes (not stubs, multihomed, or input clique)
**Sources:**[bgpy/simulation_framework/scenarios/scenario_config.py46-57](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L46-L57)[bgpy/shared/enums.py95-109](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/shared/enums.py#L95-L109)

### AS Selection Logic

```
Yes

No

Yes

No

Yes

No

Scenario.init

override_attacker_asns
is not None?

prev_attacker_asns
exists and
len == num_attackers?

prev_attacker_asns
exists and
len < num_attackers?

Use override_attacker_asns

Reuse prev_attacker_asns

Extend prev_attacker_asns
with random ASes

Randomly select
num_attackers ASes
from possible_attacker_asns

_get_possible_attacker_asns
from engine.as_graph.asn_groups
```

**Sources:**[bgpy/simulation_framework/scenarios/scenario.py101-166](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L101-L166)[bgpy/simulation_framework/scenarios/scenario.py187-220](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L187-L220)

### Override Parameters

For reproducible testing or specific scenarios, you can override the random AS selection:

```
config = ScenarioConfig(
    ScenarioCls=PrefixHijack,
    override_attacker_asns=frozenset([666]),
    override_victim_asns=frozenset([777]),
    override_adopting_asns=frozenset([1, 2, 3]),
    override_announcements=(Ann(...), ...),
    override_roas=(ROA(...), ...),
    # ...
)
```
ParameterTypeDescription`override_attacker_asns``frozenset[int] | None`Specific attacker ASNs (bypasses random selection)`override_victim_asns``frozenset[int] | None`Specific victim ASNs`override_adopting_asns``frozenset[int] | None`Specific adopting ASNs`override_announcements``tuple[Ann, ...] | None`Predefined announcements`override_roas``tuple[ROA, ...] | None`Predefined ROAs
These are primarily used by the test framework for deterministic ground truth validation.

**Sources:**[bgpy/simulation_framework/scenarios/scenario_config.py70-74](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L70-L74)

---

## Adoption Configuration

### Adoption Subcategories

The `adoption_subcategory_attrs` parameter specifies which AS groups should adopt the security policy. Adoption percentage is applied equally across all specified groups.

```
config = ScenarioConfig(
    ScenarioCls=SubprefixHijack,
    AdoptPolicyCls=ROV,
    adoption_subcategory_attrs=(
        ASGroups.STUBS_OR_MH.value,
        ASGroups.ETC.value,
        ASGroups.INPUT_CLIQUE.value,
    ),
    # ...
)
```
ParameterTypeDefaultDescription`adoption_subcategory_attrs``tuple[str, ...]``(STUBS_OR_MH, ETC, INPUT_CLIQUE)`AS groups across which to distribute adoption
**Sources:**[bgpy/simulation_framework/scenarios/scenario_config.py49-53](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L49-L53)

### Percent Adoptions

The `percent_adoptions` parameter in the `Simulation` class controls the deployment levels to simulate. It accepts both floating-point percentages and special enum values.

```
from bgpy.shared.enums import SpecialPercentAdoptions

sim = Simulation(
    percent_adoptions=(
        SpecialPercentAdoptions.ONLY_ONE,  # Exactly one AS adopts
        0.1,   # 10% adoption
        0.2,   # 20% adoption
        0.5,   # 50% adoption
        0.8,   # 80% adoption
        0.99,  # 99% adoption
        SpecialPercentAdoptions.ALL_BUT_ONE,  # All ASes adopt except one
    ),
    # ...
)
```

**Sources:**[bgpy/simulation_framework/simulation.py59-66](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L59-L66)

### SpecialPercentAdoptions Enum

```
Adoption Logic in _get_randomized_adopting_asns

SpecialPercentAdoptions

ONLY_ONE

ALL_BUT_ONE

0

float

ONLY_ONE
value=0

ALL_BUT_ONE
value=1

percent_adoption
type?

k = 1

k = len(possible_adopters) - 1

k = 0

k = ceil(len(possible_adopters)
* percent_adoption)

random.sample
(possible_adopters, k)
```

**Sources:**[bgpy/shared/enums.py111-123](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/shared/enums.py#L111-L123)[bgpy/simulation_framework/scenarios/scenario.py282-293](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L282-L293)

### Adopting AS Selection Algorithm

The `_get_randomized_adopting_asns` method implements the adoption selection logic:

```
ONLY_ONE

ALL_BUT_ONE

0

float

Done

_get_randomized_adopting_asns

adopting_asns = []

For each subcategory in
adoption_subcategory_attrs

asns = engine.as_graph
.asn_groups[subcategory]

possible_adopters =
asns - _preset_asns

percent_adoption
type?

k = 1

k = len(possible_adopters) - 1

k = 0

k = ceil(len(possible_adopters)
* percent_adoption)

adopting_asns.extend
random.sample(possible_adopters, k)

return frozenset(adopting_asns)
```

**Important:** ASes in `_preset_asns` (attackers, victims, and hardcoded ASes) are excluded from random adoption selection. Victims always adopt the `AdoptPolicyCls`, and attackers never adopt it.

**Sources:**[bgpy/simulation_framework/scenarios/scenario.py262-301](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L262-L301)[bgpy/simulation_framework/scenarios/scenario.py316-321](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L316-L321)

---

## Advanced Configuration Options

### Hardcoded Policy Assignments

The `hardcoded_asn_cls_dict` allows you to assign specific policies to specific ASNs, regardless of adoption percentage:

```
from frozendict import frozendict

config = ScenarioConfig(
    ScenarioCls=PrefixHijack,
    hardcoded_asn_cls_dict=frozendict({
        1234: CustomPolicy,
        5678: AnotherPolicy,
    }),
    # ...
)
```
ParameterTypeDescription`hardcoded_asn_cls_dict``frozendict[int, type[Policy]]`Map of ASN to Policy class for explicit assignments`hardcoded_base_asn_cls_dict``frozendict[int, type[Policy]]`Fallback policy map for non-adopting ASes
**Note:** Must use `frozendict` (not regular `dict`) because `ScenarioConfig` is a frozen dataclass and requires all fields to be hashable.

**Sources:**[bgpy/simulation_framework/scenarios/scenario_config.py61-68](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L61-L68)[bgpy/simulation_framework/scenarios/scenario.py366-373](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L366-L373)

### Custom Announcement Class

For scenarios requiring custom announcement behavior, you can specify a different announcement class:

```
config = ScenarioConfig(
    ScenarioCls=CustomScenario,
    AnnCls=CustomAnnouncement,
    # ...
)
```
ParameterTypeDefaultDescription`AnnCls``type[Ann]``Ann`The announcement class to use for this scenario
**Sources:**[bgpy/simulation_framework/scenarios/scenario_config.py40](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L40-L40)

### Labeling and Metadata

```
config = ScenarioConfig(
    ScenarioCls=PrefixHijack,
    scenario_label="ROV_Custom",  # Used in graphs and CSV aggregation
    csv_label="experimental_run_1",  # Optional notes field
    # ...
)
```
ParameterTypeDefaultDescription`scenario_label``str``AdoptPolicyCls.name`Label used for data aggregation and graphs`csv_label``str``""`Optional notes field (not used by framework)
The `scenario_label` is particularly important because it's used as a key for aggregating metrics. If you have multiple configs with the same `AdoptPolicyCls`, you must provide unique labels:

**Sources:**[bgpy/simulation_framework/scenarios/scenario_config.py78-80](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L78-L80)[bgpy/simulation_framework/simulation.py206-213](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L206-L213)

---

## Configuration Validation

The `ScenarioConfig.__post_init__` method performs several validation checks:

```
Yes

No

Yes

No

Yes

No

No

Yes

Yes

No

post_init

propagation_rounds
is None?

Set to ScenarioCls
.min_propagation_rounds
(or 2 for BGPiSec)

propagation_rounds >=
min_propagation_rounds?

Raise ValueError

AdoptPolicyCls ==
MISSINGPolicy?

Set to BasePolicyCls

hardcoded_asn_cls_dict
is frozendict?

Raise TypeError

scenario_label
is empty?

Set to AdoptPolicyCls.name

_set_AttackerBasePolicyCls
(for ASPA attacks)

_validate_no_withdrawal_mixing
```

**Sources:**[bgpy/simulation_framework/scenarios/scenario_config.py82-133](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L82-L133)

### Withdrawal Mixing Validation

The framework warns if you mix policies that support withdrawals (`BGPFull` subclasses) with those that don't:

```
# This raises a DeprecationWarning:
config = ScenarioConfig(
    ScenarioCls=PrefixHijack,
    AdoptPolicyCls=ROVFull,  # Inherits from BGPFull
    BasePolicyCls=BGP,       # Does NOT inherit from BGPFull
)
```

**Sources:**[bgpy/simulation_framework/scenarios/scenario_config.py146-173](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L146-L173)

### Attacker Policy Auto-Configuration

For ASPA-based policies, the framework automatically sets `AttackerBasePolicyCls` to enable specific attack variants:

**Sources:**[bgpy/simulation_framework/scenarios/scenario_config.py135-144](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L135-L144)

---

## Complete Configuration Example

```
from frozendict import frozendict
from bgpy.simulation_framework import Simulation, ScenarioConfig
from bgpy.simulation_framework import SubprefixHijack, PrefixHijack
from bgpy.simulation_engine import ROV, BGP, ASPA
from bgpy.shared.enums import SpecialPercentAdoptions, ASGroups

# Configuration 1: Basic ROV deployment
config_rov = ScenarioConfig(
    ScenarioCls=SubprefixHijack,
    BasePolicyCls=BGP,
    AdoptPolicyCls=ROV,
    num_attackers=1,
    num_victims=1,
    propagation_rounds=1,
    adoption_subcategory_attrs=(
        ASGroups.STUBS_OR_MH.value,
        ASGroups.ETC.value,
        ASGroups.INPUT_CLIQUE.value,
    ),
)

# Configuration 2: ASPA with custom attacker subcategory
config_aspa = ScenarioConfig(
    ScenarioCls=PrefixHijack,
    BasePolicyCls=BGP,
    AdoptPolicyCls=ASPA,
    num_attackers=2,
    attacker_subcategory_attr=ASGroups.ETC.value,
    scenario_label="ASPA_MultiAttacker",
)

# Run simulation with both configs and multiple adoption levels
sim = Simulation(
    percent_adoptions=(
        SpecialPercentAdoptions.ONLY_ONE,
        0.2,
        0.5,
        0.8,
        SpecialPercentAdoptions.ALL_BUT_ONE,
    ),
    scenario_configs=(config_rov, config_aspa),
    num_trials=100,
)

sim.run()
```

**Sources:**[bgpy/simulation_framework/simulation.py55-109](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L55-L109)

---

## Configuration in Multi-Trial Execution

```
SimulationEngine
Scenario
_run_chunk
Simulation
SimulationEngine
Scenario
_run_chunk
Simulation
Same adopting_asns
reused for all configs
loop
[For each scenario_config]
loop
[For each percent_adoption]
loop
[For each trial]
scenario_configs tuple
adopting_asns = None
Scenario(scenario_config,
percent_adoption,
adopting_asns)
Store scenario_config
Calculate/reuse
attacker_asns,
victim_asns,
adopting_asns
setup_engine(self)
get_policy_cls(as_obj)
Returns policy from config
```

**Key Insight:** Within a single trial and percent_adoption, the same `adopting_asns` set is reused across all `scenario_configs` if their `adoption_subcategory_attrs` match. This ensures fair comparison between different security policies.

**Sources:**[bgpy/simulation_framework/simulation.py393-430](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L393-L430)[bgpy/simulation_framework/simulation.py455-459](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L455-L459)

---

## Summary Table
Configuration AspectKey ParametersDefault Behavior**Scenario Type**`ScenarioCls`Required (no default)**Policies**`BasePolicyCls`, `AdoptPolicyCls`, `AttackerBasePolicyCls``BGP`, `BGP`, `None`**Attack/Victim**`num_attackers`, `num_victims`, subcategory attrs`1`, `1`, `STUBS_OR_MH`**Adoption**`adoption_subcategory_attrs`, `percent_adoptions``(STUBS_OR_MH, ETC, INPUT_CLIQUE)`**Propagation**`propagation_rounds``ScenarioCls.min_propagation_rounds`**Hardcoded**`hardcoded_asn_cls_dict`Empty frozendict**Labels**`scenario_label`, `csv_label``AdoptPolicyCls.name`, `""`
**Sources:**[bgpy/simulation_framework/scenarios/scenario_config.py28-81](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L28-L81)