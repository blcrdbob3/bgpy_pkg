# AS Graphs and Network Topology
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

This page provides a conceptual overview of how BGPy models the Internet's topology as a graph of Autonomous Systems (ASes) with customer-provider and peer-to-peer relationships. This topology forms the foundation for BGP simulations, determining how announcements propagate through the network.

For detailed information on AS graph construction from CAIDA data, see [CAIDA Data and Graph Construction](/blcrdbob3/bgpy_pkg/5.2-caida-data-and-graph-construction). For information on AS categorization and grouping, see [AS Groups and Categorization](/blcrdbob3/bgpy_pkg/5.3-as-groups-and-categorization). For comprehensive documentation of AS graph properties and algorithms, see [AS Graph Structure and Properties](/blcrdbob3/bgpy_pkg/5.1-as-graph-structure-and-properties).

---

## The Autonomous System Model

An **Autonomous System (AS)** represents an independent network entity identified by a unique ASN (Autonomous System Number). In BGPy, each AS is modeled by the `AS` class, which encapsulates the AS's network position, relationships, and routing policy.

### AS Class Structure

```
AS Class
(base_as.py)

Identity
• asn: int
• hashed_asn: int

Relationships
• customers: tuple[AS, ...]
• providers: tuple[AS, ...]
• peers: tuple[AS, ...]
• neighbors: tuple[AS, ...]

Properties
• stub: bool
• multihomed: bool
• transit: bool
• input_clique: bool
• ixp: bool

Metrics
• customer_cone_size: int | None
• provider_cone_size: int | None
• as_rank: int | None
• propagation_rank: int | None

Policy Reference
• policy: Policy
• as_graph: ASGraph
```

