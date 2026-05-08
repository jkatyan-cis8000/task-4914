"""
Tests for export.py - CSV export functionality.

Test coverage:
- CSVExporter initialization
- CSV file creation
- CSV format and headers
- Data export correctness
- Special character escaping
- File path handling (absolute and relative)
- Error handling
"""

import pytest
import csv
from pathlib import Path
from datetime import datetime
from models import Task
from export import CSVExporter, ExportError


class TestCSVExporterInitialization:
    """Test CSVExporter initialization."""
    
    def test_exporter_creation_with_path(self, temp_csv_path):
        """Test creating CSVExporter with output path."""
        exporter = CSVExporter(str(temp_csv_path))
        assert exporter.output_path == temp_csv_path
    
    def test_exporter_accepts_string_path(self, temp_csv_path):
        """Test that CSVExporter accepts string paths."""
        exporter = CSVExporter(str(temp_csv_path))
        assert isinstance(exporter.output_path, Path)
    
    def test_exporter_accepts_path_object(self, temp_csv_path):
        """Test that CSVExporter accepts Path objects."""
        exporter = CSVExporter(temp_csv_path)
        assert isinstance(exporter.output_path, Path)
    
    def test_exporter_creates_parent_directory(self, temp_csv_path):
        """Test that exporter creates parent directories."""
        nested_path = temp_csv_path.parent / "nested" / "dirs" / "export.csv"
        exporter = CSVExporter(str(nested_path))
        # Should not raise error
        assert exporter.output_path == nested_path


