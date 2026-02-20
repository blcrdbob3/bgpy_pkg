# Multi-Processing and Performance
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

This document covers the parallel execution infrastructure and performance optimization mechanisms in BGPy's simulation framework. It explains how simulations are distributed across CPU cores, how progress is tracked during multi-process execution, and how memory constraints are managed. For information about the overall simulation execution pipeline, see [4.1](/blcrdbob3/bgpy_pkg/4.1-simulation-class-and-execution-pipeline). For configuration options that affect performance, see [4.2](/blcrdbob3/bgpy_pkg/4.2-scenario-configuration).

## Overview of Multi-Processing Architecture

BGPy supports both single-process and multi-process execution modes. The `Simulation` class in [bgpy/simulation_framework/simulation.py](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py) automatically selects the execution mode based on the `parse_cpus` parameter.

```
Multi-Process Path

Single Process Path

Execution Mode Selection

Simulation Initialization

Yes

No

Simulation.init()
parse_cpus parameter

_validate_ram()
Check memory constraints

ASGraphConstructorCls.run()
Cache CAIDA data

_get_data()

parse_cpus == 1?

_get_single_process_results()

_get_mp_results()

_run_chunk()
with tqdm progress bar

SimulationEngine
single instance

multiprocessing.Pool
parse_cpus workers

Pool.apply_async()
_run_chunk per chunk

_tqdm_tracking_dir/*.txt
file-based progress

tqdm in main process
aggregates file counts
```

**Sources:**[bgpy/simulation_framework/simulation.py52-160](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L52-L160)[bgpy/simulation_framework/simulation.py250-303](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L250-L303)

## Execution Modes

### Single-Process Mode

When `parse_cpus == 1`, simulations run sequentially in the main process with a tqdm progress bar displayed directly:
CharacteristicImplementation**Trigger Condition**`parse_cpus == 1`**Method**`_get_single_process_results()`**Progress Display**Direct tqdm in `_get_run_chunk_iter()`**AS Graph Loading**Once in main process**Simplicity**Easier debugging, single call stack
The single-process path calls `_run_chunk()` once with all trials, wrapping the trial loop in a tqdm progress bar at [bgpy/simulation_framework/simulation.py483-487](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L483-L487)

### Multi-Process Mode

When `parse_cpus > 1`, trials are distributed across worker processes using Python's `multiprocessing.Pool`:
CharacteristicImplementation**Trigger Condition**`parse_cpus > 1`**Method**`_get_mp_results()`**Worker Pool**`multiprocessing.Pool(parse_cpus)`**Task Distribution**`Pool.apply_async()`**Progress Tracking**File-based via `_tqdm_tracking_dir`**AS Graph Loading**Reconstructed per worker
**Sources:**[bgpy/simulation_framework/simulation.py286-303](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L286-L303)[bgpy/simulation_framework/simulation.py327-348](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L327-L348)

## Trial Chunking Strategy

Trials are distributed across CPU cores using a round-robin chunking strategy implemented in `_get_chunks()`:

```
Worker Assignment

Trial Distribution

trials = [0, 1, 2, ..., num_trials-1]

_get_chunks(parse_cpus)

Chunk 0: [0, 3, 6, ...]
trials[0::cpus]

Chunk 1: [1, 4, 7, ...]
trials[1::cpus]

Chunk 2: [2, 5, 8, ...]
trials[2::cpus]

Worker Process 0
_run_chunk(0, chunk0)

Worker Process 1
_run_chunk(1, chunk1)

Worker Process 2
_run_chunk(2, chunk2)
```

The chunking logic at [bgpy/simulation_framework/simulation.py309-320](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L309-L320) uses Python list slicing:

```
trials_list = list(range(self.num_trials))
return [trials_list[i::cpus] for i in range(cpus)]
```

This approach ensures even distribution while minimizing the startup cost of creating new processes. Each worker runs multiple trials sequentially, which is more efficient than creating one process per trial.

**Rationale:** The comment at [bgpy/simulation_framework/simulation.py314-316](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L314-L316) explains: "We also don't multiprocess one by one because the start up cost of each process is huge (since each process must generate it's own engine) so we must divy up the work beforehand."

**Sources:**[bgpy/simulation_framework/simulation.py309-320](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L309-L320)

## Progress Tracking System

Multi-process execution requires a file-based progress tracking mechanism because each worker runs in a separate process with its own memory space.

