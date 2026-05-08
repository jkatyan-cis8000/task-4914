"""
CSV export functionality for the Todo Manager CLI.

This module provides the CSVExporter class for exporting Task objects to CSV format.
"""

import csv
from pathlib import Path
from typing import List, Optional
from models import Task


class ExportError(Exception):
    """Raised when export operations fail."""
    pass


class CSVExporter:
    """
    Handles exporting tasks to CSV files.
    
    This class provides methods to export Task objects to CSV format with proper
    formatting, escaping, and error handling.
    """
    
    # CSV column headers matching the Task dataclass fields
    CSV_HEADERS = [
        'id',
        'title',
        'description',
        'priority',
        'category',
        'completed',
        'created_at',
        'updated_at'
    ]
    
    def __init__(self, output_path: str) -> None:
        """
        Initialize the CSV exporter.
        
        Args:
            output_path: Path where CSV file will be written (absolute or relative)
            
        Raises:
            ExportError: If output path is invalid or not writable
        """
        self.output_path = Path(output_path)
        
        # Validate that the parent directory exists or can be created
        try:
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            raise ExportError(
                f"Cannot write to {self.output_path}: {e}"
            )
    
    def export_tasks(self, tasks: List[Task]) -> tuple[bool, str]:
        """
        Export a list of tasks to CSV format.
        
        Args:
            tasks: List of Task objects to export
            
        Returns:
            Tuple of (success: bool, message: str)
            - success: True if export completed successfully
            - message: Human-readable status message
            
        Raises:
            ExportError: If file write fails after validation
        """
        if not tasks:
            # Write empty CSV with just headers
            try:
                with open(self.output_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=self.CSV_HEADERS)
                    writer.writeheader()
                return True, f"Exported 0 tasks to {self.output_path}"
            except (OSError, PermissionError) as e:
                raise ExportError(f"Failed to write CSV file: {e}")
        
        try:
            with open(self.output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.CSV_HEADERS)
                writer.writeheader()
                
                for task in tasks:
                    # Convert task to dictionary and write row
                    row = self._task_to_csv_row(task)
                    writer.writerow(row)
            
            return True, f"Successfully exported {len(tasks)} tasks to {self.output_path}"
            
        except (OSError, PermissionError) as e:
            raise ExportError(f"Failed to write CSV file: {e}")
        except Exception as e:
            raise ExportError(f"Unexpected error during export: {e}")
    
    def export_by_category(self, tasks: List[Task], category: str) -> tuple[bool, str]:
        """
        Export tasks filtered by category to CSV format.
        
        Args:
            tasks: List of Task objects to filter and export
            category: Category to filter by (case-sensitive)
            
        Returns:
            Tuple of (success: bool, message: str)
            - success: True if export completed successfully
            - message: Human-readable status message with count
            
        Raises:
            ExportError: If file write fails
        """
        # Filter tasks by category
        filtered_tasks = [task for task in tasks if task.category == category]
        
        if not filtered_tasks:
            message = (
                f"No tasks found in category '{category}'. "
                f"Exported empty file to {self.output_path}"
            )
        else:
            message = (
                f"Successfully exported {len(filtered_tasks)} tasks from category "
                f"'{category}' to {self.output_path}"
            )
        
        # Use the main export method to write the filtered list
        success, _ = self.export_tasks(filtered_tasks)
        
        return success, message
    
    def _task_to_csv_row(self, task: Task) -> dict:
        """
        Convert a Task object to a CSV row dictionary.
        
        Args:
            task: Task object to convert
            
        Returns:
            Dictionary with CSV headers as keys and task data as values
        """
        return {
            'id': str(task.id),
            'title': task.title,
            'description': task.description,
            'priority': task.priority,
            'category': task.category,
            'completed': 'Yes' if task.completed else 'No',
            'created_at': task.created_at.isoformat(),
            'updated_at': task.updated_at.isoformat()
        }
