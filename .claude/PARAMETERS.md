# PARAMETERS.md

Configuration and rules for Claude Code work in this repository.

## File Modification Rules

**IMPORTANT**: Maintain pre-existing functionality by only making additions to the codebase.

**This is a light constraint with the following flexibility:**

**`.claude/` directory (reference files for AI assistants):**
- Allowed: freely write and edit any files here
- These are metadata/documentation files, not part of the main codebase

**Main codebase (`bgpy/`, source code, etc.):**
- Allowed: create new files and add new features
- Not allowed: edit existing files (preserve functionality)
- Not allowed: delete files
- Not allowed: modify git history

**Rationale**: This constraint preserves the stability of the codebase while allowing extensions and new features. Editing existing files could break functionality or introduce subtle bugs. Use `.claude/` files to document decisions and track work.

---

## Formatting & Code Style Rules

These rules come from `pyproject.toml` and enforce consistent style across the codebase.

### Line Length & General Style
- **Max line length**: 88 characters (enforced by Ruff)
- **Python version**: 3.10+ required
- **String quotes**: Double quotes preferred (enforced by Ruff)
- **Type hints**: Full type hints required (mypy strict mode enabled)

### Code Organization
- **Import sorting**: Isort with `known-first-party = ["bgpy"]` - bgpy imports come after stdlib and third-party
- **Exceptions**: __init__.py files are excluded from isort to preserve import order (avoiding circular imports)
- **Test files**: Can use private variables (SLF001 ignored in tests)

### Type Checking (mypy strict mode)
- `strict = true` - all code must be type-hinted
- `disallow_untyped_defs = false` - some flexibility on definitions
- `disallow_untyped_calls = false` - some flexibility on calls
- `warn_unreachable = true` - warns about unreachable code
- `show_error_codes = true` - always show mypy error codes

### Key Ruff Linting Rules

**What IS enforced:**
- `E`, `W` - PEP 8 errors and warnings (required)
- `F` - Pyflakes (code correctness, required)
- `I` - Isort (import ordering)
- `UP` - PyUpgrade (modern Python patterns)
- `B` - Flake8 Bugbear (bug detection)
- `SIM` - Simplify (code simplification) - with some exceptions
- `T` - Print statement checking

**What is NOT enforced (intentional exceptions):**
- `D1xx`, `D2xx`, `D3xx`, `D4xx` - Docstring formatting (lenient)
- `C90` - McCabe complexity (context-dependent, not blanket rules)
- `N803`, `N806` - Uppercase variable names allowed for class references
  - Example: `self.PolicyCls = BGP` is preferred over `self.policy_cls`
  - This makes it clear the variable holds a class type
- `N802` - Functions can be capitalized if they're properties returning classes
- `ANN` - No comment style restrictions
- `FBT` - Boolean trap allowed
- `COM` - Trailing commas not forced
- `EM` - Error message formatting flexible
- `RET` - Return type flexibility
- `ARG` - Unused arguments allowed (used in subclasses)
- `UP008` - `super(ClassName, self)` allowed (needed for multiple inheritance)
- `UP035` - Deprecated imports flexibility (avoid false positives)
- `PIE790` - `pass` in blank functions allowed with docstrings
- `B027` - Empty methods in abstract classes without decorator allowed
- `SIM105`, `SIM103`, `SIM114`, `SIM117` - Readability exceptions
- `ISC001` - String concatenation (conflicts with ruff format)
- `RUF022` - `__all__` sorting flexibility
- `G001-G004` - Logging format flexible
- `PT018` - Assert multi-check flexibility
- `PLW1641` - Hash requirements
- `PLC0207` - String split flexibility

### Writing Style (Comments, Docstrings, Documentation)
- No emojis in code, comments, or documentation
- No em-dashes (--) in comments or docstrings; use a comma, colon, or rewrite the sentence instead

### Code Patterns

**Allowed & Encouraged:**
- Dataclasses with `@dataclass(slots=True, frozen=True)` for performance
- Class registries using `__init_subclass__`
- `weakref.proxy()` for circular reference prevention
- `functools.cached_property` for lazy evaluation
- Multiprocessing and Pool for parallelization
- YAMLable serialization for reproducibility

**Don't force:**
- Complex docstrings (lenient D-rules)
- Type hints on every single variable (some flexibility)
- Magic number extraction (case-by-case)
- Complex simplifications that reduce readability

### Pytest Configuration
- Markers available: `slow`, `framework`, `unit_tests`, `engine`, `caida_collector_base_funcs`, `data_extraction_funcs`, `html_funcs`, `read_file_funcs`
- Options: `-rxXs -v` (shows skip/xfail reasons, verbose)
- Coverage: Excludes `*tests*` and `*__init__*` files

### Pre-commit Hooks
The project uses `pre-commit` for automated checks:
```bash
pre-commit run --all-files
```

Ensure all code passes:
- `ruff check` - linting
- `ruff format` - formatting
- `mypy` - type checking

---

## Files Created in This Session

Track all new files created to ensure compliance with file modification rules.

See `FILES.md` for the complete list.

---

## Quick Reference: Common Commands

```bash
# Code quality checks
ruff check bgpy              # Lint check
ruff format bgpy             # Auto-format
mypy bgpy                    # Type checking
pre-commit run --all-files   # All checks

# Testing
pytest bgpy                  # Run all tests
pytest bgpy -n auto         # Parallel tests
pytest bgpy --overwrite     # Update ground truth

# Installation
pip install -e ".[test]"    # Dev installation
```
