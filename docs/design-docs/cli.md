# CLI Module Design

## Overview

The `cli.py` module provides a professional command-line interface for the Todo Manager using the Click framework. It implements seven main commands: add, list, view, complete, delete, and export, with intuitive argument handling and formatted output.

## Module Purpose

The CLI module is the primary user-facing interface. It:
1. Handles user input and command parsing via Click
2. Validates inputs and provides helpful error messages
3. Formats and displays task information with colors and formatting
4. Integrates the Database and CSVExporter modules
5. Provides rich help text and command examples

## Key Design Decisions

### 1. **Click Framework Integration**
```python
@click.group()
def cli():
    """Main CLI group"""

@cli.command()
@click.option(...)
def add(...):
    """Add command with options"""
```

Using Click provides:
- Automatic help generation (`--help`)
- Consistent argument/option parsing
- Built-in validation
- Easy testing with CliRunner
- Professional appearance

### 2. **TaskFormatter Helper Class**
Separates display logic from command logic:
```python
class TaskFormatter:
    @staticmethod
    def format_task_list(tasks, compact=False)
    @staticmethod
    def format_single_task(task)
```

Benefits:
- Reusable formatting across commands
- Easy to update styling in one place
- Testable formatting logic
- Colors and formatting isolated from business logic

### 3. **Color-Coded Output**
- High priority: Red
- Medium priority: Yellow
- Low priority: Green
- Completed tasks: Dimmed
- Status indicators: Green (done) / Yellow (todo)

This helps users quickly scan and identify important tasks.

### 4. **Command Design**

#### **add** Command
- Required: `--title` (prompted)
- Required: `--category` (prompted)
- Optional: `--description` (default empty)
- Optional: `--priority` (default Medium)
- Returns: Created task details

#### **list** Command
- Optional: `--category` (filter by category)
- Optional: `--priority` (filter by priority)
- Optional: `--compact` (compact display format)
- Optional: `--completed` (show only completed tasks)
- Returns: Formatted task list

#### **view** Command
- Required: `task_id` (argument)
- Returns: Detailed task information

#### **complete** Command
- Required: `task_id` (argument)
- Returns: Updated task with done status

#### **delete** Command
- Required: `task_id` (argument)
- Confirmation prompt built-in via `@confirmation_option`
- Returns: Deletion confirmation

#### **export** Command
- Required: `--output` or `-o` (output file path)
- Optional: `--category` (export specific category)
- Returns: Export success message with file path

### 5. **Error Handling Strategy**
```python
try:
    # Database operations
except (DatabaseError, ValidationError) as e:
    click.echo(f"Error: {e}", err=True)
    raise SystemExit(1)
```

Design principles:
- Catch specific exception types
- Display user-friendly messages
- Use stderr for errors (`err=True`)
- Exit with code 1 on failure
- No stack traces shown to users

### 6. **Database Integration Pattern**
Each command follows this pattern:
```python
db = Database()
# ... operations ...
db.close()
```

Creates a fresh database connection per command, ensuring:
- No connection pooling complexity
- Clean isolation between commands
- Proper resource cleanup
- Simpler testing

### 7. **User Experience Features**

**Help Examples in Docstrings**
```python
def list(...):
    """
    List all tasks or filter...
    
    Examples:
    \b
      todo list --category Work    # Show Work category
    """
```

**Formatted Output**
- Table-like display for multiple tasks
- Detailed single-task view
- Clear status indicators (✓, ○)
- Consistent spacing and alignment

**Confirmation Prompts**
- Delete command uses `@confirmation_option` decorator
- Prevents accidental data loss
- Standard confirmation workflow

## Implementation Details

### Output Formatting

**Compact Format**
```
✓ [1] Buy groceries
○ [2] Review code
○ [3] Write tests
```

**Full Format**
```
────────────────────────────────────────────────────────────
ID: 1 | Status: TODO | Priority: High
Title: Buy groceries
Category: Personal
Description: Milk, eggs, bread
Created: 2026-05-08 10:30:00
────────────────────────────────────────────────────────────
```

### Priority Color Mapping
- 'Low': green (less urgent)
- 'Medium': yellow (standard)
- 'High': red (important)
- Completed: dimmed (de-emphasized)

### Exception Handling
- **DatabaseError**: Connection, query, or data persistence failures
- **ValidationError**: Invalid task data (priority, category, etc.)
- **ExportError**: File I/O failures during export
- **Click validation errors**: Automatic from Click decorators

## Testing Considerations

The module should be tested for:
1. Command argument parsing (valid and invalid inputs)
2. Error handling and messages
3. Database integration (mocked)
4. Output formatting with various task lists
5. Filter operations (category, priority, completed)
6. Export command flow
7. Confirmation prompts
8. Help text generation
9. Color output in terminal

## Integration Points

- **models.py**: Task objects received from database
- **database.py**: CRUD operations for task management
- **export.py**: CSV export functionality
- **Click framework**: Command/option parsing and execution

## Future Enhancements

Potential improvements:
1. Task editing with `edit` command
2. Recurring tasks or due dates
3. Task descriptions in list view (with --verbose)
4. Sorting options (by priority, date, etc.)
5. Task search/grep functionality
6. Bulk operations (delete multiple by filter)
7. JSON output format
8. Piping support for scripting
9. Config file for defaults (default priority, category list)
10. Interactive mode with menu system
