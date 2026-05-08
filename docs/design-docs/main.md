# Main Module Design

## Overview

The `main.py` module serves as the application entry point and initialization layer for the Todo Manager CLI. It handles application-level configuration, database initialization, and command registration.

## Module Purpose

The main module is responsible for:
1. Setting application version and metadata
2. Initializing database with default or custom paths
3. Ensuring database directory exists with proper permissions
4. Validating database connectivity on startup
5. Providing global `--db-path` and `--version` options
6. Integrating all CLI commands from the cli module
7. Serving as the entry point for setup.py configuration

## Key Design Decisions

### 1. **Layered Architecture**
```
main.py (Application initialization)
    ↓
cli.py (Command routing)
    ↓
database.py / export.py (Business logic)
    ↓
models.py (Data validation)
    ↓
SQLite (Persistence)
```

Each layer has a single responsibility and clear interfaces.

### 2. **Default Database Path**
```
~/.local/share/todo_manager/tasks.db
```

Design rationale:
- Follows XDG Base Directory specification
- Isolates application data from user home
- Cross-platform compatible (uses `Path.home()`)
- Allows easy backup/migration of data
- Single database file (no complex setup needed)

### 3. **Database Path Configuration Hierarchy**

The database path is determined in this order (first match wins):
1. `--db-path` command-line option
2. `TODO_DB_PATH` environment variable
3. Default: `~/.local/share/todo_manager/tasks.db`

This allows flexibility for:
- Testing with temporary databases
- Custom installations
- CI/CD pipelines
- Multi-user systems

### 4. **Initialization Strategy**

**On Application Startup:**
```python
1. Ensure database directory exists (create if needed)
2. Validate database connectivity
3. Register all CLI commands
4. Store db_path in context for subcommands
5. Execute user command or show help
```

Benefits:
- Early validation prevents runtime errors
- Fast failure with clear messages
- Database is ready when first command runs
- No lazy initialization complexity

### 5. **Command Registration**

```python
# Import cli group from cli module
from cli import cli as cli_group

# Register all commands
for name, cmd in cli_group.commands.items():
    main.add_command(cmd, name)
```

Design pattern:
- cli.py defines command group with all commands
- main.py imports and re-registers them
- Allows cli.py to be independent and testable
- main.py adds global options and initialization
- Decouples application setup from command definitions

### 6. **Error Handling at Initialization**

```python
def ensure_database_dir(db_path: Optional[str] = None) -> str:
    """Create database directory with error handling."""
    
def validate_database(db_path: str) -> None:
    """Test database connectivity."""
```

Both functions raise `click.ClickException` for:
- Directory creation failures
- Permission errors
- Database initialization failures

This ensures:
- User-friendly error messages
- Proper exit codes
- No stack traces for known issues

## Implementation Details

### Global Options

**`--db-path`**
- Type: String (file path)
- Environment: `TODO_DB_PATH`
- Default: None (uses hardcoded default)
- Purpose: Override database location

**`--version`**
- Built-in Click feature
- Displays: `todo, version 1.0.0`
- Comes from `__version__` constant

### Context Object

Each command receives `ctx` context object:
```python
ctx.ensure_object(dict)
ctx.obj['db_path'] = db_path  # Available to all subcommands
```

Currently stores database path; can be extended for:
- Global configuration
- User preferences
- Logging settings
- Cache data

### Main Function Signature

```python
@click.group(invoke_without_command=True)
@click.option('--db-path', ...)
@click.pass_context
def main(ctx: click.Context, db_path: Optional[str]) -> None:
    """..."""
```

The `invoke_without_command=True` parameter means:
- Main function runs even if subcommand is specified
- Allows initialization before subcommand execution
- Enables showing help when no command given

### Database Path Resolution

```python
def ensure_database_dir(db_path: Optional[str] = None) -> str:
    if db_path is None:
        data_dir = Path.home() / ".local" / "share" / "todo_manager"
        db_path = str(data_dir / "tasks.db")
    else:
        data_dir = Path(db_path).parent
    
    data_dir.mkdir(parents=True, exist_ok=True)
    return db_path
```

Features:
- Handles None by using default
- Creates parent directories recursively
- Safe to call multiple times
- Cross-platform path handling via pathlib

## Testing Considerations

The module should be tested for:
1. Default database path resolution
2. Custom database path with `--db-path` option
3. Environment variable `TODO_DB_PATH` handling
4. Directory creation when parent doesn't exist
5. Permission error handling (read-only filesystem)
6. Database initialization validation
7. Help text display when no command given
8. Version display with `--version`
9. Command registration and routing
10. Context object creation and passing

## Integration Points

- **cli.py**: Imports cli group and registers all commands
- **database.py**: Imports Database class for initialization validation
- **All subcommands**: Receive context with db_path for database access
- **setup.py**: Entry point will reference `main:main` function
- **Environment**: Reads `TODO_DB_PATH` variable

## Entry Point Configuration

In setup.py, this module will be configured as:
```python
entry_points={
    'console_scripts': [
        'todo=main:main',
    ],
}
```

This creates a `todo` command that calls `main()` function.

## Future Enhancements

Potential improvements:
1. Configuration file support (~/.config/todo_manager/config.toml)
2. Logging setup (--verbose, --debug flags)
3. Default command when no subcommand given
4. Shell completion setup
5. Plugin system for custom commands
6. Multi-profile database support
7. Database migrations/upgrades
8. Performance profiling hooks
9. Event hooks for integrations
10. Dry-run mode for testing

## Rationale for Design

**Why separate main.py from cli.py?**
- main.py handles "how to run the app" (initialization, config)
- cli.py handles "what commands exist" (command definitions)
- Allows testing commands independently of application setup
- Clean separation of concerns
- Easier to maintain and extend

**Why validate database at startup?**
- Catches configuration errors early
- Fails fast with clear messages
- Prevents user confusion with later errors
- Ensures consistent state before any command runs

**Why use Click context for db_path?**
- Avoids global variables
- Works with Click's testing framework
- Allows different paths in different test runs
- Clean thread-safe design
