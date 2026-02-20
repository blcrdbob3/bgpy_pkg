# Graph Generation
Relevant source files
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
- [bgpy/simulation_framework/utils.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/utils.py)
- [bgpy/tests/engine_tests/utils/diagram_aggregator.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/utils/diagram_aggregator.py)
- [scripts/debug_metric_keys.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/scripts/debug_metric_keys.py)
- [scripts/dependent_ex.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/scripts/dependent_ex.py)
- [scripts/tutorial/main_tutorial/simulation.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/scripts/tutorial/main_tutorial/simulation.py)

This document describes the graph generation system responsible for converting aggregated trial data into publication-ready visualizations. The `GraphFactory` class reads pickled data from the `GraphDataAggregator` (see [Data Aggregation](/blcrdbob3/bgpy_pkg/8.2-data-aggregation)) and produces PNG graphs with customizable styling, legends, and error bars.

For information about how trial outcomes are analyzed and aggregated, see [Outcome Analysis](/blcrdbob3/bgpy_pkg/8.1-outcome-analysis) and [Data Aggregation](/blcrdbob3/bgpy_pkg/8.2-data-aggregation). For AS graph topology diagrams, see [Diagram Generation](/blcrdbob3/bgpy_pkg/8.4-diagram-generation).

---

## Architecture Overview

The graph generation system consists of several specialized components that work together to transform aggregated data into styled visualizations.

**System Component Diagram**

```
Output

Styling System

GraphFactory Class

Input Data

PICKLE_DATA_TYPE
GraphCategory → DataPointAggData

GraphFactory
bgpy/simulation_framework/graphing/graph_factory/graph_factory.py

Preprocessing Functions
preprocessing_funcs.py

Generate Graph Functions
generate_graph_funcs.py

Legend and Save Functions
add_legends_and_save_funcs.py

LineInfo
line_info.py

LineData
line_data.py

LinePropertiesGenerator
line_properties_generator.py

PNG Graphs
Organized by GraphCategory
```

