"""
Tests for database.py - SQLite database abstraction layer.

Test coverage:
- Database connection and initialization
- Table creation and schema
- CRUD operations (create, read, update, delete)
- Filtering by category and priority
- Error handling
- Data persistence
"""

import pytest
import sqlite3
from datetime import datetime
from pathlib import Path
from database import Database, DatabaseError
from models import Task, ValidationError


class TestDatabaseConnection:
    """Test database connection and initialization."""
    
    def test_database_creates_file(self, temp_db_path):
        """Test that Database creates a new database file."""
        assert not temp_db_path.exists()
        db = Database(str(temp_db_path))
        assert temp_db_path.exists()
        db.close()
    
    def test_database_opens_existing_file(self, temp_db_path):
        """Test that Database can open an existing database file."""
        # Create database
        db1 = Database(str(temp_db_path))
        db1.close()
        
        # Open existing database
        db2 = Database(str(temp_db_path))
        assert db2.connection is not None
        db2.close()
    
    def test_database_initializes_table(self, temp_db_path):
        """Test that Database creates tasks table on initialization."""
        db = Database(str(temp_db_path))
        
        # Check that table exists
        cursor = db.connection.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'"
        )
        table = cursor.fetchone()
        assert table is not None
        db.close()
    
    def test_database_path_parameter(self, temp_db_path):
        """Test that Database accepts custom path parameter."""
        db = Database(str(temp_db_path))
        assert db.db_path == str(temp_db_path)
        db.close()
    
    def test_database_default_path(self):
        """Test that Database uses default path when none provided."""
        db = Database()
        expected_default = str(
            Path.home() / ".local" / "share" / "todo_manager" / "tasks.db"
        )
        assert db.db_path == expected_default
        db.close()
    
    def test_database_creates_parent_directories(self, temp_db_path):
        """Test that Database creates parent directories."""
        nested_path = temp_db_path.parent / "nested" / "dirs" / "db.sqlite"
        db = Database(str(nested_path))
        assert nested_path.exists()
        db.close()


