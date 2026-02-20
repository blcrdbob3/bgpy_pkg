# ROA and Announcement Management
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

This document details the mechanisms for generating, configuring, and managing Route Origin Authorizations (ROAs) and BGP announcements within the BGPy simulation framework. ROAs are critical for Route Origin Validation (ROV) and related security policies, while announcements represent the BGP route advertisements that propagate through the network during simulations.

For information about creating custom scenarios that generate specific ROAs and announcements, see [Creating Custom Scenarios](/blcrdbob3/bgpy_pkg/10.1-creating-custom-scenarios). For details on how policies use ROAs for validation, see [Route Origin Validation (ROV)](/blcrdbob3/bgpy_pkg/6.2-route-origin-validation-(rov)).

---

## ROA Management System

### ROA Generation Pipeline

ROAs are generated on a per-scenario basis through the `Scenario` class. The generation process follows a two-stage override mechanism:

```
Yes

No

Scenario.init()

override_roas
in config?

Use override_roas

Call _get_roas()

Subclass Implementation
(Custom ROA Logic)

Generate ROAs from
announcements

Store in self.roas

_reset_and_add_roas_to_roa_checker()

Policy.roa_checker.clear()

Loop through self.roas

Policy.roa_checker.insert(roa.prefix, roa)
```

**Sources:**[bgpy/simulation_framework/scenarios/scenario.py73-96](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L73-L96)

### ROA Checker Integration

The ROA checker serves as a global RPKI + Routinator simulation. All ROAs are stored in a single shared instance accessible to all policies:
ComponentLocationPurpose`Policy.roa_checker`Static class attributeGlobal ROA storage shared across all AS policies`roa_checker.clear()`Called per scenarioResets ROA state between scenarios`roa_checker.insert()`Called for each ROAAdds ROA with prefix as key
The ROA checker is provided by the `roa-checker` external package (version ~3.0), which implements the validation logic used by ROV policies.

```
Policy Usage

Global ROA Storage

Scenario Setup

clear() + insert()

validate()

validate()

validate()

Scenario.init()

_reset_and_add_roas_to_roa_checker()

Policy.roa_checker
(Static Instance)

ROV.process_incoming_anns()

ASPA.process_incoming_anns()

Other Security Policies
```

**Sources:**[bgpy/simulation_framework/scenarios/scenario.py90-96](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L90-L96)

### ROA Generation Methods

Scenarios implement custom ROA generation by overriding the `_get_roas()` method:

```
def _get_roas(
    self,
    *,
    announcements: tuple["Ann", ...] = (),
    engine: BaseSimulationEngine | None = None,
) -> tuple[ROA, ...]:
    """Returns a tuple of ROA's
    
    Not abstract and by default does nothing for
    backwards compatability
    """
    return ()
```

**Common ROA Generation Patterns:**

1. **Default Valid ROAs** - Generate ROAs matching victim announcements:

```
# Example pattern used in most hijack scenarios
roas = []
for ann in announcements:
    if ann.origin in self.victim_asns:
        roas.append(ROA(prefix=ann.prefix, origin=ann.origin, max_length=...))
return tuple(roas)
```
2. **Non-Routed ROAs** - Create ROAs with origin AS 0 for non-routed prefix attacks:

```
# Used in NonRoutedPrefixHijack scenarios
roa = ROA(prefix=prefix, origin=0, max_length=max_length)
```
3. **Custom ROA Configurations** - Override via `ScenarioConfig.override_roas`

**Sources:**[bgpy/simulation_framework/scenarios/scenario.py391-402](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L391-L402)[bgpy/simulation_framework/scenarios/scenario_config.py74](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L74-L74)

### Override Mechanism

ROAs can be explicitly specified to bypass generation logic:

```
Yes

No

ScenarioConfig

override_roas: tuple[ROA, ...] | None

override_roas
is not None?

Use provided ROAs directly

Call _get_roas() method

Stored in Scenario.roas
```

This override is primarily used for:

- **Testing** - Deterministic ROA configurations in test fixtures
- **YAML Deserialization** - Restoring exact scenario state from saved simulations
- **Custom Experiments** - Manually specifying complex ROA configurations

**Sources:**[bgpy/simulation_framework/scenarios/scenario.py80-83](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L80-L83)[bgpy/simulation_framework/scenarios/scenario_config.py74](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L74-L74)

---

## Announcement Management System

### Announcement Generation Pipeline

Announcements follow the same override pattern as ROAs:

```
Yes

No

Scenario.init()

override_announcements
in config?

Use override_announcements

Call _get_announcements()

Subclass Implementation
(Custom Announcement Logic)

Generate attack/victim
announcements

Store in self.announcements

Used by engine.setup()

Seeded into attacker/victim
local RIBs
```

**Sources:**[bgpy/simulation_framework/scenarios/scenario.py73-78](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L73-L78)

### Announcement Class Configuration

The `ScenarioConfig` allows specifying custom announcement classes:
ParameterDefaultPurpose`AnnCls``Announcement`Base announcement class for the scenario`override_announcements``None`Explicit announcement tuple (bypasses generation)
Example usage:

