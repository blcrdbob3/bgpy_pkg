# Installation and Setup
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

This document covers the installation process for BGPy, including system requirements, dependency installation, and initial configuration. For information about running your first simulation after installation, see [Running Your First Simulation](/blcrdbob3/bgpy_pkg/2.2-running-your-first-simulation).

## Overview

BGPy (`bgpy_pkg`) is a Python package that simulates BGP security policies and attack scenarios using real-world Internet topology data from CAIDA. Installation involves satisfying system requirements, installing the Python package and its dependencies, and optionally configuring cache directories for topology data.

**Sources:**[pyproject.toml1-323](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L1-L323)[README.md1-39](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/README.md#L1-L39)

---

## System Requirements

### Python Version

BGPy requires **Python 3.10 or higher**. The package is tested against the following Python versions:
Python VersionStatusPyPy 3.11✓ Supported (Recommended for performance)CPython 3.10✓ SupportedCPython 3.11✓ SupportedCPython 3.12✓ SupportedCPython 3.13✓ SupportedCPython 3.14✓ Supported
**Note:** PyPy is recommended for production use due to significantly better performance in long-running simulations.

**Sources:**[pyproject.toml8](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L8-L8)[pyproject.toml40-47](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L40-L47)[tox.ini3-13](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/tox.ini#L3-L13)

### Operating System

BGPy is tested on the following platforms:

- **Linux** (Ubuntu and derivatives)
- **macOS Intel**
- **macOS ARM** (Apple Silicon)

Windows support is currently disabled but may work with WSL (Windows Subsystem for Linux).

**Sources:**[pyproject.toml51-55](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L51-L55)[.github/workflows/tests.yml12](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/.github/workflows/tests.yml#L12-L12)

### System Dependencies

BGPy requires **Graphviz** to be installed on your system for generating AS graph visualizations. This is a system-level dependency that must be installed separately from Python packages.

#### Installing Graphviz

**Ubuntu/Debian:**

```
sudo apt-get update
sudo apt-get install graphviz
```

**macOS (Homebrew):**

```
brew install graphviz
```

**macOS (MacPorts):**

```
sudo port install graphviz
```

**Sources:**[.github/workflows/tests.yml16-18](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/.github/workflows/tests.yml#L16-L18)[pyproject.toml60](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L60-L60)

---

## Installation Methods

### Basic Installation (Users)

For users who want to run simulations without modifying BGPy's source code:

```
pip install bgpy_pkg
```

This installs the latest stable version from PyPI along with all required runtime dependencies.

**Sources:**[pyproject.toml5-6](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L5-L6)[pyproject.toml57-72](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L57-L72)

### Development Installation (Contributors)

For contributors who want to modify BGPy or run the test suite:

1. **Clone the repository:**

```
git clone https://github.com/jfuruness/bgpy_pkg.git
cd bgpy_pkg
```

1. **Install in editable mode with development dependencies:**

```
pip install -e ".[test]"
```

Alternatively, install from requirements files:

```
pip install -r requirements_dev.txt
```

1. **Set up pre-commit hooks:**

```
pre-commit install
```

**Sources:**[pyproject.toml81-94](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L81-L94)[requirements_dev.txt1-26](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/requirements_dev.txt#L1-L26)[.pre-commit-config.yaml1-6](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/.pre-commit-config.yaml#L1-L6)

---

## Dependency Structure

```
Development Dependencies

Development Tools

mypy==1.19.1
Type checking

ruff==0.14.13
Linting & formatting

pre-commit==4.5.1
Git hooks

tox==4.34.1
Multi-version testing

pytest-xdist==3.8.0
Parallel testing

Type stubs
types-*

Core Runtime Dependencies

bgpy_pkg

beautifulsoup4==4.14.3
HTML parsing for CAIDA data

frozendict==2.4.7
Immutable dictionaries

graphviz==0.21
Graph visualization

matplotlib==3.10.8
Result plotting

platformdirs==4.5.1
Cross-platform paths

psutil==7.2.1
RAM validation

pytest==9.0.2
Test framework

PyYAML==6.0.3
YAML serialization

requests==2.32.5
HTTP downloads

requests-cache==1.2.1
HTTP caching

roa-checker~=3.0
ROA validation

rov-collector~=1.0
ROA collection

tqdm==4.67.1
Progress bars

yamlable==1.1.1
YAML serialization
```

**Sources:**[pyproject.toml57-72](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L57-L72)[requirements.txt1-15](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/requirements.txt#L1-L15)[requirements_dev.txt1-26](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/requirements_dev.txt#L1-L26)

### Key Dependency Roles
DependencyPurposeUsed By`beautifulsoup4`Parse CAIDA HTML pages for relationship data download`CAIDAASGraphCollector``frozendict`Immutable configuration dictionaries`ScenarioConfig`, `Simulation.__init__``graphviz`Generate AS graph topology diagrams`Diagram` class`matplotlib`Plot simulation results (attack success vs adoption)`GraphFactory``psutil`Validate available RAM before multiprocessing`Simulation._validate_ram``requests-cache`Cache CAIDA data downloads to avoid repeated fetches`CAIDAASGraphCollector``roa-checker`Validate BGP announcements against ROAs (RPKI)`ROV`, `ROV++`, and derived policies`tqdm`Display progress bars during simulation runs`Simulation._get_mp_results``yamlable`Serialize simulation state for testing/reproducibility`SimulatorCodec`, test framework
**Sources:**[pyproject.toml57-72](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L57-L72)[bgpy/simulation_framework/simulation.py1-605](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L1-L605)[bgpy/simulation_framework/scenarios/scenario.py1-487](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/scenarios/scenario.py#L1-L487)

---

## Post-Installation Verification

### Verify Installation

After installing BGPy, verify the installation by checking the package version and CLI availability:

```
# Check package is installed
python -c "import bgpy; print(bgpy.__version__)"

# Verify CLI is available
bgpy --help

# Check Python version compatibility
python --version
```

### Run Test Suite (Development Installation)

If you installed with development dependencies, run the test suite to ensure everything is working:

```
# Run all tests
pytest bgpy

# Run tests in parallel (faster)
pytest bgpy -n auto

# Run specific test categories
pytest bgpy -m framework  # Framework tests
pytest bgpy -m engine     # Engine tests
pytest bgpy -m unit_tests # Unit tests
```

**Sources:**[pyproject.toml78-79](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L78-L79)[pyproject.toml108-124](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L108-L124)[tox.ini20](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/tox.ini#L20-L20)

---

## Directory Structure and Configuration

### Installation Directory Structure

```
Simulation Output Structure

/

data.csv
Aggregated metrics

data.pickle
Python objects

graphs/
PNG visualizations

Package Installation

site-packages/

bgpy/

simulation_framework/

simulation_engine/

as_graphs/

shared/

tests/

System Directories

$HOME

Desktop/

sims/
Default simulation output

Platform-specific cache dir

bgpy/
CAIDA data cache
```

**Sources:**[bgpy/simulation_framework/simulation.py131-133](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L131-L133)[bgpy/simulation_framework/simulation.py166-167](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L166-L167)

### Cache Directory Configuration

BGPy caches downloaded CAIDA AS relationship data to avoid repeated downloads. The cache location is platform-dependent and managed by the `platformdirs` library:
PlatformDefault Cache DirectoryLinux`~/.cache/bgpy/`macOS`~/Library/Caches/bgpy/`
This cache directory is specified via `SINGLE_DAY_CACHE_DIR` and passed to `CAIDAASGraphConstructor`:

**Sources:**[bgpy/simulation_framework/simulation.py79-86](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L79-L86)[pyproject.toml62](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L62-L62)

### Output Directory Configuration

By default, simulation results are written to `~/Desktop/sims/<sim_name>/`. You can customize this by passing `output_dir` to the `Simulation` class:

```
from pathlib import Path
from bgpy.simulation_framework import Simulation

sim = Simulation(
    sim_name="my_simulation",
    output_dir=Path("/custom/path/to/output")
)
```

**Sources:**[bgpy/simulation_framework/simulation.py131-133](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L131-L133)[bgpy/simulation_framework/simulation.py166-167](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L166-L167)[bgpy/simulation_framework/simulation.py573-604](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L573-L604)

---

## RAM Requirements and Multiprocessing

BGPy loads the entire Internet topology (AS graph) into memory and performs in-memory simulations for performance. The RAM requirements depend on simulation configuration:

### RAM Usage Estimates (PyPy 3.10)
ConfigurationRAM per CoreDefault (no cone storage)~0.9 GBCustomer cone sizes stored~1.6 GBBoth customer & provider cones stored~2.3 GB
BGPy validates available RAM before starting multiprocessing to prevent out-of-memory errors:

```
Yes

No

Simulation.init

_validate_ram

Expected RAM > 110% of Available?

Warn user

Proceed with simulation

Calculate: parse_cpus × ram_per_core

psutil.virtual_memory.available
```

**Configuration options to reduce RAM usage:**

- Set `parse_cpus=1` to disable multiprocessing
- Set `store_customer_cone_size=False` in `as_graph_kwargs`
- Set `store_customer_cone_asns=False` in `as_graph_kwargs`

**Sources:**[bgpy/simulation_framework/simulation.py215-249](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L215-L249)[bgpy/simulation_framework/simulation.py76-100](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L76-L100)

---

## Common Installation Issues

### Issue: `ModuleNotFoundError: No module named 'bgpy'`

**Cause:** BGPy not installed or installed in different Python environment.

**Solution:**

```
# Ensure you're using the correct Python interpreter
which python
python -m pip install bgpy_pkg

# Or for development
python -m pip install -e ".[test]"
```

### Issue: Graphviz not found

**Cause:** System-level Graphviz not installed.

**Solution:** Install Graphviz using your system package manager (see [System Dependencies](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/System Dependencies)).

### Issue: RAM validation warning

**Cause:** Insufficient available RAM for multiprocessing.

**Solution:** Reduce `parse_cpus` or disable cone storage:

```
from bgpy.simulation_framework import Simulation
from frozendict import frozendict

sim = Simulation(
    parse_cpus=1,  # Disable multiprocessing
    as_graph_constructor_kwargs=frozendict({
        "as_graph_kwargs": frozendict({
            "store_customer_cone_size": False,
            "store_customer_cone_asns": False,
        })
    })
)
```

### Issue: CAIDA download failures

**Cause:** Network issues or CAIDA server unavailable.

**Solution:** BGPy caches CAIDA data. If you have a cached version, it will be reused. For fresh downloads, ensure stable network connectivity. You can also manually download CAIDA data and specify `tsv_path`:

```
from pathlib import Path
from bgpy.simulation_framework import Simulation
from frozendict import frozendict

sim = Simulation(
    as_graph_constructor_kwargs=frozendict({
        "tsv_path": Path("/path/to/caida.tsv")
    })
)
```

**Sources:**[bgpy/simulation_framework/simulation.py215-249](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L215-L249)[bgpy/simulation_framework/simulation.py79-100](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L79-L100)[bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py18-36](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/as_graphs/caida_as_graph/caida_as_graph_constructor.py#L18-L36)

---

## Command-Line Interface

After installation, the `bgpy` command is available for running simulations from the command line:

```
# Run simulation with default parameters
bgpy

# Run with custom number of trials
bgpy --num_trials 100
bgpy --trials 100  # Alias

# Display help
bgpy --help
```

The CLI entry point is defined in `pyproject.toml` and maps to `bgpy.__main__:main`:

**Sources:**[pyproject.toml78-79](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L78-L79)[bgpy/simulation_framework/simulation.py39-49](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/bgpy/simulation_framework/simulation.py#L39-L49)

---

## Next Steps

After completing installation:

- See [Running Your First Simulation](/blcrdbob3/bgpy_pkg/2.2-running-your-first-simulation) for a walkthrough of creating and executing a basic simulation
- See [Understanding Simulation Output](/blcrdbob3/bgpy_pkg/2.3-understanding-simulation-output) to learn about result formats (CSV, pickle, graphs)
- See [Simulation Framework Architecture](/blcrdbob3/bgpy_pkg/3.1-simulation-framework-architecture) for an overview of how simulations are structured

**Sources:**[README.md22-38](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/README.md#L22-L38)