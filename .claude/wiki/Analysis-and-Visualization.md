# Analysis and Visualization
Relevant source files
- [bgpy/simulation_framework/__init__.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/__init__.py)
- [bgpy/simulation_framework/as_graph_analyzers/__init__.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/as_graph_analyzers/__init__.py)
- [bgpy/simulation_framework/as_graph_analyzers/as_graph_analyzer.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/as_graph_analyzers/as_graph_analyzer.py)
- [bgpy/simulation_framework/as_graph_analyzers/interception_as_graph_analyzer.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/as_graph_analyzers/interception_as_graph_analyzer.py)
- [bgpy/simulation_framework/graph_data_aggregator/graph_category.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graph_data_aggregator/graph_category.py)
- [bgpy/simulation_framework/graph_data_aggregator/graph_data_aggregator.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graph_data_aggregator/graph_data_aggregator.py)
- [bgpy/simulation_framework/graph_data_aggregator/trial_data.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graph_data_aggregator/trial_data.py)
- [bgpy/simulation_framework/graphing/__init__.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/__init__.py)
- [bgpy/simulation_framework/graphing/graph_factory/__init__.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/graph_factory/__init__.py)
- [bgpy/simulation_framework/graphing/graph_factory/add_legends_and_save_funcs.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/graph_factory/add_legends_and_save_funcs.py)
- [bgpy/simulation_framework/graphing/graph_factory/generate_graph_funcs.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/graph_factory/generate_graph_funcs.py)
- [bgpy/simulation_framework/graphing/graph_factory/graph_factory.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/graph_factory/graph_factory.py)
- [bgpy/simulation_framework/graphing/graph_factory/preprocessing_funcs.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/graph_factory/preprocessing_funcs.py)
- [bgpy/simulation_framework/graphing/line_data.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/line_data.py)
- [bgpy/simulation_framework/graphing/line_info.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/line_info.py)
- [bgpy/simulation_framework/graphing/line_properties_generator.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/line_properties_generator.py)
- [bgpy/simulation_framework/scenarios/__init__.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/__init__.py)
- [bgpy/simulation_framework/scenarios/custom_scenarios/__init__.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/custom_scenarios/__init__.py)
- [bgpy/simulation_framework/utils.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/utils.py)
- [bgpy/tests/engine_tests/utils/diagram_aggregator.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/diagram_aggregator.py)
- [scripts/debug_metric_keys.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/scripts/debug_metric_keys.py)
- [scripts/dependent_ex.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/scripts/dependent_ex.py)
- [scripts/tutorial/main_tutorial/simulation.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/scripts/tutorial/main_tutorial/simulation.py)

## Purpose and Scope

This document covers the analysis and visualization pipeline in BGPy, which transforms simulation results into interpretable metrics and publication-ready graphs. After the `SimulationEngine` completes BGP propagation, the analysis pipeline determines outcomes for each AS, aggregates statistics across multiple trials, and generates visualizations showing how security policies perform against various attacks.

For detailed information on specific components, see:

- Outcome classification and traceback logic: [Outcome Analysis](/blcrdbob3/bgpy_pkg/8.1-outcome-analysis)
- Statistical aggregation across trials: [Data Aggregation](/blcrdbob3/bgpy_pkg/8.2-data-aggregation)
- Graph generation and styling: [Graph Generation](/blcrdbob3/bgpy_pkg/8.3-graph-generation)
- AS graph diagram generation: [Diagram Generation](/blcrdbob3/bgpy_pkg/8.4-diagram-generation)

## Analysis Pipeline Overview

The analysis pipeline consists of three main stages that transform raw simulation state into final visualizations:

```
Persistence

Stage 3: Visualization

Stage 2: Data Aggregation

Stage 1: Outcome Analysis

SimulationEngine
(Final State)

ASGraphAnalyzer

outcomes dict
{plane: {asn: outcome}}

TrialData
(per-trial numerator/denominator)

GraphDataAggregator

DataPointAggData
(mean + yerr)

GraphFactory

LineData objects
(xs, ys, yerrs, styling)

PNG files
(publication-ready)

CSV files

Pickle files

YAML files
```

**Stage 1: Outcome Analysis** - The `ASGraphAnalyzer` examines each AS's local RIB to determine whether it routes to the attacker, victim, or is disconnected.

**Stage 2: Data Aggregation** - The `GraphDataAggregator` collects metrics from multiple trials, computing means and confidence intervals.

**Stage 3: Visualization** - The `GraphFactory` generates graphs with proper styling, legends, and "strongest attacker" aggregation lines.