```
# Using custom announcement class
scenario_config = ScenarioConfig(
    ScenarioCls=MyCustomHijack,
    AnnCls=MyCustomAnnouncement,  # Custom announcement with extra fields
    ...
)
```

The `AnnCls` parameter is stored but the specific implementation details depend on the scenario's `_get_announcements()` method, which constructs announcement instances.

**Sources:**[bgpy/simulation_framework/scenarios/scenario_config.py39-40](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L39-L40)

### Announcement Generation Methods

Scenarios implement custom announcement generation by overriding `_get_announcements()`:

```
def _get_announcements(
    self,
    *,
    engine: Optional["BaseSimulationEngine"] = None,
) -> tuple["Ann", ...]:
    """Returns announcements
    
    Empty by default for testing, typically subclassed
    """
    return ()
```

**Common Announcement Generation Patterns:**

1. **Victim Announcement** - Legitimate route from victim AS:

```
victim_ann = Announcement(
    prefix=Prefixes.PREFIX.value,
    as_path=(victim_asn,),
    timestamp=Timestamps.VICTIM.value,
)
```
2. **Attacker Announcement** - Malicious route from attacker:

```
attacker_ann = Announcement(
    prefix=attack_prefix,  # Could be same, subprefix, or superprefix
    as_path=(attacker_asn,) + forged_path,  # Potentially forged
    timestamp=Timestamps.ATTACKER.value,
)
```
3. **Multiple Announcements** - Scenarios can generate multiple announcements for complex attacks

**Sources:**[bgpy/simulation_framework/scenarios/scenario.py379-389](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L379-L389)

### Seeding Announcements into the Engine

Announcements are seeded into the simulation engine through the `setup_engine()` method:

```
AS Objects
SimulationEngine
Scenario
AS Objects
SimulationEngine
Scenario
loop
[For each AS]
loop
[For each announcement]
Engine ready for propagation
setup_engine(engine)
engine.setup(scenario)
Set policy class based on scenario.get_policy_cls()
Seed announcement into origin AS local RIB
```

The engine's `setup()` method:

1. Assigns policy classes to each AS based on `scenario.get_policy_cls()`
2. Seeds `scenario.announcements` into the appropriate origin AS local RIBs
3. Prepares the engine for BGP propagation rounds

**Sources:**[bgpy/simulation_framework/scenarios/scenario.py350-356](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L350-L356)

---

## Prefix Hierarchy Management

### Ordered Prefix-Subprefix Dictionary

The `ordered_prefix_subprefix_dict` maintains a mapping of prefixes to their more-specific subprefixes, critical for traceback operations and blackholing decisions:

```
1.0.0.0/8
(Superprefix)

1.2.0.0/16
(Prefix)

1.2.3.0/24
(Subprefix)

ordered_prefix_subprefix_dict

'1.0.0.0/8': ['1.2.0.0/16']

'1.2.0.0/16': ['1.2.3.0/24']

'1.2.3.0/24': []
```

**Construction Process:**

1. **Collect All Prefixes** - From both announcements and ROAs:

```
prefixes_set = set()
for ann in self.announcements:
    prefixes_set.add(ann.prefix)
for roa in self.roas:
    prefixes_set.add(str(roa.prefix))
```
2. **Sort by Specificity** - Most specific (smallest) prefixes first:

```
prefixes = sorted(prefixes, key=lambda x: x.num_addresses)
```
3. **Build Hierarchy** - Map each prefix to its subprefixes:

```
for outer_prefix, subprefix_list in prefix_subprefix_dict.items():
    for prefix in prefixes:
        if prefix.subnet_of(outer_prefix) and prefix != outer_prefix:
            subprefix_list.append(str(prefix))
```

**Sources:**[bgpy/simulation_framework/scenarios/scenario.py431-457](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L431-L457)

### Use Cases for Prefix Hierarchy
Use CaseComponentPurpose**Traceback**`ASGraphAnalyzer`Find most-specific prefix when tracing data plane paths**ROV++ Blackholing**`ROVPP` policiesDetermine which prefixes to blackhole when non-routed prefix detected**Superprefix Hijacks**Attack scenariosTrack relationship between legitimate prefix and attacking superprefix
**Example: Traceback with Subprefixes**

When an AS has routes to multiple prefixes covering the same address space, the analyzer uses this dictionary to select the most-specific route:

```
AS received routes for:
1.0.0.0/8 and 1.2.3.0/24

Traceback query for
1.2.3.0/24

ordered_prefix_subprefix_dict
indicates /24 is subprefix of /8

Select /24 route
(most specific)
```

**Example: ROV++ Blackholing**

When ROV++ detects an invalid announcement for a non-routed prefix, it needs to blackhole both the non-routed prefix and any less-specific covering prefixes:

