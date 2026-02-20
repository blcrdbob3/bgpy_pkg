# Diagram Generation
Relevant source files
- [bgpy/simulation_engine/ann_containers/ann_container.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/ann_containers/ann_container.py)
- [bgpy/simulation_engine/policies/aspa/aspa.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/aspa/aspa.py)
- [bgpy/simulation_engine/policies/bgp/bgp/propagate_funcs.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/bgp/bgp/propagate_funcs.py)
- [bgpy/simulation_engine/policies/path_end/path_end.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_engine/policies/path_end/path_end.py)
- [bgpy/utils/engine_runner/diagram.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/diagram.py)

## Purpose and Scope

This document describes the `Diagram` class and its role in generating visual representations of AS graphs with routing outcomes. The diagram generation system creates publication-ready visualizations that show the network topology, BGP announcement propagation, and data plane outcomes for individual simulation trials.

For statistical aggregation of trial results and graph generation across multiple trials, see [Graph Generation](/blcrdbob3/bgpy_pkg/8.3-graph-generation). For the analysis of routing outcomes that feeds into diagram generation, see [Outcome Analysis](/blcrdbob3/bgpy_pkg/8.1-outcome-analysis).

**Sources:**[bgpy/utils/engine_runner/diagram.py1-306](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/diagram.py#L1-L306)

---

## Overview

The diagram generation system produces visualizations using the Graphviz library to render AS-level network topologies with the following information:

- **AS Nodes**: Display ASN, policy type, and local RIB contents
- **Relationships**: Provider-customer (directed edges) and peer (undirected dashed edges)
- **Outcomes**: Color-coded nodes showing data plane routing destinations (attacker, victim, or disconnected)
- **Legend**: Outcome statistics and ROA information
- **Traceback Data**: Visual representation of where traffic actually flows in the data plane

### Diagram Generation Flow

```
Output

Construction Steps

Diagram Class

Input Data

BaseSimulationEngine
(post-propagation state)

Scenario
(attacker/victim ASNs, ROAs)

traceback: dict[int, int]
(AS → Outcome mapping)

diagram_ranks
(AS groupings by rank)

Diagram.init()
Create Digraph

generate_as_graph()

_add_legend()
Outcome counts + ROAs

_display_next_hop_asn()
Detect next_hop manipulation

_add_ases()
Create AS nodes with RIBs

_add_edges()
Provider/customer/peer links

_add_diagram_ranks()
Layout optimization

_add_description()
Metadata text

_render()
Generate PNG

AS Graph Visualization
(diagram.png)
```

**Sources:**[bgpy/utils/engine_runner/diagram.py16-45](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/diagram.py#L16-L45)

---

## Diagram Class

### Class Structure

The `Diagram` class encapsulates all diagram generation logic and maintains a `graphviz.Digraph` instance as state.
AttributeTypeDescription`dot``Digraph`Graphviz graph object that accumulates nodes, edges, and styling
**Sources:**[bgpy/utils/engine_runner/diagram.py16-22](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/diagram.py#L16-L22)

### Primary Method: generate_as_graph()

The `generate_as_graph()` method orchestrates the entire diagram construction process:

```
def generate_as_graph(
    self,
    engine: BaseSimulationEngine,
    scenario: Scenario,
    traceback: dict[int, int],  # AS ASN → Outcome enum value
    description: str,
    graph_data_aggregator: "GraphDataAggregator",
    diagram_ranks: tuple[tuple["AS", ...], ...],
    static_order: bool = False,
    path: Path | None = None,
    view: bool = False,
    dpi: int | None = None,
) -> None
```
ParameterTypePurpose`engine``BaseSimulationEngine`Contains the AS graph with final routing state`scenario``Scenario`Provides attacker/victim ASNs and ROA information`traceback``dict[int, int]`Maps each AS ASN to its data plane outcome`description``str`Metadata text displayed at bottom of diagram`diagram_ranks``tuple[tuple["AS", ...], ...]`Nested tuple grouping ASes by propagation rank for layout`static_order``bool`Whether to enforce strict ordering within ranks`path``Path | None`Output file path (without extension)`view``bool`Whether to automatically open the rendered diagram`dpi``int | None`Resolution for PNG output
**Sources:**[bgpy/utils/engine_runner/diagram.py24-44](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/diagram.py#L24-L44)

---

## AS Node Representation

### Node Construction Pipeline

```
Styling

HTML Table Structure

Node Generation

AS Object Data Extraction

AS object
(from engine.as_graph)

policy.local_rib
(prefix → Ann mapping)

asn: int

policy.name: str

_encode_as_obj_as_node()

_get_html()
Build HTML table

_get_kwargs()
Styling attributes

ASN row
(with emoji if attacker/victim)

Policy name row

Local RIB header

Announcement rows
(prefix, path, emoji, next_hop)

shape: circle/octagon/double

fillcolor: gradient based on outcome

Graphviz attributes
```

**Sources:**[bgpy/utils/engine_runner/diagram.py114-146](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/diagram.py#L114-L146)

### Node HTML Structure

Each AS node is rendered as an HTML table with the following structure:
Row ContentDescriptionExampleASNAutonomous System Number with emoji if attacker (😈) or victim (😇)`😈666😈`Policy NameName of the BGP policy deployed`(ASPA)`Local RIB HeaderSeparator indicating RIB contents follow`Local RIB`Announcement RowsOne row per announcement: `mask | path | emoji | [next_hop]``/24 | 1, 2, 3 | 😈 | 2`
The announcement emoji indicates:

- `😈` (U+1F608): Announcement contains attacker ASN in path
- `😇` (U+1F607): Announcement originated by victim
- `☁` (U+1F6E1): Preventive announcement (e.g., ROV++ proactive defense)
- `✱` (U+2731): ROV++ blackhole announcement

**Sources:**[bgpy/utils/engine_runner/diagram.py148-206](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/diagram.py#L148-L206)

### Node Styling and Color Coding

```
Node Attributes

Outcome-Based Coloring

Policy Type Check

Attacker/Victim Identification

Yes

No

Yes

No

Basic BGP

Security Policy

Basic BGP

Security Policy

ASN in
scenario.attacker_asns?

ASN in
scenario.victim_asns?

policy in
[BGPFull, BGP]?

traceback[asn]

ATTACKER_SUCCESS

VICTIM_SUCCESS

DISCONNECTED

fillcolor: #FF7F7F
shape: doublecircle or doubleoctagon

fillcolor: #90ee90
shape: doublecircle or doubleoctagon

fillcolor: #ff6060:yellow
shape: circle or octagon

fillcolor: #90ee90:white
shape: circle or octagon

fillcolor: grey:white
shape: circle or octagon
```
Node CategoryFill ColorShapeMeaningAttacker AS`#FF7F7F` (light red)`doublecircle` (BGP) or `doubleoctagon` (security policy)AS initiating the attackVictim AS`#90ee90` (light green)`doublecircle` (BGP) or `doubleoctagon` (security policy)AS being attackedOther AS → Attacker`#ff6060:yellow` (red-to-yellow gradient)`circle` (BGP) or `octagon` (security policy)Data plane traffic flows to attackerOther AS → Victim`#90ee90:white` (green-to-white gradient)`circle` (BGP) or `octagon` (security policy)Data plane traffic flows to victimOther AS → Disconnected`grey:white` (grey-to-white gradient)`circle` (BGP) or `octagon` (security policy)No valid route to destination
**Sources:**[bgpy/utils/engine_runner/diagram.py208-247](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/diagram.py#L208-L247)

---

## Edge Representation

### Relationship Types

The diagram displays two types of AS relationships:
RelationshipVisual RepresentationGraphviz AttributesMeaningProvider-CustomerDirected edge (arrow)`dir="forward"` (default)Provider (tail) → Customer (head)Peer-PeerUndirected dashed edge`dir="none"`, `style="dashed"`, `penwidth="2"`Mutual peering relationship
### Edge Generation Logic

```
Peer Edges

Provider-Customer Edges

Iterate AS Graph

Yes
Avoid duplicates

No
Skip

for as_obj in engine.as_graph

for customer_obj in as_obj.customers

dot.edge(provider_asn, customer_asn)

for peer_obj in as_obj.peers

as_obj.asn > peer_obj.asn?

dot.edge(asn1, asn2,
dir='none', style='dashed')
```

The peer edge deduplication check (`as_obj.asn > peer_obj.asn`) ensures that each peer relationship is only added once, since peering is symmetric and iterating over all ASes would otherwise create duplicate edges.

**Sources:**[bgpy/utils/engine_runner/diagram.py249-266](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/diagram.py#L249-L266)

---

## Legend and Metadata

### Legend Components

The legend is rendered as an HTML table in the top-left corner containing:

1. **Outcome Statistics** (for the most specific prefix only):

- Attacker Success Count: Number of ASes with `Outcomes.ATTACKER_SUCCESS`
- Victim Success Count: Number of ASes with `Outcomes.VICTIM_SUCCESS`
- Disconnected Count: Number of ASes with `Outcomes.DISCONNECTED`
2. **ROA Information**: Table of all ROAs in the scenario:

- Prefix: IP prefix covered by ROA
- Origin: Authorized origin ASN
- Max Length: Maximum prefix length allowed

```
ROA Iteration

Outcome Counting

Legend Construction

Count outcomes from traceback dict

Outcome Statistics Table
(colored rows)

ROA Information Table

sum(1 for x in traceback.values()
if x == ATTACKER_SUCCESS)

sum(1 for x in traceback.values()
if x == VICTIM_SUCCESS)

sum(1 for x in traceback.values()
if x == DISCONNECTED)

for roa in scenario.roas

TR: prefix | origin | max_length

Legend
```

**Sources:**[bgpy/utils/engine_runner/diagram.py46-94](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/diagram.py#L46-L94)

### Description Metadata

A description string is rendered at the bottom of the diagram using Graphviz's `label` attribute. When `next_hop_asn` is displayed, the description is automatically augmented with column explanations.

**Sources:**[bgpy/utils/engine_runner/diagram.py292-298](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/diagram.py#L292-L298)

---

## Next Hop ASN Display

### Detection Logic

The `_display_next_hop_asn()` method determines whether to show the `next_hop_asn` column in local RIBs. This column is displayed only when the next hop has been manipulated, which occurs when:

1. **Single-hop paths**: `ann.as_path[0] != ann.next_hop_asn` (origin manipulated next hop)
2. **Multi-hop paths**: `ann.as_path[1] != ann.next_hop_asn` (intermediate AS manipulated next hop)

```
Result

Next Hop Validation

Check All Announcements

1

>1

Yes

No

Yes

No

All checked

for as_obj in engine.as_graph

for ann in as_obj.policy.local_rib.values()

len(ann.as_path)

as_path[0] !=
next_hop_asn?

as_path[1] !=
next_hop_asn?

return True
(display next_hop column)

return False
(hide next_hop column)
```

This is relevant for scenarios where attacks manipulate the next hop field, such as route leaks or certain ASPA evasion techniques.

**Sources:**[bgpy/utils/engine_runner/diagram.py96-112](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/diagram.py#L96-L112)

---

## Diagram Ranks and Layout

### Rank Organization

Diagram ranks control the vertical positioning of nodes to reflect the AS hierarchy and propagation order. ASes in the same rank are placed at the same vertical level.
Layout ModeDescriptionUse CaseDynamic (`static_order=False`)Nodes within ranks can be reordered by Graphviz for aesthetic optimizationDefault mode for cleaner layoutsStatic (`static_order=True`)Nodes within ranks maintain strict left-to-right order using invisible edgesWhen precise ordering matters for analysis
### Rank Implementation

```
Static Order Mode

Dynamic Order Mode

Rank Iteration

False

True

for i, rank in enumerate(diagram_ranks)

Create Digraph subgraph
with name 'Propagation_rank_i'

subgraph.attr(rank='same')

Add all AS nodes to subgraph

Create inline subgraph
(with statement)

subgraph.attr(rank='same')

Iterate ASes in rank

Add invisible edge
from previous to current

static_order?
```

In static order mode, invisible edges (`style="invis"`) are added between consecutive nodes in a rank to enforce left-to-right ordering: `previous_asn → current_asn [style="invis"]`.

**Sources:**[bgpy/utils/engine_runner/diagram.py268-290](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/diagram.py#L268-L290)

---

## Rendering and Output

### Render Method

The `_render()` method invokes Graphviz to generate the final PNG image:

```
def _render(
    self, 
    path: Path | None = None, 
    view: bool = False, 
    dpi: int | None = None
) -> None
```
ParameterTypePurpose`path``Path | None`Output file path without extension (`.png` appended automatically)`view``bool`If `True`, automatically opens the rendered diagram in the default viewer`dpi``int | None`Dots per inch for PNG resolution (higher = sharper but larger file)
**Sources:**[bgpy/utils/engine_runner/diagram.py300-305](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/diagram.py#L300-L305)

---

## Integration with Testing Framework

The diagram generation system is primarily used within the testing framework via `EngineTester`. After each simulation trial, diagrams can be generated to visually debug routing behavior:

```
Test Aggregation

Diagram Generation

Post-Simulation Analysis

Test Execution

EngineTester

_run_engine()

ASGraphAnalyzer

data_plane_outcomes
(traceback dict)

Diagram()

generate_as_graph()

test_output/diagram.png

pytest_sessionfinish

Combine all test diagrams
into single PDF
```

The `pytest_sessionfinish` hook in the test framework collects all generated diagrams and combines them into a single PDF for easy review of multiple test cases.

**Sources:**[bgpy/utils/engine_runner/diagram.py1-306](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/diagram.py#L1-L306)

---

## Example Node Configurations

### AS Node Examples

Here are examples of how different AS types appear in the diagram:
AS TypeVisual RepresentationDescriptionAttacker with BGPRed double circle with ASN `😈666😈`Basic BGP policy, initiating attackVictim with ASPAGreen double octagon with ASN `😇1😇`Advanced security policy, under attackTransit AS routing to attackerCircle/octagon with red-to-yellow gradientNeither attacker nor victim, but forwards traffic to attackerStub AS routing to victimCircle/octagon with green-to-white gradientSuccessfully routing to legitimate destinationDisconnected ASCircle/octagon with grey-to-white gradientNo valid route due to security policy blocking announcements
**Sources:**[bgpy/utils/engine_runner/diagram.py208-247](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/utils/engine_runner/diagram.py#L208-L247)