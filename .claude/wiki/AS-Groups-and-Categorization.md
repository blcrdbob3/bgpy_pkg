# AS Groups and Categorization
Relevant source files
- [bgpy/as_graphs/base/as_graph/as_graph.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py)
- [bgpy/as_graphs/base/as_graph/base_as.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/base_as.py)
- [bgpy/as_graphs/base/as_graph/cone_funcs.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/cone_funcs.py)
- [bgpy/as_graphs/base/as_graph/customer_cone_funcs.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/customer_cone_funcs.py)
- [bgpy/as_graphs/base/as_graph/graph_building_funcs.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/graph_building_funcs.py)
- [bgpy/as_graphs/base/as_graph_collector.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph_collector.py)
- [bgpy/utils/engine_runner/engine_run_config.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/engine_run_config.py)
- [bgpy/utils/engine_runner/engine_runner.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/engine_runner.py)

## Purpose and Scope

This document explains how Autonomous Systems (ASes) are categorized into groups within BGPy. AS categorization serves two purposes: (1) classifying individual ASes based on their topological properties (stub, multihomed, transit), and (2) organizing ASes into groups for analysis and policy adoption selection.

For information about the underlying AS graph structure and relationships, see [AS Graph Structure and Properties](/blcrdbob3/bgpy_pkg/5.1-as-graph-structure-and-properties). For information about how AS graphs are constructed from CAIDA data, see [CAIDA Data and Graph Construction](/blcrdbob3/bgpy_pkg/5.2-caida-data-and-graph-construction).

---

## Individual AS Classification

Individual ASes are categorized based on their connectivity patterns according to RFC1772 definitions. These classifications are implemented as cached properties on the `AS` class and are computed on-demand when first accessed.

### AS Classification Properties

