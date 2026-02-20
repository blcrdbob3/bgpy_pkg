# AS Graph System
Relevant source files
- [bgpy/as_graphs/base/as_graph/as_graph.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py)
- [bgpy/as_graphs/base/as_graph/base_as.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/base_as.py)
- [bgpy/as_graphs/base/as_graph/cone_funcs.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/cone_funcs.py)
- [bgpy/as_graphs/base/as_graph/customer_cone_funcs.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/customer_cone_funcs.py)
- [bgpy/as_graphs/base/as_graph/graph_building_funcs.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/graph_building_funcs.py)
- [bgpy/as_graphs/base/as_graph_collector.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph_collector.py)
- [bgpy/as_graphs/base/as_graph_constructor.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph_constructor.py)
- [bgpy/as_graphs/base/as_graph_info.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph_info.py)
- [bgpy/as_graphs/base/links/customer_provider_link.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/links/customer_provider_link.py)
- [bgpy/as_graphs/base/links/link.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/links/link.py)
- [bgpy/as_graphs/base/links/peer_link.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/links/peer_link.py)
- [bgpy/tests/engine_tests/utils/engine_test_config.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_test_config.py)
- [bgpy/utils/engine_runner/engine_run_config.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/engine_run_config.py)
- [bgpy/utils/engine_runner/engine_runner.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/engine_runner.py)

The AS Graph System is the foundational component that models the Internet's topology as a graph of Autonomous Systems (ASes). It constructs a network topology from real-world data sources (primarily CAIDA), establishes AS relationships (customer-provider and peer links), calculates graph-theoretic properties (propagation ranks, customer cones), and categorizes ASes into functional groups. This system is used by the Simulation Engine to propagate BGP announcements according to valley-free routing rules.

For detailed information about AS structure and properties, see [AS Graph Structure and Properties](/blcrdbob3/bgpy_pkg/5.1-as-graph-structure-and-properties). For CAIDA data handling, see [CAIDA Data and Graph Construction](/blcrdbob3/bgpy_pkg/5.2-caida-data-and-graph-construction). For AS categorization logic, see [AS Groups and Categorization](/blcrdbob3/bgpy_pkg/5.3-as-groups-and-categorization).

## System Overview

The AS Graph system consists of three primary layers: data collection, graph construction, and property calculation.

```
Property Calculation

Graph Layer

Construction Layer

Data Collection Layer

implements

implements

ASGraphCollector
(Abstract Base)

CAIDAASGraphCollector

cache_dir
(SINGLE_DAY_CACHE_DIR)

ASGraphConstructor
(Abstract Base)

CAIDAASGraphConstructor

ASGraphInfo
(customer_provider_links,
peer_links, ixp_asns)

ASGraph
(as_dict, propagation_ranks,
as_groups)

AS
(asn, customers, providers,
peers, policy)

Links
(CustomerProviderLink,
PeerLink)

_assign_propagation_ranks()
Rank leaves to clique

_get_size_of_and_store_cone()
Customer/Provider cones

_get_as_rank()
CAIDA AS Rank algorithm
```

