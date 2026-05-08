# Export Module Design

## Overview

The `export.py` module provides CSV export functionality for the Todo Manager CLI. It implements a `CSVExporter` class that converts Task objects into CSV format with proper escaping, validation, and error handling.

## Module Purpose

The export functionality allows users to:
1. Export all tasks to a CSV file for data analysis, backup, or sharing
2. Export tasks filtered by category to CSV
3. Generate properly formatted CSV with standard headers
4. Handle file system errors gracefully with informative error messages

## Key Design Decisions

### 1. **Separation of Concerns**
- The `CSVExporter` class handles only CSV formatting and file I/O
- Task filtering is delegated to the caller or provided via `export_by_category()`
- No database logic; only works with Task objects passed to it

### 2. **Clean Interface**
```python
exporter = CSVExporter('/path/to/output.csv')
success, message = exporter.export_tasks(task_list)
success, message = exporter.export_by_category(task_list, 'Work')
```

The interface is simple and predictable:
- Constructor takes output path and validates directory access
- Methods return (success: bool, message: str) tuples for easy CLI integration
- All errors are raised as `ExportError` for consistent error handling

### 3. **CSV Format Design**
Headers match Task dataclass fields for clarity:
- `id, title, description, priority, category, completed, created_at, updated_at`
- Timestamps exported in ISO format for standardization
- Boolean `completed` field converted to human-readable "Yes"/"No"
- Proper CSV escaping via `csv.DictWriter` (handles quotes, newlines, etc.)

### 4. **Robustness**
- Directory creation: Parent directories are created automatically if needed
- Empty task lists: Export succeeds with just headers (useful for templates)
- Encoding: Always UTF-8 for internationalization support
- Error messages: Informative messages that help users understand and fix issues

### 5. **Path Handling**
- Uses `pathlib.Path` for cross-platform compatibility
- Accepts both absolute and relative paths
- Automatically handles path normalization

## Implementation Details

### CSV Row Conversion
The `_task_to_csv_row()` private method handles Task-to-CSV conversion:
- Converts ID to string for CSV format
- Uses task's `isoformat()` timestamps for consistency
- Transforms boolean `completed` to "Yes"/"No" for readability
- Preserves all task information without loss of data

### Error Handling
The module uses a custom `ExportError` exception:
- Raised during initialization if output path is invalid
- Raised during export if file write fails
- Provides context about what went wrong for debugging

### Method Design

**`export_tasks(tasks: List[Task])`**
- Primary export method
- Handles empty lists gracefully
- Returns (success, message) tuple for CLI integration
- Raises `ExportError` on file I/O failures

**`export_by_category(tasks: List[Task], category: str)`**
- Convenience method for filtered exports
- Filters tasks by exact category match
- Reports count of exported tasks
- Reuses `export_tasks()` to avoid code duplication

## Testing Considerations

The module should be tested for:
1. Successful export of task lists with various priorities and categories
2. Proper CSV escaping (special characters, newlines, quotes)
3. Empty task list handling
4. File path validation and creation
5. Permission errors when output directory is not writable
6. Category filtering accuracy
7. Timestamp format consistency

## Integration Points

- **models.py**: Depends on Task dataclass; uses Task attributes for export
- **cli.py**: Called from export command with task list and output path
- **database.py**: Receives Task objects from database queries; passes to exporter

## Future Enhancements

Potential improvements for future iterations:
1. JSON export format
2. Excel/XLSX export support
3. Export filtering by date range
4. Export with custom column selection
5. Streaming export for large task lists
6. Template-based export formats