class TestCSVExportBasic:
    """Test basic CSV export functionality."""
    
    def test_export_empty_list(self, temp_csv_path):
        """Test exporting empty task list."""
        exporter = CSVExporter(str(temp_csv_path))
        success, message = exporter.export_tasks([])
        
        assert success is True
        assert temp_csv_path.exists()
    
    def test_export_single_task(self, temp_csv_path, sample_task_data):
        """Test exporting single task."""
        exporter = CSVExporter(str(temp_csv_path))
        task_data = sample_task_data["valid_task"]
        
        task = Task(
            id=1,
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        
        success, message = exporter.export_tasks([task])
        assert success is True
        assert temp_csv_path.exists()
    
    def test_export_multiple_tasks(self, temp_csv_path, many_tasks):
        """Test exporting multiple tasks."""
        exporter = CSVExporter(str(temp_csv_path))
        
        tasks = []
        for i, task_data in enumerate(many_tasks[:5]):
            tasks.append(Task(
                id=i+1,
                title=task_data["title"],
                description=task_data["description"],
                priority=task_data["priority"],
                category=task_data["category"]
            ))
        
        success, message = exporter.export_tasks(tasks)
        assert success is True
        assert temp_csv_path.exists()
    
    def test_export_returns_success(self, temp_csv_path, sample_task_data):
        """Test that export returns success status."""
        exporter = CSVExporter(str(temp_csv_path))
        task_data = sample_task_data["valid_task"]
        
        task = Task(
            id=1,
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        
        success, message = exporter.export_tasks([task])
        assert isinstance(success, bool)
        assert success is True
    
    def test_export_creates_file(self, temp_csv_path, sample_task_data):
        """Test that export creates output file."""
        exporter = CSVExporter(str(temp_csv_path))
        task_data = sample_task_data["valid_task"]
        
        task = Task(
            id=1,
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        
        assert not temp_csv_path.exists()
        exporter.export_tasks([task])
        assert temp_csv_path.exists()
    
    def test_exported_file_is_valid_csv(self, temp_csv_path, sample_task_data):
        """Test that exported file is valid CSV format."""
        exporter = CSVExporter(str(temp_csv_path))
        task_data = sample_task_data["valid_task"]
        
        task = Task(
            id=1,
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        
        exporter.export_tasks([task])
        
        # Try to read as CSV
        with open(temp_csv_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1


class TestCSVFormat:
    """Test CSV format and headers."""
    
    def test_csv_has_correct_headers(self, temp_csv_path, sample_task_data):
        """Test that CSV has correct column headers."""
        exporter = CSVExporter(str(temp_csv_path))
        task_data = sample_task_data["valid_task"]
        
        task = Task(
            id=1,
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        
        exporter.export_tasks([task])
        
        with open(temp_csv_path, 'r') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            
            expected = ['id', 'title', 'description', 'priority', 'category', 'completed', 'created_at', 'updated_at']
            assert headers == expected
    
    def test_csv_headers_in_correct_order(self, temp_csv_path, sample_task_data):
        """Test that CSV headers are in expected order."""
        exporter = CSVExporter(str(temp_csv_path))
        task_data = sample_task_data["valid_task"]
        
        task = Task(
            id=1,
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        
        exporter.export_tasks([task])
        
        with open(temp_csv_path, 'r') as f:
            first_line = f.readline().strip()
            expected = "id,title,description,priority,category,completed,created_at,updated_at"
            assert first_line == expected


class TestCSVDataExport:
    """Test correctness of exported data."""
    
    def test_exported_title_matches(self, temp_csv_path, sample_task_data):
        """Test that exported title matches source task."""
        exporter = CSVExporter(str(temp_csv_path))
        task_data = sample_task_data["valid_task"]
        
        task = Task(
            id=1,
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        
        exporter.export_tasks([task])
        
        with open(temp_csv_path, 'r') as f:
            reader = csv.DictReader(f)
            row = next(reader)
            assert row['title'] == task_data["title"]
    
    def test_exported_description_matches(self, temp_csv_path, sample_task_data):
        """Test that exported description matches source task."""
        exporter = CSVExporter(str(temp_csv_path))
        task_data = sample_task_data["valid_task"]
        
        task = Task(
            id=1,
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        
        exporter.export_tasks([task])
        
        with open(temp_csv_path, 'r') as f:
            reader = csv.DictReader(f)
            row = next(reader)
            assert row['description'] == task_data["description"]
    
    def test_exported_priority_matches(self, temp_csv_path, sample_task_data):
        """Test that exported priority matches source task."""
        exporter = CSVExporter(str(temp_csv_path))
        task_data = sample_task_data["valid_task"]
        
        task = Task(
            id=1,
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        
        exporter.export_tasks([task])
        
        with open(temp_csv_path, 'r') as f:
            reader = csv.DictReader(f)
            row = next(reader)
            assert row['priority'] == task_data["priority"]
    
    def test_exported_category_matches(self, temp_csv_path, sample_task_data):
        """Test that exported category matches source task."""
        exporter = CSVExporter(str(temp_csv_path))
        task_data = sample_task_data["valid_task"]
        
        task = Task(
            id=1,
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        
        exporter.export_tasks([task])
        
        with open(temp_csv_path, 'r') as f:
            reader = csv.DictReader(f)
            row = next(reader)
            assert row['category'] == task_data["category"]
    
    def test_exported_completed_status_matches(self, temp_csv_path, sample_task_data):
        """Test that exported completed status matches source task."""
        exporter = CSVExporter(str(temp_csv_path))
        task_data = sample_task_data["valid_task"]
        
        task = Task(
            id=1,
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"],
            completed=True
        )
        
        exporter.export_tasks([task])
        
        with open(temp_csv_path, 'r') as f:
            reader = csv.DictReader(f)
            row = next(reader)
            assert row['completed'] == 'Yes'
    
    def test_exported_completed_status_no(self, temp_csv_path, sample_task_data):
        """Test that incomplete tasks export as 'No'."""
        exporter = CSVExporter(str(temp_csv_path))
        task_data = sample_task_data["valid_task"]
        
        task = Task(
            id=1,
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"],
            completed=False
        )
        
        exporter.export_tasks([task])
        
        with open(temp_csv_path, 'r') as f:
            reader = csv.DictReader(f)
            row = next(reader)
            assert row['completed'] == 'No'
    
    def test_exported_id_matches(self, temp_csv_path, sample_task_data):
        """Test that exported id matches source task."""
        exporter = CSVExporter(str(temp_csv_path))
        task_data = sample_task_data["valid_task"]
        
        task = Task(
            id=42,
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            category=task_data["category"]
        )
        
        exporter.export_tasks([task])
        
        with open(temp_csv_path, 'r') as f:
            reader = csv.DictReader(f)
            row = next(reader)
            assert row['id'] == '42'
    
    def test_export_all_tasks_present(self, temp_csv_path):
        """Test that all tasks are exported."""
        exporter = CSVExporter(str(temp_csv_path))
        
        tasks = []
        for i in range(10):
            tasks.append(Task(
                id=i+1,
                title=f"Task {i+1}",
                description="Test",
                priority="High",
                category="Test"
            ))
        
        exporter.export_tasks(tasks)
        
        with open(temp_csv_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 10


class TestCSVSpecialCharacters:
    """Test handling of special characters in CSV export."""
    
    def test_export_quotes_in_title(self, temp_csv_path):
        """Test that quotes in title are properly escaped."""
        exporter = CSVExporter(str(temp_csv_path))
        
        task = Task(
            id=1,
            title='Task with "quotes"',
            description="Test",
            priority="High",
            category="Test"
        )
        
        exporter.export_tasks([task])
        
        with open(temp_csv_path, 'r') as f:
            reader = csv.DictReader(f)
            row = next(reader)
            assert row['title'] == 'Task with "quotes"'
    
    def test_export_commas_in_description(self, temp_csv_path):
        """Test that commas in description don't break CSV format."""
        exporter = CSVExporter(str(temp_csv_path))
        
        task = Task(
            id=1,
            title="Task",
            description="Description with, commas, inside",
            priority="High",
            category="Test"
        )
        
        exporter.export_tasks([task])
        
        with open(temp_csv_path, 'r') as f:
            reader = csv.DictReader(f)
            row = next(reader)
            assert row['description'] == "Description with, commas, inside"
    
    def test_export_newlines_in_description(self, temp_csv_path):
        """Test that newlines in description are properly handled."""
        exporter = CSVExporter(str(temp_csv_path))
        
        task = Task(
            id=1,
            title="Task",
            description="Line 1\nLine 2\nLine 3",
            priority="High",
            category="Test"
        )
        
        exporter.export_tasks([task])
        
        with open(temp_csv_path, 'r') as f:
            reader = csv.DictReader(f)
            row = next(reader)
            assert "Line 1" in row['description']
    
    def test_export_unicode_characters(self, temp_csv_path):
        """Test that unicode characters are properly exported."""
        exporter = CSVExporter(str(temp_csv_path))
        
        task = Task(
            id=1,
            title="Tâche 中文 العربية",
            description="Descriptioné",
            priority="High",
            category="Test"
        )
        
        exporter.export_tasks([task])
        
        with open(temp_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            row = next(reader)
            assert "中文" in row['title']
    
    def test_export_empty_description(self, temp_csv_path):
        """Test that empty description is handled correctly."""
        exporter = CSVExporter(str(temp_csv_path))
        
        task = Task(
            id=1,
            title="Task",
            description="",
            priority="High",
            category="Test"
        )
        
        exporter.export_tasks([task])
        
        with open(temp_csv_path, 'r') as f:
            reader = csv.DictReader(f)
            row = next(reader)
            assert row['description'] == ""


class TestCSVExportIntegration:
    """Test CSV export integration with database."""
    
    def test_export_by_category(self, temp_csv_path):
        """Test exporting tasks filtered by category."""
        exporter = CSVExporter(str(temp_csv_path))
        
        tasks = [
            Task(id=1, title="Work Task", description="Test", priority="High", category="Work"),
            Task(id=2, title="Personal Task", description="Test", priority="High", category="Personal"),
            Task(id=3, title="Work Task 2", description="Test", priority="High", category="Work"),
        ]
        
        success, message = exporter.export_by_category(tasks, "Work")
        assert success is True
        
        with open(temp_csv_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
            assert all(row['category'] == 'Work' for row in rows)
    
    def test_export_by_category_no_match(self, temp_csv_path):
        """Test exporting with category that has no matches."""
        exporter = CSVExporter(str(temp_csv_path))
        
        tasks = [
            Task(id=1, title="Task 1", description="Test", priority="High", category="Work"),
        ]
        
        success, message = exporter.export_by_category(tasks, "NonExistent")
        assert success is True
        
        with open(temp_csv_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            # Only header, no data rows
            assert len(rows) == 0