**Sources:**[bgpy/as_graphs/base/as_graph/as_graph.py1-305](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L1-L305)[bgpy/as_graphs/base/as_graph_constructor.py1-107](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph_constructor.py#L1-L107)[bgpy/as_graphs/base/as_graph_collector.py1-58](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph_collector.py#L1-L58)[bgpy/as_graphs/base/as_graph_info.py1-53](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph_info.py#L1-L53)

## Core Data Structures

### ASGraph Class

The `ASGraph` class is the central container for the network topology. It stores ASes and provides iteration, lookup, and grouping capabilities.
PropertyTypeDescription`as_dict``frozendict[int, AS]`Immutable mapping from ASN to AS object`ases``tuple[AS, ...]`Tuple of all AS objects for iteration`ixp_asns``frozenset[int]`Set of Internet Exchange Point ASNs`propagation_ranks``tuple[tuple[AS, ...], ...]`ASes grouped by propagation rank (leaves to clique)`as_groups``frozendict[str, frozenset[AS]]`Categorized AS groups (stubs, multihomed, transit, etc.)`asn_groups``frozendict[str, frozenset[int]]`Same as as_groups but with ASNs instead of AS objects`as_group_filters``frozendict[str, Callable]`Filter functions that define AS groups
**Sources:**[bgpy/as_graphs/base/as_graph/as_graph.py38-305](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L38-L305)

### AS Class

The `AS` class represents an individual Autonomous System with its relationships and properties.
PropertyTypeDescription`asn``int`Autonomous System Number`customers``tuple[AS, ...]`Customer ASes (weakref proxies)`providers``tuple[AS, ...]`Provider ASes (weakref proxies)`peers``tuple[AS, ...]`Peer ASes (weakref proxies)`policy``Policy`BGP policy implementation for this AS`input_clique``bool`Whether AS is in the input clique (top tier)`ixp``bool`Whether AS is an Internet Exchange Point`propagation_rank``int | None`Distance from leaves (higher = more central)`customer_cone_size``int | None`Number of ASes in customer cone`customer_cone_asns``frozenset[int] | None`ASNs in customer cone`provider_cone_size``int | None`Number of ASes in provider cone`as_rank``int | None`CAIDA AS Rank (based on customer cone size)`as_graph``CallableProxyType[ASGraph]`Weakref to parent ASGraph
**Sources:**[bgpy/as_graphs/base/as_graph/base_as.py14-212](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/base_as.py#L14-L212)

### Link Classes

Links represent relationships between ASes and are stored in `ASGraphInfo` during construction.

```
«abstract»

Link

+asns: tuple[int, ...]

+hash() : int

+eq(other) : bool

CustomerProviderLink

-__customer_asn: int

-__provider_asn: int

+customer_asn: int

+provider_asn: int

+asns: tuple[int, ...]

PeerLink

-__peer_asns: tuple[int, int]

+peer_asns: tuple[int, int]

+asns: tuple[int, ...]
```

**Sources:**[bgpy/as_graphs/base/links/link.py1-34](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/links/link.py#L1-L34)[bgpy/as_graphs/base/links/customer_provider_link.py1-50](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/links/customer_provider_link.py#L1-L50)[bgpy/as_graphs/base/links/peer_link.py1-42](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/links/peer_link.py#L1-L42)

## Graph Construction Pipeline

The graph construction process follows a four-stage pipeline:

```
ASGraph
ASGraphInfo
ASGraphCollector
ASGraphConstructor
User
ASGraph
ASGraphInfo
ASGraphCollector
ASGraphConstructor
User
Download & cache
CAIDA data
Parse relationships
from downloaded file
_gen_graph()
_add_relationships()
_assign_propagation_ranks()
_get_size_of_and_store_cone()
run()
run()
dl_path
_get_as_graph_info(dl_path)
create ASGraphInfo
ASGraph(as_graph_info)
as_graph
write_tsv(as_graph)
as_graph
```

**Sources:**[bgpy/as_graphs/base/as_graph_constructor.py36-107](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph_constructor.py#L36-L107)[bgpy/as_graphs/base/as_graph/as_graph.py141-192](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L141-L192)

### Graph Initialization Stages

The `ASGraph.__init__()` method orchestrates graph construction through several stages:

1. **AS Object Generation** (`_gen_graph()`): Creates AS objects for all ASNs

- Creates empty AS objects with policies
- Marks IXP and input clique ASes
- Uses temporary sets for relationship building: `peers_setup_set`, `customers_setup_set`, `providers_setup_set`
2. **Relationship Linking** (`_add_relationships()`): Establishes connections

- Iterates through `customer_provider_links` in ASGraphInfo
- Iterates through `peer_links` in ASGraphInfo
- Adds references to temporary sets
3. **Relationship Finalization** (`_make_relationships_tuples()`): Converts sets to tuples

- Sorts relationships by ASN
- Converts to immutable tuples with weakref proxies
- Creates `*_asns` frozensets (e.g., `customer_asns`)
- Deletes temporary setup sets
4. **Propagation Rank Assignment** (`_assign_propagation_ranks()`): Ranks ASes by distance from leaves

- Leaf ASes (stubs) get rank 0
- Each AS's rank is `max(customer_ranks) + 1`
5. **Optional: Customer Cone Calculation** (`_get_size_of_and_store_cone()`): Recursively calculates cones

- Only runs if `store_customer_cone_size=True`
- Uses DFS to traverse customer relationships
- Calculates AS Rank based on cone size
6. **AS Group Creation** (`_set_as_groups()`): Categorizes ASes

- Applies filter functions from `_default_as_group_filters`
- Creates `as_groups` and `asn_groups` frozen dicts

**Sources:**[bgpy/as_graphs/base/as_graph/as_graph.py141-192](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L141-L192)[bgpy/as_graphs/base/as_graph/graph_building_funcs.py13-100](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/graph_building_funcs.py#L13-L100)

## AS Relationships

BGPy models three types of AS relationships that determine routing behavior:
RelationshipDirectionEconomic ModelPropagation RulesCustomer-ProviderCustomer → ProviderCustomer pays providerProviders accept from customers, propagate to allPeer-PeerBidirectionalSettlement-free exchangePeers accept from peers, don't propagate to other peersProvider-CustomerProvider → CustomerProvider provides transitProviders propagate to customers only if learned from customers/peers
### Valley-Free Routing

The propagation ranks enforce valley-free routing, which prohibits paths that go "up" (to a provider) and then "down" (to a customer). The `ASGraph.propagation_ranks` tuple organizes ASes such that:

- Rank 0: Leaf ASes (stubs with only one neighbor)
- Rank 1: ASes whose highest customer is rank 0
- Rank N: ASes whose highest customer is rank N-1
- Top ranks: Input clique (Tier-1 ISPs with only peer/customer relationships)

```
Rank 0 (Leaves)

Rank 1

Rank 2

Rank 3 (Input Clique)

peer

provider

provider

provider

provider

provider

provider

provider

provider

AS 1 (Tier-1)
input_clique=True

AS 2 (Tier-1)
input_clique=True

AS 10 (ISP)

AS 11 (ISP)

AS 100 (Multihomed)
multihomed=True

AS 101 (Multihomed)

AS 1000 (Stub)
stub=True

AS 1001 (Stub)

AS 1002 (Stub)
```

**Sources:**[bgpy/as_graphs/base/as_graph/propagation_rank_funcs.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/propagation_rank_funcs.py) (referenced but not provided), [bgpy/as_graphs/base/as_graph/as_graph.py173-176](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L173-L176)

## Graph Properties and Metrics

### Propagation Ranks

Propagation ranks determine the order in which BGP announcements propagate through the network. They are calculated using a bottom-up approach:

```
_assign_propagation_ranks()

loop

Initialize:
all ASes unranked

Find leaf ASes
(stubs)

Set leaves to rank 0

_assign_ranks_helper():
For each AS with unranked
customers, wait

When all customers ranked:
rank = max(customer_ranks) + 1

Repeat until all ranked
```

The resulting `propagation_ranks` tuple groups ASes by rank for efficient iteration during simulation.

**Sources:**[bgpy/as_graphs/base/as_graph/as_graph.py173-176](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L173-L176)

### Customer and Provider Cones

Cones represent the set of ASes reachable through specific relationship types:

- **Customer Cone**: All ASes reachable by following customer links recursively. Represents the "influence" or "reach" of an AS.
- **Provider Cone**: All ASes reachable by following provider links recursively. Represents how many upstream providers an AS has.

The cone calculation algorithm uses memoization for efficiency:

```
# Simplified logic from _get_cone_helper
def _get_cone_helper(as_obj, cone_dict, rel_attr):
    if as_obj.asn in cone_dict:
        return cone_dict[as_obj.asn]  # Already computed
    
    cone_dict[as_obj.asn] = set()
    for neighbor in getattr(as_obj, rel_attr):  # "customers" or "providers"
        cone_dict[as_obj.asn].add(neighbor.asn)
        # Recursively compute neighbor's cone
        self._get_cone_helper(neighbor, cone_dict, rel_attr)
        # Add neighbor's cone to this AS's cone
        cone_dict[as_obj.asn].update(cone_dict[neighbor.asn])
    
    return cone_dict[as_obj.asn]
```

**Sources:**[bgpy/as_graphs/base/as_graph/cone_funcs.py8-111](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/cone_funcs.py#L8-L111)

### CAIDA AS Rank

AS Rank is calculated using CAIDA's algorithm, which ranks ASes by customer cone size:

1. Sort ASes by `customer_cone_size` (descending)
2. Assign ranks sequentially, starting from 0
3. Ties receive the same rank, but the sequence continues (e.g., ranks 0, 0, 2, not 0, 0, 1)

This matches CAIDA's AS Rank methodology as documented at [https://asrank.caida.org/about](https://asrank.caida.org/about).

**Sources:**[bgpy/as_graphs/base/as_graph/cone_funcs.py75-111](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/cone_funcs.py#L75-L111)

## AS Categorization

ASes are categorized based on their relationship patterns using RFC 1772 definitions and CAIDA conventions:
CategoryDefinitionPropertyFilter Function**Stub**Exactly one neighbor`as_obj.stub``len(neighbors) == 1`**Multihomed**No customers, multiple providers/peers`as_obj.multihomed``len(customers) == 0 and len(peers) + len(providers) > 1`**Transit**Has customers and multiple neighbors`as_obj.transit``len(customers) > 0 and total_neighbors > 1`**Input Clique**Tier-1 ISP (from CAIDA data)`as_obj.input_clique`Set during graph construction**IXP**Internet Exchange Point`as_obj.ixp`Set during graph construction**ETC**ASes not in other categoriesComputed`not (stub or multihomed or input_clique or ixp)`
### AS Group Filters

The `ASGraph.as_group_filters` property provides callable filters for categorizing ASes:

```
# Example filter from _default_as_group_filters
def stub_no_ixp_filter(as_graph: ASGraph) -> frozenset[AS]:
    return frozenset(x for x in as_graph if x.stub and not x.ixp)
```

Available AS groups (keys in `as_groups` and `asn_groups`):

- `ASGroups.STUBS.value`: Stub ASes (excluding IXPs)
- `ASGroups.MULTIHOMED.value`: Multihomed ASes (excluding IXPs)
- `ASGroups.STUBS_OR_MH.value`: Stubs or multihomed (excluding IXPs)
- `ASGroups.INPUT_CLIQUE.value`: Input clique ASes (excluding IXPs)
- `ASGroups.TRANSIT.value`: Transit ASes (excluding IXPs)
- `ASGroups.ETC.value`: Other ASes (excluding IXPs)
- `ASGroups.IXPS.value`: Internet Exchange Points
- `ASGroups.ALL_WOUT_IXPS.value`: All ASes except IXPs

**Sources:**[bgpy/as_graphs/base/as_graph/as_graph.py193-271](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L193-L271)[bgpy/as_graphs/base/as_graph/base_as.py134-172](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/base_as.py#L134-L172)

## Immutability and Serialization

### Immutability Design

The AS Graph system uses immutable data structures extensively to prevent accidental modification and enable safe caching:

- `as_dict`: `frozendict[int, AS]` - Cannot add/remove ASes after construction
- Relationships: `tuple[AS, ...]` with weakref proxies - Cannot modify neighbor lists
- ASN sets: `frozenset[int]` - Cannot modify relationship ASN sets
- Groups: `frozendict[str, frozenset[AS]]` - Cannot modify categorizations

The graph is frozen after construction by converting the temporary `dict` to `frozendict`:

```
# From _set_non_yaml_attrs
self.as_dict: frozendict[int, AS] = dict()  # type: ignore during construction
# ... build graph ...
self.as_dict = frozendict(self.as_dict)  # Freeze after construction
```

**Sources:**[bgpy/as_graphs/base/as_graph/as_graph.py141-192](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L141-L192)

### YAML Serialization

The AS Graph supports YAML serialization for testing and reproducibility:

```
Deserialization

Serialization

ASGraph

to_yaml_dict()

dict with:
- as_dict: dict[int, AS]
- ixp_asns: list[int]

yaml.dump()

yaml.load()

from_yaml_dict()

Reconstruct ASGraph:
- Convert ASNs to AS refs
- Set weakref proxies
- Rebuild relationships
```

When deserializing from YAML (`_set_yaml_attrs()`):

1. Load AS objects with ASN references (not object references)
2. Convert ASN integers to AS object references using `as_dict` lookup
3. Set up weakref proxies for `as_graph` references
4. Rebuild `propagation_ranks` tuple

**Sources:**[bgpy/as_graphs/base/as_graph/as_graph.py119-140](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L119-L140)[bgpy/as_graphs/base/as_graph/as_graph.py277-293](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L277-L293)[bgpy/as_graphs/base/as_graph/base_as.py177-208](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/base_as.py#L177-L208)

## Integration with Simulation Engine

The AS Graph system integrates with the Simulation Engine through several mechanisms:

### Policy Assignment

Each AS object contains a `policy` attribute that implements BGP routing logic. Policies are assigned during graph construction:

```
# From _gen_graph
as_ = BaseASCls(
    asn=asn,
    policy=BasePolicyCls(),  # Policy is instantiated here
    as_graph=self,
)
as_.policy.as_ = proxy(as_)  # Bidirectional weakref link
```

The policy can access the AS's relationships, the AS graph, and make routing decisions.

**Sources:**[bgpy/as_graphs/base/as_graph/graph_building_funcs.py21-34](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/graph_building_funcs.py#L21-L34)

### Propagation Order

The `propagation_ranks` tuple provides the iteration order for the Simulation Engine. Announcements propagate rank-by-rank to enforce valley-free routing:

```
# Typical usage in SimulationEngine
for rank in engine.as_graph.propagation_ranks:
    for as_obj in rank:
        as_obj.policy.process_incoming_anns(...)
```

**Sources:**[bgpy/as_graphs/base/as_graph/as_graph.py137-139](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L137-L139)[bgpy/as_graphs/base/as_graph/as_graph.py176](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L176-L176)

### AS Group Selection

Attack scenarios and adoption configurations use AS groups to select victim/attacker ASes:

```
# Example: Select random stub AS as victim
victim_asn = random.choice(list(as_graph.asn_groups[ASGroups.STUBS.value]))
```

**Sources:**[bgpy/as_graphs/base/as_graph/as_graph.py213-222](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L213-L222)