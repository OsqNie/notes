import click
import json
import sys
from datetime import datetime
from dateutil.parser import parse as parse_date
from typing import Optional

from ..database import Database
from ..models import Task, Note, Package
from .formatters import format_tasks_table, format_notes_table, format_packages_table
from .interactive import start_interactive_mode


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Notes - A dual-interface task and note management application."""
    if ctx.invoked_subcommand is None:
        # No subcommand provided, start interactive mode
        start_interactive_mode()


@cli.group()
def task():
    """Task management commands."""
    pass


@cli.group()
def note():
    """Note management commands."""
    pass


@cli.group()
def package():
    """Package (project) management commands."""
    pass


# Task commands
@task.command()
@click.argument('title')
@click.option('--description', '-d', help='Task description')
@click.option('--due', help='Due date (YYYY-MM-DD, "tomorrow", "next week")')
@click.option('--priority', '-p', type=click.Choice(['low', 'medium', 'high', 'urgent']), 
              default='medium', help='Task priority')
@click.option('--package', help='Package name to assign task to')
@click.option('--tags', help='Comma-separated tags')
def create(title, description, due, priority, package, tags):
    """Create a new task."""
    with Database() as db:
        # Parse due date
        due_date = None
        if due:
            try:
                if due.lower() == 'tomorrow':
                    from datetime import date, timedelta
                    due_date = datetime.combine(date.today() + timedelta(days=1), datetime.min.time())
                elif due.lower() == 'next week':
                    from datetime import date, timedelta
                    due_date = datetime.combine(date.today() + timedelta(weeks=1), datetime.min.time())
                else:
                    due_date = parse_date(due)
            except Exception as e:
                click.echo(f"Error parsing due date: {e}", err=True)
                return

        # Find package ID if package name provided
        package_id = None
        if package:
            packages = db.list_packages()
            matching_packages = [p for p in packages if p.name.lower() == package.lower()]
            if matching_packages:
                package_id = matching_packages[0].id
            else:
                click.echo(f"Package '{package}' not found", err=True)
                return

        # Parse tags
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]

        # Create task
        task_obj = Task(
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            package_id=package_id,
            tags=tag_list
        )

        db.create_task(task_obj)
        click.echo(f"Task created with ID: {task_obj.id}")


@task.command()
@click.option('--status', type=click.Choice(['pending', 'in-progress', 'completed', 'cancelled']),
              help='Filter by status')
@click.option('--priority', type=click.Choice(['low', 'medium', 'high', 'urgent']),
              help='Filter by priority')
@click.option('--package', help='Filter by package name')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json', 'markdown']),
              default='table', help='Output format')
def list(status, priority, package, output_format):
    """List tasks with optional filtering."""
    with Database() as db:
        filters = {}
        if status:
            filters['status'] = status
        if priority:
            filters['priority'] = priority
        
        # Find package ID if package name provided
        if package:
            packages = db.list_packages()
            matching_packages = [p for p in packages if p.name.lower() == package.lower()]
            if matching_packages:
                filters['package_id'] = matching_packages[0].id
            else:
                click.echo(f"Package '{package}' not found", err=True)
                return

        tasks = db.list_tasks(filters)
        
        if output_format == 'json':
            click.echo(json.dumps([task.to_dict() for task in tasks], indent=2))
        elif output_format == 'markdown':
            for task in tasks:
                click.echo(f"## {task.title}")
                click.echo(f"- **Status**: {task.status}")
                click.echo(f"- **Priority**: {task.priority}")
                if task.due_date:
                    click.echo(f"- **Due**: {task.due_date.strftime('%Y-%m-%d')}")
                if task.description:
                    click.echo(f"- **Description**: {task.description}")
                click.echo()
        else:
            format_tasks_table(tasks)


@task.command()
@click.argument('task_id')
@click.option('--title', help='Update task title')
@click.option('--description', help='Update task description')
@click.option('--status', type=click.Choice(['pending', 'in-progress', 'completed', 'cancelled']),
              help='Update task status')
@click.option('--priority', type=click.Choice(['low', 'medium', 'high', 'urgent']),
              help='Update task priority')
@click.option('--due', help='Update due date')
@click.option('--tags', help='Update tags (comma-separated)')
def update(task_id, title, description, status, priority, due, tags):
    """Update an existing task."""
    with Database() as db:
        task_obj = db.get_task(task_id)
        if not task_obj:
            click.echo(f"Task with ID {task_id} not found", err=True)
            return

        # Update fields if provided
        if title:
            task_obj.title = title
        if description is not None:  # Allow empty string
            task_obj.description = description
        if status:
            task_obj.update_status(status)
        if priority:
            task_obj.priority = priority
        if due:
            try:
                if due.lower() == 'tomorrow':
                    from datetime import date, timedelta
                    task_obj.due_date = datetime.combine(date.today() + timedelta(days=1), datetime.min.time())
                elif due.lower() == 'next week':
                    from datetime import date, timedelta
                    task_obj.due_date = datetime.combine(date.today() + timedelta(weeks=1), datetime.min.time())
                else:
                    task_obj.due_date = parse_date(due)
            except Exception as e:
                click.echo(f"Error parsing due date: {e}", err=True)
                return
        if tags is not None:
            task_obj.tags = [tag.strip() for tag in tags.split(',')] if tags else []

        task_obj.updated_at = datetime.now()
        db.update_task(task_obj)
        click.echo(f"Task {task_id} updated successfully")


@task.command()
@click.argument('task_id')
def complete(task_id):
    """Mark a task as completed."""
    with Database() as db:
        task_obj = db.get_task(task_id)
        if not task_obj:
            click.echo(f"Task with ID {task_id} not found", err=True)
            return

        task_obj.mark_completed()
        db.update_task(task_obj)
        click.echo(f"Task '{task_obj.title}' marked as completed")


@task.command()
@click.argument('task_id')
@click.confirmation_option(prompt='Are you sure you want to delete this task?')
def delete(task_id):
    """Delete a task."""
    with Database() as db:
        task_obj = db.get_task(task_id)
        if not task_obj:
            click.echo(f"Task with ID {task_id} not found", err=True)
            return

        if db.delete_task(task_id):
            click.echo(f"Task '{task_obj.title}' deleted successfully")
        else:
            click.echo("Failed to delete task", err=True)


# Note commands
@note.command()
@click.argument('title')
@click.option('--content', '-c', help='Note content')
@click.option('--package', help='Package name to assign note to')
@click.option('--tags', help='Comma-separated tags')
def create(title, content, package, tags):
    """Create a new note."""
    with Database() as db:
        # Find package ID if package name provided
        package_id = None
        if package:
            packages = db.list_packages()
            matching_packages = [p for p in packages if p.name.lower() == package.lower()]
            if matching_packages:
                package_id = matching_packages[0].id
            else:
                click.echo(f"Package '{package}' not found", err=True)
                return

        # Parse tags
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]

        # Create note
        note_obj = Note(
            title=title,
            content=content or '',
            package_id=package_id,
            tags=tag_list
        )

        db.create_note(note_obj)
        click.echo(f"Note created with ID: {note_obj.id}")


@note.command()
@click.option('--package', help='Filter by package name')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json', 'markdown']),
              default='table', help='Output format')
def list(package, output_format):
    """List notes with optional filtering."""
    with Database() as db:
        filters = {}
        
        # Find package ID if package name provided
        if package:
            packages = db.list_packages()
            matching_packages = [p for p in packages if p.name.lower() == package.lower()]
            if matching_packages:
                filters['package_id'] = matching_packages[0].id
            else:
                click.echo(f"Package '{package}' not found", err=True)
                return

        notes = db.list_notes(filters)
        
        if output_format == 'json':
            click.echo(json.dumps([note.to_dict() for note in notes], indent=2))
        elif output_format == 'markdown':
            for note in notes:
                click.echo(f"## {note.title}")
                if note.content:
                    click.echo(note.content)
                click.echo()
        else:
            format_notes_table(notes)


@note.command()
@click.argument('note_id')
def edit(note_id):
    """Edit a note (opens in default editor)."""
    import tempfile
    import os
    
    with Database() as db:
        note_obj = db.get_note(note_id)
        if not note_obj:
            click.echo(f"Note with ID {note_id} not found", err=True)
            return

        # Create temporary file with note content
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.md', delete=False) as f:
            f.write(f"# {note_obj.title}\n\n")
            f.write(note_obj.content)
            temp_file = f.name

        try:
            # Open in default editor
            click.edit(filename=temp_file)
            
            # Read back the content
            with open(temp_file, 'r') as f:
                content = f.read()
            
            # Extract title and content
            lines = content.split('\n')
            if lines[0].startswith('# '):
                note_obj.title = lines[0][2:].strip()
                note_obj.content = '\n'.join(lines[2:]).strip()
            else:
                note_obj.content = content.strip()
            
            note_obj.updated_at = datetime.now()
            db.update_note(note_obj)
            click.echo(f"Note '{note_obj.title}' updated successfully")
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file)


@note.command()
@click.argument('note_id')
@click.confirmation_option(prompt='Are you sure you want to delete this note?')
def delete(note_id):
    """Delete a note."""
    with Database() as db:
        note_obj = db.get_note(note_id)
        if not note_obj:
            click.echo(f"Note with ID {note_id} not found", err=True)
            return

        if db.delete_note(note_id):
            click.echo(f"Note '{note_obj.title}' deleted successfully")
        else:
            click.echo("Failed to delete note", err=True)


# Package commands
@package.command()
@click.argument('name')
@click.option('--description', '-d', help='Package description')
@click.option('--parent', help='Parent package name')
@click.option('--due', help='Due date (YYYY-MM-DD)')
def create(name, description, parent, due):
    """Create a new package."""
    with Database() as db:
        # Parse due date
        due_date = None
        if due:
            try:
                due_date = parse_date(due)
            except Exception as e:
                click.echo(f"Error parsing due date: {e}", err=True)
                return

        # Find parent package ID if parent name provided
        parent_id = None
        if parent:
            packages = db.list_packages()
            matching_packages = [p for p in packages if p.name.lower() == parent.lower()]
            if matching_packages:
                parent_id = matching_packages[0].id
            else:
                click.echo(f"Parent package '{parent}' not found", err=True)
                return

        # Create package
        package_obj = Package(
            name=name,
            description=description,
            parent_id=parent_id,
            due_date=due_date
        )

        db.create_package(package_obj)
        click.echo(f"Package created with ID: {package_obj.id}")


@package.command()
@click.option('--format', 'output_format', type=click.Choice(['table', 'json', 'markdown']),
              default='table', help='Output format')
def list(output_format):
    """List all packages."""
    with Database() as db:
        packages = db.list_packages()
        
        if output_format == 'json':
            click.echo(json.dumps([pkg.to_dict() for pkg in packages], indent=2))
        elif output_format == 'markdown':
            for pkg in packages:
                click.echo(f"## {pkg.name}")
                if pkg.description:
                    click.echo(f"- **Description**: {pkg.description}")
                click.echo(f"- **Status**: {pkg.status}")
                if pkg.due_date:
                    click.echo(f"- **Due**: {pkg.due_date.strftime('%Y-%m-%d')}")
                click.echo()
        else:
            format_packages_table(packages)


@package.command()
@click.argument('package_id')
def archive(package_id):
    """Archive a package."""
    with Database() as db:
        package_obj = db.get_package(package_id)
        if not package_obj:
            click.echo(f"Package with ID {package_id} not found", err=True)
            return

        package_obj.archive()
        db.update_package(package_obj)
        click.echo(f"Package '{package_obj.name}' archived successfully")


# Global commands
@cli.command()
@click.argument('query')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json']),
              default='table', help='Output format')
def search(query, output_format):
    """Search across tasks, notes, and packages."""
    with Database() as db:
        results = db.search(query)
        
        if output_format == 'json':
            # Convert objects to dictionaries for JSON serialization
            json_results = {
                'tasks': [task.to_dict() for task in results['tasks']],
                'notes': [note.to_dict() for note in results['notes']],
                'packages': [pkg.to_dict() for pkg in results['packages']]
            }
            click.echo(json.dumps(json_results, indent=2))
        else:
            click.echo(f"Search results for: '{query}'\n")
            
            if results['tasks']:
                click.echo("=== TASKS ===")
                format_tasks_table(results['tasks'])
                click.echo()
            
            if results['notes']:
                click.echo("=== NOTES ===")
                format_notes_table(results['notes'])
                click.echo()
            
            if results['packages']:
                click.echo("=== PACKAGES ===")
                format_packages_table(results['packages'])


@cli.command()
@click.option('--port', '-p', default=8080, help='Port to run the server on')
def server(port):
    """Start the web server for the GUI interface."""
    from ..api.app import create_app
    
    app = create_app()
    click.echo(f"Starting Notes web server on http://localhost:{port}")
    click.echo("Press Ctrl+C to stop the server")
    app.run(host='0.0.0.0', port=port, debug=False)


if __name__ == '__main__':
    cli()