```
"tqdm Progress Bar"
"Worker 1
_run_chunk()"
"Worker 0
_run_chunk()"
"_tqdm_tracking_dir
TemporaryDirectory"
"Main Process
_get_mp_results()"
"tqdm Progress Bar"
"Worker 1
_run_chunk()"
"Worker 0
_run_chunk()"
"_tqdm_tracking_dir
TemporaryDirectory"
"Main Process
_get_mp_results()"
loop
[Every trial completion]
loop
[Every 0.5 seconds]
Create temp directory
apply_async(_run_chunk, (0, chunk0))
apply_async(_run_chunk, (1, chunk1))
Write to 0.txt
total completed count
Write to 1.txt
total completed count
Read all *.txt files
Update with sum of counts
Return GraphDataAggregator
Return GraphDataAggregator
Cleanup directory
```

### Temporary Directory Creation

At initialization, `Simulation` creates a temporary directory for progress tracking at [bgpy/simulation_framework/simulation.py156-159](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L156-L159):

```
with TemporaryDirectory() as tmp_dir:
    tmp_dir_str = tmp_dir
self._tqdm_tracking_dir: Path = Path(tmp_dir_str)
self._tqdm_tracking_dir.mkdir(parents=True)
```

### Worker Progress Updates

Each worker writes its progress to a file named `{chunk_id}.txt` containing the total number of completed trial-percent_adoption pairs. The `_write_tqdm_progress()` method at [bgpy/simulation_framework/simulation.py491-497](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L491-L497):

```
def _write_tqdm_progress(self, chunk_id: int, completed: int) -> None:
    if self.parse_cpus > 1:
        with (self._tqdm_tracking_dir / f"{chunk_id}.txt").open("w") as f:
            f.write(str(completed))
```

Workers update this file after completing each percent_adoption within a trial at [bgpy/simulation_framework/simulation.py432-435](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L432-L435)

### Main Process Aggregation

The main process periodically reads all tracking files and updates the tqdm progress bar. The `_update_tqdm_progress_bar()` method at [bgpy/simulation_framework/simulation.py360-371](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L360-L371):

```
def _update_tqdm_progress_bar(self, pbar: tqdm) -> None:
    total_completed = 0
    for file_path in self._tqdm_tracking_dir.iterdir():
        try:
            total_completed += int(file_path.read_text())
        except ValueError:
            pass  # File being written
    pbar.n = total_completed
    pbar.refresh()
```

This aggregation happens every 0.5 seconds in the polling loop at [bgpy/simulation_framework/simulation.py344-347](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L344-L347)

**Sources:**[bgpy/simulation_framework/simulation.py156-159](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L156-L159)[bgpy/simulation_framework/simulation.py360-371](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L360-L371)[bgpy/simulation_framework/simulation.py491-497](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L491-L497)

## AS Graph Serialization and Reconstruction

A critical performance consideration is how the AS graph is shared across worker processes. BGPy uses a TSV-based reconstruction approach rather than pickle serialization.

### The Weakref Problem

The `ASGraph` and `SimulationEngine` contain weakrefs (weak references) which cannot be pickled reliably. As noted in the comment at [bgpy/simulation_framework/simulation.py463-465](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L463-L465): "engine isn't picklable or dillable, as it has weakrefs, which will deserialize to dead refs."

### Two-Phase Loading Strategy

```
Worker Process: Reconstruction

Main Process: Initialization

File system

run() before multiprocessing
ASGraphConstructorCls.run()

CAIDA data cached to TSV
SINGLE_DAY_CACHE_DIR

_get_engine_for_run_chunk()

ASGraphConstructorCls(**kwargs).run()
tsv_path=None

Load from cached TSV
Not from pickle

SimulationEngine(as_graph)
Fresh instance per worker
```

#### Main Process: Pre-Caching

Before starting worker processes, the main process caches the CAIDA AS graph at [bgpy/simulation_framework/simulation.py258](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L258-L258):

```
self.ASGraphConstructorCls(**self.as_graph_constructor_kwargs).run()
```

This ensures the CAIDA data is downloaded and stored in `SINGLE_DAY_CACHE_DIR` before workers start, preventing multiple simultaneous downloads.

#### Worker Process: Reconstruction

Each worker reconstructs the AS graph from the cached data in `_get_engine_for_run_chunk()` at [bgpy/simulation_framework/simulation.py461-474](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L461-L474):