```
Non-routed ROA: 1.2.0.0/16 origin AS 0
Attacker announces: 1.0.0.0/8 (superprefix hijack)

ROV++ must blackhole:
- 1.0.0.0/8 (the attacking superprefix)
- Any prefixes between /8 and /16 in the hierarchy

```

**Sources:**[bgpy/simulation_framework/scenarios/scenario.py86-88](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L86-L88)[bgpy/simulation_framework/scenarios/scenario.py431-457](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L431-L457)

---

## Integration with Simulation Execution

### Scenario Setup Sequence

The complete ROA and announcement management sequence during scenario initialization:

```
SimulationEngine
Policy.roa_checker
Scenario.__init__()
ScenarioConfig
SimulationEngine
Policy.roa_checker
Scenario.__init__()
ScenarioConfig
Step 1: Get Announcements
alt
[override_announcements exists]
Step 2: Get ROAs
alt
[override_roas exists]
Step 3: Reset & Load ROAs
loop
[For each ROA]
Step 4: Build Prefix Hierarchy
Scenario ready
Initialize scenario with config
Use override_announcements
Call _get_announcements(engine)
Use override_roas
Call _get_roas(announcements, engine)
roa_checker.clear()
roa_checker.insert(roa.prefix, roa)
_get_ordered_prefix_subprefix_dict()
Later: setup_engine(engine)
Seed announcements into origin AS RIBs
```

**Sources:**[bgpy/simulation_framework/scenarios/scenario.py73-89](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L73-L89)

### Policy-ROA Interaction

During BGP propagation, policies query the ROA checker for validation:

```
Yes

No

AS receives incoming
announcement

Policy.process_incoming_anns()

ROV-based Policy?

Query Policy.roa_checker

roa_checker.get_validity(prefix, origin)

Return ROAValidity enum

Policy decides:
VALID → Accept
INVALID → Reject
UNKNOWN → Accept

Process without ROA validation

Update local RIB
```

**ROA Validity States:**
StateMeaningPolicy Action (ROV)`VALID`Prefix-origin pair matches ROAAccept announcement`INVALID`Prefix-origin pair violates ROAReject announcement`UNKNOWN`No ROA covers this prefixAccept announcement (permissive)
**Sources:**[bgpy/shared/enums.py54-66](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/shared/enums.py#L54-L66)

### Announcement Lifecycle

```
Scenario._get_announcements()

Generated Announcements

Scenario.announcements tuple

Scenario.setup_engine(engine)

Engine.setup(scenario)

Seed into origin AS local RIBs

SimulationEngine.run()

Propagation Round 0

Announcements propagate
through network

ASGraphAnalyzer.analyze()

Determine outcomes based
on final announcement state
```

**Key Points:**

- Announcements are **immutable** once generated (stored as tuple)
- **Origin AS** for each announcement is determined by `ann.origin` or the first ASN in `ann.as_path`
- During propagation, announcements are **copied and modified** (AS path prepending, etc.)
- Some scenarios use **post_propagation_hook** to inject additional announcements mid-simulation (e.g., `AccidentalRouteLeak`)

**Sources:**[bgpy/simulation_framework/scenarios/scenario.py350-356](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L350-L356)[bgpy/simulation_framework/simulation.py499-537](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L499-L537)

---

## YAML Serialization and Override Mechanisms

### Preserving State for Testing

Both ROAs and announcements support YAML serialization for deterministic testing:

```
Simulation Run

Scenario.to_yaml_dict()

ScenarioConfig with overrides

YAML File

Test Suite

ScenarioConfig.from_yaml_dict()

Restored Scenario

Exact reproduction
of original state
```

When serializing a scenario to YAML, the actual announcements and ROAs used are stored as overrides:

```
def __to_yaml_dict__(self) -> dict[Any, Any]:
    """This optional method is called when you call yaml.dump()"""
    
    config_to_save = replace(
        self.scenario_config,
        override_attacker_asns=self.attacker_asns,
        override_victim_asns=self.victim_asns,
        override_adopting_asns=self.adopting_asns,
        override_announcements=self.announcements,  # Store actual announcements
    )
    
    return {
        "scenario_config": config_to_save,
        "percent_adoption": self.percent_adoption,
    }
```

This ensures that when the YAML is deserialized, the exact same announcements and ROAs are used, bypassing random generation for reproducible tests.

**Sources:**[bgpy/simulation_framework/scenarios/scenario.py463-477](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L463-L477)[bgpy/simulation_framework/scenarios/scenario_config.py216-242](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py#L216-L242)

### Override Priority

The override mechanism follows a strict priority:

1. **Explicit Override** (highest priority) - `override_announcements` / `override_roas` in config
2. **YAML Deserialization** - Restored from saved state (uses override mechanism)
3. **Generated** (lowest priority) - `_get_announcements()` / `_get_roas()` methods

This design allows:

- **Flexibility** in custom scenarios (override generation)
- **Reproducibility** in testing (YAML serialization)
- **Extensibility** for new attack types (custom generation methods)

**Sources:**[bgpy/simulation_framework/scenarios/scenario.py73-83](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L73-L83)