# Data Aggregation
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

## Purpose and Scope

This document describes the data aggregation subsystem in BGPy, which collects simulation results across multiple trials and computes statistical summaries for analysis and visualization. The `GraphDataAggregator` class and its associated data structures (`TrialData`, `GraphCategory`, `DataPointKey`, `DataPointAggData`) coordinate the collection, aggregation, and export of metrics from BGP simulations.

For information about how aggregated data is visualized, see [Graph Generation](/blcrdbob3/bgpy_pkg/8.3-graph-generation). For details on outcome analysis that produces the raw results being aggregated, see [Outcome Analysis](/blcrdbob3/bgpy_pkg/8.1-outcome-analysis).

## System Architecture

The data aggregation pipeline consists of four phases: trial-level collection, cross-trial aggregation, statistical computation, and data export.

```
Phase 4: Data Export

Phase 3: Statistical Aggregation

Phase 2: Per-Trial Aggregation

Phase 1: Trial-Level Collection

SimulationEngine
as_graph with outcomes

outcomes dict
{Plane: {asn: Outcome}}

TrialData
(GraphCategory 1)

TrialData
(GraphCategory 2)

TrialData
(GraphCategory N)

DataPointKey
propagation_round
percent_adopt
scenario_config

list[float]
percent per trial

mean(percent_list)

yerr = 1.645 * 2 * stdev / sqrt(n)

DataPointAggData
value, yerr

CSV File
Human-readable rows

Pickle File
PICKLE_DATA_TYPE
```