```
def _get_engine_for_run_chunk(self) -> BaseSimulationEngine:
    constructor_kwargs = dict(self.as_graph_constructor_kwargs)
    constructor_kwargs["tsv_path"] = None
    as_graph: ASGraph = self.ASGraphConstructorCls(**constructor_kwargs).run()
    engine = self.SimulationEngineCls(
        as_graph,
        cached_as_graph_tsv_path=self.as_graph_constructor_kwargs.get("tsv_path"),
    )
    return engine
```

Key implementation details:

- `tsv_path` is set to `None` to force loading from the default cache directory
- Each worker gets a fresh `ASGraph` and `SimulationEngine` instance
- No pickling or unpickling of complex objects with weakrefs

**Sources:**[bgpy/simulation_framework/simulation.py258](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L258-L258)[bgpy/simulation_framework/simulation.py461-474](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L461-L474)

## RAM Management and Validation

BGPy validates available RAM before starting simulations to prevent out-of-memory errors during execution.

### Memory Consumption Model

The `_validate_ram()` method at [bgpy/simulation_framework/simulation.py215-248](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L215-L248) estimates memory usage based on AS graph configuration:
ConfigurationRAM per Core (PyPy)No cone storage0.9 GBCustomer cone size only1.6 GBBoth customer & provider cones2.3 GB
The memory model at [bgpy/simulation_framework/simulation.py221-234](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L221-L234):

```
store_customer_cone_asns = graph_kwargs.get("store_customer_cone_asns", False)
store_provider_cone_asns = graph_kwargs.get("store_provider_cone_asns", False)

if store_customer_cone_asns and store_provider_cone_asns:
    total_gb_ram_per_core = 2.3
elif store_customer_cone_asns or store_provider_cone_asns:
    total_gb_ram_per_core = 1.6
else:
    total_gb_ram_per_core = 0.9
```

### Validation Logic

```
Yes

No

Simulation.init()

_validate_ram()

Get as_graph_kwargs
cone storage settings

expected_ram =
parse_cpus * ram_per_core

available_ram =
psutil.virtual_memory().available

expected * 1.1
> available?

warn() with details

Continue initialization
```

The validation uses `psutil.virtual_memory().available` to check available RAM at [bgpy/simulation_framework/simulation.py238](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L238-L238) and warns if expected usage exceeds 110% of available memory at [bgpy/simulation_framework/simulation.py242-248](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L242-L248)

**Important Note:** These RAM estimates are specific to PyPy 3.10 as documented in the comments at [bgpy/simulation_framework/simulation.py218-219](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L218-L219) CPython may have different memory characteristics.

**Sources:**[bgpy/simulation_framework/simulation.py215-248](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L215-L248)

## Performance Optimization Guidelines

### Recommended Python Implementation

The README at [README.md](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/README.md) and project metadata indicate PyPy is the recommended Python implementation for performance. PyPy's JIT compiler provides significant speedups for BGPy's computation-intensive propagation algorithms.

### CPU Core Configuration

The `parse_cpus` parameter controls parallelization:

```
parse_cpus: int = max(cpu_count() - 1, 1)  # Default
```

Best practices:

- **Default behavior:** Uses all cores minus one at [bgpy/simulation_framework/simulation.py76](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L76-L76)
- **Automatic limiting:**`parse_cpus` is capped at `num_trials` since there's no benefit to more workers than trials at [bgpy/simulation_framework/simulation.py123](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L123-L123)
- **RAM constraints:** Reduce `parse_cpus` if RAM validation warnings appear

### AS Graph Storage Options

Control memory usage by configuring AS graph storage in `as_graph_kwargs`:

```
as_graph_kwargs = frozendict({
    "store_customer_cone_size": True,   # Minimal overhead
    "store_customer_cone_asns": False,  # +0.7 GB/core
    "store_provider_cone_size": False,  # Rarely needed
    "store_provider_cone_asns": False,  # +0.7 GB/core
})
```

Default configuration at [bgpy/simulation_framework/simulation.py88-96](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L88-L96) balances functionality and memory usage.

### Trial Configuration

- **Larger `num_trials`:** Better statistical significance and better multi-core utilization
- **Smaller `num_trials`:** Faster iteration during development, but may underutilize cores
- **Rule of thumb:** Use `num_trials >= parse_cpus` for efficient parallelization

