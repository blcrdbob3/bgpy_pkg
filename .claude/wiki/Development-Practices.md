# Development Practices
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

This document covers the development workflow, code quality tools, testing infrastructure, and continuous integration setup for BGPy contributors. It describes the tooling used to maintain code quality, the automated testing framework, and the CI/CD pipeline that validates changes.

For information about the testing framework architecture and ground truth management, see [Test Framework Architecture](/blcrdbob3/bgpy_pkg/9.1-test-framework-architecture) and [Ground Truth Management](/blcrdbob3/bgpy_pkg/9.2-ground-truth-management).

---

## Overview

BGPy employs a comprehensive development workflow that ensures code quality and correctness through static analysis, automated testing, and continuous integration. The project supports multiple Python versions (3.10-3.14 and PyPy 3.11) across Linux and macOS platforms.

**Development Workflow Diagram**

```
CI/CD

Multi-Version Testing

Code Quality Tools

Local Development

Developer

Write Code

pre-commit hooks
check-added-large-files

Manual Checks

ruff
Linting & Formatting

mypy
Type Checking

pytest
Unit & Integration Tests

tox
Test Orchestrator

PyPy 3.11

Python 3.10

Python 3.11

Python 3.12

Python 3.13

Python 3.14

GitHub Actions

Test Matrix
Ubuntu & macOS

Status Badges
```

