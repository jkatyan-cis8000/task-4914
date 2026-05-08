# Project Setup and Configuration Design

## Overview

This document describes the setup and configuration infrastructure for the Todo Manager CLI project. It covers package configuration, entry points, dependencies, and project structure.

## Design Decisions

### 1. Package Structure at Root Level

**Decision**: Keep Python modules at the project root level rather than in a `src/` subdirectory.

**Rationale**:
- Simpler module imports within the project
- Easier development and testing workflow
- Matches common flat structure for small to medium projects
- Reduces directory nesting complexity

**Trade-offs**:
- Less isolation from package structure (root contains both package and config files)
- Mitigated by using `__init__.py` to mark the project as a package

### 2. Entry Point Configuration

**Decision**: Use `setup.py` with `entry_points` for the `todo` command.

**Entry Point Definition**:
```python
entry_points={
    "console_scripts": [
        "todo=main:main",
    ],
}
```

**Rationale**:
- Standard Python packaging approach
- Automatically creates shell script for `todo` command
- Works across platforms (Linux, macOS, Windows)
- Clean separation between CLI entry point and module logic
- `main:main` refers to the `main()` function in the `main.py` module

**Alternative Considered**: Direct script in `scripts/` directory
- Rejected: Less portable, requires platform-specific adjustments

### 3. Dependency Management

**Dependencies**:
- `click>=8.0.0`: Professional CLI framework
- `pytest>=7.0.0`: Testing framework (dev only)
- `pytest-cov>=4.0.0`: Code coverage (dev only)
- `sqlite3`: Bundled with Python (no external dependency)
- `csv`: Bundled with Python (no external dependency)

**Rationale**:
- Minimal external dependencies for core functionality
- Standard library usage for database and CSV operations reduces complexity
- Click provides professional command-line handling with minimal learning curve

**Split Installation**:
```bash
pip install .              # Core only
pip install -e .[dev]      # With development tools
```

### 4. .gitignore Configuration

**Included Entries**:
- Python artifacts: `__pycache__/`, `*.pyc`, `*.pyo`, `*.egg-info/`
- Testing: `.pytest_cache/`, `.coverage`, `htmlcov/`
- Database files: `tasks.db`, `*.db`
- Virtual environments: `venv/`, `env/`, `.venv/`
- IDE files: `.vscode/`, `.idea/`, `*.swp`, `*.swo`
- Build artifacts: `build/`, `dist/`, `eggs/`

**Rationale**:
- Prevents accidental commit of generated files
- Protects user data (database files)
- Keeps repository clean for version control

### 5. Root __init__.py

**Decision**: Create `__init__.py` at project root to mark it as a package.

**Exports**:
```python
from models import Task, ValidationError, VALID_PRIORITIES
```

**Rationale**:
- Marks the directory as a Python package
- Provides convenient access to core types
- Enables direct imports like `from todo_manager import Task`
- Supports future `from . import models` patterns

### 6. Documentation Organization

**Structure**:
- `README.md`: User-facing documentation with examples and usage
- `ARCHITECTURE.md`: Developer documentation describing module structure
- `docs/design-docs/`: Detailed design decisions for each component

**Rationale**:
- Separate concerns for users vs. developers
- Design docs explain the "why" behind technical decisions
- Easy to find appropriate documentation for different audiences

## Installation Modes

### Development Installation
```bash
pip install -e .[dev]
```
- Installs package in editable mode
- Includes pytest and pytest-cov for development
- Allows local module modifications to be reflected immediately

### Production Installation
```bash
pip install .
```
- Installs only required dependencies
- Click framework for CLI operation
- Lightweight without development tools

### From Requirements File
```bash
pip install -r requirements.txt
```
- Installs both core and development dependencies
- Useful for CI/CD and development environment setup

## Database Initialization

**Default Location**: `~/.local/share/todo_manager/tasks.db`

**Directory Structure Created**:
```
~/.local/share/
└── todo_manager/
    └── tasks.db
```

**Initialization Logic** (in `main.py`):
1. Check if directory exists, create if needed
2. Initialize database connection via `Database` class
3. Call `Database.create_table()` to create schema if not exists
4. Handle any initialization errors gracefully

**Rationale**:
- Follows Linux XDG Base Directory specification
- Centralized location for application data
- Easy to backup and manage
- Respects user's home directory structure

**Customization**:
- Environment variable: `TODO_DB_PATH`
- CLI flag: `--db-path`

## Version Specification

**Python Requirement**: `>=3.9`

**Rationale**:
- Uses type hints (f-strings, dataclasses all require 3.7+)
- Uses walrus operator and other modern features (3.8+)
- Targeted at 3.9+ for consistent support
- Covers Python versions from 2023 forward

**Supported Versions**:
- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12

## Testing and Quality

**Test Framework**: pytest

**Test Organization**:
```
tests/
├── __init__.py
├── conftest.py           # Shared fixtures
├── test_models.py        # Task model tests
├── test_database.py      # Database operation tests
├── test_export.py        # CSV export tests
└── test_cli.py           # CLI command tests
```

**Coverage Target**: >90%

**Running Tests**:
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_models.py -v

# Run with verbose output
pytest -v
```

## Module Imports

**Import Pattern**: Relative to project root
```python
# In database.py
from models import Task, ValidationError, VALID_PRIORITIES

# In cli.py
from database import Database
from export import CSVExporter
from models import Task
```

**Rationale**:
- Simple, flat namespace
- No need for relative imports with `.`
- Clear dependencies between modules
- Works well with pytest discovery

## Package Metadata

**Metadata in setup.py**:
- `name`: "todo-manager"
- `version`: "1.0.0"
- `author`: "Todo Manager Team"
- `description`: Brief description
- `long_description`: README.md content
- `classifiers`: PyPI metadata for discoverability
- `keywords`: Search terms for package discovery

**Rationale**:
- Professional package appearance
- Proper metadata for PyPI publishing
- Clear versioning scheme (semantic versioning)
- Helps users find and understand the project

## Deployment Considerations

### Local Development
```bash
pip install -e .[dev]
pytest  # Verify tests pass
todo list  # Test CLI
```

### Installation on New Machine
```bash
pip install .
mkdir -p ~/.local/share/todo_manager/
todo add --title "Getting started" --priority High --category Work
```

### Docker Containerization (Future)
Could add Dockerfile with:
- Base image: `python:3.11-slim`
- Install from requirements.txt
- Set entrypoint to `todo` command
- Mount volume for persistent database

## Future Enhancements

1. **Configuration File**: Add support for `~/.config/todo_manager/config.ini`
2. **Logging**: Add logging configuration file
3. **Migration System**: Version database schema with migration support
4. **Plugin System**: Allow extending CLI with custom commands
5. **Package Publishing**: Publish to PyPI for `pip install todo-manager`

## Checklist for Setup Verification

- [x] `setup.py` with correct entry points
- [x] `requirements.txt` with all dependencies
- [x] `.gitignore` updated for Python artifacts
- [x] `__init__.py` created at root level
- [x] `README.md` with comprehensive documentation
- [x] `ARCHITECTURE.md` for developers
- [x] Design docs in `docs/design-docs/`
- [ ] All modules (models, database, export, cli, main) completed
- [ ] Test suite complete and passing
- [ ] Integration verified end-to-end

## Summary

The setup configuration provides a professional, maintainable foundation for the Todo Manager CLI project. It uses standard Python packaging practices, minimizes external dependencies, and organizes code for easy development and testing. The modular structure enables parallel development while maintaining clear interfaces between components.
