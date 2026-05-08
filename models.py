"""
Data models and validation for the Todo Manager CLI.

This module provides the Task dataclass with validation and serialization methods.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, Literal
import json


# Type aliases for valid enums
PriorityType = Literal["Low", "Medium", "High"]
VALID_PRIORITIES = {"Low", "Medium", "High"}


class ValidationError(ValueError):
    """Raised when Task validation fails."""
    pass


@dataclass
class Task:
    """
    Represents a single task in the todo manager.
    
    Attributes:
        id: Unique identifier for the task
        title: Short task title
        description: Detailed task description
        priority: Task priority level (Low, Medium, High)
        category: Task category for grouping
        completed: Whether the task is marked complete
        created_at: Timestamp when task was created
        updated_at: Timestamp of last update
    """
    
    id: int
    title: str
    description: str
    priority: PriorityType
    category: str
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self) -> None:
        """Validate task fields after initialization."""
        self._validate()
    
    def _validate(self) -> None:
        """
        Validate task fields.
        
        Raises:
            ValidationError: If any field is invalid
        """
        # Validate title
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValidationError("Title must be a non-empty string")
        
        # Validate description
        if not isinstance(self.description, str):
            raise ValidationError("Description must be a string")
        
        # Validate priority
        if self.priority not in VALID_PRIORITIES:
            raise ValidationError(
                f"Priority must be one of {VALID_PRIORITIES}, got '{self.priority}'"
            )
        
        # Validate category
        if not isinstance(self.category, str) or not self.category.strip():
            raise ValidationError("Category must be a non-empty string")
        
        # Validate completed flag
        if not isinstance(self.completed, bool):
            raise ValidationError("Completed must be a boolean")
        
        # Validate timestamps
        if not isinstance(self.created_at, datetime):
            raise ValidationError("created_at must be a datetime object")
        
        if not isinstance(self.updated_at, datetime):
            raise ValidationError("updated_at must be a datetime object")
    
    def to_dict(self) -> dict:
        """
        Convert task to dictionary representation.
        
        Returns:
            Dictionary with all task fields (timestamps as ISO format strings)
        """
        data = asdict(self)
        # Convert datetime objects to ISO format strings
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        """
        Create a Task from dictionary representation.
        
        Args:
            data: Dictionary with task fields
            
        Returns:
            Task instance
            
        Raises:
            ValidationError: If data is invalid
        """
        try:
            # Create a copy to avoid modifying the original
            task_data = data.copy()
            
            # Convert timestamp strings to datetime if needed
            if isinstance(task_data.get('created_at'), str):
                task_data['created_at'] = datetime.fromisoformat(task_data['created_at'])
            
            if isinstance(task_data.get('updated_at'), str):
                task_data['updated_at'] = datetime.fromisoformat(task_data['updated_at'])
            
            return cls(**task_data)
        except TypeError as e:
            raise ValidationError(f"Invalid task data: {e}")
    
    def to_json(self) -> str:
        """
        Convert task to JSON string.
        
        Returns:
            JSON representation of the task
        """
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Task':
        """
        Create a Task from JSON string.
        
        Args:
            json_str: JSON string representation
            
        Returns:
            Task instance
            
        Raises:
            ValidationError: If JSON is invalid or data is invalid
        """
        try:
            data = json.loads(json_str)
            return cls.from_dict(data)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON: {e}")