Sources: [pyproject.toml1-323](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L1-L323)[tox.ini1-33](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/tox.ini#L1-L33)[.github/workflows/tests.yml1-29](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/.github/workflows/tests.yml#L1-L29)[.pre-commit-config.yaml1-6](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/.pre-commit-config.yaml#L1-L6)

---

## Code Quality Tools

### Type Checking with mypy

BGPy uses strict type checking with `mypy` to catch type errors before runtime. The configuration is defined in `pyproject.toml`.

**mypy Configuration**
SettingValuePurpose`strict``true`Enables all optional error checking flags`ignore_missing_imports``true`Allows imports from untyped third-party libraries`show_error_codes``true`Displays error codes for easier lookup`warn_unreachable``true`Warns about unreachable code paths`disallow_untyped_calls``false`Allows calling untyped functions`disallow_incomplete_defs``false`Allows incomplete function definitions`disallow_untyped_defs``false`Allows functions without type annotations
Sources: [pyproject.toml126-136](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L126-L136)

**Running mypy**

```
# Via tox
tox -e mypy

# Directly
mypy bgpy
```

The `mypy` environment uses Python 3.10 as the base interpreter and installs all development dependencies from `requirements_dev.txt`.

Sources: [tox.ini22-25](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/tox.ini#L22-L25)[pyproject.toml22-25](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L22-L25)

### Linting and Formatting with ruff

BGPy uses `ruff` for both linting and code formatting. Ruff is a fast Python linter written in Rust that replaces multiple tools (flake8, black, isort, etc.).

**Ruff Configuration Overview**

```
Special Configurations

Per-File Overrides

Disabled Rule Categories

Ruff Lint Rules

select = ['ALL']
Enable all rules

ignore = [...]
~80 disabled rules

CPY: Copyright notices

DTZ: Datetime timezone

D100-D419: Pydocstyle

ANN: Type annotations style

RET: Return patterns

COM: Trailing commas

ERA: Commented code

init.py
Skip isort (I)

tests/**/*.py
Allow private access (SLF001)

isort:
known-first-party = ['bgpy']

flake8-bugbear:
extend-immutable-calls

flake8-pytest-style:
mark-parentheses = false
```

Sources: [pyproject.toml161-323](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L161-L323)

**Key Disabled Rules**

BGPy disables several rule categories to maintain a pragmatic balance between strictness and developer productivity:

- **Docstring rules (D100-D419)**: Lenient comment style to encourage documentation without imposing rigid formats
- **Type annotation style (ANN)**: Allows flexible annotation styles
- **Boolean trap (FBT)**: Permits boolean arguments which are sometimes necessary
- **Return patterns (RET)**: Allows various return statement patterns
- **Magic numbers (PLR2004)**: Context-dependent, often false positives
- **Uppercase variables (N803, N806, N802)**: Allows uppercase for class-type variables (e.g., `self.GraphFactoryCls`)

Sources: [pyproject.toml164-262](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L164-L262)

**Running ruff**

```
# Via tox
tox -e ruff

# Directly - check
ruff check bgpy

# Directly - format
ruff format bgpy
```

Sources: [tox.ini27-32](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/tox.ini#L27-L32)

### Flake8 Configuration

While ruff handles most linting, `flake8` configuration is maintained for compatibility:

```
[flake8]
max-line-length = 88
```

Sources: [setup.cfg1-3](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/setup.cfg#L1-L3)

---

## Pre-commit Hooks

BGPy uses `pre-commit` to run checks before commits are finalized. Currently configured hooks:

**Pre-commit Configuration**

```
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
    -   id: check-added-large-files
```

This prevents accidentally committing large files to the repository.

**Installing pre-commit**

```
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

Sources: [.pre-commit-config.yaml1-6](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/.pre-commit-config.yaml#L1-L6)[pyproject.toml84](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L84-L84)

---

## Testing Infrastructure

### Pytest Configuration

BGPy uses `pytest` as its testing framework with custom markers for categorizing tests.

**Pytest Configuration**

```
Warning Filters

Test Markers

Pytest Settings

addopts = '-rxXs -v'
Show skip/xfail reasons

slow: All slow tests

framework: Framework tests

unit_tests: Unit tests

engine: Engine tests

caida_collector_base_funcs

data_extraction_funcs

html_funcs

read_file_funcs

ignore::DeprecationWarning:yamlable

ignore::DeprecationWarning:tqdm

ignore::DeprecationWarning:dateutil.tz.tz
```

Sources: [pyproject.toml108-124](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L108-L124)

**Running Tests**

```
# Run all tests
pytest bgpy

# Run with parallelization
pytest bgpy -n auto

# Run specific marker
pytest bgpy -m slow

# Run with coverage
pytest bgpy --cov=bgpy --cov-report=html
```

**Test Markers Usage**

```
import pytest

@pytest.mark.slow
def test_full_simulation():
    """Mark computationally expensive tests"""
    pass

@pytest.mark.engine
def test_propagation():
    """Mark engine-specific tests"""
    pass
```

Sources: [pyproject.toml108-119](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L108-L119)

### Coverage Configuration

BGPy tracks code coverage to ensure comprehensive testing:

```
[tool.coverage.run]
branch = true
omit = [
    "*tests*",
    "*__init__*"
]

[tool.coverage.report]
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "raise NotImplementedError",
    "if __name__ == .__main__.:"
]
```

Sources: [pyproject.toml143-159](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L143-L159)

### Tox Multi-Version Testing

BGPy uses `tox` to test across multiple Python versions and platforms. This ensures compatibility and catches version-specific issues.

**Tox Configuration Structure**

```
Commands

Quality Environments

Test Environments

Tox Environments

tox.ini

pypy3
(PyPy 3.11)

python3.10

python3.11

python3.12

python3.13

python3.14

mypy
(Python 3.10)

ruff
(Python 3.10)

pytest bgpy
--basetemp={envtmpdir}

mypy bgpy

ruff check bgpy

ruff format bgpy
```

Sources: [tox.ini1-33](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/tox.ini#L1-L33)

**Tox Environment Definitions**
EnvironmentPython VersionCommandsDependencies`pypy3`PyPy 3.11`pytest bgpy`pytest, pytest-xdist`python3.10`CPython 3.10`pytest bgpy`pytest, pytest-xdist`python3.11`CPython 3.11`pytest bgpy`pytest, pytest-xdist`python3.12`CPython 3.12`pytest bgpy`pytest, pytest-xdist`python3.13`CPython 3.13`pytest bgpy`pytest, pytest-xdist`python3.14`CPython 3.14`pytest bgpy`pytest, pytest-xdist`mypy`CPython 3.10`mypy bgpy`requirements_dev.txt`ruff`CPython 3.10`ruff check``ruff format`ruff
Sources: [tox.ini6-32](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/tox.ini#L6-L32)

**Running Tox**

```
# Run all environments
tox

# Run specific environment
tox -e python3.12

# Run in parallel
tox -p

# Recreate environments
tox -r
```

---

## Continuous Integration

### GitHub Actions Workflow

BGPy uses GitHub Actions for continuous integration, running tests on every push and pull request.

**CI/CD Pipeline**

```
Outputs

Workflow Steps

Job Matrix

Trigger Events

Python Versions

Operating Systems

git push

Pull Request

strategy.matrix

ubuntu-latest

macos-latest

pypy-3.11

3.10

3.11

3.12

3.13

3.14

checkout@v2
Clone repository

setup-graphviz@v1
Install Graphviz

setup-python@v2
Install Python

pip install tox
tox-gh-actions

tox
Run tests

✓ Tests Pass

✗ Tests Fail

Status Badge
```

Sources: [.github/workflows/tests.yml1-29](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/.github/workflows/tests.yml#L1-L29)

**Test Matrix Configuration**

The GitHub Actions workflow creates a test matrix with:

- **Operating Systems**: Ubuntu, macOS
- **Python Versions**: PyPy 3.11, CPython 3.10-3.14
- **Total Combinations**: 12 (2 OS × 6 Python versions)

Sources: [.github/workflows/tests.yml8-13](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/.github/workflows/tests.yml#L8-L13)

**GitHub Actions Integration with Tox**

The `tox-gh-actions` package automatically maps GitHub Actions matrix Python versions to tox environments:

```
[gh-actions]
python =
    pypy-3.11: pypy3
    3.10: python3.10, ruff, mypy
    3.11: python3.11
    3.12: python3.12
    3.13: python3.13
    3.14: python3.14
```

Note that `ruff` and `mypy` only run on Python 3.10 to avoid redundant checks.

Sources: [tox.ini6-13](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/tox.ini#L6-L13)[.github/workflows/tests.yml13](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/.github/workflows/tests.yml#L13-L13)

**Required Dependencies in CI**

```
- name: Setup Graphviz
  uses: ts-graphviz/setup-graphviz@v1

- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install tox tox-gh-actions
```

Graphviz is required for diagram generation features used in tests.

Sources: [.github/workflows/tests.yml16-27](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/.github/workflows/tests.yml#L16-L27)

---

## Dependency Management

### Production Dependencies

BGPy maintains strict version pinning for production dependencies to ensure reproducibility:

**Core Dependencies**
PackageVersionPurpose`beautifulsoup4`4.14.3HTML parsing for CAIDA data`frozendict`2.4.7Immutable dictionary structures`graphviz`0.21Graph visualization`matplotlib`3.10.8Plotting and graphs`platformdirs`4.5.1Platform-specific directories`psutil`7.2.1System resource monitoring`pytest`9.0.2Testing framework`PyYAML`6.0.3YAML serialization`requests`2.32.5HTTP client`requests-cache`1.2.1HTTP caching`roa-checker`~3.0ROA validation`rov-collector`~1.0ROV data collection`tqdm`4.67.1Progress bars`yamlable`1.1.1Enhanced YAML serialization
Sources: [requirements.txt1-14](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/requirements.txt#L1-L14)[pyproject.toml57-72](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L57-L72)

### Development Dependencies

Additional tools for development and testing:
PackageVersionPurpose`pre-commit`4.5.1Pre-commit hook management`types-*`VariousType stubs for mypy`mypy`1.19.1Static type checker`tox`4.34.1Multi-environment testing`pytest-xdist`3.8.0Parallel test execution`ruff`0.14.13Fast Python linter
Sources: [requirements_dev.txt15-25](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/requirements_dev.txt#L15-L25)[pyproject.toml81-94](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L81-L94)

### Version Pinning Strategy

BGPy uses exact version pinning (`==`) for most dependencies to ensure:

1. **Reproducibility**: Same versions across all environments
2. **Stability**: Avoid breaking changes from automatic updates
3. **Compatibility**: Known working combinations

Only `roa-checker` and `rov-collector` use semantic versioning constraints (`~=`) as they are BGPy-ecosystem packages.

Sources: [requirements.txt1-14](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/requirements.txt#L1-L14)[pyproject.toml57-72](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L57-L72)

---

## Python Version Support

### Supported Versions

BGPy officially supports:

- **PyPy**: 3.11
- **CPython**: 3.10, 3.11, 3.12, 3.13, 3.14

The minimum required version is Python 3.10.

Sources: [pyproject.toml8](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L8-L8)[pyproject.toml41-47](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L41-L47)

### Platform Support

- **Linux**: Full support (Ubuntu tested in CI)
- **macOS**: Full support (both Intel and ARM)
- **Windows**: Not officially supported (commented out in CI)

Sources: [.github/workflows/tests.yml12](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/.github/workflows/tests.yml#L12-L12)[pyproject.toml51-54](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L51-L54)

### Type Hints and py.typed

BGPy is a fully typed package with a `py.typed` marker file, indicating that type checkers should use the package's inline type annotations:

```
[tool.setuptools.package-data]
bgpy = ["py.typed"]
```

Sources: [pyproject.toml100-101](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L100-L101)[MANIFEST.in3-4](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/MANIFEST.in#L3-L4)

---

## Development Workflow Summary

**Recommended Development Steps**

1. **Initial Setup**

```
git clone https://github.com/jfuruness/bgpy_pkg
cd bgpy_pkg
pip install -e ".[test]"
pre-commit install
```
2. **Before Committing**

```
# Run linter
ruff check bgpy
ruff format bgpy

# Run type checker
mypy bgpy

# Run tests
pytest bgpy
```
3. **Multi-Version Testing**

```
# Test all versions
tox

# Or specific version
tox -e python3.12
```
4. **Push Changes**

```
git push origin feature-branch
# GitHub Actions will run full test matrix
```

Sources: [pyproject.toml1-323](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/pyproject.toml#L1-L323)[tox.ini1-33](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/tox.ini#L1-L33)[.github/workflows/tests.yml1-29](https://github.com/blcrdbob3/bgpy_pkg/blob/39199d7d/.github/workflows/tests.yml#L1-L29)