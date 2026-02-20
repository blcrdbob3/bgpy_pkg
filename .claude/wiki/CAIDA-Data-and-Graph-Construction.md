# CAIDA Data and Graph Construction
Relevant source files
- [.github/workflows/tests.yml](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/.github/workflows/tests.yml)
- [.pre-commit-config.yaml](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/.pre-commit-config.yaml)
- [LICENSE.txt](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/LICENSE.txt)
- [MANIFEST.in](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/MANIFEST.in)
- [README.md](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/README.md)
- [bgpy/as_graphs/base/as_graph_constructor.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph_constructor.py)
- [bgpy/as_graphs/base/as_graph_info.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph_info.py)
- [bgpy/as_graphs/base/links/customer_provider_link.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/links/customer_provider_link.py)
- [bgpy/as_graphs/base/links/link.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/links/link.py)
- [bgpy/as_graphs/base/links/peer_link.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/links/peer_link.py)
- [bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py)
- [bgpy/shared/enums.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/shared/enums.py)
- [bgpy/simulation_framework/scenarios/scenario.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py)
- [bgpy/simulation_framework/scenarios/scenario_config.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario_config.py)
- [bgpy/simulation_framework/simulation.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py)
- [bgpy/tests/engine_tests/utils/engine_test_config.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/engine_test_config.py)
- [pyproject.toml](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml)
- [requirements.txt](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/requirements.txt)
- [requirements_dev.txt](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/requirements_dev.txt)
- [setup.cfg](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/setup.cfg)
- [tox.ini](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/tox.ini)

## Purpose and Scope

This page documents how BGPy downloads, parses, and constructs AS graphs from CAIDA (Center for Applied Internet Data Analysis) relationship data. The construction pipeline transforms raw CAIDA text files into the `ASGraph` object that simulations operate on.

For information about the structure and properties of the constructed AS graph, see [AS Graph Structure and Properties](/blcrdbob3/bgpy_pkg/5.1-as-graph-structure-and-properties). For details on how ASes are categorized after construction, see [AS Groups and Categorization](/blcrdbob3/bgpy_pkg/5.3-as-groups-and-categorization).

## Graph Construction Pipeline

The graph construction process follows a multi-stage pipeline that separates data acquisition, parsing, and graph instantiation:

```
Path to file

CPLinks + PeerLinks
IXP ASNs + Clique ASNs

Construct AS objects
Set relationships

Optional

CAIDAASGraphCollector
Download CAIDA File

_get_as_graph_info()
Parse File

ASGraphInfo
Intermediate Representation

_get_as_graph()
Instantiate ASGraph

write_tsv()
Cache to TSV

CAIDAASGraph
Final Graph Object
```