### Startup Cost Amortization

The chunking strategy amortizes the high per-process startup cost (AS graph loading, engine initialization) across multiple trials. This is why `_get_chunks()` creates round-robin chunks rather than spawning one process per trial.

**Sources:**[bgpy/simulation_framework/simulation.py76](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L76-L76)[bgpy/simulation_framework/simulation.py123](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L123-L123)[bgpy/simulation_framework/simulation.py88-96](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L88-L96)[bgpy/simulation_framework/simulation.py314-316](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L314-L316)

## Deterministic Randomness

BGPy supports deterministic simulations through the `python_hash_seed` parameter, which enables reproducible multi-process execution.

### Seed Management

```
No

Yes

python_hash_seed parameter

Check PYTHONHASHSEED
environment variable

env matches
parameter?

raise RuntimeError

random.seed(python_hash_seed)

Spawn worker processes

_seed_random(chunk_id)
in each worker

random.seed(seed + chunk_id)
```

The seeding logic at [bgpy/simulation_framework/simulation.py269-281](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L269-L281):

1. **Environment validation:** Checks that `PYTHONHASHSEED` environment variable matches `python_hash_seed` parameter
2. **Main process seeding:** Seeds random number generator in main process
3. **Worker differentiation:** Each worker calls `_seed_random(seed_suffix=str(chunk_id))` at [bgpy/simulation_framework/simulation.py381](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L381-L381) to ensure different random sequences per worker while maintaining determinism

This approach ensures:

- Reproducible results across runs with the same seed
- Different random selections per worker (avoiding identical trials)
- Full determinism when `PYTHONHASHSEED` environment variable is set

**Sources:**[bgpy/simulation_framework/simulation.py269-281](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L269-L281)[bgpy/simulation_framework/simulation.py381](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L381-L381)

## Task Completion Monitoring

The main process polls for task completion using an async task management pattern at [bgpy/simulation_framework/simulation.py340-347](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L340-L347):

```
tasks: list[ApplyResult[GraphDataAggregator]] = [
    p.apply_async(self._run_chunk, x) for x in enumerate(chunks)
]
completed: list[GraphDataAggregator] = []
while tasks:
    completed, tasks = self._get_completed_and_tasks(completed, tasks)
    self._update_tqdm_progress_bar(pbar)
    time.sleep(0.5)
```

The `_get_completed_and_tasks()` method at [bgpy/simulation_framework/simulation.py350-358](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L350-L358) checks `task.ready()` to identify completed workers and moves their results into the `completed` list.

This polling approach:

- Allows incremental progress bar updates
- Handles worker completion in any order
- Aggregates results as they become available
- Avoids blocking on any single worker

**Sources:**[bgpy/simulation_framework/simulation.py340-358](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L340-L358)

## Integration with Testing Framework

The multi-processing infrastructure integrates with pytest for deterministic testing. Key considerations:
AspectTesting BehaviorProduction Behavior**CAIDA Caching**`pytest_configure` hook caches data before parallel test executionPre-cached in `run()` method**Serialization**Ground truth stored in YAML using `SimulatorCodec`Results stored in CSV/pickle**Determinism**`python_hash_seed` ensures reproducible fixturesOptional for production runs**Progress Display**Minimal progress output during testsFull tqdm progress bars
The testing framework at [bgpy/tests/engine_tests/](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/tests/engine_tests/) (not shown in provided files) uses the same chunking and seeding mechanisms to ensure consistent ground truth validation.

**Sources:** Context from [pyproject.toml108-119](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L108-L119) and overall system architecture diagram

## Related Components

- **[4.1](/blcrdbob3/bgpy_pkg/4.1-simulation-class-and-execution-pipeline) Simulation Class and Execution Pipeline:** Overall simulation orchestration that uses this multi-processing infrastructure
- **[4.2](/blcrdbob3/bgpy_pkg/4.2-scenario-configuration) Scenario Configuration:** Configuration parameters that affect trial count and complexity
- **[5.2](/blcrdbob3/bgpy_pkg/5.2-caida-data-and-graph-construction) CAIDA Data and Graph Construction:** AS graph loading and caching mechanisms used by workers
- **[9.1](/blcrdbob3/bgpy_pkg/9.1-test-framework-architecture) Test Framework Architecture:** Testing integration with multi-processing