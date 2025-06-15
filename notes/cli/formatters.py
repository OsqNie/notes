import click
from typing import List
from datetime import datetime, timedelta
from ..models import Task, Note, Package


def format_tasks_table(tasks: List[Task], filter_completed_days: int = 7):
    """Format tasks as a compact table for CLI output."""
    if not tasks:
        click.echo("No tasks.")
        return
    
    # Filter out old completed tasks
    filtered_tasks = []
    cutoff_date = datetime.now() - timedelta(days=filter_completed_days)
    
    for task in tasks:
        if task.status == 'completed':
            if task.completed_at and task.completed_at >= cutoff_date:
                filtered_tasks.append(task)
        else:
            filtered_tasks.append(task)
    
    if not filtered_tasks:
        click.echo("No tasks.")
        return
    
    # Sort tasks: active tasks first, then completed tasks
    active_tasks = [t for t in filtered_tasks if t.status != 'completed']
    completed_tasks = [t for t in filtered_tasks if t.status == 'completed']
    sorted_tasks = active_tasks + completed_tasks
    
    # Compact output
    for task in sorted_tasks:
        # Shorter status indicators
        status_map = {'pending': 'TODO', 'in-progress': 'PROG', 'completed': 'DONE', 'cancelled': 'CANC'}
        status = status_map.get(task.status, task.status.upper())
        
        # Priority indicators 
        priority_map = {'low': 'L', 'medium': 'M', 'high': 'H', 'urgent': 'U'}
        priority = priority_map.get(task.priority, 'M')
        
        # Due date
        due_str = task.due_date.strftime('%m/%d') if task.due_date else '     '
        
        # Truncate title if too long
        title = task.title[:40] + '...' if len(task.title) > 40 else task.title
        
        row = f"{task.id[:6]:<6} [{status:<4}] [{priority}] {due_str} {title}"
        
        # Color coding
        if task.status == 'completed':
            click.echo(click.style(row, fg='green', dim=True))
        elif task.status == 'in-progress':
            click.echo(click.style(row, fg='yellow'))
        elif task.priority == 'urgent':
            click.echo(click.style(row, fg='red'))
        elif task.priority == 'high':
            click.echo(click.style(row, fg='magenta'))
        else:
            click.echo(row)


def format_notes_table(notes: List[Note]):
    """Format notes as a compact table for CLI output."""
    if not notes:
        click.echo("No notes.")
        return
    
    for note in notes:
        updated_str = note.updated_at.strftime('%m/%d')
        tags_str = ','.join(note.tags[:2]) if note.tags else ''
        title = note.title[:35] + '...' if len(note.title) > 35 else note.title
        
        row = f"{note.id[:6]:<6} {updated_str} {title}"
        if tags_str:
            row += f" [{tags_str}]"
        click.echo(row)


def format_packages_table(packages: List[Package]):
    """Format packages as a compact table for CLI output."""
    if not packages:
        click.echo("No packages.")
        return
    
    for pkg in packages:
        due_str = pkg.due_date.strftime('%m/%d') if pkg.due_date else '     '
        status_map = {'active': 'ACT', 'completed': 'DONE', 'archived': 'ARC'}
        status = status_map.get(pkg.status, pkg.status.upper()[:4])
        name = pkg.name[:30] + '...' if len(pkg.name) > 30 else pkg.name
        
        row = f"{pkg.id[:6]:<6} [{status:<4}] {due_str} {name}"
        
        # Color coding
        if pkg.status == 'completed':
            click.echo(click.style(row, fg='green'))
        elif pkg.status == 'archived':
            click.echo(click.style(row, fg='cyan', dim=True))
        else:
            click.echo(row)


def print_ascii_banner():
    """Print ASCII art banner for the application."""
    banner = """
 ███▄    █  ▒█████  ▄▄▄█████▓▓█████   ██████ 
 ██ ▀█   █ ▒██▒  ██▒▓  ██▒ ▓▒▓█   ▀ ▒██    ▒ 
▓██  ▀█ ██▒▒██░  ██▒▒ ▓██░ ▒░▒███   ░ ▓██▄   
▓██▒  ▐▌██▒▒██   ██░░ ▓██▓ ░ ▒▓█  ▄   ▒   ██▒
▒██░   ▓██░░ ████▓▒░  ▒██▒ ░ ░▒████▒▒██████▒▒
░ ▒░   ▒ ▒ ░ ▒░▒░▒░   ▒ ░░   ░░ ▒░ ░▒ ▒▓▒ ▒ ░
░ ░░   ░ ▒░  ░ ▒ ▒░     ░     ░ ░  ░░ ░▒  ░ ░
   ░   ░ ░ ░ ░ ░ ▒    ░         ░   ░  ░  ░  
         ░     ░ ░              ░  ░      ░  
    """
    click.echo(click.style(banner, fg='cyan', bold=True))
    click.echo(click.style("Task & Note Management System", fg='white', dim=True))
    click.echo()