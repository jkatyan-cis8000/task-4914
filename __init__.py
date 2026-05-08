"""
Todo Manager CLI - A modular Python CLI todo manager with SQLite persistence.

This package provides a command-line interface for managing tasks with support for
priorities, categories, and CSV export functionality.
"""

__version__ = "1.0.0"
__author__ = "Todo Manager Team"

from models import Task, ValidationError, VALID_PRIORITIES

__all__ = [
    "Task",
    "ValidationError",
    "VALID_PRIORITIES",
]