Sources: [bgpy/simulation_framework/graphing/graph_factory/graph_factory.py1-213](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/graph_factory/graph_factory.py#L1-L213)[bgpy/simulation_framework/graphing/__init__.py1-7](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/__init__.py#L1-L7)

---

## GraphFactory Class

The `GraphFactory` class is the main orchestrator for graph generation. It loads pickled data, filters it, and generates all graphs in batch.

### Initialization

The `GraphFactory` constructor accepts extensive configuration options for customizing graph appearance:
ParameterTypePurpose`pickle_path``Path`Path to pickled `PICKLE_DATA_TYPE` data from `GraphDataAggregator``graph_dir``Path`Output directory for PNG graphs`label_replacement_dict``frozendict`Maps scenario labels to display labels`x_axis_label_replacement_dict``frozendict`Customizes x-axis labels`y_axis_label_replacement_dict``frozendict`Customizes y-axis labels`x_limit``int`Maximum x-axis value (default 100)`y_limit``int`Maximum y-axis value (default 100)`line_info_dict``frozendict[str, LineInfo]`Pre-configured line styling`strongest_attacker_dict``frozendict[str, tuple[LineInfo, ...]]`Defines strongest attacker aggregations`labels_to_remove``frozenset[str]`Labels to exclude from graphs`add_legend``bool`Whether to add legend (default `True`)
Sources: [bgpy/simulation_framework/graphing/graph_factory/graph_factory.py53-105](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/graph_factory/graph_factory.py#L53-L105)

### Data Filtering

Upon initialization, `GraphFactory` performs several filtering operations:

1. **Propagation Round Filtering**: Extracts only the final propagation round for each scenario via `_get_last_propagation_round_graph_data()`. This ensures graphs show converged results.
2. **Label Removal**: Filters out unwanted scenario labels using `_remove_labels()`.
3. **Line Info Filtering**: Retains only `LineInfo` objects relevant to labels present in the data.
4. **Strongest Attacker Filtering**: Retains only strongest attacker configurations where constituent lines exist in the data.

Sources: [bgpy/simulation_framework/graphing/graph_factory/graph_factory.py107-161](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/graph_factory/graph_factory.py#L107-L161)

### Main Entry Point

The `generate_graphs()` method iterates through all `GraphCategory` keys in the pickled data and generates one PNG per category:

```
def generate_graphs(self) -> None:
    """Generates default graphs"""
    for graph_category, data_dict in tqdm(self.graph_data.items(), ...):
        self._generate_graph(graph_category, data_dict)
```

Sources: [bgpy/simulation_framework/graphing/graph_factory/graph_factory.py163-172](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/graph_factory/graph_factory.py#L163-L172)

---

## Line Styling System

The styling system separates line appearance configuration (`LineInfo`) from line data (`LineData`) for maximum flexibility.

### LineInfo Class

`LineInfo` is a frozen dataclass that defines how a line appears on a graph:
FieldTypePurpose`label``str`Display label for the line`marker``str`Matplotlib marker style (e.g., `"."`, `"x"`, `"*"`)`ls``str`Line style (e.g., `"-"`, `"--"`, `"-."`)`color``str`Matplotlib color (e.g., `"b"`, `"darkorange"`)`unrelated_to_adoption``bool`If `True`, averages y-values across all adoption percentages`hardcoded_xs``tuple[float, ...]`Manually specified x-values (overrides data)`hardcoded_ys``tuple[float, ...]`Manually specified y-values (overrides data)`hardcoded_yerrs``tuple[float, ...]`Manually specified error bars (overrides data)`extra_kwargs``frozendict`Additional matplotlib kwargs (e.g., `lw`, `zorder`)`strongest_attacker_legend_label``str | None`Label for strongest attacker legend entry
The `__post_init__` method automatically generates default marker, line style, and color if not provided using `LinePropertiesGenerator`.

Sources: [bgpy/simulation_framework/graphing/line_info.py1-35](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/line_info.py#L1-L35)

### LineData Class

`LineData` combines `LineInfo` with actual plot data:
FieldTypePurpose`label``str`Line label`formatted_graph_rows``Any`Original `DataPointAggData` rows (may be `None` for hardcoded lines)`line_info``LineInfo`Styling configuration`xs``tuple[float, ...]`X-axis values (typically percent adoption)`ys``tuple[float, ...]`Y-axis values (typically percent outcome)`yerrs``tuple[float, ...]`Error bar values (90% confidence intervals)
Sources: [bgpy/simulation_framework/graphing/line_data.py1-17](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/line_data.py#L1-L17)

### LinePropertiesGenerator Class

`LinePropertiesGenerator` provides cycling iterators for markers, line styles, and colors to ensure visual distinction between lines:

- **Markers**: `[".", "1", "*", "x", "d", "2", "3", "4", "v", "+", "s"]`
- **Line Styles**: `["-", "--", "-.", ":", "solid", "dotted", "dashdot", "dashed"]`
- **Colors**: `["b", "g", "r", "c", "m", "y", "darkorange", "darkgoldenrod", ...]`

The `_expand()` method duplicates and reverses these lists to create extended cycling patterns, preventing early repeats.

Sources: [bgpy/simulation_framework/graphing/line_properties_generator.py1-70](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/line_properties_generator.py#L1-L70)

---

## Graph Generation Pipeline

The graph generation process flows through three stages: preprocessing, data graphing, and legend/save operations.

**Graph Generation Pipeline**

```
_generate_graph()
Entry Point

_preprocessing_steps()
Create fig, ax
Build line_data_dict

_get_graph_name()
as_group/in_adopting_asns/plane/outcome.png

_customize_graph()
Set DPI, font size
Set axis limits & labels

_get_line_data_dict()
Convert DataPointAggData to LineData

_get_line_data()
Sort by percent_adopt
Extract xs, ys, yerrs

_get_line_info()
Lookup or generate LineInfo

_add_hardcoded_lines_to_line_data_dict()
Add lines with hardcoded_xs

_graph_data()
Plot all lines

_plot_non_aggregated_lines()
Plot lines not in labels_to_aggregate

_plot_strongest_attacker_lines()
Compute max across attacks
Plot aggregated line + scatter

_get_agg_data()
Build strongest_agg_dict
Build scatter_line_data_dict

_get_agg_line_data()
Convert to LineData objects

_plot_scatter_plots()
Plot grey markers

_add_legends_and_save()
Add main & strongest attacker legends

_add_legend()
Sort by mean y-value
Create first legend

_add_strongest_attacker_legend()
Create second legend below first

_save_and_close_graph()
Write PNG, close figure, gc.collect()
```

Sources: [bgpy/simulation_framework/graphing/graph_factory/generate_graph_funcs.py13-39](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/graph_factory/generate_graph_funcs.py#L13-L39)[bgpy/simulation_framework/graphing/graph_factory/preprocessing_funcs.py23-208](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/graph_factory/preprocessing_funcs.py#L23-L208)[bgpy/simulation_framework/graphing/graph_factory/add_legends_and_save_funcs.py8-173](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/graph_factory/add_legends_and_save_funcs.py#L8-L173)

### Preprocessing Stage

The `_preprocessing_steps()` function performs initial setup:

1. **Graph Name Generation**: Constructs the output path using `_get_graph_name()`:

```
{as_group}/in_adopting_asns_is_{in_adopting_asns}/{plane}/{outcome}.png

```
2. **Graph Customization**: Calls `_customize_graph()` to set DPI (300), font size (14), axis limits, and axis labels.
3. **Line Data Dictionary Construction**: Builds a `dict[str, LineData]` by:

- Grouping `DataPointAggData` rows by scenario label
- For each label, calling `_get_line_data()` to extract xs, ys, yerrs
- Looking up or generating `LineInfo` via `_get_line_info()`
- Adding hardcoded lines (those with `hardcoded_xs`) via `_add_hardcoded_lines_to_line_data_dict()`

Sources: [bgpy/simulation_framework/graphing/graph_factory/preprocessing_funcs.py23-104](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/graph_factory/preprocessing_funcs.py#L23-L104)

### Data Graphing Stage

The `_graph_data()` function plots all lines:

1. **Non-Aggregated Lines**: `_plot_non_aggregated_lines()` plots any line whose label is not in `labels_to_aggregate` using `ax.errorbar()`.
2. **Strongest Attacker Lines**: `_plot_strongest_attacker_lines()` performs special aggregation (see next section).

Sources: [bgpy/simulation_framework/graphing/graph_factory/generate_graph_funcs.py42-87](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/graph_factory/generate_graph_funcs.py#L42-L87)

### Legend and Save Stage

The `_add_legends_and_save()` function finalizes the graph:

1. **Main Legend**: `_add_legend()` creates the primary legend, sorting lines by mean y-value (descending) for visual consistency.
2. **Strongest Attacker Legend**: `_add_strongest_attacker_legend()` adds a second legend titled "Strongest Attacker" below the first, showing which attack types are represented by the grey markers.
3. **Save**: `_save_and_close_graph()` writes the PNG, closes matplotlib figures, and explicitly calls `gc.collect()` to prevent memory leaks when running many simulations sequentially.

Sources: [bgpy/simulation_framework/graphing/graph_factory/add_legends_and_save_funcs.py8-173](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/graph_factory/add_legends_and_save_funcs.py#L8-L173)

---

## Strongest Attacker Aggregation

The strongest attacker feature allows multiple attack scenarios to be aggregated into a single "envelope" line showing the maximum attack success at each adoption level.

### Concept

When evaluating a defense policy (e.g., ASPA), you may want to show the worst-case attack success across multiple attack types (e.g., `ForgedOriginPrefixHijack`, `ShortestPathPrefixHijack`). Instead of cluttering the graph with many lines, the strongest attacker line shows the maximum y-value at each x-value, with grey markers indicating which specific attack was strongest at that point.

### Configuration

The `strongest_attacker_dict` parameter maps aggregated line labels to tuples of `LineInfo` objects for constituent attacks:

```
strongest_attacker_dict = frozendict({
    "ASPA Strongest Attacker": (
        LineInfo("ForgedOriginPrefixHijack", marker="o", ...),
        LineInfo("ShortestPathPrefixHijack", marker="s", ...),
    )
})
```

Sources: [bgpy/simulation_framework/graphing/graph_factory/graph_factory.py97-105](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/graph_factory/graph_factory.py#L97-L105)

### Algorithm

**Strongest Attacker Computation Flow**

```
_plot_strongest_attacker_lines()

Pop labels_to_aggregate from line_data_dict
Store in max_attacker_data_dict

_get_agg_data()

Initialize:
strongest_agg_dict: label → {agg_xs, agg_ys, agg_yerrs}
scatter_plots: label → {xs, ys, yerrs}

For each x in agg_xs:

Find line_info with max y-value
Store max_val, best_label, new_yerr

Append max_val to agg_ys

Append (x, max_val, new_yerr)
to scatter_plots[best_label]

_get_scatter_line_data_dict()
Convert scatter_plots to LineData
with lw=0, mfc=color, mec=color

_get_agg_line_data()
Convert strongest_agg_dict to LineData
with ms=0, elinewidth=0

Plot aggregated lines
_plot_line_data()

Plot scatter plots
_plot_scatter_plots()

Return non_aggregated_line_data_dict
and max_attacker_data_dict
```

The `_get_agg_data()` function performs the core computation:

1. **Initialization**: Creates `strongest_agg_dict` (for the aggregated line) and `scatter_plots` (for the grey markers).
2. **Per-X-Value Loop**: For each x-value (adoption percentage):

- Compares y-values across all constituent attacks
- Identifies the attack with maximum y-value
- Appends max y-value to the aggregated line
- Appends (x, y, yerr) to the scatter plot for the winning attack
3. **Scatter Plot Conversion**: `_get_scatter_line_data_dict()` converts scatter data to `LineData` objects with:

- `lw=0` (invisible line)
- `mfc` and `mec` set to original line color
- `color="grey"` (for error bars)
- Original marker from `LineInfo`
4. **Aggregated Line Conversion**: `_get_agg_line_data()` converts aggregated data to `LineData` objects with:

- `ms=0` (invisible markers)
- `elinewidth=0` (invisible error bars)
- Same line style and color as first constituent attack

Sources: [bgpy/simulation_framework/graphing/graph_factory/generate_graph_funcs.py62-219](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/graph_factory/generate_graph_funcs.py#L62-L219)

### Visual Result

The resulting graph contains:

- A solid line showing the envelope of maximum attack success
- Grey markers at each x-value indicating which specific attack was strongest
- A second legend titled "Strongest Attacker" mapping markers to attack types

---

## Customization Options

### Label Replacement

The `label_replacement_dict` allows post-hoc renaming of scenario labels without re-running simulations:

```
label_replacement_dict = frozendict({
    "PrefixHijack_ROV": "ROV Defense"
})
```

This is deprecated in favor of configuring `LineInfo` objects directly via `line_info_dict`.

Sources: [bgpy/simulation_framework/graphing/graph_factory/preprocessing_funcs.py201-203](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/graph_factory/preprocessing_funcs.py#L201-L203)

### Axis Customization

The `x_axis_label_replacement_dict` and `y_axis_label_replacement_dict` override default axis labels:

- Default x-label: `"Percent Adoption"`
- Default y-label: `"PERCENT {outcome}"` (e.g., `"PERCENT ATTACKER SUCCESS"`)

Sources: [bgpy/simulation_framework/graphing/graph_factory/preprocessing_funcs.py53-68](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/graph_factory/preprocessing_funcs.py#L53-L68)

### Hardcoded Lines

`LineInfo` objects with `hardcoded_xs`, `hardcoded_ys`, and `hardcoded_yerrs` allow adding theoretical or baseline lines that don't come from simulation data. These are automatically added via `_add_hardcoded_lines_to_line_data_dict()`.

Sources: [bgpy/simulation_framework/graphing/graph_factory/preprocessing_funcs.py88-103](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/graph_factory/preprocessing_funcs.py#L88-L103)

### Adoption-Independent Lines

Setting `unrelated_to_adoption=True` in `LineInfo` causes `_get_ys()` and `_get_yerrs()` to average values across all adoption percentages, producing a horizontal line. This is useful for showing baseline attack success in the absence of any defense.

Sources: [bgpy/simulation_framework/graphing/graph_factory/preprocessing_funcs.py157-184](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/graph_factory/preprocessing_funcs.py#L157-L184)

---

## Output Format

### Directory Structure

Graphs are organized by `GraphCategory` components:

```
{graph_dir}/
  {as_group}/
    in_adopting_asns_is_{in_adopting_asns}/
      {plane}/
        {outcome}.png

```

Example: `ALL_WOUT_IXPS/in_adopting_asns_is_TRUE/DATA/ATTACKER_SUCCESS.png`

Sources: [bgpy/simulation_framework/graphing/graph_factory/preprocessing_funcs.py44-50](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/graph_factory/preprocessing_funcs.py#L44-L50)

### Graph Specifications

All PNG graphs are generated with:

- **DPI**: 300 (publication quality)
- **Font Size**: 14
- **Marker Size**: 10
- **Error Bars**: 90% confidence intervals (computed by `GraphDataAggregator._get_yerr()`)
- **Axis Limits**: 0-100 for both x and y (configurable via `x_limit` and `y_limit`)

Sources: [bgpy/simulation_framework/graphing/graph_factory/preprocessing_funcs.py53-68](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/graph_factory/preprocessing_funcs.py#L53-L68)

### Memory Management

The `_save_and_close_graph()` function includes extensive cleanup to prevent memory leaks:

```
ax.cla()
plt.cla()
plt.clf()
plt.close(fig)
gc.collect()
```

This is critical when generating hundreds of graphs across multiple simulations, as matplotlib can leak memory even after closing figures.

Sources: [bgpy/simulation_framework/graphing/graph_factory/add_legends_and_save_funcs.py147-173](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/graph_factory/add_legends_and_save_funcs.py#L147-L173)

---

## Usage Example

```
from pathlib import Path
from frozendict import frozendict
from bgpy.simulation_framework import GraphFactory, LineInfo

# Generate graphs from pickled data
factory = GraphFactory(
    pickle_path=Path("output/data.pickle"),
    graph_dir=Path("output/graphs"),
    line_info_dict=frozendict({
        "ROV": LineInfo("ROV", marker="o", color="b"),
        "ASPA": LineInfo("ASPA", marker="s", color="r"),
    }),
    strongest_attacker_dict=frozendict({
        "ASPA Strongest": (
            LineInfo("ForgedOrigin", marker="^"),
            LineInfo("ShortestPath", marker="v"),
        ),
    }),
    x_limit=100,
    y_limit=100,
)

factory.generate_graphs()
```

Sources: [bgpy/simulation_framework/graphing/graph_factory/graph_factory.py53-172](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graphing/graph_factory/graph_factory.py#L53-L172)