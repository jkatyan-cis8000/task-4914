# Todo Manager CLI

A modular Python CLI todo manager with SQLite persistence, priority/category support, and CSV export capabilities.

## Features

- ✅ **Task Management**: Create, view, update, and delete tasks
- 📋 **Priority Levels**: Organize tasks by Low, Medium, or High priority
- 🏷️ **Categories**: Group tasks into custom categories
- 💾 **SQLite Storage**: Persistent storage with automatic database initialization
- 📊 **CSV Export**: Export tasks to CSV format for data analysis
- 🔍 **Filtering**: Filter tasks by priority or category
- 📝 **Rich Task Details**: Store title, description, timestamps, and completion status
- 🎯 **Type-Safe**: Full type annotations for better development experience

## Installation

### From Source

1. Clone the repository:
```bash
git clone https://github.com/yourusername/todo-manager.git
cd todo-manager
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install the package in development mode:
```bash
pip install -e .
```

## Quick Start

### Basic Commands

Add a new task:
```bash
todo add --title "Buy groceries" --description "Milk, eggs, bread" --priority Medium --category Shopping
```

List all tasks:
```bash
todo list
```

View a specific task:
```bash
todo view 1
```

Mark a task as complete:
```bash
todo complete 1
```

Delete a task:
```bash
todo delete 1
```

### Filtering Tasks

List tasks by priority:
```bash
todo list --priority High
```

List tasks by category:
```bash
todo list --category Work
```

### Export Tasks

Export all tasks to CSV:
```bash
todo export --output tasks.csv
```

Export tasks from a specific category:
```bash
todo export --output work_tasks.csv --category Work
```

## Usage Guide

### Environment Setup

By default, tasks are stored in `~/.local/share/todo_manager/tasks.db`. You can customize this location:

```bash
# Using environment variable
export TODO_DB_PATH=/custom/path/tasks.db
todo list

# Using command-line option
todo --db-path /custom/path/tasks.db list
```

### Task Properties

Each task includes the following information:

- **id**: Unique identifier (auto-generated)
- **title**: Short task title (required)
- **description**: Detailed task description (optional)
- **priority**: Low, Medium, or High (required)
- **category**: Task category for grouping (required)
- **completed**: Whether the task is marked complete (default: false)
- **created_at**: Timestamp of task creation (auto-generated)
- **updated_at**: Timestamp of last update (auto-generated)

### Priority Levels

- **Low**: Non-urgent tasks, nice-to-have items
- **Medium**: Important tasks with normal urgency
- **High**: Urgent tasks that need immediate attention

## Examples

### Workflow Example

1. Create a shopping list:
```bash
todo add --title "Weekly shopping" --description "Groceries for the week" --priority High --category Shopping
todo add --title "Buy office supplies" --description "Pens, paper, notebooks" --priority Medium --category Shopping
todo add --title "Pick up dry cleaning" --description "Red jacket and dress shirt" --priority Medium --category Errands
```

2. View all shopping tasks:
```bash
todo list --category Shopping
```

3. Mark the first task as complete:
```bash
todo complete 1
```

4. Export shopping tasks:
```bash
todo export --output shopping.csv --category Shopping
```

### Project Management Example

1. Create project tasks:
```bash
todo add --title "Setup development environment" --description "Install Python, dependencies" --priority High --category DevSetup
todo add --title "Create project structure" --description "Organize directories and modules" --priority High --category DevSetup
todo add --title "Write unit tests" --description "Test coverage >90%" --priority Medium --category Testing
todo add --title "Code review" --description "Review all pull requests" --priority Medium --category Development
```

2. View high-priority development tasks:
```bash
todo list --priority High
```

3. View all development tasks:
```bash
todo list --category Development
```

4. Mark tasks complete as you finish them:
```bash
todo complete 1
todo complete 2
```

5. Export project progress:
```bash
todo export --output project_status.csv
```

## Architecture

The application is organized into modular components:

- **models.py**: Task dataclass and validation
- **database.py**: SQLite database abstraction and CRUD operations
- **export.py**: CSV export functionality
- **cli.py**: Command-line interface with Click framework
- **main.py**: Application entry point
- **tests/**: Comprehensive test suite with pytest

For detailed architecture information, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Development

### Running Tests

Run the complete test suite:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=. --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_models.py -v
```

### Running with Debug Output

Use the `-v` (verbose) flag with pytest for detailed test output:
```bash
pytest -v
```

## Project Structure

```
todo-manager/
├── models.py              # Task dataclass and validation
├── database.py            # SQLite database abstraction
├── export.py              # CSV export functionality
├── cli.py                 # Click-based CLI commands
├── main.py                # Application entry point
├── requirements.txt       # Python dependencies
├── setup.py               # Package configuration
├── .gitignore             # Git ignore rules
├── README.md              # This file
├── ARCHITECTURE.md        # Architecture documentation
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── conftest.py        # pytest fixtures
│   ├── test_models.py     # Task model tests
│   ├── test_database.py   # Database operation tests
│   ├── test_export.py     # CSV export tests
│   └── test_cli.py        # CLI command tests
└── docs/
    └── design-docs/       # Design documentation
        ├── models.md
        ├── database.md
        ├── export.md
        └── ...
```

## Dependencies

### Required
- **click** (>=8.0.0): Professional command-line interface framework
- **Python 3.9+**: Core language
- **sqlite3**: Standard library for database (no additional install needed)

### Development
- **pytest** (>=7.0.0): Testing framework
- **pytest-cov** (>=4.0.0): Code coverage plugin

All dependencies are listed in `requirements.txt`.

## Configuration

The application uses the following default configuration:

- **Database Location**: `~/.local/share/todo_manager/tasks.db`
- **Database Type**: SQLite
- **CSV Export Headers**: id, title, description, priority, category, completed, created_at, updated_at

### Customizing Configuration

Set environment variables to customize behavior:

```bash
# Custom database location
export TODO_DB_PATH=/path/to/custom/database.db

# Run with custom database
todo list
```

Or use command-line options:

```bash
todo --db-path /custom/path/tasks.db list
```

## Error Handling

The application provides helpful error messages for common issues:

- **Invalid Priority**: Priority must be "Low", "Medium", or "High"
- **Missing Required Fields**: Title and category are required
- **Nonexistent Task**: Attempting to view or modify a task that doesn't exist
- **Database Connection Error**: Issues connecting to or writing to the database
- **CSV Export Error**: Issues writing CSV file or invalid output path

## Troubleshooting

### Database not found
If you see a database error, ensure the directory `~/.local/share/todo_manager/` exists:
```bash
mkdir -p ~/.local/share/todo_manager/
```

### Permission denied on database
Make sure the todo_manager directory is writable:
```bash
chmod 755 ~/.local/share/todo_manager/
```

### "todo command not found"
Ensure the package is installed:
```bash
pip install -e .
```

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please ensure:

1. All tests pass: `pytest`
2. Code coverage is maintained: `pytest --cov`
3. Code follows the existing style
4. New features include tests and documentation
5. Design decisions are documented in `docs/design-docs/`

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

## Future Enhancements

Potential improvements for future versions:

- [ ] Task due dates and reminders
- [ ] Task dependencies and subtasks
- [ ] Multiple database backends (PostgreSQL, MySQL)
- [ ] Web interface
- [ ] Task tags in addition to categories
- [ ] Recurring tasks
- [ ] Task templates
- [ ] Collaboration features
- [ ] JSON import/export
- [ ] Task search functionality

## Changelog

### Version 1.0.0
- Initial release with core functionality
- Task CRUD operations
- Priority and category support
- CSV export
- Comprehensive test suite
- SQLite persistence
