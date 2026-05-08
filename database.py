"""
SQLite database abstraction layer for the Todo Manager CLI.

This module provides the Database class for managing task persistence with CRUD operations.
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from models import Task, ValidationError, VALID_PRIORITIES


class DatabaseError(Exception):
    """Raised when database operations fail."""
    pass


class Database:
    """
    SQLite database abstraction for managing tasks.
    
    Handles connection management, table creation, and CRUD operations.
    All operations return Task objects for consistency.
    """
    
    # SQL schema for tasks table
    SCHEMA_V1 = """
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
    """
    
    def __init__(self, db_path: Optional[str] = None) -> None:
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file.
                    Defaults to ~/.local/share/todo_manager/tasks.db
                    
        Raises:
            DatabaseError: If database connection fails
        """
        if db_path is None:
            # Use default path
            default_dir = Path.home() / ".local" / "share" / "todo_manager"
            db_path = str(default_dir / "tasks.db")
        
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        
        try:
            self._connect()
            self.create_table()
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to initialize database: {e}")
    
    def _connect(self) -> None:
        """
        Establish database connection.
        
        Creates parent directories if they don't exist.
        
        Raises:
            DatabaseError: If connection fails
        """
        try:
            # Create parent directories if needed
            db_file = Path(self.db_path)
            db_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Connect to database (creates file if it doesn't exist)
            self.connection = sqlite3.connect(self.db_path)
            # Enable foreign keys
            self.connection.execute("PRAGMA foreign_keys = ON")
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to connect to database: {e}")
    
    def create_table(self) -> None:
        """
        Initialize tasks table.
        
        Creates the table if it doesn't exist. Safe to call multiple times.
        
        Raises:
            DatabaseError: If table creation fails
        """
        if self.connection is None:
            raise DatabaseError("Database not connected")
        
        try:
            self.connection.execute(self.SCHEMA_V1)
            self.connection.commit()
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to create table: {e}")
    
    def _row_to_task(self, row: tuple) -> Task:
        """
        Convert database row tuple to Task object.
        
        Args:
            row: Tuple from database (id, title, description, priority, category, completed, created_at, updated_at)
            
        Returns:
            Task instance
            
        Raises:
            DatabaseError: If conversion fails
        """
        try:
            task_id, title, description, priority, category, completed, created_at, updated_at = row
            
            return Task(
                id=task_id,
                title=title,
                description=description,
                priority=priority,
                category=category,
                completed=bool(completed),
                created_at=datetime.fromisoformat(created_at),
                updated_at=datetime.fromisoformat(updated_at)
            )
        except (ValidationError, ValueError) as e:
            raise DatabaseError(f"Failed to convert row to Task: {e}")
    
    def create_task(
        self,
        title: str,
        description: str,
        priority: str,
        category: str
    ) -> Task:
        """
        Create and insert a new task.
        
        Args:
            title: Task title
            description: Task description
            priority: Priority level (Low, Medium, High)
            category: Task category
            
        Returns:
            Created Task object with auto-generated id
            
        Raises:
            DatabaseError: If insertion fails
            ValidationError: If data is invalid
        """
        if self.connection is None:
            raise DatabaseError("Database not connected")
        
        try:
            # Validate all fields before insertion
            if not isinstance(title, str) or not title.strip():
                raise ValidationError("Title must be a non-empty string")
            
            if not isinstance(description, str):
                raise ValidationError("Description must be a string")
            
            # Validate priority
            if priority not in VALID_PRIORITIES:
                raise ValidationError(f"Invalid priority: {priority}")
            
            if not isinstance(category, str) or not category.strip():
                raise ValidationError("Category must be a non-empty string")
            
            now = datetime.now().isoformat()
            
            cursor = self.connection.cursor()
            cursor.execute(
                """
                INSERT INTO tasks (title, description, priority, category, completed, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (title, description, priority, category, False, now, now)
            )
            self.connection.commit()
            
            task_id = cursor.lastrowid
            
            # Return the created task
            return self.get_task(task_id)
        except sqlite3.IntegrityError as e:
            raise DatabaseError(f"Failed to create task (integrity error): {e}")
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to create task: {e}")
    
    def get_task(self, task_id: int) -> Task:
        """
        Retrieve a single task by ID.
        
        Args:
            task_id: ID of the task to retrieve
            
        Returns:
            Task object
            
        Raises:
            DatabaseError: If task not found or query fails
        """
        if self.connection is None:
            raise DatabaseError("Database not connected")
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            
            if row is None:
                raise DatabaseError(f"Task {task_id} not found")
            
            return self._row_to_task(row)
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to get task: {e}")
    
    def list_tasks(self) -> List[Task]:
        """
        Retrieve all tasks.
        
        Returns:
            List of Task objects
            
        Raises:
            DatabaseError: If query fails
        """
        if self.connection is None:
            raise DatabaseError("Database not connected")
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
            rows = cursor.fetchall()
            
            return [self._row_to_task(row) for row in rows]
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to list tasks: {e}")
    
    def list_by_category(self, category: str) -> List[Task]:
        """
        Retrieve all tasks in a specific category.
        
        Args:
            category: Category to filter by
            
        Returns:
            List of Task objects matching the category
            
        Raises:
            DatabaseError: If query fails
        """
        if self.connection is None:
            raise DatabaseError("Database not connected")
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT * FROM tasks WHERE category = ? ORDER BY created_at DESC",
                (category,)
            )
            rows = cursor.fetchall()
            
            return [self._row_to_task(row) for row in rows]
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to list tasks by category: {e}")
    
    def list_by_priority(self, priority: str) -> List[Task]:
        """
        Retrieve all tasks with a specific priority level.
        
        Args:
            priority: Priority level to filter by (Low, Medium, High)
            
        Returns:
            List of Task objects matching the priority
            
        Raises:
            DatabaseError: If priority is invalid or query fails
            ValidationError: If priority is invalid
        """
        if self.connection is None:
            raise DatabaseError("Database not connected")
        
        if priority not in VALID_PRIORITIES:
            raise ValidationError(f"Invalid priority: {priority}")
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT * FROM tasks WHERE priority = ? ORDER BY created_at DESC",
                (priority,)
            )
            rows = cursor.fetchall()
            
            return [self._row_to_task(row) for row in rows]
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to list tasks by priority: {e}")
    
    def update_task(self, task_id: int, **updates) -> Task:
        """
        Update a task with new values.
        
        Args:
            task_id: ID of the task to update
            **updates: Fields to update (title, description, priority, category, completed)
            
        Returns:
            Updated Task object
            
        Raises:
            DatabaseError: If task not found or update fails
            ValidationError: If update data is invalid
        """
        if self.connection is None:
            raise DatabaseError("Database not connected")
        
        # Get the current task to validate
        current_task = self.get_task(task_id)
        
        # Prepare update data
        allowed_fields = {'title', 'description', 'priority', 'category', 'completed'}
        update_data = {k: v for k, v in updates.items() if k in allowed_fields}
        
        if not update_data:
            return current_task
        
        # Validate priority if being updated
        if 'priority' in update_data:
            if update_data['priority'] not in VALID_PRIORITIES:
                raise ValidationError(f"Invalid priority: {update_data['priority']}")
        
        # Add updated_at timestamp
        update_data['updated_at'] = datetime.now().isoformat()
        
        try:
            # Build the UPDATE statement
            set_clause = ", ".join([f"{k} = ?" for k in update_data.keys()])
            values = list(update_data.values()) + [task_id]
            
            cursor = self.connection.cursor()
            cursor.execute(
                f"UPDATE tasks SET {set_clause} WHERE id = ?",
                values
            )
            
            if cursor.rowcount == 0:
                raise DatabaseError(f"Task {task_id} not found")
            
            self.connection.commit()
            
            # Return the updated task
            return self.get_task(task_id)
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to update task: {e}")
    
    def delete_task(self, task_id: int) -> None:
        """
        Delete a task by ID.
        
        Args:
            task_id: ID of the task to delete
            
        Raises:
            DatabaseError: If task not found or deletion fails
        """
        if self.connection is None:
            raise DatabaseError("Database not connected")
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            
            if cursor.rowcount == 0:
                raise DatabaseError(f"Task {task_id} not found")
            
            self.connection.commit()
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to delete task: {e}")
    
    def close(self) -> None:
        """
        Close the database connection.
        
        Should be called when done with the database.
        """
        if self.connection:
            try:
                self.connection.close()
            except sqlite3.Error as e:
                raise DatabaseError(f"Failed to close database: {e}")
            finally:
                self.connection = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
