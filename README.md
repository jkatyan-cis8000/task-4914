# Todo Manager CLI

A modular, feature-rich Python command-line todo manager with SQLite persistence, priority/category support, and CSV export capabilities.

## Features

✨ **Core Features:**
- ➕ Add tasks with title, description, priority, and category
- 📋 List all tasks or filter by category/priority
- ✅ Mark tasks as complete
- 🗑️ Delete tasks
- 💾 Store tasks in SQLite database (automatic persistence)
- 📊 Export tasks to CSV format
- 📁 Organize tasks by categories
- ⭐ Set task priorities (Low, Medium, High)

## Installation

### From Source

```bash
# Clone the repository
git clone <repository-url>
cd task-4914

# Install in development mode
pip install -e .
```

### Using setup.py

```bash
python setup.py install
```

### With Development Dependencies

```bash
pip install -e ".[dev]"
```

## Quick Start

### Using the CLI

```bash
# Add a new task
todo add --title "Buy groceries" --description "Milk, eggs, bread" --priority "High" --category "Shopping"

# List all tasks
todo list

# View a specific task
todo view 1

# Mark task as complete
todo complete 1

# Delete a task
todo delete 1

# Export tasks to CSV
todo export --output tasks.csv

# Filter tasks by category
todo list --category "Work"

# Filter tasks by priority
todo list --priority "High"
```

### Using Python Directly

```python
from database import Database
from export import CSVExporter

# Create and manage tasks
db = Database()
task = db.create_task("Learn Python", "Complete Python tutorial", "Medium", "Learning")
print(f"Created task: {task.title} (ID: {task.id})")

# List tasks
all_tasks = db.list_tasks()
for task in all_tasks:
    print(f"[{task.id}] {task.title} - {task.category}")

# Filter by category
work_tasks = db.list_by_category("Work")

# Export to CSV
exporter = CSVExporter("tasks.csv")
success, message = exporter.export_tasks(all_tasks)
print(message)

db.close()
```

## Command Reference

### `add` - Add a New Task

```bash
todo add [OPTIONS]

Options:
  --title TEXT           Task title (will prompt if not provided)
  --description TEXT     Detailed description (optional)
  --priority [Low|Medium|High]  Priority level (default: Medium)
  --category TEXT        Task category (will prompt if not provided)
```

**Example:**
```bash
todo add --title "Review code" --description "Code review for PR #123" --priority "High" --category "Work"
```

### `list` - View Tasks

```bash
todo list [OPTIONS]

Options:
  --category TEXT        Filter by category
  --priority [Low|Medium|High]  Filter by priority
  --compact              Show compact list format
  --completed            Show only completed tasks
```

**Examples:**
```bash
todo list                          # Show all tasks
todo list --category "Work"        # Show Work category tasks
todo list --priority "High"        # Show high priority tasks
todo list --compact                # Show compact format
todo list --completed              # Show only completed tasks
```

### `view` - Show Task Details

```bash
todo view TASK_ID

Arguments:
  TASK_ID               Task ID to view
```

**Example:**
```bash
todo view 1
```

### `complete` - Mark Task as Complete

```bash
todo complete TASK_ID

Arguments:
  TASK_ID               Task ID to mark complete
```

**Example:**
```bash
todo complete 5
```

### `delete` - Remove a Task

```bash
todo delete TASK_ID

Arguments:
  TASK_ID               Task ID to delete
```

**Example:**
```bash
todo delete 3
```

### `export` - Export to CSV

```bash
todo export [OPTIONS]

Options:
  --output TEXT         Output CSV file path (required)
  --category TEXT       Export only tasks from this category (optional)
```

**Examples:**
```bash
todo export --output tasks.csv                  # Export all tasks
todo export -o tasks.csv --category "Work"     # Export Work tasks only
```

## Database

### Default Location

Tasks are stored in SQLite at: `~/.local/share/todo_manager/tasks.db`

### Custom Database Path

Set a custom database location using the `--db-path` option or `TODO_DB_PATH` environment variable:

```bash
# Using option
todo --db-path /path/to/custom/db list

# Using environment variable
export TODO_DB_PATH=/path/to/custom/db
todo list
```

### Database Schema

```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    priority TEXT NOT NULL CHECK(priority IN ('Low', 'Medium', 'High')),
    category TEXT NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
```

## CSV Export Format

Exported CSV files contain the following columns:

```
id,title,description,priority,category,completed,created_at,updated_at
1,Buy groceries,Milk and eggs,High,Shopping,No,2026-05-08T10:30:00.000000,2026-05-08T10:30:00.000000
```