Sources: [bgpy/simulation_framework/as_graph_analyzers/as_graph_analyzer.py1-187](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/as_graph_analyzers/as_graph_analyzer.py#L1-L187)[bgpy/simulation_framework/graph_data_aggregator/graph_data_aggregator.py1-268](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graph_data_aggregator/graph_data_aggregator.py#L1-L268)[bgpy/simulation_framework/graphing/graph_factory/graph_factory.py1-213](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/graph_factory/graph_factory.py#L1-L213)

## Key Components and Data Structures

### Core Analysis Classes
ClassFilePurpose`ASGraphAnalyzer``as_graph_analyzers/as_graph_analyzer.py`Determines data plane and control plane outcomes for each AS`InterceptionASGraphAnalyzer``as_graph_analyzers/interception_as_graph_analyzer.py`Specialized analyzer for interception attacks`GraphDataAggregator``graph_data_aggregator/graph_data_aggregator.py`Aggregates trial data and computes statistics`GraphFactory``graphing/graph_factory/graph_factory.py`Generates matplotlib visualizations
### Data Structures

The analysis pipeline uses several immutable data structures to organize metrics:

```
Visualization Data

Aggregated Data

Trial Data

Data Point Identification

Categorization

GraphCategory
plane: Plane
as_group: ASGroups
outcome: Outcomes
in_adopting_asns: InAdoptingASNs

DataPointKey
propagation_round: int
percent_adopt: float
scenario_config: ScenarioConfig

TrialData
numerator: float
denominator: float
graph_category: GraphCategory

DataPointAggData
value: float
yerr: float
data_point_key: DataPointKey

LineData
xs: tuple[float, ...]
ys: tuple[float, ...]
yerrs: tuple[float, ...]
line_info: LineInfo

LineInfo
label: str
marker: str
ls: str
color: str
extra_kwargs: frozendict
```

**GraphCategory** - Identifies a specific type of graph (e.g., "data plane, stub ASes, attacker success, adopting ASes"). Each unique `GraphCategory` generates one PNG file.

**DataPointKey** - Identifies a single point on a graph, defined by the propagation round, percent adoption, and scenario configuration.

**TrialData** - Tracks numerator and denominator for a single trial. For example, if measuring "attacker success in adopting ASes," the numerator is the count of adopting ASes where the attacker succeeded, and the denominator is the total count of adopting ASes.

**DataPointAggData** - Contains the aggregated value (mean across trials) and error bars (90% confidence interval) for a data point.

**LineData** - Contains all information needed to plot a single line on a graph: x-values (percent adoptions), y-values (metric values), error bars, and styling information.

**LineInfo** - Defines styling properties for a line: label, marker style, line style, color, and additional matplotlib kwargs.

Sources: [bgpy/simulation_framework/graph_data_aggregator/graph_category.py1-14](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graph_data_aggregator/graph_category.py#L1-L14)[bgpy/simulation_framework/graph_data_aggregator/data_point_key.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graph_data_aggregator/data_point_key.py)[bgpy/simulation_framework/graph_data_aggregator/trial_data.py1-102](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graph_data_aggregator/trial_data.py#L1-L102)[bgpy/simulation_framework/graph_data_aggregator/data_point_agg_data.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graph_data_aggregator/data_point_agg_data.py)[bgpy/simulation_framework/graphing/line_data.py1-17](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/line_data.py#L1-L17)[bgpy/simulation_framework/graphing/line_info.py1-35](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/line_info.py#L1-L35)

## Outcome Determination

The `ASGraphAnalyzer` determines outcomes through two independent methods:

### Data Plane Analysis (Traceback)

Data plane analysis follows the `next_hop_asn` field recursively to determine the ultimate destination of traffic:

```
Yes

No

No

Yes

Yes

No

Yes

No

Yes

No

Yes

No

AS receives traffic
for victim prefix

Outcome
cached?

Get most specific
announcement from RIB

Announcement
exists?

AS is
attacker?

AS is
victim?

End of path?
(len==1 or next_hop==self)

Loop
detected?

Recursively analyze
next_hop_asn

Return cached outcome

ATTACKER_SUCCESS

VICTIM_SUCCESS

DISCONNECTED

DATA_PLANE_LOOP
```

The traceback logic is implemented in `_get_as_outcome_data_plane()` which recursively follows the `next_hop_asn` field of announcements. The algorithm maintains a `visited_asns` set to detect routing loops and caches results in `_data_plane_outcomes` to avoid redundant computation.

Sources: [bgpy/simulation_framework/as_graph_analyzers/as_graph_analyzer.py86-150](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/as_graph_analyzers/as_graph_analyzer.py#L86-L150)

### Control Plane Analysis

Control plane analysis examines the `origin` field of announcements without traceback:

```
No

Yes

Yes

No

Yes

No

Analyze AS control plane

Get most specific
announcement from RIB

Announcement
exists?

ann.origin in
attacker_asns?

ann.origin in
victim_asns?

DISCONNECTED

ATTACKER_SUCCESS

VICTIM_SUCCESS
```

Control plane analysis is simpler because it only checks the announcement origin, not the full routing path. This is useful for understanding which routes are being propagated, regardless of where traffic actually flows.

Sources: [bgpy/simulation_framework/as_graph_analyzers/as_graph_analyzer.py155-178](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/as_graph_analyzers/as_graph_analyzer.py#L155-L178)

## Trial Aggregation and Statistical Analysis

The `GraphDataAggregator` collects data across multiple trials to compute statistical measures:

### Per-Trial Data Collection

For each trial, the aggregator creates a `TrialData` object for every `GraphCategory`. As it iterates through ASes, it updates numerators and denominators:

```
Result

For each AS in trial

Yes

No

Yes

No

Yes

No

AS object

AS in
target group?

Matches adoption
filter?

denominator += 1

Outcome matches
target?

numerator += 1

percent =
numerator * 100 / denominator
```

Example: For the graph category "data plane, stub ASes, attacker success, adopting ASes":

- **Denominator**: Count of ASes that are (1) stubs AND (2) adopting the security policy
- **Numerator**: Count of those ASes where the data plane outcome is `ATTACKER_SUCCESS`
- **Percent**: `(numerator / denominator) * 100`

Sources: [bgpy/simulation_framework/graph_data_aggregator/trial_data.py23-102](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graph_data_aggregator/trial_data.py#L23-L102)

### Cross-Trial Aggregation

After all trials complete, the aggregator computes statistics for each `DataPointKey`:

```
List of percentages
from all trials
[45.2, 47.8, 46.1, ...]

mean = sum(percentages) / len(percentages)

stdev = standard_deviation(percentages)

yerr = 1.645 * 2 * stdev / sqrt(n)
(90% confidence interval)

DataPointAggData
value=mean, yerr=yerr
```

The error bars represent 90% confidence intervals, calculated using the formula: `1.645 * 2 * stdev / sqrt(n)`, where `n` is the number of trials. This gives users a sense of the variance in results.

Sources: [bgpy/simulation_framework/graph_data_aggregator/graph_data_aggregator.py259-267](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graph_data_aggregator/graph_data_aggregator.py#L259-L267)

## Graph Generation Process

The `GraphFactory` transforms aggregated data into publication-ready matplotlib graphs:

### Preprocessing and Line Construction

```
Finalization

Plotting

Preprocessing

Input

Pickle file with
GraphCategory -> DataPointKey -> DataPointAggData

Filter to last
propagation round

Group by
scenario_label

For each label:
Create LineData
(sort by percent_adopt,
extract xs/ys/yerrs)

Apply LineInfo styling
(marker, color, linestyle)

Plot non-aggregated lines

Plot strongest attacker
aggregation lines

Plot scatter points
for strongest attacker

Add primary legend
(sorted by mean value)

Add secondary legend
(strongest attacker markers)

Save to PNG
```

The factory processes each `GraphCategory` independently, generating one PNG file per category. The filename encodes the graph properties: `{as_group}/in_adopting_asns_is_{in_adopting_asns}/{plane}/{outcome}.png`.

Sources: [bgpy/simulation_framework/graphing/graph_factory/graph_factory.py163-172](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/graph_factory/graph_factory.py#L163-L172)[bgpy/simulation_framework/graphing/graph_factory/preprocessing_funcs.py23-41](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/graph_factory/preprocessing_funcs.py#L23-L41)

### Strongest Attacker Aggregation

The "strongest attacker" feature creates envelope lines showing the maximum attack success across multiple attack types:

```
Visualization

Aggregation Process

Input Lines

Forged Origin
ys: [20, 35, 48, 60, 70]

Shortest Path
ys: [15, 30, 55, 65, 68]

First ASN Strip
ys: [10, 25, 40, 50, 62]

For each x:
max_y = max(ForgedOrigin[x],
ShortestPath[x],
FirstASN[x])

Create envelope line
ys: [20, 35, 55, 65, 70]

Track which attack
was strongest at each x

Plot envelope line
(no markers)

Plot scatter points
at (x, max_y) with
marker showing best attack
```

This allows researchers to visualize the "worst-case" attack scenario at each adoption level. The scatter points use different markers to show which specific attack was strongest at each point.

Sources: [bgpy/simulation_framework/graphing/graph_factory/generate_graph_funcs.py62-137](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/graph_factory/generate_graph_funcs.py#L62-L137)

## Output Formats

The analysis pipeline produces multiple output formats for different use cases:

### CSV Files

Human-readable tabular data with columns:

- `scenario_cls`, `AdoptingPolicyCls`, `BasePolicyCls`
- `in_adopting_asns`, `outcome_type`, `as_group`, `outcome`
- `percent_adopt`, `propagation_round`
- `value` (mean), `yerr` (error bars)
- `scenario_config_label`, `scenario_label`

Sources: [bgpy/simulation_framework/graph_data_aggregator/graph_data_aggregator.py177-217](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graph_data_aggregator/graph_data_aggregator.py#L177-L217)

### Pickle Files

Python objects for programmatic access:

```
dict[GraphCategory, dict[DataPointKey, DataPointAggData]]

```

This format preserves full type information and allows easy manipulation of results in Python scripts.

Sources: [bgpy/simulation_framework/graph_data_aggregator/graph_data_aggregator.py219-231](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graph_data_aggregator/graph_data_aggregator.py#L219-L231)

### PNG Graphs

Publication-ready visualizations with:

- X-axis: Percent adoption (0-100%)
- Y-axis: Metric value (e.g., percent attacker success)
- Error bars: 90% confidence intervals
- Primary legend: Sorted by mean value (descending)
- Secondary legend: Strongest attacker markers (if applicable)
- DPI: 300 for high-resolution output

Sources: [bgpy/simulation_framework/graphing/graph_factory/preprocessing_funcs.py53-68](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/graph_factory/preprocessing_funcs.py#L53-L68)[bgpy/simulation_framework/graphing/graph_factory/add_legends_and_save_funcs.py147-172](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/graph_factory/add_legends_and_save_funcs.py#L147-L172)

### YAML Files (Engine State)

For debugging and reproducibility, the simulation can export the complete engine state and outcomes to YAML format. This includes the full AS graph topology, routing tables, and analysis results.

Sources: [bgpy/simulation_framework/utils.py1-50](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/utils.py#L1-L50)

## Line Styling and Customization

The `LineInfo` and `LinePropertiesGenerator` classes provide flexible styling:

### Automatic Style Assignment

The `LinePropertiesGenerator` cycles through markers, line styles, and colors:
PropertyOptionsMarkers`.`, `1`, `*`, `x`, `d`, `2`, `3`, `4`, `v`, `+`, `s`Line Styles`-`, `--`, `-.`, `:`, `solid`, `dotted`, `dashdot`, `dashed`Colors`b`, `g`, `r`, `c`, `m`, `y`, `darkorange`, `darkgoldenrod`, `lightcoral`, `sienna`, `gold`, `darkolivegreen`, `steelblue`
The generator expands options in a pattern to maximize visual distinctiveness before repeating combinations.

Sources: [bgpy/simulation_framework/graphing/line_properties_generator.py1-70](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/line_properties_generator.py#L1-L70)

### Manual Style Override

Users can provide a `line_info_dict` to the `GraphFactory` constructor to override default styling:

```
line_info_dict = frozendict({
    "ROV": LineInfo(
        label="ROV",
        marker="o",
        ls="solid",
        color="blue"
    ),
    "ASPA": LineInfo(
        label="ASPA",
        marker="s",
        ls="dashed",
        color="red"
    )
})
```

This enables consistent styling across multiple simulation runs.

Sources: [bgpy/simulation_framework/graphing/line_info.py11-35](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/line_info.py#L11-L35)[bgpy/simulation_framework/graphing/graph_factory/graph_factory.py53-105](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/graph_factory/graph_factory.py#L53-L105)

## Integration with Simulation Framework

The analysis pipeline integrates with the simulation framework through the `Simulation` class:

```
GraphFactory
GraphDataAggregator
ASGraphAnalyzer
SimulationEngine
Simulation
GraphFactory
GraphDataAggregator
ASGraphAnalyzer
SimulationEngine
Simulation
Increments numerators/
denominators for each
GraphCategory
loop
[For each trial]
Computes means and yerrs
run_trial(scenario, percent_adopt)
engine (final state)
__init__(engine, scenario)
analyze()
outcomes dict
aggregate_and_store_trial_data(...)
run_trial(...)
analyze()
aggregate_and_store_trial_data(...)
write_data(csv_path, pickle_path)
__init__(pickle_path, graph_dir)
generate_graphs()
PNG files written
```

The `Simulation` class coordinates the entire pipeline, calling each component in sequence. After all trials complete, it writes aggregated data to CSV and pickle files, then generates graphs.

Sources: [bgpy/simulation_framework/__init__.py1-60](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/__init__.py#L1-L60)