# AS Graph Structure and Properties
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

This page documents the structure and properties of the AS (Autonomous System) class and the ASGraph topology model. It covers the fundamental building blocks of the Internet topology representation in BGPy: individual AS objects, their relationships (customer/provider/peer), propagation ranks for simulation ordering, and customer/provider cone metrics for AS importance.

For information about how AS graphs are constructed from CAIDA data, see [CAIDA Data and Graph Construction](/blcrdbob3/bgpy_pkg/5.2-caida-data-and-graph-construction). For AS categorization into groups (stubs, multihomed, transit, etc.), see [AS Groups and Categorization](/blcrdbob3/bgpy_pkg/5.3-as-groups-and-categorization).

---

## AS Class Structure

The `AS` class represents a single Autonomous System in the Internet topology. Each AS object stores its relationships with other ASes and properties used during BGP simulations.

### Core Attributes

The `AS` class [bgpy/as_graphs/base/as_graph/base_as.py14-73](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/base_as.py#L14-L73) contains the following key attributes:
AttributeTypeDescription`asn``int`Unique autonomous system number identifier`peers``tuple[AS, ...]`References to peering ASes`providers``tuple[AS, ...]`References to provider ASes`customers``tuple[AS, ...]`References to customer ASes`input_clique``bool`Whether AS is in the input clique (Tier-1 ISPs)`ixp``bool`Whether AS is an Internet Exchange Point`customer_cone_size``int | None`Number of ASes in customer cone`customer_cone_asns``frozenset[int] | None`ASNs in customer cone`provider_cone_size``int | None`Number of ASes in provider cone`provider_cone_asns``frozenset[int] | None`ASNs in provider cone`as_rank``int | None`CAIDA AS Rank based on customer cone`propagation_rank``int | None`Rank for BGP propagation ordering`policy``Policy`BGP policy implementation for this AS`as_graph``ASGraph` (proxy)Weak reference to containing graph
**Storage Patterns**: Relationships are stored in dual formats for efficiency:

- **ASN frozensets** (`peer_asns`, `provider_asns`, `customer_asns`): Used for fast membership checks
- **AS tuples** (`peers`, `providers`, `customers`): Used for graph traversal with direct object references

Sources: [bgpy/as_graphs/base/as_graph/base_as.py17-73](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/base_as.py#L17-L73)

### AS Classification Properties

The `AS` class provides cached properties [bgpy/as_graphs/base/as_graph/base_as.py134-172](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/base_as.py#L134-L172) for RFC 1772-compliant AS classification:

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

These classifications are computed lazily and cached for performance during simulations.

Sources: [bgpy/as_graphs/base/as_graph/base_as.py134-172](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/base_as.py#L134-L172)

---

## AS Relationship Types

BGPy models the Internet topology using three fundamental relationship types defined by business agreements between ASes. These relationships dictate route export policies in the Gao-Rexford model.

```
Relationship Types

Customer-Provider
AS pays provider
Export: any route

Provider-Customer
Provider gets paid
Export: any route

Peer-Peer
Settlement-free
Export: customers only

Peer-Peer

No export

Provider AS
(provider_asns)

Central AS
(asn: int)

Customer AS
(customer_asns)

Peer AS 1
(peer_asns)

Peer AS 2
```

**Diagram: AS Relationship Model and Export Policies**

### Relationship Storage

Relationships are stored bidirectionally [bgpy/as_graphs/base/as_graph/base_as.py41-47](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/base_as.py#L41-L47):

- **From AS perspective**: Each AS stores `customers`, `providers`, and `peers` tuples
- **Symmetric enforcement**: When AS X is Y's customer, AS Y is X's provider
- **Weak references**: Relationships use weak proxies via `weakref.proxy()` to avoid circular reference issues during serialization

The graph building process [bgpy/as_graphs/base/as_graph/graph_building_funcs.py55-77](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/graph_building_funcs.py#L55-L77) establishes these bidirectional links:

```
def _add_relationships(self, as_graph_info: "ASGraphInfo") -> None:
    """Adds relationships to the graph as references"""
    
    for cp_link in as_graph_info.customer_provider_links:
        customer = self.as_dict[cp_link.customer_asn]
        provider = self.as_dict[cp_link.provider_asn]
        # Store references bidirectionally
        customer.providers_setup_set.add(provider)
        provider.customers_setup_set.add(customer)
    
    for peer_link in as_graph_info.peer_links:
        asn1, asn2 = peer_link.asns
        p1, p2 = self.as_dict[asn1], self.as_dict[asn2]
        # Add symmetric peer references
        p1.peers_setup_set.add(p2)
        p2.peers_setup_set.add(p1)
```

Sources: [bgpy/as_graphs/base/as_graph/base_as.py41-47](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/base_as.py#L41-L47)[bgpy/as_graphs/base/as_graph/graph_building_funcs.py55-77](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/graph_building_funcs.py#L55-L77)

### Valley-Free Routing Constraint

The relationships enforce valley-free routing: once a route traverses a customer-to-provider or peer-to-peer link, it cannot subsequently traverse a provider-to-customer link. This prevents economic incentive violations where an AS would provide transit between its providers.

Sources: High-level architecture diagrams

---

## Propagation Ranks

Propagation ranks determine the order in which ASes process and propagate BGP announcements during simulation. They ensure that announcements flow from the network core (input clique) toward the edges (stub ASes) in a topologically consistent manner.

```
Propagation Rank Assignment

Rank 0: Input Clique
(input_clique=True)
propagation_rank=0

Rank 1: Direct Customers
of Input Clique
propagation_rank=1

Rank 2: Next Level
propagation_rank=2

Rank N: Edge ASes
(stubs)
propagation_rank=N

ASGraph.propagation_ranks:
tuple[tuple[AS, ...], ...]
Indexed by rank number
```

**Diagram: Propagation Rank Hierarchy**

### Rank Calculation Algorithm

Propagation ranks are assigned during graph construction [bgpy/as_graphs/base/as_graph/as_graph.py173-176](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L173-L176) using a breadth-first traversal:

1. **Initialize**: Input clique ASes receive `propagation_rank = 0`[bgpy/as_graphs/base/as_graph/propagation_rank_funcs.py1-50](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/propagation_rank_funcs.py#L1-L50)
2. **Traverse**: For each rank, process all ASes and assign their customers to the next rank
3. **Store**: The `ASGraph.propagation_ranks` attribute stores `tuple[tuple[AS, ...], ...]` where each inner tuple contains all ASes at that rank

The implementation uses helper functions to build ranks:

```
def _assign_propagation_ranks(self) -> None:
    """Assigns propagation rank to each AS"""
    self._assign_ranks_helper()

def _get_propagation_ranks(self) -> tuple[tuple[AS, ...], ...]:
    """Returns ranks grouped by propagation rank"""
    # Groups ASes by their propagation_rank attribute
    # Returns tuple of tuples for immutability
```

### Usage in Simulation

During simulation execution, the `SimulationEngine` iterates through propagation ranks sequentially, processing all ASes at rank N before moving to rank N+1. This ensures that higher-tier ASes have already propagated their announcements before lower-tier ASes process them.

Sources: [bgpy/as_graphs/base/as_graph/as_graph.py29-34](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L29-L34)[bgpy/as_graphs/base/as_graph/as_graph.py173-176](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L173-L176)

---

## Customer and Provider Cones

Customer and provider cones are recursive metrics that measure an AS's reach and influence in the Internet topology. They are computationally expensive to calculate but essential for AS ranking and importance metrics.

### Customer Cone

The **customer cone** of an AS is the set of all ASes reachable by recursively following customer links. It represents the ASes that could potentially send traffic through this AS.

```
Customer Cone Calculation

provider

provider

provider

provider

AS 1
Transit Provider

AS 2
customer_cone_size = ?

AS 3
Multihomed

AS 4
Stub

AS 5
Stub

AS 2 customer_cone_asns:
{3, 4, 5}
customer_cone_size: 3

AS 3 customer_cone_asns:
{5}
customer_cone_size: 1

AS 4 customer_cone_asns:
{}
customer_cone_size: 0
```

**Diagram: Customer Cone Recursive Calculation**

### Calculation Implementation

Customer cones are calculated recursively using memoization [bgpy/as_graphs/base/as_graph/cone_funcs.py19-39](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/cone_funcs.py#L19-L39):

```
def _get_and_store_customer_cone_and_set_size(self, store_asns: bool = False) -> None:
    # Base case: stubs and multihomed have cone size 0
    non_edges: list[AS] = []
    cone_dict: dict[int, set[int]] = {}
    for as_obj in self:
        if as_obj.stub or as_obj.multihomed:
            as_obj.customer_cone_size = 0
            cone_dict[as_obj.asn] = set()
        else:
            non_edges.append(as_obj)
    
    # Recursive case: collect all customer ASNs transitively
    for as_obj in non_edges:
        customer_cone: set[int] = self._get_cone_helper(
            as_obj, cone_dict, Relationships.CUSTOMERS.name.lower()
        )
        as_obj.customer_cone_size = len(customer_cone)
        if store_asns:
            as_obj.customer_cone_asns = frozenset(customer_cone)
```

The `_get_cone_helper`[bgpy/as_graphs/base/as_graph/cone_funcs.py54-72](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/cone_funcs.py#L54-L72) recursively traverses the graph:

```
def _get_cone_helper(
    self,
    as_obj: AS,
    cone_dict: dict[int, set[int]],
    rel_attr: str,  # "customers" or "providers"
) -> set[int]:
    """Recursively determines the cone size of an AS"""
    
    as_asn = as_obj.asn
    if as_asn in cone_dict:
        return cone_dict[as_asn]  # Memoization
    else:
        cone_dict[as_asn] = set()
        for neighbor in getattr(as_obj, rel_attr):
            cone_dict[as_asn].add(neighbor.asn)
            if neighbor.asn not in cone_dict:
                self._get_cone_helper(neighbor, cone_dict, rel_attr)
            cone_dict[as_asn].update(cone_dict[neighbor.asn])
    return cone_dict[as_asn]
```

### Provider Cone

The **provider cone** is calculated similarly but follows provider links instead of customer links [bgpy/as_graphs/base/as_graph/cone_funcs.py41-51](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/cone_funcs.py#L41-L51) It represents the ASes that could potentially provide transit to this AS.

### Performance Considerations

Cone calculation is **disabled by default** because it has runtime greater than the entire graph generation process [bgpy/as_graphs/base/as_graph/as_graph.py177-191](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L177-L191) Control flags determine what to compute:
FlagPurpose`store_customer_cone_size`Calculate and store customer cone sizes`store_customer_cone_asns`Store full ASN sets (memory intensive)`store_provider_cone_size`Calculate and store provider cone sizes`store_provider_cone_asns`Store full provider ASN sets
Sources: [bgpy/as_graphs/base/as_graph/cone_funcs.py8-72](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/cone_funcs.py#L8-L72)[bgpy/as_graphs/base/as_graph/as_graph.py177-191](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L177-L191)

---

## AS Rank

AS Rank is a widely-used metric from CAIDA that ranks ASes by their customer cone size. It provides a quantitative measure of AS importance and influence in the Internet topology.

### Ranking Algorithm

The AS Rank algorithm [bgpy/as_graphs/base/as_graph/cone_funcs.py75-111](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/cone_funcs.py#L75-L111) implements CAIDA's specification:

1. **Sort ASes** by `customer_cone_size` in descending order (largest first)
2. **Assign ranks** sequentially, starting from rank 0
3. **Handle ties**: ASes with identical cone sizes receive the same rank
4. **Continue sequence**: After a tie, the next rank continues as if the sequence never stopped incrementing

**Example**:

```
ASN 1: cone_size=100 → as_rank=0
ASN 2: cone_size=100 → as_rank=0  (tie)
ASN 3: cone_size=99  → as_rank=2  (not rank 1!)

```

### Implementation

```
def _get_as_rank(self) -> None:
    """Calculate the AS rank following CAIDA's methodology"""
    
    # Highest customer cone size first
    ases = sorted(self, key=lambda x: x.customer_cone_size, reverse=True)
    last_as = ases[0]
    last_as.as_rank = 0
    
    for i, as_obj in enumerate(ases[1:]):
        if as_obj.customer_cone_size == last_as.customer_cone_size:
            as_obj.as_rank = last_as.as_rank  # Same rank for tie
        else:
            as_obj.as_rank = i  # Continue sequence
        last_as = as_obj
```

AS Rank is calculated after customer cone computation completes [bgpy/as_graphs/base/as_graph/as_graph.py185](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L185-L185)

Sources: [bgpy/as_graphs/base/as_graph/cone_funcs.py75-111](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/cone_funcs.py#L75-L111)[bgpy/as_graphs/base/as_graph/as_graph.py179-185](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L179-L185)

---

## ASGraph Container

The `ASGraph` class [bgpy/as_graphs/base/as_graph/as_graph.py38-305](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L38-L305) serves as the container for all AS objects and provides iteration and lookup interfaces.

### Core Data Structures
AttributeTypeDescription`as_dict``frozendict[int, AS]`Immutable mapping from ASN to AS object`ases``tuple[AS, ...]`Tuple of all AS objects for iteration`propagation_ranks``tuple[tuple[AS, ...], ...]`ASes grouped by propagation rank`ixp_asns``frozenset[int]`Set of IXP ASNs`as_groups``frozendict[str, frozenset[AS]]`Pre-computed AS group filters`asn_groups``frozendict[str, frozenset[int]]`Pre-computed ASN group filters
### Immutability Design

After construction, the ASGraph is **immutable**[bgpy/as_graphs/base/as_graph/as_graph.py164-172](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L164-L172):

```
# Can't allow modification of the AS dict since other things like
# as group filters will be broken then
self.as_dict = frozendict(self.as_dict)
```

This ensures that AS groups, cones, and ranks remain consistent throughout simulation execution.

### Iteration Interface

`ASGraph` implements Python's iteration protocol [bgpy/as_graphs/base/as_graph/as_graph.py299-304](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L299-L304):

```
def __getitem__(self, index: int) -> AS:
    return self.ases[index]

def __len__(self) -> int:
    return len(self.as_dict)
```

This allows natural iteration:

```
for as_obj in as_graph:
    process(as_obj)
```

Sources: [bgpy/as_graphs/base/as_graph/as_graph.py38-305](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L38-L305)[bgpy/as_graphs/base/as_graph/as_graph.py164-172](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L164-L172)[bgpy/as_graphs/base/as_graph/as_graph.py299-304](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L299-L304)

---

## Summary Table
ConceptKey AttributesPurpose**AS Object**`asn`, `peers`, `providers`, `customers`Represents single autonomous system with relationships**Relationships**Stored as tuples and frozensetsDefine business agreements and route export policies**Propagation Rank**`propagation_rank`, `propagation_ranks`Order BGP announcement propagation from core to edge**Customer Cone**`customer_cone_size`, `customer_cone_asns`Measures AS's downstream reach**Provider Cone**`provider_cone_size`, `provider_cone_asns`Measures AS's upstream connectivity**AS Rank**`as_rank`CAIDA's importance metric based on customer cone**AS Classification**`stub`, `multihomed`, `transit`RFC 1772 topology roles
Sources: [bgpy/as_graphs/base/as_graph/base_as.py1-212](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/base_as.py#L1-L212)[bgpy/as_graphs/base/as_graph/as_graph.py38-305](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L38-L305)