## Project Structure

```
todo-manager/
├── models.py           # Task dataclass and validation
├── database.py         # SQLite abstraction layer
├── export.py           # CSV export functionality
├── cli.py              # Click-based CLI commands
├── main.py             # Application entry point
├── setup.py            # Package configuration
├── requirements.txt    # Dependencies
├── ARCHITECTURE.md     # Detailed architecture documentation
├── tests/              # Comprehensive test suite
│   ├── conftest.py     # Pytest fixtures
│   ├── test_models.py  # Model tests
│   ├── test_database.py # Database tests
│   ├── test_export.py  # Export tests
│   └── test_cli.py     # CLI tests
└── docs/               # Design documentation
```

## Architecture

The project follows a modular, layered architecture:

- **Models Layer** (`models.py`): Defines the `Task` dataclass with validation
- **Persistence Layer** (`database.py`): SQLite database abstraction
- **Export Layer** (`export.py`): CSV export functionality
- **CLI Layer** (`cli.py`): User-facing command interface
- **Entry Point** (`main.py`): Application initialization and routing

For detailed architecture information, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Testing

The project includes comprehensive test coverage with 216 tests across all modules:

```bash
# Run all tests
pytest tests/

# Run with coverage report
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_models.py -v

# Run specific test class
pytest tests/test_database.py::TestCreateTask -v
```

### Test Coverage

- ✅ Task model validation
- ✅ Database CRUD operations
- ✅ CSV export functionality
- ✅ CLI command functionality
- ✅ Error handling and edge cases
- ✅ Data filtering and persistence
- ✅ Integration workflows

## Error Handling

The application provides clear error messages for common issues:

```bash
# Invalid priority
$ todo add --title "Task" --category "Work" --priority "Critical"
Error: Priority must be one of {'Low', 'Medium', 'High'}

# Non-existent task
$ todo view 999
Error: Task 999 not found

# Missing required option
$ todo export
Error: Missing option '--output'
```

## Dependencies

- **Click** (>=8.0.0) - CLI framework
- **pytest** (>=7.0.0) - Testing framework (dev only)
- **pytest-cov** (>=4.0.0) - Coverage reporting (dev only)

All standard library modules used: `sqlite3`, `csv`, `pathlib`, `datetime`

## Version

Current version: **1.0.0**

## License

This project is provided as-is for educational and development purposes.

## Contributing

Contributions are welcome! The codebase is designed to be modular and easy to extend:

1. Core logic in separate modules (models, database, export)
2. Comprehensive tests for all functionality
3. Clear separation of concerns
4. Well-documented code and architecture

## Examples

### Complete Workflow

```bash
# Add some tasks
todo add --title "Project Planning" --priority "High" --category "Work"
todo add --title "Buy lunch" --category "Shopping"
todo add --title "Team meeting" --priority "Medium" --category "Work"

# View all tasks
todo list

# Complete a task
todo complete 1

# View only work tasks
todo list --category "Work"

# View high priority tasks
todo list --priority "High"

# Export everything to CSV
todo export --output all_tasks.csv

# Export only work tasks
todo export --output work_tasks.csv --category "Work"

# View details of a specific task
todo view 3
```

### Task Management Example

```bash
# Add a new project task
todo add --title "Implement authentication" \
         --description "Add user login and registration" \
         --priority "High" \
         --category "Development"

# List all development tasks
todo list --category "Development"

# Mark as complete once done
todo complete 1

# View the updated task
todo view 1

# Export project documentation
todo export --output project_status.csv --category "Development"
```

## Troubleshooting

### Database Permission Error

If you get a permission error when creating tasks:

```bash
# Check directory permissions
ls -la ~/.local/share/todo_manager/

# Set custom database location
export TODO_DB_PATH=/tmp/my_tasks.db
todo add --title "Test" --category "Test"
```

### Tasks Not Appearing

```bash
# Check database path
echo $TODO_DB_PATH

# List all tasks (should work after adding)
todo list

# Check database file exists
ls -la ~/.local/share/todo_manager/tasks.db
```

### Import Errors

```bash
# Ensure package is installed in development mode
pip install -e .

# Check Python path
python -c "import models; print(models.__file__)"
```

## Support

For issues, errors, or feature requests, check:

1. The test suite in `tests/` for usage examples
2. Command help: `todo COMMAND --help`
3. Global help: `todo --help`
4. Architecture documentation: `ARCHITECTURE.md`

---

Built with ❤️ using Python, Click, and SQLite
