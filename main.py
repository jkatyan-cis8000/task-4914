"""
Application entry point for the Todo Manager CLI.

This module initializes the application, handles configuration, and provides
the main entry point for the CLI.
"""

import os
import sys
from pathlib import Path
from typing import Optional

import click

from cli import cli as cli_group
from database import Database, DatabaseError


__version__ = '1.0.0'


def ensure_database_dir(db_path: Optional[str] = None) -> str:
    """
    Ensure the database directory exists.
    
    Args:
        db_path: Custom database path or None to use default
        
    Returns:
        Path to the database file
        
    Raises:
        click.ClickException: If directory creation fails
    """
    if db_path is None:
        # Use default location
        data_dir = Path.home() / ".local" / "share" / "todo_manager"
        db_path = str(data_dir / "tasks.db")
    else:
        data_dir = Path(db_path).parent
    
    try:
        data_dir.mkdir(parents=True, exist_ok=True)
    except (OSError, PermissionError) as e:
        raise click.ClickException(
            f"Failed to create database directory {data_dir}: {e}"
        )
    
    return db_path


def validate_database(db_path: str) -> None:
    """
    Validate that the database can be accessed and initialized.
    
    Args:
        db_path: Path to the database file
        
    Raises:
        click.ClickException: If database validation fails
    """
    try:
        db = Database(db_path)
        db.close()
    except DatabaseError as e:
        raise click.ClickException(
            f"Failed to initialize database: {e}"
        )


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name='todo')
@click.option(
    '--db-path',
    envvar='TODO_DB_PATH',
    default=None,
    help='Path to SQLite database file (default: ~/.local/share/todo_manager/tasks.db). '
         'Can also set TODO_DB_PATH environment variable.'
)
@click.pass_context
def main(ctx: click.Context, db_path: Optional[str]) -> None:
    """
    Todo Manager CLI - A simple command-line todo list manager.
    
    Manage your tasks with priorities, categories, filtering, and CSV export.
    
    Examples:
    \b
      todo add --title "Buy groceries" --category Personal
      todo list --category Work
      todo complete 1
      todo export --output tasks.csv
    
    Use 'todo COMMAND --help' for command-specific help.
    """
    # Ensure database directory exists
    db_path = ensure_database_dir(db_path)
    
    # Validate database initialization
    validate_database(db_path)
    
    # Store db_path in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj['db_path'] = db_path
    
    # If no subcommand provided, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# Copy all commands from cli_group to main
for name, cmd in cli_group.commands.items():
    main.add_command(cmd, name)


if __name__ == '__main__':
    main()