**Sources:**[bgpy/as_graphs/base/as_graph_constructor.py36-61](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph_constructor.py#L36-L61)[bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py41-82](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py#L41-L82)

## Class Hierarchy

The graph construction system uses an abstract base class pattern to support different data sources:

```
creates

«abstract»

ASGraphConstructor

+ASGraphCollectorCls

+ASGraphCls

+as_graph_collector_kwargs

+as_graph_kwargs

+tsv_path

+run() : ASGraph

+write_tsv() : None

#_get_as_graph_info() : ASGraphInfo

#_get_as_graph() : ASGraph

CAIDAASGraphConstructor

+CAIDAASGraphCollector

+CAIDAASGraph

#_get_as_graph_info() : ASGraphInfo

#_get_as_graph() : ASGraph

-_extract_input_clique_asns()

-_extract_ixp_asns()

-_extract_provider_customers()

-_extract_peers()

ASGraphInfo

+customer_provider_links: frozenset[CPLink]

+peer_links: frozenset[PeerLink]

+unlinked_asns: frozenset[int]

+ixp_asns: frozenset[int]

+input_clique_asns: frozenset[int]

+diagram_ranks: tuple

+asns: list[int]

+links: frozenset[Link]
```

**Sources:**[bgpy/as_graphs/base/as_graph_constructor.py16-107](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph_constructor.py#L16-L107)[bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py18-128](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py#L18-L128)[bgpy/as_graphs/base/as_graph_info.py7-53](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph_info.py#L7-L53)

## CAIDA Data Format

CAIDA publishes AS relationship files in a text format with pipe-delimited fields. The file contains both metadata (comments) and relationship data:
Line TypeFormatDescriptionExampleInput Clique`# input clique: <asn1> <asn2> ...`ASes in the top-level clique`# input clique: 174 209 701 ...`IXP ASes`# IXP ASes: <asn1> <asn2> ...`Detected Internet Exchange Points`# IXP ASes: 1200 2200 ...`Customer-Provider`<provider>|<customer>|-1|<source>`Provider-to-customer relationship`174|3356|-1|CAIDA`Peer`<peer1>|<peer2>|0|<source>`Peer-to-peer relationship`174|3356|0|CAIDA`
The `-1` flag indicates a customer-provider relationship, while `0` indicates a peering relationship. The `<source>` field identifies the data source (typically "CAIDA").

**Sources:**[bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py53-70](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py#L53-L70)

## ASGraphConstructor Base Class

The `ASGraphConstructor` base class [bgpy/as_graphs/base/as_graph_constructor.py16-107](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph_constructor.py#L16-L107) defines the construction contract:

### Initialization

The constructor accepts:

- `ASGraphCollectorCls`: Class responsible for downloading/caching CAIDA data
- `ASGraphCls`: Target graph class to instantiate
- `as_graph_collector_kwargs`: Configuration for the collector (e.g., `cache_dir`)
- `as_graph_kwargs`: Configuration for the graph (e.g., cone storage options)
- `tsv_path`: Optional path to cache the graph as TSV
- `stubs`: Whether to include stub ASes (default: `True`)

**Sources:**[bgpy/as_graphs/base/as_graph_constructor.py17-34](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph_constructor.py#L17-L34)

### The run() Method

The `run()` method [bgpy/as_graphs/base/as_graph_constructor.py36-61](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph_constructor.py#L36-L61) orchestrates the entire construction process:

```
dl_path

ASGraphInfo

ASGraph

Yes

No

run()

as_graph_collector.run()

_get_as_graph_info(dl_path)

_get_as_graph(as_graph_info)

stubs == False?

_get_as_graph_info()
with invalid_asns

_get_as_graph()
without stubs

write_tsv(as_graph, tsv_path)

return as_graph
```

**Sources:**[bgpy/as_graphs/base/as_graph_constructor.py36-61](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph_constructor.py#L36-L61)

### TSV Caching

The `write_tsv()` static method [bgpy/as_graphs/base/as_graph_constructor.py73-91](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph_constructor.py#L73-L91) serializes the graph to a tab-separated values file:

```
# TSV format: One AS per row with columns from AS.db_row property
# Example columns: asn, input_clique, stub, providers, customers, peers, etc.
```

This TSV cache is used during multiprocessing to avoid pickling the graph (which fails due to weakrefs).

**Sources:**[bgpy/as_graphs/base/as_graph_constructor.py73-91](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph_constructor.py#L73-L91)[bgpy/simulation_framework/simulation.py467-469](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L467-L469)

## CAIDAASGraphConstructor Implementation

`CAIDAASGraphConstructor`[bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py18-128](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py#L18-L128) implements the abstract methods for CAIDA data:

### Parsing the CAIDA File

The `_get_as_graph_info()` method [bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py41-77](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py#L41-L77) parses the downloaded file line by line:

```
Yes

No

Yes

No

Yes (CP link)

No (Peer link)

After all lines

_get_as_graph_info(dl_path)

Line starts with
'# input clique'?

_extract_input_clique_asns()

Line starts with
'# IXP ASes'?

_extract_ixp_asns()

Line contains
'-1'?

_extract_provider_customers()

_extract_peers()

Return ASGraphInfo
with all links
```

**Sources:**[bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py41-77](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py#L41-L77)

### Link Extraction Methods

The constructor provides four specialized extraction methods:
MethodLine FormatExtractsResult`_extract_input_clique_asns()``# input clique: 174 209 ...`Space-separated ASNsAdds to `input_clique_asns` set`_extract_ixp_asns()``# IXP ASes: 1200 2200 ...`Space-separated ASNsAdds to `ixp_asns` set`_extract_provider_customers()``174|3356|-1|CAIDA`Provider and customerCreates `CPLink``_extract_peers()``174|3356|0|CAIDA`Two peer ASNsCreates `PeerLink`
All methods check `invalid_asns` to filter out stub ASes when `stubs=False`.

**Sources:**[bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py88-127](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py#L88-L127)

## ASGraphInfo: Intermediate Representation

`ASGraphInfo`[bgpy/as_graphs/base/as_graph_info.py7-53](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph_info.py#L7-L53) is a frozen dataclass that holds parsed relationship data before graph construction:

### Structure

```
@dataclass(frozen=True, slots=True)
class ASGraphInfo:
    customer_provider_links: frozenset[CPLink] = frozenset()
    peer_links: frozenset[PeerLink] = frozenset()
    unlinked_asns: frozenset[int] = frozenset()
    ixp_asns: frozenset[int] = frozenset()
    input_clique_asns: frozenset[int] = frozenset()
    diagram_ranks: tuple[tuple[int, ...], ...] = ()
```

**Sources:**[bgpy/as_graphs/base/as_graph_info.py7-20](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph_info.py#L7-L20)

### Properties

- `asns`: Returns sorted list of all unique ASNs across all links and unlinked ASes
- `links`: Returns union of all link types (`customer_provider_links | peer_links`)

**Sources:**[bgpy/as_graphs/base/as_graph_info.py36-52](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph_info.py#L36-L52)

### Validation

The `__post_init__()` method [bgpy/as_graphs/base/as_graph_info.py22-28](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph_info.py#L22-L28) validates that no ASN pair appears in both customer-provider and peer link sets, which would represent an inconsistent topology.

**Sources:**[bgpy/as_graphs/base/as_graph_info.py22-28](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/as_graph_info.py#L22-L28)

## Link Classes

The system uses two link classes to represent AS relationships:

```
«abstract»

Link

+asns* tuple[int, ...]

+init(asn1, asn2)

+hash() : int

+eq(other) : bool

+lt(other) : bool

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

### CustomerProviderLink

`CustomerProviderLink`[bgpy/as_graphs/base/links/customer_provider_link.py4-50](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/links/customer_provider_link.py#L4-L50) represents a directed customer-provider relationship:

- Stores `customer_asn` and `provider_asn` as immutable private attributes
- The `asns` property returns a sorted tuple for hashing/equality
- Two links are equal if they have the same customer and provider

**Sources:**[bgpy/as_graphs/base/links/customer_provider_link.py4-50](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/links/customer_provider_link.py#L4-L50)

### PeerLink

`PeerLink`[bgpy/as_graphs/base/links/peer_link.py6-42](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/links/peer_link.py#L6-L42) represents an undirected peer-to-peer relationship:

- Stores both ASNs in sorted order as `peer_asns`
- The constructor automatically sorts ASNs to ensure `PeerLink(1, 2) == PeerLink(2, 1)`
- The `asns` property returns the sorted pair

**Sources:**[bgpy/as_graphs/base/links/peer_link.py6-42](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/base/links/peer_link.py#L6-L42)

## Graph Instantiation

After parsing, `_get_as_graph()`[bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py79-82](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py#L79-L82) instantiates the graph:

```
def _get_as_graph(self, as_graph_info: ASGraphInfo) -> ASGraph:
    return self.ASGraphCls(as_graph_info, **self.as_graph_kwargs)
```

The `as_graph_kwargs` typically include:

- `store_customer_cone_size`: Whether to calculate and store customer cone sizes
- `store_customer_cone_asns`: Whether to store full customer cone ASN sets
- `store_provider_cone_size`: Whether to calculate provider cone sizes
- `store_provider_cone_asns`: Whether to store full provider cone ASN sets

These options control memory vs. performance tradeoffs, as storing full cone ASN sets can increase memory usage from 0.9GB/core to 2.3GB/core.

**Sources:**[bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py79-82](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py#L79-L82)[bgpy/simulation_framework/simulation.py88-97](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L88-L97)

## Integration with Simulations

The `Simulation` class integrates graph construction at two key points:

### Initialization and Caching

During `Simulation.__init__()`[bgpy/simulation_framework/simulation.py55-159](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L55-L159) the constructor parameters specify:

```
ASGraphConstructorCls: type[ASGraphConstructor] = CAIDAASGraphConstructor
as_graph_constructor_kwargs = frozendict({
    "as_graph_collector_kwargs": frozendict({
        "cache_dir": SINGLE_DAY_CACHE_DIR,
    }),
    "as_graph_kwargs": frozendict({
        "store_customer_cone_size": True,
        "store_customer_cone_asns": False,
        ...
    }),
    "tsv_path": None,  # Or Path to TSV for caching
})
```

The simulation then caches the CAIDA data before running trials [bgpy/simulation_framework/simulation.py258](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L258-L258):

```
def run(self, ...):
    # Cache the CAIDA graph before multiprocessing
    self.ASGraphConstructorCls(**self.as_graph_constructor_kwargs).run()
    graph_data_aggregator = self._get_data()
    ...
```

**Sources:**[bgpy/simulation_framework/simulation.py78-100](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L78-L100)[bgpy/simulation_framework/simulation.py250-268](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L250-L268)

### Multiprocessing Reconstruction

In multiprocessing mode, each worker process reconstructs the graph from the cached TSV [bgpy/simulation_framework/simulation.py461-474](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L461-L474):

```
def _get_engine_for_run_chunk(self) -> BaseSimulationEngine:
    """engine isn't picklable/dillable due to weakrefs"""
    constructor_kwargs = dict(self.as_graph_constructor_kwargs)
    constructor_kwargs["tsv_path"] = None  # Read from cache, don't write
    as_graph = self.ASGraphConstructorCls(**constructor_kwargs).run()
    engine = self.SimulationEngineCls(as_graph, ...)
    return engine
```

This avoids attempting to pickle the graph (which fails due to weakrefs in AS neighbor relationships).

**Sources:**[bgpy/simulation_framework/simulation.py461-474](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L461-L474)

## Configuration Examples

### Default Configuration

The default configuration downloads and caches CAIDA data with minimal memory usage:

```
Simulation(
    ASGraphConstructorCls=CAIDAASGraphConstructor,
    as_graph_constructor_kwargs=frozendict({
        "as_graph_collector_kwargs": frozendict({
            "cache_dir": SINGLE_DAY_CACHE_DIR,
        }),
        "as_graph_kwargs": frozendict({
            "store_customer_cone_size": True,
            "store_customer_cone_asns": False,
            "store_provider_cone_size": False,
            "store_provider_cone_asns": False,
        }),
    })
)
```

**Memory usage:** ~0.9GB per core

**Sources:**[bgpy/simulation_framework/simulation.py78-100](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L78-L100)

### High-Memory Configuration

For analyses requiring full cone information:

```
as_graph_constructor_kwargs=frozendict({
    "as_graph_kwargs": frozendict({
        "store_customer_cone_size": True,
        "store_customer_cone_asns": True,
        "store_provider_cone_size": True,
        "store_provider_cone_asns": True,
    }),
})
```

**Memory usage:** ~2.3GB per core

**Sources:**[bgpy/simulation_framework/simulation.py88-97](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L88-L97)[bgpy/simulation_framework/simulation.py215-248](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L215-L248)

### TSV Caching Configuration

To cache the graph as TSV for faster subsequent loads:

```
as_graph_constructor_kwargs=frozendict({
    "tsv_path": Path.home() / "Desktop" / "caida.tsv",
})
```

The TSV file is written after construction and can be used to bypass CAIDA parsing in future runs.

**Sources:**[bgpy/simulation_framework/simulation.py98](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L98-L98)