**Sources:**[bgpy/as_graphs/base/as_graph/base_as.py13-73](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/base_as.py#L13-L73)

### Key AS Attributes
AttributeTypeDescription`asn``int`Autonomous System Number (unique identifier)`customers``tuple[AS, ...]`ASes that are customers (pay this AS for transit)`providers``tuple[AS, ...]`ASes that provide transit to this AS`peers``tuple[AS, ...]`ASes with settlement-free peering relationships`policy``Policy`BGP policy implementation (e.g., `BGP`, `ROV`, `ASPA`)`propagation_rank``intNone``customer_cone_size``intNone`
**Sources:**[bgpy/as_graphs/base/as_graph/base_as.py17-73](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/base_as.py#L17-L73)

---

## AS Relationships and Valley-Free Routing

BGPy models three types of business relationships between ASes, which determine routing policies and announcement propagation according to the **Gao-Rexford model** of valley-free routing.

### Relationship Types

```
Valley-Free Propagation

to customers

to customers

to peers

to providers
(from customers only)

Provider

AS

Customer

Peer

Peer-to-Peer Relationship

peer link
(settlement-free)

Peer AS 1

Peer AS 2

Customer-Provider Relationship

customer link

provider link

Provider AS
(Transit Network)

Customer AS
(Pays for Transit)
```

**Sources:**[bgpy/as_graphs/base/as_graph/base_as.py45-47](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/base_as.py#L45-L47)[bgpy/shared/enums.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/shared/enums.py) (Relationships enum)

### Valley-Free Routing Rules

An AS will propagate announcements according to these rules:

1. **Customer Routes** → Propagate to providers, peers, and customers
2. **Peer Routes** → Propagate to customers only (not to providers or other peers)
3. **Provider Routes** → Propagate to customers only (not to providers or peers)

These rules ensure that ASes do not provide free transit between their providers or between their peers, which would violate economic relationships.

**Sources:** Implementation details in policy classes (see [Base BGP Policies](/blcrdbob3/bgpy_pkg/6.1-base-bgp-policies))

---

## The AS Graph Structure

The `ASGraph` class encapsulates the entire Internet topology as a graph where nodes are ASes and edges are relationships.

### ASGraph Core Components

```
ASGraph
(as_graph.py)

Data Storage
• as_dict: frozendict[int, AS]
• ases: tuple[AS, ...]
• ixp_asns: frozenset[int]

Propagation Structure
• propagation_ranks: tuple[tuple[AS, ...], ...]
• _assign_propagation_ranks()
• _get_propagation_ranks()

AS Categorization
• as_groups: frozendict[str, frozenset[AS]]
• asn_groups: frozendict[str, frozenset[int]]
• as_group_filters: frozendict

Graph Building
• _gen_graph()
• _add_relationships()
• _make_relationships_tuples()

Cone Calculations
• _get_size_of_and_store_cone()
• _get_as_rank()
```

**Sources:**[bgpy/as_graphs/base/as_graph/as_graph.py37-305](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L37-L305)

### Key Data Structures
AttributeTypePurpose`as_dict``frozendict[int, AS]`Maps ASN → AS object for O(1) lookup`ases``tuple[AS, ...]`All ASes for iteration`propagation_ranks``tuple[tuple[AS, ...], ...]`ASes grouped by propagation rank (see below)`as_groups``frozendict[str, frozenset[AS]]`Categorized AS sets (stubs, multihomed, transit, etc.)`ixp_asns``frozenset[int]`Internet Exchange Point ASNs
**Sources:**[bgpy/as_graphs/base/as_graph/as_graph.py127-176](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L127-L176)

### Graph Construction Process

```
ASGraphInfo
(relationship data)

_gen_graph()
Create AS objects

_add_relationships()
Add references

_make_relationships_tuples()
Convert to tuples

_assign_propagation_ranks()
Rank for propagation

_get_size_of_and_store_cone()
Calculate metrics

_set_as_groups()
Categorize ASes

ASGraph Ready
```

**Sources:**[bgpy/as_graphs/base/as_graph/as_graph.py141-192](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L141-L192)[bgpy/as_graphs/base/as_graph/graph_building_funcs.py13-100](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/graph_building_funcs.py#L13-L100)

---

## Propagation Ranks

**Propagation ranks** determine the order in which announcements propagate through the network. ASes are ranked from leaves (high rank numbers) to the core/clique (rank 0), ensuring that announcements flow from the edges toward the center and then back out.

### Propagation Rank Assignment

```
Rank N: Leaves

Rank 2: Next Level

Rank 1: Direct Customers of Clique

Rank 0: Input Clique

Tier-1 AS

Tier-1 AS

Tier-1 AS

Transit AS

Transit AS

Transit AS

Multihomed AS

Stub AS

Stub AS

Stub AS
```

**Sources:**[bgpy/as_graphs/base/as_graph/propagation_rank_funcs.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/propagation_rank_funcs.py)

During simulation, announcements propagate in rounds:

1. **Round 0:** Input clique ASes propagate to their customers
2. **Round 1:** Rank 1 ASes propagate to customers, peers, and providers
3. **Round N:** Continues until all ranks have propagated

This ensures proper valley-free propagation order.

**Sources:**[bgpy/as_graphs/base/as_graph/as_graph.py173-176](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L173-L176)

---

## AS Categorization

ASes are automatically categorized based on their relationships, following RFC 1772 definitions.

### AS Types

```
AS Categories

Stub AS
• neighbors == 1
• No transit provided

Multihomed AS
• customers == 0
• multiple providers/peers
• No transit provided

Transit AS
• customers > 0
• Provides transit

IXP
• Internet Exchange Point
• Special handling

Input Clique
• Tier-1 ASes
• Provider-free core
```

**Sources:**[bgpy/as_graphs/base/as_graph/base_as.py134-172](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/base_as.py#L134-L172)

### AS Type Properties
PropertyDefinitionCode Reference`stub``len(neighbors) == 1`[base_as.py135-138](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/base_as.py#L135-L138)`multihomed``len(customers) == 0 and len(peers) + len(providers) > 1`[base_as.py141-144](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/base_as.py#L141-L144)`transit``len(customers) > 0 and total_neighbors > 1`[base_as.py147-153](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/base_as.py#L147-L153)`input_clique`Flag set during construction for tier-1 ASes[base_as.py50](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/base_as.py#L50-L50)`ixp`Flag set for Internet Exchange Points[base_as.py51](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/base_as.py#L51-L51)
**Sources:**[bgpy/as_graphs/base/as_graph/base_as.py134-172](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/base_as.py#L134-L172)

### Default AS Groups

The `ASGraph` maintains pre-computed sets of ASes by category for efficient filtering during simulations:
Group KeyFilter Description`ASGroups.STUBS.value`Stub ASes (excluding IXPs)`ASGroups.MULTIHOMED.value`Multihomed ASes (excluding IXPs)`ASGroups.TRANSIT.value`Transit ASes (excluding IXPs)`ASGroups.INPUT_CLIQUE.value`Input clique ASes (excluding IXPs)`ASGroups.IXPS.value`Internet Exchange Points`ASGroups.ALL_WOUT_IXPS.value`All ASes except IXPs
**Sources:**[bgpy/as_graphs/base/as_graph/as_graph.py224-271](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L224-L271)

---

## Customer and Provider Cones

**Customer cone** and **provider cone** metrics quantify an AS's reach in the network topology.

### Cone Definitions

- **Customer Cone:** The set of all ASes reachable by traversing customer links downward (recursively including customers of customers)
- **Provider Cone:** The set of all ASes reachable by traversing provider links upward (recursively including providers of providers)

### AS Rank

The **AS Rank** is calculated from customer cone size, following CAIDA's methodology. Larger customer cones indicate more influential ASes (typically large transit providers).

**Calculation:**

1. Sort ASes by `customer_cone_size` (descending)
2. Assign rank based on position, with ties receiving the same rank
3. Continue sequence without gaps (e.g., ranks 1, 1, 3 if two ASes tie for #1)

**Sources:**[bgpy/as_graphs/base/as_graph/cone_funcs.py75-111](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/cone_funcs.py#L75-L111)

### Cone Size Computation

```
AS with customers

Initialize cone_dict

For each customer:
recursively compute their cone

Union all customer cones

Add direct customers

Store cone size and ASNs

Base case:
Stub/multihomed AS
cone size = 0
```

**Sources:**[bgpy/as_graphs/base/as_graph/cone_funcs.py8-72](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/cone_funcs.py#L8-L72)

Cone calculation is optional (controlled by `store_customer_cone_size`, `store_customer_cone_asns`, `store_provider_cone_size`, `store_provider_cone_asns` flags) since it adds significant computation time.

**Sources:**[bgpy/as_graphs/base/as_graph/as_graph.py79-82](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L79-L82)

---

## AS Graph Initialization

### Constructor Parameters

```
ASGraph(
    as_graph_info: ASGraphInfo,           # Contains relationship data
    BaseASCls: type[AS] = AS,             # AS class (for subclassing)
    BasePolicyCls: type[Policy] = BGP,    # Default policy for all ASes
    store_customer_cone_size: bool = True,
    store_customer_cone_asns: bool = False,
    store_provider_cone_size: bool = False,
    store_provider_cone_asns: bool = False,
    yaml_as_dict: frozendict[int, AS] | None = None,  # For YAML deserialization
    yaml_ixp_asns: frozenset[int] = frozenset(),
)
```

**Sources:**[bgpy/as_graphs/base/as_graph/as_graph.py74-89](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L74-L89)

### Normal Initialization Flow

1. `ASGraphInfo` provides relationship data (from CAIDA or custom sources)
2. `_gen_graph()` creates all `AS` objects with the specified policy
3. `_add_relationships()` populates relationship references
4. `_make_relationships_tuples()` converts relationship sets to immutable tuples
5. `_assign_propagation_ranks()` computes propagation order
6. Optionally compute customer/provider cones
7. `_set_as_groups()` categorizes ASes for efficient filtering

**Sources:**[bgpy/as_graphs/base/as_graph/as_graph.py141-192](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L141-L192)

---

## Integration with Simulations

The `ASGraph` serves as the topology foundation for BGP simulations:

1. **Engine Initialization:** The `SimulationEngine` receives an `ASGraph` during construction
2. **Policy Assignment:** Each AS has a `policy` attribute determining its BGP behavior
3. **Announcement Propagation:** The engine iterates through `propagation_ranks` to simulate BGP propagation
4. **Outcome Analysis:** AS categorization (`as_groups`) enables analysis by AS type (e.g., stub adoption rates)

**Sources:**[bgpy/utils/engine_runner/engine_runner.py92-102](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/engine_runner.py#L92-L102)

### Usage Example Pattern

```
# Create AS graph from CAIDA data
as_graph = CAIDAASGraph(
    as_graph_info=caida_graph_info,
    BasePolicyCls=ROV,  # All ASes start with ROV policy
)

# Access ASes
for as_obj in as_graph:
    print(f"AS{as_obj.asn}: {len(as_obj.customers)} customers")

# Access by ASN
as_obj = as_graph.as_dict[64512]

# Iterate by propagation rank
for rank_ases in as_graph.propagation_ranks:
    # Process each rank in order
    pass
```

**Sources:**[bgpy/as_graphs/base/as_graph/as_graph.py299-305](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph/as_graph.py#L299-L305) (iterator methods)

---

## Summary

The AS graph topology model provides:

- **Realistic Internet structure** based on CAIDA relationship data
- **Business relationship modeling** (customer-provider, peer-to-peer)
- **Valley-free routing enforcement** through relationship-aware propagation
- **Efficient categorization** for analysis and selective policy adoption
- **Propagation ordering** ensuring correct BGP simulation semantics
- **Flexible policy assignment** supporting heterogeneous security policy deployments

For detailed information on graph construction from CAIDA data, see [CAIDA Data and Graph Construction](/blcrdbob3/bgpy_pkg/5.2-caida-data-and-graph-construction). For policy implementation details, see [BGP Policies Overview](/blcrdbob3/bgpy_pkg/3.3-bgp-policies-overview).