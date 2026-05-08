"""
Pytest configuration and shared fixtures for Todo Manager CLI tests.

This module provides:
- Temporary database fixture for isolated test runs
- Test data fixtures with various task scenarios
- Temporary file paths for export testing
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta


@pytest.fixture
def temp_db_path():
    """
    Provide a temporary database path that is cleaned up after each test.
    
    Yields:
        Path: Temporary database file path
    """
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_tasks.db"
    yield db_path
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_csv_path():
    """
    Provide a temporary CSV file path for export testing.
    
    Yields:
        Path: Temporary CSV file path
    """
    temp_dir = tempfile.mkdtemp()
    csv_path = Path(temp_dir) / "export.csv"
    yield csv_path
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_task_data():
    """
    Provide sample task data for testing.
    
    Returns:
        dict: Dictionary with various task data scenarios
    """
    now = datetime.now()
    return {
        "valid_task": {
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "priority": "High",
            "category": "Shopping",
        },
        "another_task": {
            "title": "Complete project",
            "description": "Finish the todo manager CLI",
            "priority": "High",
            "category": "Work",
        },
        "low_priority_task": {
            "title": "Organize desk",
            "description": "Clean and organize workspace",
            "priority": "Low",
            "category": "Personal",
        },
        "medium_priority_task": {
            "title": "Schedule meeting",
            "description": "Book conference room",
            "priority": "Medium",
            "category": "Work",
        },
        "no_description": {
            "title": "Quick task",
            "description": "",
            "priority": "Medium",
            "category": "General",
        },
        "timestamps": {
            "created_at": now,
            "updated_at": now,
        },
    }


@pytest.fixture
def invalid_task_data():
    """
    Provide invalid task data for error testing.
    
    Returns:
        dict: Dictionary with various invalid task data
    """
    return {
        "invalid_priority": {
            "title": "Test",
            "description": "Test",
            "priority": "Critical",  # Invalid priority
            "category": "General",
        },
        "missing_title": {
            "title": "",
            "description": "Test",
            "priority": "High",
            "category": "General",
        },
        "missing_priority": {
            "title": "Test",
            "description": "Test",
            "category": "General",
        },
        "missing_category": {
            "title": "Test",
            "description": "Test",
            "priority": "High",
        },
    }


@pytest.fixture
def many_tasks():
    """
    Provide a larger set of tasks for testing list operations and filtering.
    
    Returns:
        list: List of task dictionaries
    """
    categories = ["Work", "Personal", "Shopping", "Health"]
    priorities = ["Low", "Medium", "High"]
    tasks = []
    
    for i in range(20):
        tasks.append({
            "title": f"Task {i+1}",
            "description": f"Description for task {i+1}",
            "priority": priorities[i % 3],
            "category": categories[i % 4],
        })
    
    return tasks


@pytest.fixture
def mock_database():
    """
    Provide a mock database interface for CLI testing.
    
    This is a placeholder for use in test_cli.py with mocking.
    """
    class MockDatabase:
        def __init__(self):
            self.tasks = {}
            self.next_id = 1
        
        def create_task(self, title, description, priority, category):
            """Mock create_task implementation"""
            pass
        
        def get_task(self, task_id):
            """Mock get_task implementation"""
            pass
        
        def list_tasks(self):
            """Mock list_tasks implementation"""
            pass
        
        def list_by_category(self, category):
            """Mock list_by_category implementation"""
            pass
        
        def list_by_priority(self, priority):
            """Mock list_by_priority implementation"""
            pass
        
        def update_task(self, task_id, **updates):
            """Mock update_task implementation"""
            pass
        
        def delete_task(self, task_id):
            """Mock delete_task implementation"""
            pass
    
    return MockDatabase()
