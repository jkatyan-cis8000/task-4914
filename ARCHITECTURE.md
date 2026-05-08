# Todo Manager CLI - Architecture

## Overview
A modular Python CLI todo manager with SQLite persistence, category/priority filtering, and CSV export capabilities.

## Module Structure

### 1. **models.py**
**Responsibility**: Data models and validation
- `Task` dataclass with fields: id, title, description, priority (Low/Medium/High), category, completed, created_at, updated_at
- Task validation and serialization
- **Interfaces**: Provides Task class for use by other modules

### 2. **database.py**
**Responsibility**: SQLite database abstraction layer
- `Database` class managing SQLite connections and operations
- Methods: `create_task()`, `get_task()`, `list_tasks()`, `update_task()`, `delete_task()`, `list_by_category()`
- Automatic table creation and migrations
- **Interfaces**: 
  - Constructor takes database path
  - Returns Task objects from queries
  - Raises DatabaseError on failures

### 3. **export.py**
**Responsibility**: CSV export functionality
- `CSVExporter` class handling task export
- Methods: `export_tasks()`, `export_by_category()`
- CSV header: id, title, description, priority, category, completed, created_at, updated_at
- **Interfaces**: 
  - Constructor takes output path
  - `export_tasks(tasks)` returns success/failure
  - Works with Task objects from database module

### 4. **cli.py**
**Responsibility**: Command-line interface and user interaction
- CLI commands: 
  - `add` - add new task
  - `list` - view all or filtered tasks
  - `complete` - mark task complete
  - `delete` - remove task
  - `export` - export to CSV
  - `view` - view task details
- Uses `click` framework for CLI implementation
- Command routing and argument parsing
- **Interfaces**: 
  - Takes database instance
  - Calls database and export modules
  - Formats and displays results to stdout

### 5. **main.py**
**Responsibility**: Application entry point and initialization
- Application setup and configuration
- Database initialization
- CLI entry point (main function)
- **Interfaces**: Orchestrates all modules

### 6. **tests/** directory
**Responsibility**: Comprehensive test coverage
- `test_models.py` - Task validation and serialization
- `test_database.py` - Database CRUD operations
- `test_export.py` - CSV export functionality
- `test_cli.py` - CLI commands and user interaction
- Uses `pytest` framework
- Fixtures for temporary database and test data

## Data Flow

```
User Input (CLI)
    ↓
cli.py (command handling)
    ↓
database.py (persistence)
    ↓
models.py (data validation)
    ↓
SQLite (storage)

Export Flow:
database.py (query tasks)
    ↓
export.py (format to CSV)
    ↓
CSV file
```

## Key Design Decisions

1. **Separation of Concerns**: Each module has single responsibility
2. **SQLite for Persistence**: Reliable, requires no setup
3. **Click for CLI**: Professional command-line argument handling
4. **Task Model**: Immutable data structure for type safety
5. **Database Abstraction**: Easy to swap implementations if needed
6. **Comprehensive Tests**: All modules tested independently

## Dependencies

- `click` - CLI framework
- `pytest` - Testing framework
- `sqlite3` - Standard library, no external dependency needed for core DB
- `csv` - Standard library for export

## Configuration

- Default database location: `~/.local/share/todo_manager/tasks.db`
- Environment variable override: `TODO_DB_PATH`

## Error Handling

- DatabaseError for persistence issues
- ValueError for invalid data
- Click decorators for CLI validation
- Graceful error messages to users