**Sources:**[bgpy/simulation_framework/graph_data_aggregator/graph_data_aggregator.py1-268](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graph_data_aggregator/graph_data_aggregator.py#L1-L268)

## Key Data Structures

### GraphCategory

The `GraphCategory` dataclass defines the type of graph/metric being tracked. It specifies four filtering dimensions that determine which ASes are counted and what constitutes success.

```
GraphCategory

+Plane plane

+ASGroups as_group

+Outcomes outcome

+InAdoptingASNs in_adopting_asns

Plane

DATA

CTRL

ASGroups

ALL_WOUT_IXPS

STUBS_OR_MH

STUBS

...

Outcomes

ATTACKER_SUCCESS

VICTIM_SUCCESS

DISCONNECTED

InAdoptingASNs

TRUE

FALSE

ANY
```
FieldTypePurpose`plane``Plane`Whether to track data plane (traceback) or control plane (announcements)`as_group``ASGroups`Which category of ASes to include (e.g., stubs, multihomed, all)`outcome``Outcomes`Which outcome to count (attacker success, victim success, disconnected)`in_adopting_asns``InAdoptingASNs`Whether to filter by adopting (TRUE), non-adopting (FALSE), or all (ANY)
Example: A `GraphCategory` with `plane=DATA`, `as_group=ALL_WOUT_IXPS`, `outcome=ATTACKER_SUCCESS`, `in_adopting_asns=TRUE` would track the percentage of adopting ASes (excluding IXPs) whose data plane traffic reaches the attacker.

**Sources:**[bgpy/simulation_framework/graph_data_aggregator/graph_category.py1-14](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graph_data_aggregator/graph_category.py#L1-L14)

### DataPointKey

The `DataPointKey` identifies a single point on a graph. It combines propagation round, adoption percentage, and scenario configuration to uniquely identify a data point.

```
DataPointKey

+int propagation_round

+float|SpecialPercentAdoptions percent_adopt

+ScenarioConfig scenario_config

ScenarioConfig

+Type[Scenario] ScenarioCls

+Type[Policy] AdoptPolicyCls

+Type[Policy] BasePolicyCls

+str scenario_label

+int propagation_rounds
```

The `DataPointKey` is used as a dictionary key in the aggregator's internal data structure to group all trials that share the same configuration. For example, all trials of "ROV vs. Prefix Hijack at 50% adoption, round 0" would map to the same `DataPointKey`.

**Sources:**[bgpy/simulation_framework/graph_data_aggregator/graph_data_aggregator.py16-17](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graph_data_aggregator/graph_data_aggregator.py#L16-L17)

### TrialData

The `TrialData` class tracks metrics for a single trial and single graph category. It maintains a numerator (count of ASes matching the outcome) and denominator (count of ASes in the category).

```
Yes

Yes

No

No

TrialData
_numerator = 0
_denominator = 0

add_data(as_obj, engine, scenario, outcomes)

AS in as_group?
AS matches in_adopting_asns?

_denominator += 1

outcome matches
graph_category.outcome?

_numerator += 1

get_percent()
returns _numerator * 100 / _denominator
```

The key methods are:

- **`add_data()`**: Evaluates whether an AS should be counted, updates numerator/denominator [bgpy/simulation_framework/graph_data_aggregator/trial_data.py23-47](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graph_data_aggregator/trial_data.py#L23-L47)
- **`_add_denominator()`**: Checks if AS is in the target group and adoption status [bgpy/simulation_framework/graph_data_aggregator/trial_data.py49-75](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graph_data_aggregator/trial_data.py#L49-L75)
- **`_add_numerator()`**: If denominator was incremented, checks if outcome matches [bgpy/simulation_framework/graph_data_aggregator/trial_data.py77-101](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graph_data_aggregator/trial_data.py#L77-L101)
- **`get_percent()`**: Returns percentage or None if no ASes were tracked [bgpy/simulation_framework/graph_data_aggregator/trial_data.py17-21](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graph_data_aggregator/trial_data.py#L17-L21)

**Sources:**[bgpy/simulation_framework/graph_data_aggregator/trial_data.py1-102](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graph_data_aggregator/trial_data.py#L1-L102)

### DataPointAggData

The `DataPointAggData` class stores aggregated statistics for a single data point after combining all trials. It contains the mean value, error bars (yerr), and the associated `DataPointKey`.
FieldTypeDescription`value``float`Mean across all trial percentages`yerr``float`90% confidence interval half-width`data_point_key``DataPointKey`Associated configuration identifying this point
**Sources:**[bgpy/simulation_framework/graph_data_aggregator/graph_data_aggregator.py15-21](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graph_data_aggregator/graph_data_aggregator.py#L15-L21)

## Aggregation Process

### Per-Trial Data Collection

The `aggregate_and_store_trial_data()` method is called after each trial completes. It iterates through all ASes in the simulation and updates `TrialData` objects for each `GraphCategory`.

```
AS objects
TrialData instances
GraphDataAggregator
Simulation
AS objects
TrialData instances
GraphDataAggregator
Simulation
Create TrialData for each GraphCategory
Skip this AS
loop
[For each TrialData]
alt
[AS in untracked_asns]
[AS is trackable]
loop
[For each AS in engine.as_graph]
Create DataPointKey from round, percent_adopt, scenario_config
alt
[percent is not None]
loop
[For each TrialData]
aggregate_and_store_trial_data(engine, percent_adopt, trial, scenario, round, outcomes)
trial_datas = [TrialData(gc) for gc in graph_categories]
Get AS object
add_data(as_obj, engine, scenario, ctrl_outcome, data_outcome)
_add_denominator() checks filters
_add_numerator() if outcome matches
percent = get_percent()
data[graph_category][data_point_key].append(percent)
```

The internal data structure is:

```
DATA_TYPE = dict[GraphCategory, defaultdict[DataPointKey, list[float]]]
```

Each `GraphCategory` maps to a dictionary of `DataPointKey` to a list of percentages (one per trial).

**Sources:**[bgpy/simulation_framework/graph_data_aggregator/graph_data_aggregator.py75-156](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graph_data_aggregator/graph_data_aggregator.py#L75-L156)

### Cross-Trial Statistical Aggregation

After all trials complete, the `get_pickle_data()` and `get_csv_rows()` methods compute aggregated statistics across trials.

```
Output: PICKLE_DATA_TYPE

Statistical Computation

Input: DATA_TYPE

GraphCategory 1

GraphCategory 2

DataPointKey 1

DataPointKey 2

[0.45, 0.52, 0.48, ...]
list of trial percentages

[0.78, 0.81, 0.76, ...]
list of trial percentages

mean(percent_list)

stdev(percent_list)

len(percent_list)

yerr = 1.645 * 2 * stdev / sqrt(n)

DataPointAggData
value=0.483
yerr=0.021

DataPointAggData
value=0.783
yerr=0.015
```

#### Error Bar Calculation

The `_get_yerr()` method computes the 90% confidence interval half-width using the formula:

```
yerr = (1.645 * 2 * stdev) / sqrt(n)

```

Where:

- `1.645` is the z-score for 90% confidence
- `stdev` is the standard deviation across trial percentages
- `n` is the number of trials
- The factor of `2` doubles the confidence interval half-width

If only one trial exists (`len(percent_list) == 1`), `yerr` is set to `0`.

**Sources:**[bgpy/simulation_framework/graph_data_aggregator/graph_data_aggregator.py259-267](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graph_data_aggregator/graph_data_aggregator.py#L259-L267)

### Multi-Process Aggregation

When simulations run in parallel across multiple CPU cores, each process maintains its own `GraphDataAggregator`. The `__add__()` and `__radd__()` methods enable merging aggregators from different processes.

```
Main Process

Process 3

Process 2

Process 1

GraphDataAggregator
trials 0, 3, 6, ...

GraphDataAggregator
trials 1, 4, 7, ...

GraphDataAggregator
trials 2, 5, 8, ...

sum([GDA1, GDA2, GDA3])
calls add() repeatedly

Combined GraphDataAggregator
all trials merged
```

The `__add__()` method creates a new `GraphDataAggregator` with combined data:

```
new_data: DATA_TYPE = {x: defaultdict(list) for x in self.graph_categories}
for obj in (self, other):
    for graph_category, data_dict in obj.data.items():
        for data_point_key, percents in data_dict.items():
            new_data[graph_category][data_point_key].extend(percents)
```

**Sources:**[bgpy/simulation_framework/graph_data_aggregator/graph_data_aggregator.py48-69](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graph_data_aggregator/graph_data_aggregator.py#L48-L69)

## Data Export Formats

### CSV Output

The `get_csv_rows()` method produces human-readable rows with the following columns:
ColumnDescriptionExample`scenario_cls`Scenario class name`"PrefixHijack"``AdoptingPolicyCls`Adopting policy class`"ROV"``BasePolicyCls`Base policy class`"BGP"``in_adopting_asns`Adoption filter`"TRUE"`, `"FALSE"`, `"ANY"``outcome_type`Plane type`"DATA"`, `"CTRL"``as_group`AS group`"All (Wout IXPs)"``outcome`Outcome type`"ATTACKER_SUCCESS"``percent_adopt`Adoption percentage`0.5` or `"ONLY_ONE"``propagation_round`Round number`0``value`Mean percentage`45.3``yerr`Error bar`2.1``scenario_config_label`CSV label`"ROV Subprefix Hijack"``scenario_label`Scenario label`"ROV"`
**Sources:**[bgpy/simulation_framework/graph_data_aggregator/graph_data_aggregator.py177-217](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graph_data_aggregator/graph_data_aggregator.py#L177-L217)

### Pickle Output

The `get_pickle_data()` method produces a dictionary structure optimized for programmatic access:

```
PICKLE_DATA_TYPE = dict[GraphCategory, dict[DataPointKey, DataPointAggData]]
```

This nested structure enables efficient lookup by graph category and data point configuration. The `GraphFactory` loads this pickle file to generate visualizations.

**Sources:**[bgpy/simulation_framework/graph_data_aggregator/graph_data_aggregator.py219-231](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graph_data_aggregator/graph_data_aggregator.py#L219-L231)

### Data Storage Validation

The `_data_is_storable()` method validates that data exists before writing:

```
Yes

No

percent_list empty?

warn: No data tracked
for this DataPointKey

Return True
Data is storable

Return False
Skip this data point
```

This validation prevents writing invalid entries when no ASes fall into a particular category. For example, if a simulation has only one adopting AS and it's multihomed (not a stub), then the "stubs" graph category would have no data to track.

**Sources:**[bgpy/simulation_framework/graph_data_aggregator/graph_data_aggregator.py233-257](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graph_data_aggregator/graph_data_aggregator.py#L233-L257)

## Integration with Simulation Pipeline

The aggregator integrates with the broader simulation pipeline at two key points:

1. **During execution**: After each trial, `Simulation.run()` calls `aggregate_and_store_trial_data()` to collect results
2. **After completion**: `Simulation.run()` calls `write_data()` to export CSV and pickle files

```
GraphDataAggregator
ASGraphAnalyzer
SimulationEngine
Simulation
GraphDataAggregator
ASGraphAnalyzer
SimulationEngine
Simulation
For each trial
After all trials
run()
Propagate announcements
analyze()
Compute outcomes
outcomes dict
aggregate_and_store_trial_data(...)
Create TrialData objects
Iterate all ASes
Store percents in data dict
write_data(csv_path, pickle_path)
get_csv_rows()
get_pickle_data()
Write files
```

**Sources:**[bgpy/simulation_framework/graph_data_aggregator/graph_data_aggregator.py161-175](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/graph_data_aggregator/graph_data_aggregator.py#L161-L175)