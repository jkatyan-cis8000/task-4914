# Database Layer Design Document

## Overview

The `database.py` module provides a clean SQLite abstraction layer (`Database` class) for persistent task storage. It handles connection management, schema creation, and CRUD operations while maintaining consistency with the `Task` model through type-safe conversions.

## Design Decisions

### 1. **Single Database Class**

Rather than separating concerns into multiple classes (Connection, Query, etc.), we use a single `Database` class because:
- **Simplicity**: All database operations in one place for the CLI
- **Lifecycle**: Manages connection lifetime (open/close)
- **Context Manager**: Supports `with` statement for automatic cleanup
- **Dependency**: CLI gets one object to pass around

### 2. **Automatic Path Setup**

Default database location: `~/.local/share/todo_manager/tasks.db`
- **Why**: Follows XDG Base Directory convention on Linux/Mac
- **Auto-create**: Parent directories created automatically
- **Override**: Constructor accepts custom `db_path` for testing
- **Idempotent**: Safe to call multiple times (mkdir with `exist_ok=True`)

### 3. **Task Objects as Results**

All query methods return `Task` objects:
- **Type Safety**: Callers work with strongly-typed objects, not tuples/dicts
- **Validation**: Data is validated immediately after retrieval
- **Consistency**: Same format whether task is freshly created or loaded from disk
- **Error Early**: Invalid data in database caught at retrieval time, not later

The conversion happens in `_row_to_task()`:
- Unpacks tuple from database
- Converts timestamp strings → datetime objects
- Raises `DatabaseError` if Task validation fails

### 4. **Schema as Class Constant**

```python
SCHEMA_V1 = """CREATE TABLE IF NOT EXISTS tasks (...)"""
```
- **Version Control**: Future migrations can add SCHEMA_V2, SCHEMA_V3, etc.
- **Clarity**: SQL is documented right in the code
- **Idempotent**: `IF NOT EXISTS` prevents errors on repeated calls
- **Constraints**: Schema includes CHECK for priority validation

### 5. **Explicit Error Types**

Two exception types:
- **`DatabaseError`**: Database operations failed (connection, query, integrity)
- **`ValidationError`** (from models): Data is structurally invalid

This separation allows callers to:
- Catch database issues and retry/recover
- Catch validation issues and report user error

### 6. **Timestamps as ISO Strings**

Database stores timestamps as ISO format strings:
- **Portable**: Works with any SQL client/tool
- **Readable**: Human-readable in database browser
- **Python**: Converted to datetime on retrieval with `datetime.fromisoformat()`
- **Consistency**: Ensures created_at/updated_at are always synchronized

### 7. **No Query Abstraction Layer**

We use raw SQL via sqlite3, not an ORM:
- **Simplicity**: Direct, understandable SQL
- **Performance**: No overhead of ORM machinery
- **Transparency**: What you see is what executes
- **Future**: Can add ORM later if needed

## API Surface

### Constructor

```python
Database(db_path: Optional[str] = None)
```
- Creates connection and initializes schema
- Raises `DatabaseError` if initialization fails
- Thread-safe (single connection per instance, use multiple instances for threads)

### CRUD Operations

#### Create
```python
create_task(title: str, description: str, priority: str, category: str) -> Task
```
- Auto-generates id and timestamps
- Validates priority before insert
- Returns the created Task with id populated
- Raises `DatabaseError` on insert failure, `ValidationError` on bad priority

#### Retrieve
```python
get_task(task_id: int) -> Task
list_tasks() -> List[Task]
list_by_category(category: str) -> List[Task]
list_by_priority(priority: str) -> List[Task]
```
- All return Task objects
- Ordered by created_at descending (newest first)
- `get_task()` raises `DatabaseError` if id not found
- `list_by_priority()` validates priority argument

#### Update
```python
update_task(task_id: int, **updates) -> Task
```
- Only allows updates to: title, description, priority, category, completed
- Auto-updates the updated_at timestamp
- Validates priority if being changed
- Returns the modified Task
- Raises `DatabaseError` if id not found

#### Delete
```python
delete_task(task_id: int) -> None
```
- Raises `DatabaseError` if id not found
- Cascading deletes handled by SQLite (if future FK constraints added)

### Lifecycle Management

```python
close() -> None
__enter__() -> Database
__exit__(...) -> None
```
- Context manager support for automatic cleanup
- Manual `close()` also available

## Database Schema

```sql
CREATE TABLE IF NOT EXISTS tasks (
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

### Constraints

- **id**: Auto-incremented primary key
- **title, description**: Text, non-null
- **priority**: CHECK constraint ensures valid values
- **category**: Required (non-null)
- **completed**: Boolean with default False
- **Timestamps**: ISO format strings, non-null

### Indexing

Currently no explicit indexes (future optimization):
- Queries filter by id (primary key, auto-indexed)
- Category/priority filters could benefit from indexes under load
- Add as needed: `CREATE INDEX idx_tasks_category ON tasks(category)`

## Error Handling

### Database Errors

Operational failures (connection, permissions, disk full):
```python
try:
    task = db.create_task(...)
except DatabaseError as e:
    logger.error(f"Database operation failed: {e}")
    # Retry logic, fallback, etc.
```

### Validation Errors

Invalid input data:
```python
try:
    task = db.create_task(title="", priority="Invalid")
except ValidationError as e:
    logger.error(f"Invalid data: {e}")
    # Inform user, re-prompt, etc.
```

## Integration Points

### With models.py

- Creates Task objects from database rows
- Task validation ensures consistency
- Serialization methods (to_dict, to_json) used by export/CLI

### With export.py

- Retrieves tasks via `list_tasks()`
- Converts to dicts via `Task.to_dict()`
- No direct coupling to export format

### With cli.py

- CLI creates Database instance at startup
- Calls CRUD methods for user commands
- Displays Task objects (formatted by CLI, not database)

## Testing Strategy

See `test_database.py` for comprehensive coverage:
- Initialization (path creation, schema)
- Create operations (auto-increment, validation)
- Read operations (single, multiple, filtering)
- Update operations (field updates, timestamp changes)
- Delete operations (success, not-found)
- Error conditions (bad priority, missing id, etc.)
- Fixtures for temp database cleanup

## Future Enhancements

1. **Indexes**: Add for category/priority on large datasets
2. **Transactions**: Explicit transaction batching for multi-step operations
3. **Pagination**: Limit/offset for large task lists
4. **Soft Deletes**: completed_at timestamp instead of hard delete
5. **Migrations**: Version-based schema upgrades
6. **Connection Pool**: For future multi-threaded/async support
7. **Search**: Full-text search on title/description