The following table summarizes the AS classification properties:
PropertyDefinitionImplementationRFC1772 Compliance**Stub**AS with exactly one neighbor`len(self.neighbors) == 1`Yes**Multihomed**AS with no customers and multiple providers/peers`len(self.customers) == 0 and len(self.peers) + len(self.providers) > 1`Yes**Transit**AS with customers and multiple total neighbors`len(self.customers) > 0 and len(self.customers) + len(self.peers) + len(self.providers) > 1`Yes**Input Clique**AS manually marked as part of the input cliqueSet during graph construction from CAIDA dataNo (CAIDA-specific)**IXP**Internet Exchange PointSet during graph construction from CAIDA IXP listNo (infrastructure)
Sources: [bgpy/as_graphs/base/as_graph/base_as.py134-165](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/base_as.py#L134-L165)

### Classification Logic Diagram

```
Yes

No

Yes

Yes

No

No

Yes

No

AS Object

len(neighbors) == 1?

len(customers) == 0?

len(peers + providers) > 1?

len(customers) > 0 and
total neighbors > 1?

Stub AS

Multihomed AS

Transit AS

Other AS
```

Sources: [bgpy/as_graphs/base/as_graph/base_as.py134-153](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/base_as.py#L134-L153)

### Property Implementation

The `AS` class implements these properties using Python's `@cached_property` decorator for efficient lazy evaluation:

```
@cached_property
def stub(self) -> bool:
    """Returns True if AS is a stub by RFC1772"""
    return len(self.neighbors) == 1

@cached_property
def multihomed(self) -> bool:
    """Returns True if AS is multihomed by RFC1772"""
    return len(self.customers) == 0 and len(self.peers) + len(self.providers) > 1

@cached_property
def transit(self) -> bool:
    """Returns True if AS is a transit AS by RFC1772"""
    return (
        len(self.customers) > 0
        and len(self.customers) + len(self.peers) + len(self.providers) > 1
    )
```

The `neighbors` property is a convenience accessor that combines all relationship types:

```
@cached_property
def neighbors(self) -> tuple["AS", ...]:
    """Returns customers + peers + providers"""
    return self.customers + self.peers + self.providers
```

Sources: [bgpy/as_graphs/base/as_graph/base_as.py134-165](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/base_as.py#L134-L165)

---

## AS Group Filters

While individual AS properties classify single ASes, AS group filters organize collections of ASes for use in simulations and analysis. The `ASGraph` class maintains filter functions that generate frozen sets of ASes matching specific criteria.

### Default AS Group Filters

The `ASGraph._default_as_group_filters` property defines the standard groups used throughout BGPy:
Group NameFilter DescriptionTypical Use Case`ASGroups.IXPS.value`All IXP ASesExclude from analysis or treat specially`ASGroups.STUBS.value`Stub ASes (excluding IXPs)Edge network analysis`ASGroups.MULTIHOMED.value`Multihomed ASes (excluding IXPs)Multi-homing defense effectiveness`ASGroups.STUBS_OR_MH.value`Stubs or multihomed (excluding IXPs)Combined edge network analysis`ASGroups.INPUT_CLIQUE.value`Input clique ASes (excluding IXPs)Tier-1 provider analysis`ASGroups.ETC.value`ASes not in other categories (excluding IXPs)Catch-all for uncategorized ASes`ASGroups.TRANSIT.value`Transit ASes (excluding IXPs)Provider network analysis`ASGroups.ALL_WOUT_IXPS.value`All ASes (excluding IXPs)Complete network analysis
Sources: [bgpy/as_graphs/base/as_graph/as_graph.py224-271](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L224-L271)

### Filter Function Architecture

```
Application

Storage

Filter Definition

_default_as_group_filters()

ixp_filter()

stub_no_ixp_filter()

multihomed_no_ixp_filter()

input_clique_no_ixp_filter()

transit_no_ixp_filter()

etc_no_ixp_filter()

all_no_ixp_filter()

as_group_filters
frozendict[str, Callable]

as_groups
frozendict[str, frozenset[AS]]

asn_groups
frozendict[str, frozenset[int]]

_set_as_groups()

Execute filter_func(as_graph)
```

Sources: [bgpy/as_graphs/base/as_graph/as_graph.py193-271](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L193-L271)

### Filter Function Implementation

Each filter function takes an `ASGraph` instance and returns a `frozenset[AS]`. The filters consistently exclude IXPs (except for the IXP filter itself) to prevent infrastructure ASes from skewing analysis results.

Example filter implementations from [bgpy/as_graphs/base/as_graph/as_graph.py230-258](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L230-L258):

```
def stub_no_ixp_filter(as_graph: "ASGraph") -> frozenset[AS]:
    return frozenset(x for x in as_graph if x.stub and not x.ixp)

def multihomed_no_ixp_filter(as_graph: "ASGraph") -> frozenset[AS]:
    return frozenset(x for x in as_graph if x.multihomed and not x.ixp)

def transit_no_ixp_filter(as_graph: "ASGraph") -> frozenset[AS]:
    return frozenset(x for x in as_graph if x.transit and not x.ixp)

def etc_no_ixp_filter(as_graph: "ASGraph") -> frozenset[AS]:
    return frozenset(
        x
        for x in as_graph
        if not (x.stub or x.multihomed or x.input_clique or x.ixp)
    )
```

The `etc_no_ixp_filter` captures ASes that don't fit into other standard categories, providing complete coverage of the AS space.

Sources: [bgpy/as_graphs/base/as_graph/as_graph.py230-258](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L230-L258)

---

## AS Group Storage and Initialization

### Initialization Process

AS groups are initialized during `ASGraph.__init__` via the `_set_as_groups()` method. This process:

1. Creates a mutable dictionary from default filters
2. Merges any `additional_as_group_filters` provided by the user
3. Converts to a frozen dictionary of filter functions
4. Executes each filter to populate `as_groups` and `asn_groups`

```
Group Storage
Filter Functions
_set_as_groups()
ASGraph.__init__()
Group Storage
Filter Functions
_set_as_groups()
ASGraph.__init__()
loop
[For each filter]
Call with additional_as_group_filters
Get _default_as_group_filters
Merge additional filters
Create frozendict of filters
Execute filter_func(as_graph)
Return frozenset[AS]
Store in as_groups[key]
Store ASNs in asn_groups[key]
Freeze as_groups
Freeze asn_groups
Return
```

Sources: [bgpy/as_graphs/base/as_graph/as_graph.py193-223](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L193-L223)

### Storage Data Structures

The `ASGraph` class maintains three related data structures for AS groups:
AttributeTypePurpose`as_group_filters``frozendict[str, Callable[[ASGraph], frozenset[AS]]]`Maps group names to filter functions for lazy re-evaluation if needed`as_groups``frozendict[str, frozenset[AS]]`Maps group names to sets of AS objects for direct iteration`asn_groups``frozendict[str, frozenset[int]]`Maps group names to sets of ASNs for efficient membership testing
All three structures are frozen to prevent modification after initialization, ensuring graph consistency.

Implementation from [bgpy/as_graphs/base/as_graph/as_graph.py208-222](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L208-L222):

```
# Store filter functions
self.as_group_filters: frozendict[str, Callable[[ASGraph], frozenset[AS]]] = (
    frozendict(as_group_filters)
)

# Execute filters and store results
as_groups: dict[str, frozenset[AS]] = dict()
asn_groups: dict[str, frozenset[int]] = dict()

for as_group_key, filter_func in self.as_group_filters.items():
    as_groups[as_group_key] = filter_func(self)
    asn_groups[as_group_key] = frozenset(x.asn for x in filter_func(self))

# Freeze results
self.as_groups: frozendict[str, frozenset[AS]] = frozendict(as_groups)
self.asn_groups: frozendict[str, frozenset[int]] = frozendict(asn_groups)
```

Sources: [bgpy/as_graphs/base/as_graph/as_graph.py208-222](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L208-L222)

---

## Custom AS Group Filters

Users can define custom AS group filters to support specialized analysis needs. Custom filters are provided via the `additional_as_group_filters` parameter during `ASGraph` initialization.

### Adding Custom Filters

Custom filters must conform to the signature: `Callable[[ASGraph], frozenset[AS]]`

Example custom filter definition:

```
from frozendict import frozendict
from bgpy.as_graphs import ASGraph

def large_transit_filter(as_graph: ASGraph) -> frozenset[AS]:
    """Filter for transit ASes with >100 customers"""
    return frozenset(
        x for x in as_graph 
        if x.transit and len(x.customers) > 100
    )

# Provide during initialization
additional_filters = frozendict({
    "large_transit": large_transit_filter
})

as_graph = ASGraph(
    as_graph_info=info,
    additional_as_group_filters=additional_filters
)

# Access the custom group
large_transit_ases = as_graph.as_groups["large_transit"]
```

Custom filters are merged with default filters in [bgpy/as_graphs/base/as_graph/as_graph.py201-209](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L201-L209):

```
as_group_filters: dict[str, Callable[[ASGraph], frozenset[AS]]] = dict(
    self._default_as_group_filters
)

if additional_as_group_filters:
    as_group_filters.update(additional_as_group_filters)
```

Sources: [bgpy/as_graphs/base/as_graph/as_graph.py86-88](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L86-L88)[bgpy/as_graphs/base/as_graph/as_graph.py193-209](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L193-L209)

---

## Access Patterns and Use Cases

### Direct AS Property Access

Individual AS classification properties are accessed directly on `AS` instances:

```
as_obj = as_graph.as_dict[64512]

# Check classification
if as_obj.stub:
    print("AS is a stub")
if as_obj.multihomed:
    print("AS is multihomed")
if as_obj.transit:
    print("AS is a transit provider")
```

Sources: [bgpy/as_graphs/base/as_graph/base_as.py134-153](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/base_as.py#L134-L153)

### AS Group Iteration

AS groups are typically accessed for iterating over specific AS categories:

```
# Iterate over all stub ASes
for stub_as in as_graph.as_groups[ASGroups.STUBS.value]:
    # Process stub AS
    pass

# Iterate over transit ASes
for transit_as in as_graph.as_groups[ASGroups.TRANSIT.value]:
    # Process transit AS
    pass
```

### ASN Group Membership Testing

ASN groups enable efficient membership testing:

```
from bgpy.shared.enums import ASGroups

asn = 64512
if asn in as_graph.asn_groups[ASGroups.STUBS.value]:
    print(f"AS{asn} is a stub")
```

### Use in Simulations

AS groups are extensively used in the simulation framework for:

1. **Policy Adoption Selection**: Randomly selecting ASes from specific groups to adopt security policies
2. **Attacker/Victim Selection**: Choosing appropriate ASes based on network position
3. **Analysis Segmentation**: Computing metrics separately for different AS categories
4. **Visualization**: Coloring or styling nodes based on AS group membership

Example from simulation framework (conceptual):

```
# Select 10% of transit ASes to adopt ROV
adopting_transit = random.sample(
    list(as_graph.as_groups[ASGroups.TRANSIT.value]),
    k=int(len(as_graph.as_groups[ASGroups.TRANSIT.value]) * 0.10)
)
```

Sources: [bgpy/as_graphs/base/as_graph/as_graph.py212-222](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L212-L222)

---

## AS Group Enumeration

The `ASGroups` enum defines standard group names used throughout BGPy. These enum values serve as keys in the `as_groups` and `asn_groups` dictionaries.

```
ASGroups Enum

IXPS

STUBS

MULTIHOMED

STUBS_OR_MH

INPUT_CLIQUE

ETC

TRANSIT

ALL_WOUT_IXPS
```

The enum is defined in [bgpy/shared/enums.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/shared/enums.py) and imported throughout the codebase to ensure consistent group naming.

Sources: [bgpy/as_graphs/base/as_graph/as_graph.py9](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L9-L9)[bgpy/as_graphs/base/as_graph/as_graph.py260-271](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L260-L271)

---

## Summary

AS categorization in BGPy operates at two levels:

1. **Individual AS Properties**: Computed on-demand using cached properties based on RFC1772 definitions (`stub`, `multihomed`, `transit`)
2. **AS Group Filters**: Pre-computed collections of ASes organized by category, with both AS objects and ASN sets for efficient access

This dual-level system enables both fine-grained per-AS decisions and efficient bulk operations on AS categories. The use of frozen data structures ensures graph immutability and prevents accidental modification during simulations.

Sources: [bgpy/as_graphs/base/as_graph/as_graph.py193-271](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L193-L271)[bgpy/as_graphs/base/as_graph/base_as.py134-165](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/base_as.py#L134-L165)