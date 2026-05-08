"""
Command-line interface for the Todo Manager CLI using Click framework.

This module provides all CLI commands for managing tasks: add, list, view, complete, delete, and export.
"""

import click
from typing import Optional
from datetime import datetime
from database import Database, DatabaseError
from export import CSVExporter, ExportError
from models import ValidationError, VALID_PRIORITIES


# Custom formatting for CLI output
class TaskFormatter:
    """Helper class for formatting task output."""
    
    PRIORITY_COLORS = {
        'Low': 'green',
        'Medium': 'yellow',
        'High': 'red'
    }
    
    @staticmethod
    def format_task_list(tasks, compact: bool = False) -> str:
        """Format a list of tasks for display."""
        if not tasks:
            return "No tasks found."
        
        if compact:
            lines = []
            for task in tasks:
                status = "✓" if task.completed else "○"
                priority_color = TaskFormatter.PRIORITY_COLORS.get(task.priority, 'white')
                line = f"{status} [{task.id}] {task.title}"
                if task.completed:
                    line = click.style(line, dim=True)
                lines.append(line)
            return "\n".join(lines)
        
        else:
            lines = []
            for task in tasks:
                status = "DONE" if task.completed else "TODO"
                priority_color = TaskFormatter.PRIORITY_COLORS.get(task.priority, 'white')
                
                lines.append(f"\n{click.style('─' * 60, dim=True)}")
                lines.append(f"ID: {task.id} | Status: {click.style(status, fg='green' if task.completed else 'red')} | Priority: {click.style(task.priority, fg=priority_color)}")
                lines.append(f"Title: {task.title}")
                lines.append(f"Category: {task.category}")
                if task.description:
                    lines.append(f"Description: {task.description}")
                lines.append(f"Created: {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
            lines.append(f"\n{click.style('─' * 60, dim=True)}")
            lines.append(f"Total: {len(tasks)} task(s)")
            return "\n".join(lines)
    
    @staticmethod
    def format_single_task(task) -> str:
        """Format a single task for detailed display."""
        lines = [
            f"\n{click.style('Task Details', bold=True)}",
            f"{click.style('─' * 40, dim=True)}",
            f"ID:          {task.id}",
            f"Title:       {task.title}",
            f"Description: {task.description or '(none)'}",
            f"Priority:    {click.style(task.priority, fg=TaskFormatter.PRIORITY_COLORS.get(task.priority, 'white'))}",
            f"Category:    {task.category}",
            f"Status:      {click.style('DONE ✓' if task.completed else 'TODO', fg='green' if task.completed else 'yellow')}",
            f"Created:     {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Updated:     {task.updated_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"{click.style('─' * 40, dim=True)}\n",
        ]
        return "\n".join(lines)


@click.group()
@click.version_option(version='1.0.0', prog_name='todo')
@click.pass_context
def cli(ctx):
    """
    Todo Manager - A simple command-line todo list manager.
    
    Manage your tasks with priorities, categories, and CSV export.
    """
    # Ensure context object exists for passing database
    ctx.ensure_object(dict)


@cli.command()
@click.option('--title', prompt='Task title', help='Short description of the task')
@click.option('--description', default='', help='Detailed description of the task')
@click.option('--priority', 
              type=click.Choice(['Low', 'Medium', 'High'], case_sensitive=True),
              default='Medium',
              help='Task priority level')
@click.option('--category', 
              prompt='Category',
              help='Task category for grouping')
@click.pass_context
def add(ctx, title: str, description: str, priority: str, category: str):
    """
    Add a new task to the todo list.
    
    You will be prompted for title and category. Use --description and --priority for other fields.
    """
    try:
        db = Database()
        task = db.create_task(title, description, priority, category)
        db.close()
        
        click.echo(f"\n{click.style('✓ Task created successfully!', fg='green', bold=True)}")
        click.echo(TaskFormatter.format_single_task(task))
        
    except (DatabaseError, ValidationError) as e:
        click.echo(f"\n{click.style(f'✗ Error: {e}', fg='red', bold=True)}", err=True)
        raise SystemExit(1)


@cli.command()
@click.option('--category', default=None, help='Filter tasks by category')
@click.option('--priority', 
              type=click.Choice(['Low', 'Medium', 'High'], case_sensitive=True),
              default=None,
              help='Filter tasks by priority')
@click.option('--compact', is_flag=True, help='Show compact list format')
@click.option('--completed', is_flag=True, help='Show only completed tasks')
def list(category: Optional[str], priority: Optional[str], compact: bool, completed: bool):
    """
    List all tasks or filter by category/priority.
    
    Examples:
    \b
      todo list                    # Show all tasks
      todo list --category Work    # Show tasks in Work category
      todo list --priority High    # Show high priority tasks
      todo list --compact          # Show compact format
      todo list --completed        # Show only completed tasks
    """
    try:
        db = Database()
        
        # Get tasks based on filters
        if category:
            tasks = db.list_by_category(category)
        elif priority:
            tasks = db.list_by_priority(priority)
        else:
            tasks = db.list_tasks()
        
        # Filter by completion status if requested
        if completed:
            tasks = [t for t in tasks if t.completed]
        
        db.close()
        
        if not tasks:
            click.echo(f"\n{click.style('No tasks found.', fg='yellow')}")
        else:
            click.echo(TaskFormatter.format_task_list(tasks, compact=compact))
        
    except DatabaseError as e:
        click.echo(f"\n{click.style(f'✗ Error: {e}', fg='red', bold=True)}", err=True)
        raise SystemExit(1)


@cli.command()
@click.argument('task_id', type=int)
def view(task_id: int):
    """
    View detailed information about a specific task.
    
    Example:
    \b
      todo view 1    # View task with ID 1
    """
    try:
        db = Database()
        task = db.get_task(task_id)
        db.close()
        
        click.echo(TaskFormatter.format_single_task(task))
        
    except DatabaseError as e:
        click.echo(f"\n{click.style(f'✗ Error: {e}', fg='red', bold=True)}", err=True)
        raise SystemExit(1)


@cli.command()
@click.argument('task_id', type=int)
def complete(task_id: int):
    """
    Mark a task as completed.
    
    Example:
    \b
      todo complete 1    # Mark task 1 as done
    """
    try:
        db = Database()
        task = db.update_task(task_id, completed=True)
        db.close()
        
        click.echo(f"\n{click.style(f'✓ Task {task_id} marked as completed!', fg='green', bold=True)}")
        click.echo(TaskFormatter.format_single_task(task))
        
    except DatabaseError as e:
        click.echo(f"\n{click.style(f'✗ Error: {e}', fg='red', bold=True)}", err=True)
        raise SystemExit(1)


@cli.command()
@click.argument('task_id', type=int)
@click.confirmation_option(prompt='Are you sure you want to delete this task?')
def delete(task_id: int):
    """
    Delete a task from the todo list.
    
    Example:
    \b
      todo delete 1    # Delete task 1 (with confirmation)
    """
    try:
        db = Database()
        db.delete_task(task_id)
        db.close()
        
        click.echo(f"\n{click.style(f'✓ Task {task_id} deleted successfully!', fg='green', bold=True)}\n")
        
    except DatabaseError as e:
        click.echo(f"\n{click.style(f'✗ Error: {e}', fg='red', bold=True)}", err=True)
        raise SystemExit(1)


@cli.command()
@click.option('--output', '-o', required=True, help='Output CSV file path')
@click.option('--category', default=None, help='Export only tasks from this category')
def export(output: str, category: Optional[str]):
    """
    Export tasks to CSV file.
    
    Examples:
    \b
      todo export --output tasks.csv                    # Export all tasks
      todo export -o tasks.csv --category Work          # Export Work category only
    """
    try:
        db = Database()
        
        # Get tasks to export
        if category:
            tasks = db.list_by_category(category)
        else:
            tasks = db.list_tasks()
        
        db.close()
        
        # Perform export
        exporter = CSVExporter(output)
        
        if category:
            success, message = exporter.export_by_category(tasks, category)
        else:
            success, message = exporter.export_tasks(tasks)
        
        if success:
            click.echo(f"\n{click.style('✓ ' + message, fg='green', bold=True)}\n")
        else:
            click.echo(f"\n{click.style(f'✗ {message}', fg='red', bold=True)}", err=True)
            raise SystemExit(1)
        
    except (DatabaseError, ExportError) as e:
        click.echo(f"\n{click.style(f'✗ Error: {e}', fg='red', bold=True)}", err=True)
        raise SystemExit(1)


if __name__ == '__main__':
    cli(obj={})