class TestCreateTask:
    """Test create_task operation."""
    
    def test_create_task_basic(self, temp_db_path, sample_task_data):
        """Test creating a basic task."""
        db = Database(str(temp_db_path))
        task_data = sample_task_data["valid_task"]
        
        task = db.create_task(
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        
        assert isinstance(task, Task)
        assert task.title == task_data["title"]
        db.close()
    
    def test_create_task_returns_task_object(self, temp_db_path, sample_task_data):
        """Test that create_task returns a Task object."""
        db = Database(str(temp_db_path))
        task_data = sample_task_data["valid_task"]
        
        result = db.create_task(
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        
        assert isinstance(result, Task)
        db.close()
    
    def test_create_task_assigns_id(self, temp_db_path, sample_task_data):
        """Test that created task has an ID."""
        db = Database(str(temp_db_path))
        task_data = sample_task_data["valid_task"]
        
        task = db.create_task(
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        
        assert task.id is not None
        assert isinstance(task.id, int)
        assert task.id > 0
        db.close()
    
    def test_create_multiple_tasks(self, temp_db_path, sample_task_data):
        """Test creating multiple tasks."""
        db = Database(str(temp_db_path))
        
        task1 = db.create_task(
            title="Task 1",
            description="First task",
            priority="High",
            category="Work"
        )
        
        task2 = db.create_task(
            title="Task 2",
            description="Second task",
            priority="Low",
            category="Personal"
        )
        
        assert task1.id != task2.id
        assert task1.title == "Task 1"
        assert task2.title == "Task 2"
        db.close()
    
    def test_create_task_with_all_fields(self, temp_db_path, sample_task_data):
        """Test creating task with title, description, priority, and category."""
        db = Database(str(temp_db_path))
        task_data = sample_task_data["valid_task"]
        
        task = db.create_task(
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        
        assert task.title == task_data["title"]
        assert task.description == task_data["description"]
        assert task.priority == task_data["priority"]
        assert task.category == task_data["category"]
        db.close()
    
    def test_create_task_invalid_priority(self, temp_db_path, invalid_task_data):
        """Test that invalid priority is rejected."""
        db = Database(str(temp_db_path))
        
        with pytest.raises(ValidationError):
            db.create_task(
                title="Test",
                description="Test",
                priority="Critical",
                category="General"
            )
        db.close()
    
    def test_create_task_empty_title(self, temp_db_path):
        """Test that empty title is rejected."""
        db = Database(str(temp_db_path))
        
        with pytest.raises(ValidationError):
            db.create_task(
                title="",
                description="Test",
                priority="High",
                category="General"
            )
        db.close()
    
    def test_create_task_sets_completed_false(self, temp_db_path, sample_task_data):
        """Test that new tasks are not completed by default."""
        db = Database(str(temp_db_path))
        task_data = sample_task_data["valid_task"]
        
        task = db.create_task(
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        
        assert task.completed is False
        db.close()


class TestGetTask:
    """Test get_task operation."""
    
    def test_get_task_by_id(self, temp_db_path, sample_task_data):
        """Test retrieving a task by ID."""
        db = Database(str(temp_db_path))
        task_data = sample_task_data["valid_task"]
        
        created = db.create_task(
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        
        retrieved = db.get_task(created.id)
        assert retrieved.id == created.id
        assert retrieved.title == created.title
        db.close()
    
    def test_get_task_returns_task_object(self, temp_db_path, sample_task_data):
        """Test that get_task returns a Task object."""
        db = Database(str(temp_db_path))
        task_data = sample_task_data["valid_task"]
        
        created = db.create_task(
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        
        retrieved = db.get_task(created.id)
        assert isinstance(retrieved, Task)
        db.close()
    
    def test_get_task_nonexistent(self, temp_db_path):
        """Test that getting nonexistent task raises error."""
        db = Database(str(temp_db_path))
        
        with pytest.raises(DatabaseError):
            db.get_task(999)
        db.close()
    
    def test_get_task_preserves_data(self, temp_db_path, sample_task_data):
        """Test that retrieved task has correct data."""
        db = Database(str(temp_db_path))
        task_data = sample_task_data["valid_task"]
        
        created = db.create_task(
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        
        retrieved = db.get_task(created.id)
        assert retrieved.title == task_data["title"]
        assert retrieved.description == task_data["description"]
        assert retrieved.priority == task_data["priority"]
        assert retrieved.category == task_data["category"]
        db.close()


class TestListTasks:
    """Test list_tasks operation."""
    
    def test_list_empty_database(self, temp_db_path):
        """Test listing tasks in empty database."""
        db = Database(str(temp_db_path))
        tasks = db.list_tasks()
        assert tasks == []
        db.close()
    
    def test_list_single_task(self, temp_db_path, sample_task_data):
        """Test listing database with one task."""
        db = Database(str(temp_db_path))
        task_data = sample_task_data["valid_task"]
        
        created = db.create_task(
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        
        tasks = db.list_tasks()
        assert len(tasks) == 1
        assert tasks[0].id == created.id
        db.close()
    
    def test_list_multiple_tasks(self, temp_db_path, many_tasks):
        """Test listing database with multiple tasks."""
        db = Database(str(temp_db_path))
        
        for task_data in many_tasks:
            db.create_task(
                title=task_data["title"],
                description=task_data["description"],
                priority=task_data["priority"],
                category=task_data["category"]
            )
        
        tasks = db.list_tasks()
        assert len(tasks) == len(many_tasks)
        db.close()
    
    def test_list_returns_all_tasks(self, temp_db_path, many_tasks):
        """Test that list_tasks returns all created tasks."""
        db = Database(str(temp_db_path))
        
        for task_data in many_tasks[:5]:
            db.create_task(
                title=task_data["title"],
                description=task_data["description"],
                priority=task_data["priority"],
                category=task_data["category"]
            )
        
        tasks = db.list_tasks()
        assert len(tasks) == 5
        db.close()
    
    def test_list_tasks_returns_task_objects(self, temp_db_path, sample_task_data):
        """Test that list_tasks returns Task objects."""
        db = Database(str(temp_db_path))
        task_data = sample_task_data["valid_task"]
        
        db.create_task(
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        
        tasks = db.list_tasks()
        assert all(isinstance(t, Task) for t in tasks)
        db.close()


class TestListByCategory:
    """Test list_by_category filtering."""
    
    def test_filter_by_category_single_match(self, temp_db_path, many_tasks):
        """Test filtering by category with single match."""
        db = Database(str(temp_db_path))
        
        for task_data in many_tasks:
            db.create_task(
                title=task_data["title"],
                description=task_data["description"],
                priority=task_data["priority"],
                category=task_data["category"]
            )
        
        work_tasks = db.list_by_category("Work")
        assert all(t.category == "Work" for t in work_tasks)
        assert len(work_tasks) > 0
        db.close()
    
    def test_filter_by_category_multiple_matches(self, temp_db_path):
        """Test filtering by category with multiple matches."""
        db = Database(str(temp_db_path))
        
        for i in range(3):
            db.create_task(
                title=f"Work Task {i}",
                description="Work",
                priority="High",
                category="Work"
            )
        
        work_tasks = db.list_by_category("Work")
        assert len(work_tasks) == 3
        assert all(t.category == "Work" for t in work_tasks)
        db.close()
    
    def test_filter_by_category_no_matches(self, temp_db_path, many_tasks):
        """Test filtering by category with no matches."""
        db = Database(str(temp_db_path))
        
        for task_data in many_tasks[:3]:
            db.create_task(
                title=task_data["title"],
                description=task_data["description"],
                priority=task_data["priority"],
                category=task_data["category"]
            )
        
        tasks = db.list_by_category("NonexistentCategory")
        assert tasks == []
        db.close()
    
    def test_filter_by_category_case_sensitive(self, temp_db_path):
        """Test that category filtering is case-sensitive."""
        db = Database(str(temp_db_path))
        
        db.create_task(
            title="Test",
            description="Test",
            priority="High",
            category="Work"
        )
        
        # Should not match lowercase
        tasks = db.list_by_category("work")
        assert tasks == []
        
        # Should match correct case
        tasks = db.list_by_category("Work")
        assert len(tasks) == 1
        db.close()


class TestListByPriority:
    """Test list_by_priority filtering."""
    
    def test_filter_by_priority_high(self, temp_db_path, many_tasks):
        """Test filtering by High priority."""
        db = Database(str(temp_db_path))
        
        for task_data in many_tasks:
            db.create_task(
                title=task_data["title"],
                description=task_data["description"],
                priority=task_data["priority"],
                category=task_data["category"]
            )
        
        high_tasks = db.list_by_priority("High")
        assert all(t.priority == "High" for t in high_tasks)
        assert len(high_tasks) > 0
        db.close()
    
    def test_filter_by_priority_medium(self, temp_db_path):
        """Test filtering by Medium priority."""
        db = Database(str(temp_db_path))
        
        for i in range(3):
            db.create_task(
                title=f"Medium Task {i}",
                description="Test",
                priority="Medium",
                category="Test"
            )
        
        medium_tasks = db.list_by_priority("Medium")
        assert len(medium_tasks) == 3
        db.close()
    
    def test_filter_by_priority_low(self, temp_db_path):
        """Test filtering by Low priority."""
        db = Database(str(temp_db_path))
        
        db.create_task(
            title="Low Task",
            description="Test",
            priority="Low",
            category="Test"
        )
        
        low_tasks = db.list_by_priority("Low")
        assert len(low_tasks) == 1
        assert low_tasks[0].priority == "Low"
        db.close()
    
    def test_filter_by_invalid_priority(self, temp_db_path):
        """Test filtering by invalid priority."""
        db = Database(str(temp_db_path))
        
        with pytest.raises(ValidationError):
            db.list_by_priority("Critical")
        db.close()


class TestUpdateTask:
    """Test update_task operation."""
    
    def test_update_task_title(self, temp_db_path, sample_task_data):
        """Test updating task title."""
        db = Database(str(temp_db_path))
        task_data = sample_task_data["valid_task"]
        
        task = db.create_task(
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        
        updated = db.update_task(task.id, title="New Title")
        assert updated.title == "New Title"
        db.close()
    
    def test_update_task_description(self, temp_db_path, sample_task_data):
        """Test updating task description."""
        db = Database(str(temp_db_path))
        task_data = sample_task_data["valid_task"]
        
        task = db.create_task(
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        
        updated = db.update_task(task.id, description="New description")
        assert updated.description == "New description"
        db.close()
    
    def test_update_task_priority(self, temp_db_path, sample_task_data):
        """Test updating task priority."""
        db = Database(str(temp_db_path))
        task_data = sample_task_data["valid_task"]
        
        task = db.create_task(
            title=task_data["title"],
            description=task_data["description"],
            priority="Low",
            category=task_data["category"]
        )
        
        updated = db.update_task(task.id, priority="High")
        assert updated.priority == "High"
        db.close()
    
    def test_update_task_category(self, temp_db_path, sample_task_data):
        """Test updating task category."""
        db = Database(str(temp_db_path))
        task_data = sample_task_data["valid_task"]
        
        task = db.create_task(
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category="OldCategory"
        )
        
        updated = db.update_task(task.id, category="NewCategory")
        assert updated.category == "NewCategory"
        db.close()
    
    def test_update_task_mark_complete(self, temp_db_path, sample_task_data):
        """Test marking task as complete."""
        db = Database(str(temp_db_path))
        task_data = sample_task_data["valid_task"]
        
        task = db.create_task(
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        
        assert task.completed is False
        updated = db.update_task(task.id, completed=True)
        assert updated.completed is True
        db.close()
    
    def test_update_task_mark_incomplete(self, temp_db_path, sample_task_data):
        """Test marking completed task as incomplete."""
        db = Database(str(temp_db_path))
        task_data = sample_task_data["valid_task"]
        
        task = db.create_task(
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        
        # Mark it complete first
        completed_task = db.update_task(task.id, completed=True)
        assert completed_task.completed is True
        
        # Then mark it incomplete
        updated = db.update_task(task.id, completed=False)
        assert updated.completed is False
        db.close()
    
    def test_update_multiple_fields(self, temp_db_path, sample_task_data):
        """Test updating multiple fields at once."""
        db = Database(str(temp_db_path))
        task_data = sample_task_data["valid_task"]
        
        task = db.create_task(
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        
        updated = db.update_task(
            task.id,
            title="New Title",
            description="New Description",
            priority="High"
        )
        
        assert updated.title == "New Title"
        assert updated.description == "New Description"
        assert updated.priority == "High"
        db.close()
    
    def test_update_nonexistent_task(self, temp_db_path):
        """Test that updating nonexistent task raises error."""
        db = Database(str(temp_db_path))
        
        with pytest.raises(DatabaseError):
            db.update_task(999, title="New Title")
        db.close()
    
    def test_update_task_invalid_priority(self, temp_db_path, sample_task_data):
        """Test that invalid priority in update is rejected."""
        db = Database(str(temp_db_path))
        task_data = sample_task_data["valid_task"]
        
        task = db.create_task(
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        
        with pytest.raises(ValidationError):
            db.update_task(task.id, priority="Critical")
        db.close()
    
    def test_update_changes_updated_at(self, temp_db_path, sample_task_data):
        """Test that updated_at timestamp is changed on update."""
        db = Database(str(temp_db_path))
        task_data = sample_task_data["valid_task"]
        
        task = db.create_task(
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        
        original_updated_at = task.updated_at
        updated = db.update_task(task.id, title="New Title")
        
        assert updated.updated_at > original_updated_at
        db.close()


class TestDeleteTask:
    """Test delete_task operation."""
    
    def test_delete_task(self, temp_db_path, sample_task_data):
        """Test deleting a task."""
        db = Database(str(temp_db_path))
        task_data = sample_task_data["valid_task"]
        
        task = db.create_task(
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        
        db.delete_task(task.id)
        
        with pytest.raises(DatabaseError):
            db.get_task(task.id)
        db.close()
    
    def test_delete_task_removes_from_list(self, temp_db_path, sample_task_data):
        """Test that deleted task is no longer in list."""
        db = Database(str(temp_db_path))
        task_data = sample_task_data["valid_task"]
        
        task = db.create_task(
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        
        db.delete_task(task.id)
        tasks = db.list_tasks()
        
        assert all(t.id != task.id for t in tasks)
        db.close()
    
    def test_delete_nonexistent_task(self, temp_db_path):
        """Test that deleting nonexistent task raises error."""
        db = Database(str(temp_db_path))
        
        with pytest.raises(DatabaseError):
            db.delete_task(999)
        db.close()
    
    def test_delete_multiple_tasks(self, temp_db_path):
        """Test deleting multiple tasks."""
        db = Database(str(temp_db_path))
        
        task1 = db.create_task(
            title="Task 1",
            description="Test",
            priority="High",
            category="Test"
        )
        
        task2 = db.create_task(
            title="Task 2",
            description="Test",
            priority="High",
            category="Test"
        )
        
        db.delete_task(task1.id)
        db.delete_task(task2.id)
        
        tasks = db.list_tasks()
        assert len(tasks) == 0
        db.close()


class TestDatabasePersistence:
    """Test data persistence across database sessions."""
    
    def test_data_persists_after_close_reopen(self, temp_db_path, sample_task_data):
        """Test that data persists when database is closed and reopened."""
        task_data = sample_task_data["valid_task"]
        
        # Create and close
        db1 = Database(str(temp_db_path))
        task = db1.create_task(
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        task_id = task.id
        db1.close()
        
        # Reopen and check
        db2 = Database(str(temp_db_path))
        retrieved = db2.get_task(task_id)
        assert retrieved.title == task_data["title"]
        db2.close()
    
    def test_id_increment_persists(self, temp_db_path):
        """Test that task ID counter persists."""
        # Create two tasks, close, reopen
        db1 = Database(str(temp_db_path))
        task1 = db1.create_task(
            title="Task 1",
            description="Test",
            priority="High",
            category="Test"
        )
        db1.close()
        
        db2 = Database(str(temp_db_path))
        task2 = db2.create_task(
            title="Task 2",
            description="Test",
            priority="High",
            category="Test"
        )
        
        # Second task should have higher ID
        assert task2.id > task1.id
        db2.close()


class TestContextManager:
    """Test database context manager functionality."""
    
    def test_database_context_manager(self, temp_db_path, sample_task_data):
        """Test using database with context manager."""
        task_data = sample_task_data["valid_task"]
        
        with Database(str(temp_db_path)) as db:
            task = db.create_task(
                title=task_data["title"],
                description=task_data["description"],
                priority=task_data["priority"],
                category=task_data["category"]
            )
            assert task.id is not None
        
        # Connection should be closed after context exit
        assert db.connection is None
