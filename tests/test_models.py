"""
Tests for models.py - Task dataclass and validation.

Test coverage:
- Task dataclass instantiation
- Task field validation (priority, category)
- Task serialization (to_dict, from_dict)
- Timestamp handling
- Error cases (invalid priority, missing required fields)
"""

import pytest
import json
from datetime import datetime
from models import Task, ValidationError, VALID_PRIORITIES


class TestTaskInstantiation:
    """Test Task dataclass creation and field initialization."""
    
    def test_create_task_with_all_fields(self, sample_task_data):
        """Test creating a Task with all fields populated."""
        task_data = sample_task_data["valid_task"]
        task = Task(
            id=1,
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        assert task.id == 1
        assert task.title == task_data["title"]
        assert task.description == task_data["description"]
        assert task.priority == task_data["priority"]
        assert task.category == task_data["category"]
    
    def test_create_task_with_defaults(self, sample_task_data):
        """Test creating a Task with default values."""
        task_data = sample_task_data["valid_task"]
        task = Task(
            id=1,
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        assert task.completed is False
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)
    
    def test_task_has_required_fields(self, sample_task_data):
        """Test that Task has all required fields."""
        task_data = sample_task_data["valid_task"]
        task = Task(
            id=1,
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        assert hasattr(task, 'id')
        assert hasattr(task, 'title')
        assert hasattr(task, 'description')
        assert hasattr(task, 'priority')
        assert hasattr(task, 'category')
        assert hasattr(task, 'completed')
        assert hasattr(task, 'created_at')
        assert hasattr(task, 'updated_at')


class TestTaskValidation:
    """Test Task validation logic."""
    
    def test_valid_priority_high(self, sample_task_data):
        """Test that 'High' is a valid priority."""
        task_data = sample_task_data["valid_task"]
        task = Task(
            id=1,
            title=task_data["title"],
            description=task_data["description"],
            priority="High",
            category=task_data["category"]
        )
        assert task.priority == "High"
    
    def test_valid_priority_medium(self, sample_task_data):
        """Test that 'Medium' is a valid priority."""
        task_data = sample_task_data["valid_task"]
        task = Task(
            id=1,
            title=task_data["title"],
            description=task_data["description"],
            priority="Medium",
            category=task_data["category"]
        )
        assert task.priority == "Medium"
    
    def test_valid_priority_low(self, sample_task_data):
        """Test that 'Low' is a valid priority."""
        task_data = sample_task_data["valid_task"]
        task = Task(
            id=1,
            title=task_data["title"],
            description=task_data["description"],
            priority="Low",
            category=task_data["category"]
        )
        assert task.priority == "Low"
    
    def test_invalid_priority_raises_error(self, sample_task_data):
        """Test that invalid priority raises ValueError."""
        task_data = sample_task_data["valid_task"]
        with pytest.raises(ValidationError):
            Task(
                id=1,
                title=task_data["title"],
                description=task_data["description"],
                priority="Critical",
                category=task_data["category"]
            )
    
    def test_empty_title_raises_error(self, sample_task_data):
        """Test that empty title is rejected."""
        task_data = sample_task_data["valid_task"]
        with pytest.raises(ValidationError):
            Task(
                id=1,
                title="",
                description=task_data["description"],
                priority=task_data["priority"],
                category=task_data["category"]
            )
    
    def test_missing_category_raises_error(self, sample_task_data):
        """Test that missing category is rejected."""
        task_data = sample_task_data["valid_task"]
        with pytest.raises(ValidationError):
            Task(
                id=1,
                title=task_data["title"],
                description=task_data["description"],
                priority=task_data["priority"],
                category=""
            )
    
    def test_case_sensitive_priority(self, sample_task_data):
        """Test priority validation is case-sensitive."""
        task_data = sample_task_data["valid_task"]
        with pytest.raises(ValidationError):
            Task(
                id=1,
                title=task_data["title"],
                description=task_data["description"],
                priority="high",  # lowercase invalid
                category=task_data["category"]
            )


class TestTaskSerialization:
    """Test Task to_dict and from_dict methods."""
    
    def test_task_to_dict(self, sample_task_data):
        """Test converting Task to dictionary."""
        task_data = sample_task_data["valid_task"]
        task = Task(
            id=1,
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        result = task.to_dict()
        assert isinstance(result, dict)
        assert result['id'] == 1
        assert result['title'] == task_data["title"]
    
    def test_task_to_dict_includes_all_fields(self, sample_task_data):
        """Test that to_dict includes all Task fields."""
        task_data = sample_task_data["valid_task"]
        task = Task(
            id=1,
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        result = task.to_dict()
        assert 'id' in result
        assert 'title' in result
        assert 'description' in result
        assert 'priority' in result
        assert 'category' in result
        assert 'completed' in result
        assert 'created_at' in result
        assert 'updated_at' in result
    
    def test_task_from_dict(self, sample_task_data):
        """Test creating Task from dictionary."""
        task_data = sample_task_data["valid_task"]
        data = {
            'id': 1,
            'title': task_data["title"],
            'description': task_data["description"],
            'priority': task_data["priority"],
            'category': task_data["category"],
            'completed': False,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        task = Task.from_dict(data)
        assert task.id == 1
        assert task.title == task_data["title"]
    
    def test_task_from_dict_roundtrip(self, sample_task_data):
        """Test that Task survives to_dict and from_dict conversion."""
        task_data = sample_task_data["valid_task"]
        original = Task(
            id=1,
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        as_dict = original.to_dict()
        restored = Task.from_dict(as_dict)
        
        assert restored.id == original.id
        assert restored.title == original.title
        assert restored.description == original.description
        assert restored.priority == original.priority
        assert restored.category == original.category
        assert restored.completed == original.completed
    
    def test_serialization_preserves_timestamps(self, sample_task_data):
        """Test that timestamps are preserved through serialization."""
        task_data = sample_task_data["valid_task"]
        created = datetime(2024, 1, 1, 12, 0, 0)
        updated = datetime(2024, 1, 2, 14, 30, 0)
        
        original = Task(
            id=1,
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"],
            created_at=created,
            updated_at=updated
        )
        as_dict = original.to_dict()
        restored = Task.from_dict(as_dict)
        
        assert restored.created_at == created
        assert restored.updated_at == updated


class TestTaskTimestamps:
    """Test timestamp handling in Task."""
    
    def test_created_at_is_set(self, sample_task_data):
        """Test that created_at is automatically set."""
        task_data = sample_task_data["valid_task"]
        before = datetime.now()
        task = Task(
            id=1,
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        after = datetime.now()
        
        assert before <= task.created_at <= after
    
    def test_updated_at_is_set(self, sample_task_data):
        """Test that updated_at is automatically set."""
        task_data = sample_task_data["valid_task"]
        before = datetime.now()
        task = Task(
            id=1,
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        after = datetime.now()
        
        assert before <= task.updated_at <= after
    
    def test_timestamps_are_datetime_objects(self, sample_task_data):
        """Test that timestamps are datetime objects."""
        task_data = sample_task_data["valid_task"]
        task = Task(
            id=1,
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)


class TestTaskComparison:
    """Test Task comparison and equality."""
    
    def test_tasks_with_same_data_are_equal(self, sample_task_data):
        """Test that Tasks with identical data are equal."""
        task_data = sample_task_data["valid_task"]
        now = datetime.now()
        task1 = Task(
            id=1,
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"],
            created_at=now,
            updated_at=now
        )
        task2 = Task(
            id=1,
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"],
            created_at=now,
            updated_at=now
        )
        assert task1 == task2
    
    def test_tasks_with_different_id_are_not_equal(self, sample_task_data):
        """Test that Tasks with different IDs are not equal."""
        task_data = sample_task_data["valid_task"]
        now = datetime.now()
        task1 = Task(
            id=1,
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"],
            created_at=now,
            updated_at=now
        )
        task2 = Task(
            id=2,
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"],
            created_at=now,
            updated_at=now
        )
        assert task1 != task2


class TestTaskJSONSerialization:
    """Test JSON serialization methods."""
    
    def test_task_to_json(self, sample_task_data):
        """Test converting Task to JSON string."""
        task_data = sample_task_data["valid_task"]
        task = Task(
            id=1,
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        json_str = task.to_json()
        assert isinstance(json_str, str)
        # Verify it's valid JSON
        parsed = json.loads(json_str)
        assert parsed['id'] == 1
    
    def test_task_from_json(self, sample_task_data):
        """Test creating Task from JSON string."""
        task_data = sample_task_data["valid_task"]
        original = Task(
            id=1,
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        json_str = original.to_json()
        restored = Task.from_json(json_str)
        
        assert restored.id == original.id
        assert restored.title == original.title
    
    def test_invalid_json_raises_error(self):
        """Test that invalid JSON raises ValidationError."""
        with pytest.raises(ValidationError):
            Task.from_json("invalid json")
    
    def test_json_roundtrip(self, sample_task_data):
        """Test Task JSON roundtrip conversion."""
        task_data = sample_task_data["valid_task"]
        original = Task(
            id=1,
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        json_str = original.to_json()
        restored = Task.from_json(json_str)
        
        assert restored.title == original.title
        assert restored.priority == original.priority
        assert restored.category == original.category
