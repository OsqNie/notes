import click
import os
import sys
import readline
from datetime import datetime
from typing import Optional, List

from ..database import Database
from ..models import Task, Note, Package
from .formatters import format_tasks_table, format_notes_table, format_packages_table, print_ascii_banner


class InteractiveApp:
    """Interactive command-line application mode."""
    
    def __init__(self):
        self.db = Database()
        self.current_package = None
        self.running = True
        self.setup_tab_completion()
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()
    
    def setup_tab_completion(self):
        """Setup tab completion for the interactive shell."""
        try:
            # Set up readline for tab completion
            readline.set_completer(self.complete)
            readline.parse_and_bind("tab: complete")
            
            # Enable history
            readline.parse_and_bind("set show-all-if-ambiguous on")
            readline.parse_and_bind("set completion-ignore-case on")
        except ImportError:
            # readline not available on this platform
            pass
    
    def get_completions(self, text: str) -> List[str]:
        """Get completion suggestions for the given text."""
        completions = []
        
        # Command completions including flags
        commands = [
            'help', 'quit', 'exit', 'status', 'clear', 'gui',
            'list', 'ls', 'packages', 'p', 'package', 'create-package', 
            'package-info', 'tasks', 't', 'task', 'create-task', 
            'complete', 'rm', 'remove', 'archive', 'notes', 'n', 
            'note', 'create-note', 'search', 'find', 's', 'edit'
        ]
        
        # Parse the text more carefully to handle flags
        stripped_text = text.strip()
        
        # If text is empty or just starting, suggest commands
        if not stripped_text or ' ' not in stripped_text:
            completions.extend([cmd for cmd in commands if cmd.startswith(stripped_text.lower())])
        else:
            # Split on spaces but be aware of the last token being completed
            import shlex
            try:
                parts = shlex.split(stripped_text)
                # If the text ends with a space, we're completing a new argument
                if stripped_text.endswith(' '):
                    parts.append('')
            except ValueError:
                # Fall back to simple split if shlex fails
                parts = stripped_text.split()
                if stripped_text.endswith(' '):
                    parts.append('')
            
            if len(parts) >= 1:
                cmd = parts[0].lower()
                
                # Handle ls/list command with flags
                if cmd in ['list', 'ls']:
                    if len(parts) == 2 and parts[1].startswith('-'):
                        # Complete flags for ls/list
                        flags = ['-a', '--all']
                        current_flag = parts[1]
                        completions.extend([flag for flag in flags if flag.startswith(current_flag)])
                
                # For commands that take task/note/package identifiers
                elif cmd in ['complete', 'task', 'rm', 'remove', 'archive', 'edit']:
                    # Skip flags and find the identifier position
                    identifier_pos = 1
                    while identifier_pos < len(parts) and parts[identifier_pos].startswith('-'):
                        identifier_pos += 1
                    
                    if len(parts) == identifier_pos + 1:
                        # We're completing the identifier
                        search_term = parts[identifier_pos].lower().strip('"') if identifier_pos < len(parts) else ''
                        tasks = self.db.list_tasks()
                        for task in tasks:
                            task_id = task.id[:8]
                            if not search_term or task_id.startswith(search_term) or search_term in task.title.lower():
                                completions.extend([task_id, f'"{task.title}"'])
                
                elif cmd in ['note']:
                    identifier_pos = 1
                    while identifier_pos < len(parts) and parts[identifier_pos].startswith('-'):
                        identifier_pos += 1
                    
                    if len(parts) == identifier_pos + 1:
                        search_term = parts[identifier_pos].lower().strip('"') if identifier_pos < len(parts) else ''
                        notes = self.db.list_notes()
                        for note in notes:
                            note_id = note.id[:8]
                            if not search_term or note_id.startswith(search_term) or search_term in note.title.lower():
                                completions.extend([note_id, f'"{note.title}"'])
                
                elif cmd in ['package']:
                    identifier_pos = 1
                    while identifier_pos < len(parts) and parts[identifier_pos].startswith('-'):
                        identifier_pos += 1
                    
                    if len(parts) == identifier_pos + 1:
                        search_term = parts[identifier_pos].lower().strip('"') if identifier_pos < len(parts) else ''
                        packages = self.db.list_packages()
                        for pkg in packages:
                            if not search_term or search_term in pkg.name.lower():
                                completions.append(f'"{pkg.name}"')
        
        return completions
    
    def complete(self, text: str, state: int) -> Optional[str]:
        """Completion function for readline."""
        if state == 0:
            # Get the current line buffer
            line_buffer = readline.get_line_buffer()
            # If the line buffer is empty or just whitespace, show all commands
            if not line_buffer.strip():
                self.completion_matches = [
                    'help', 'quit', 'exit', 'status', 'clear', 'gui',
                    'list', 'ls', 'packages', 'p', 'package', 'create-package', 
                    'package-info', 'tasks', 't', 'task', 'create-task', 
                    'complete', 'rm', 'remove', 'archive', 'notes', 'n', 
                    'note', 'create-note', 'search', 'find', 's', 'edit'
                ]
            else:
                self.completion_matches = self.get_completions(line_buffer)
            
            # Filter completions that match the current text being completed
            if text:
                self.completion_matches = [
                    match for match in self.completion_matches 
                    if match.lower().startswith(text.lower())
                ]
        
        try:
            return self.completion_matches[state]
        except (IndexError, AttributeError):
            return None
    
    def show_banner(self):
        """Show the application banner."""
        print_ascii_banner()
        print("Interactive Mode - Type 'help' for commands or 'quit' to exit")
        if self.current_package:
            print(f"Current package: {self.current_package.name}")
        print()
    
    def launch_gui(self):
        """Launch the web GUI in the background."""
        import threading
        import webbrowser
        import time
        from ..api.app import create_app
        
        print("Starting web GUI server...")
        
        app = create_app()
        
        def run_server():
            app.run(host='127.0.0.1', port=8080, debug=False, use_reloader=False)
        
        # Start server in background thread
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Give server a moment to start
        time.sleep(2)
        
        # Open browser
        try:
            webbrowser.open('http://localhost:8080')
            print("Web GUI opened in your browser at http://localhost:8080")
            print("The server will continue running in the background.")
            print("You can continue using this interactive mode alongside the GUI.")
        except Exception as e:
            print(f"Could not open browser automatically: {e}")
            print("Please manually open http://localhost:8080 in your browser")
    
    def show_help(self):
        """Show available commands."""
        help_text = """
Available Commands:

GENERAL:
  help                    Show this help message
  quit, exit              Exit the application
  status                  Show current status and statistics
  clear                   Clear the screen
  gui                     Launch web GUI in browser

QUICK VIEWS:
  list, ls                Context-aware list of active tasks
  list -a, ls -a          List all tasks (including completed)
  
PACKAGES:
  packages                List all packages
  package <name>          Switch to a package
  create-package <name>   Create a new package
  package-info            Show current package details
  rm <name>, remove <name> Delete a package and all contents
  archive <name>          Archive a package

TASKS:
  tasks                   List tasks (in current package if set)
  task <id>               Show task details
  create-task <title>     Create a new task
  edit <id>               Interactive edit task with arrow keys
  complete <id>           Mark task as completed
  rm <id>, remove <id>    Delete a task
  archive <id>            Archive a task (mark as cancelled)

NOTES:
  notes                   List notes (in current package if set)
  note <id>               Show note details
  create-note <title>     Create a new note
  rm <id>, remove <id>    Delete a note

SEARCH:
  search <query>          Search across all content
  find <query>            Alias for search

SHORTCUTS:
  t                       Alias for 'tasks'
  n                       Alias for 'notes'
  p                       Alias for 'packages'
  s <query>               Alias for 'search'
  ls, list                Context-aware active tasks

NOTE: IDs can be partial (first 8 chars) or you can use partial title matches!
Examples: complete "wireframes", rm "meeting", archive "old project"
"""
        print(help_text)
    
    def show_status(self):
        """Show current status and statistics."""
        all_tasks = self.db.list_tasks()
        all_notes = self.db.list_notes()
        all_packages = self.db.list_packages()
        
        pending_tasks = [t for t in all_tasks if t.status == 'pending']
        in_progress_tasks = [t for t in all_tasks if t.status == 'in-progress']
        completed_tasks = [t for t in all_tasks if t.status == 'completed']
        high_priority_tasks = [t for t in all_tasks if t.priority == 'high' and t.status != 'completed']
        
        print("Current Status:")
        print(f"  Total tasks: {len(all_tasks)}")
        print(f"  - Pending: {len(pending_tasks)}")
        print(f"  - In Progress: {len(in_progress_tasks)}")
        print(f"  - Completed: {len(completed_tasks)}")
        print(f"  - High Priority (active): {len(high_priority_tasks)}")
        print(f"  Total notes: {len(all_notes)}")
        print(f"  Total packages: {len(all_packages)}")
        
        if self.current_package:
            package_tasks = self.db.list_tasks({'package_id': self.current_package.id})
            package_notes = self.db.list_notes({'package_id': self.current_package.id})
            print(f"\nCurrent Package: {self.current_package.name}")
            print(f"  Tasks in package: {len(package_tasks)}")
            print(f"  Notes in package: {len(package_notes)}")
        print()
    
    def list_packages(self):
        """List all packages."""
        packages = self.db.list_packages()
        if not packages:
            print("No packages found. Create one with 'create-package <name>'")
            return
            
        print("Packages:")
        format_packages_table(packages)
        print()
    
    def switch_package(self, name: str):
        """Switch to a specific package."""
        packages = self.db.list_packages()
        matching = [p for p in packages if p.name.lower() == name.lower()]
        
        if not matching:
            print(f"Package '{name}' not found.")
            print("Available packages:")
            for p in packages:
                print(f"  - {p.name}")
            return
        
        self.current_package = matching[0]
        print(f"Switched to package: {self.current_package.name}")
    
    def create_package(self, name: str):
        """Create a new package."""
        description = input(f"Description for '{name}' (optional): ").strip()
        
        package = Package(
            name=name,
            description=description if description else None
        )
        
        created_package = self.db.create_package(package)
        print(f"Package '{created_package.name}' created successfully!")
        
        switch = input("Switch to this package? (y/N): ").strip().lower()
        if switch in ['y', 'yes']:
            self.current_package = created_package
            print(f"Switched to package: {self.current_package.name}")
    
    def show_package_info(self):
        """Show current package details."""
        if not self.current_package:
            print("No package selected. Use 'package <name>' to switch to a package.")
            return
        
        package_tasks = self.db.list_tasks({'package_id': self.current_package.id})
        package_notes = self.db.list_notes({'package_id': self.current_package.id})
        
        print(f"Package: {self.current_package.name}")
        if self.current_package.description:
            print(f"Description: {self.current_package.description}")
        print(f"Status: {self.current_package.status}")
        if self.current_package.due_date:
            print(f"Due date: {self.current_package.due_date.strftime('%Y-%m-%d')}")
        print(f"Tasks: {len(package_tasks)}")
        print(f"Notes: {len(package_notes)}")
        print()
    
    def list_tasks(self):
        """List tasks (filtered by current package if set)."""
        filters = {}
        if self.current_package:
            filters['package_id'] = self.current_package.id
            
        tasks = self.db.list_tasks(filters)
        
        if not tasks:
            context = f" in package '{self.current_package.name}'" if self.current_package else ""
            print(f"No tasks found{context}.")
            return
        
        context = f" in {self.current_package.name}" if self.current_package else ""
        print(f"Tasks{context}:")
        format_tasks_table(tasks)
        print()
    
    def list_active_items(self, show_all=False):
        """Show a context-aware list of active tasks and recent activity."""
        if show_all:
            print("All Items:")
        else:
            print("Active Items:")
        
        # Get tasks based on show_all parameter
        all_tasks = self.db.list_tasks()
        
        # Filter to current package if set
        if self.current_package:
            all_tasks = [t for t in all_tasks if t.package_id == self.current_package.id]
        
        if show_all:
            # Show all tasks, sort by status and priority
            active_tasks = all_tasks
        else:
            # Separate active and recently completed tasks
            active_tasks = [t for t in all_tasks if t.status in ['pending', 'in-progress']]
        
        if not active_tasks and not self.current_package:
            no_items_msg = "No tasks" if show_all else "No active tasks"
            print(f"{no_items_msg}. Use 'create-task <title>' to create one.")
            return
        elif not active_tasks and self.current_package:
            no_items_msg = "No tasks" if show_all else "No active tasks"
            print(f"{no_items_msg} in {self.current_package.name}. Use 'create-task <title>' to create one.")
            return
        
        # Sort by priority and due date, with completed items at the end if showing all
        def task_sort_key(task):
            status_order = {'pending': 0, 'in-progress': 1, 'completed': 2, 'cancelled': 3}
            priority_order = {'urgent': 0, 'high': 1, 'medium': 2, 'low': 3}
            status_val = status_order.get(task.status, 4)
            priority_val = priority_order.get(task.priority, 4)
            due_val = task.due_date.timestamp() if task.due_date else float('inf')
            return (status_val, priority_val, due_val)
        
        active_tasks.sort(key=task_sort_key)
        
        # Show tasks with enhanced formatting  
        display_count = len(active_tasks) if show_all else min(10, len(active_tasks))
        for i, task in enumerate(active_tasks[:display_count]):
            due_indicator = ""
            if task.due_date:
                days_until_due = (task.due_date.date() - datetime.now().date()).days
                if days_until_due < 0:
                    due_indicator = f" (overdue by {abs(days_until_due)} days)"
                elif days_until_due == 0:
                    due_indicator = " (due today)"
                elif days_until_due == 1:
                    due_indicator = " (due tomorrow)"
                elif days_until_due <= 7:
                    due_indicator = f" (due in {days_until_due} days)"
            
            priority_map = {'urgent': 'U', 'high': 'H', 'medium': 'M', 'low': 'L'}
            status_map = {'pending': 'TODO', 'in-progress': 'PROG', 'completed': 'DONE', 'cancelled': 'CANC'}
            
            priority_indicator = priority_map.get(task.priority, 'M')
            status_indicator = status_map.get(task.status, 'TODO')
            
            # Truncate title and description for single line
            title = task.title[:35] + '...' if len(task.title) > 35 else task.title
            desc_suffix = ""
            if task.description:
                desc_suffix = f" | {task.description[:25]}{'...' if len(task.description) > 25 else ''}"
            
            # Create single line with ID, status, priority, title, due date, and description
            line = f"{task.id[:6]} [{status_indicator}] [{priority_indicator}] {due_indicator:<12} {title}{desc_suffix}"
            
            # Apply colors optimized for dark terminals
            import click
            if task.status == 'completed':
                click.echo(click.style(line, fg='bright_green', dim=True))
            elif task.status == 'cancelled':
                click.echo(click.style(line, fg='bright_black', dim=True))
            elif task.status == 'in-progress':
                click.echo(click.style(line, fg='bright_yellow', bold=True))
            elif task.priority == 'urgent':
                click.echo(click.style(line, fg='bright_red', bold=True))
            elif task.priority == 'high':
                click.echo(click.style(line, fg='bright_magenta'))
            elif task.priority == 'medium':
                click.echo(click.style(line, fg='bright_cyan'))
            else:
                # Low priority - use bright white for good visibility on dark backgrounds
                click.echo(click.style(line, fg='bright_white'))
        
        if not show_all and len(active_tasks) > 10:
            print(f"... and {len(active_tasks) - 10} more active tasks. Use 'tasks' to see all.")
        
        print(f"Quick actions: 'complete <id>' to mark done, 'task <id>' for details")
    
    def show_task(self, identifier: str):
        """Show detailed task information."""
        task = self.db.get_task(identifier) or self.find_task_by_partial_identifier(identifier)
        if not task:
            print(f"Task '{identifier}' not found.")
            return
        
        print(f"Task: {task.title}")
        print(f"ID: {task.id}")
        print(f"Status: {task.status}")
        print(f"Priority: {task.priority}")
        if task.description:
            print(f"Description: {task.description}")
        if task.due_date:
            print(f"Due date: {task.due_date.strftime('%Y-%m-%d %H:%M')}")
        if task.tags:
            print(f"Tags: {', '.join(task.tags)}")
        print(f"Created: {task.created_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"Updated: {task.updated_at.strftime('%Y-%m-%d %H:%M')}")
        if task.completed_at:
            print(f"Completed: {task.completed_at.strftime('%Y-%m-%d %H:%M')}")
        print()
    
    def create_task(self, title: str):
        """Create a new task interactively."""
        print(f"Creating task: {title}")
        
        try:
            description = input("Description (optional): ").strip()
        except EOFError:
            description = ""
        
        try:
            print("Priority levels: low, medium, high, urgent")
            priority = input("Priority (medium): ").strip().lower()
            if priority not in ['low', 'medium', 'high', 'urgent']:
                priority = 'medium'
        except EOFError:
            priority = 'medium'
        
        try:
            due_date_str = input("Due date (YYYY-MM-DD or 'tomorrow'): ").strip()
        except EOFError:
            due_date_str = ""
            
        due_date = None
        if due_date_str:
            try:
                if due_date_str.lower() == 'tomorrow':
                    from datetime import date, timedelta
                    due_date = datetime.combine(date.today() + timedelta(days=1), datetime.min.time())
                elif due_date_str.lower() == 'next week':
                    from datetime import date, timedelta
                    due_date = datetime.combine(date.today() + timedelta(weeks=1), datetime.min.time())
                else:
                    from dateutil.parser import parse as parse_date
                    due_date = parse_date(due_date_str)
            except Exception:
                print("Invalid date format, skipping due date.")
        
        try:
            tags_str = input("Tags (comma-separated): ").strip()
            tags = [tag.strip() for tag in tags_str.split(',')] if tags_str else []
        except EOFError:
            tags = []
        
        task = Task(
            title=title,
            description=description if description else None,
            priority=priority,
            due_date=due_date,
            package_id=self.current_package.id if self.current_package else None,
            tags=tags
        )
        
        created_task = self.db.create_task(task)
        print(f"Task '{created_task.title}' created successfully! (ID: {created_task.id[:8]})")
    
    def find_task_by_partial_identifier(self, identifier: str):
        """Find a task by partial ID or title."""
        all_tasks = self.db.list_tasks()
        
        # First try partial ID matching
        id_matches = [t for t in all_tasks if t.id.startswith(identifier)]
        
        # Then try partial title matching (case insensitive)
        title_matches = [t for t in all_tasks if identifier.lower() in t.title.lower()]
        
        # Combine matches, prioritizing ID matches
        all_matches = id_matches + [t for t in title_matches if t not in id_matches]
        
        if len(all_matches) == 1:
            return all_matches[0]
        elif len(all_matches) > 1:
            self.show_multiple_task_matches(identifier, all_matches)
            return None
        else:
            return None
    
    def show_multiple_task_matches(self, identifier: str, tasks):
        """Show detailed information for multiple task matches."""
        print(f"\nMultiple tasks match '{identifier}':")
        print("=" * 80)
        
        for i, task in enumerate(tasks):
            due_str = ""
            if task.due_date:
                due_str = f" | Due: {task.due_date.strftime('%Y-%m-%d')}"
            
            priority_map = {'urgent': 'U', 'high': 'H', 'medium': 'M', 'low': 'L'}
            status_map = {'pending': 'TODO', 'in-progress': 'PROG', 'completed': 'DONE', 'cancelled': 'CANC'}
            
            priority_indicator = priority_map.get(task.priority, 'M')
            status_indicator = status_map.get(task.status, 'TODO')
            
            print(f"{i+1:2}. [{priority_indicator}] [{status_indicator}] {task.title}")
            print(f"    ID: {task.id[:8]} | Status: {task.status} | Priority: {task.priority}{due_str}")
            
            if task.description:
                desc = task.description[:100] + "..." if len(task.description) > 100 else task.description
                print(f"    {desc}")
            
            if task.tags:
                print(f"    Tags: {', '.join(task.tags)}")
            print()
        
        print("Use the exact ID (8 characters) to specify which task:")
        for i, task in enumerate(tasks):
            print(f"   complete {task.id[:8]}    # {task.title}")
        print()
    
    def find_note_by_partial_identifier(self, identifier: str):
        """Find a note by partial ID or title."""
        all_notes = self.db.list_notes()
        
        # First try partial ID matching
        id_matches = [n for n in all_notes if n.id.startswith(identifier)]
        
        # Then try partial title matching (case insensitive)
        title_matches = [n for n in all_notes if identifier.lower() in n.title.lower()]
        
        # Combine matches, prioritizing ID matches
        all_matches = id_matches + [n for n in title_matches if n not in id_matches]
        
        if len(all_matches) == 1:
            return all_matches[0]
        elif len(all_matches) > 1:
            self.show_multiple_note_matches(identifier, all_matches)
            return None
        else:
            return None
    
    def show_multiple_note_matches(self, identifier: str, notes):
        """Show detailed information for multiple note matches."""
        print(f"\nMultiple notes match '{identifier}':")
        print("=" * 80)
        
        for i, note in enumerate(notes):
            print(f"{i+1:2}. {note.title}")
            print(f"    ID: {note.id[:8]} | Updated: {note.updated_at.strftime('%Y-%m-%d %H:%M')}")
            
            if note.content:
                content_preview = note.content[:100] + "..." if len(note.content) > 100 else note.content
                print(f"    {content_preview}")
            
            if note.tags:
                print(f"    Tags: {', '.join(note.tags)}")
            print()
        
        print("Use the exact ID (8 characters) to specify which note:")
        for i, note in enumerate(notes):
            print(f"   note {note.id[:8]}    # {note.title}")
        print()

    def complete_task(self, identifier: str):
        """Mark a task as completed."""
        task = self.db.get_task(identifier) or self.find_task_by_partial_identifier(identifier)
        if not task:
            print(f"Task '{identifier}' not found.")
            return
        
        task.mark_completed()
        self.db.update_task(task)
        print(f"Task '{task.title}' marked as completed!")
    
    def edit_task_interactive(self, identifier: str):
        """Interactive task editor with arrow key navigation."""
        task = self.db.get_task(identifier) or self.find_task_by_partial_identifier(identifier)
        if not task:
            print(f"Task '{identifier}' not found.")
            return
        
        # Check if we can use advanced terminal features
        try:
            import termios
            import tty
            import sys
            has_termios = True
            # Store original terminal settings
            old_settings = termios.tcgetattr(sys.stdin)
        except ImportError:
            # Fall back to simple line-based editing on Windows
            has_termios = False
        
        if not has_termios:
            self._edit_task_simple(task)
            return
        
        try:
            # Fields that can be edited
            fields = [
                ('title', 'Title', task.title),
                ('description', 'Description', task.description or ''),
                ('priority', 'Priority', task.priority),
                ('status', 'Status', task.status),
                ('due_date', 'Due Date', task.due_date.strftime('%Y-%m-%d') if task.due_date else ''),
                ('tags', 'Tags', ', '.join(task.tags) if task.tags else '')
            ]
            
            current_field = 0
            editing = False
            edit_value = ""
            
            def draw_screen():
                # Clear screen
                print('\033[2J\033[H', end='')
                
                # Header
                print("=" * 60)
                print(f"   EDITING TASK: {task.title}")
                print("=" * 60)
                print("Use ↑/↓ arrows to navigate, Enter to edit, Ctrl+C to cancel, Ctrl+S to save")
                print()
                
                # Draw fields
                for i, (field_name, display_name, value) in enumerate(fields):
                    if i == current_field:
                        if editing:
                            # Show current edit value
                            print(f"> {display_name:12}: {edit_value}█")
                        else:
                            # Highlight current field
                            print(f"> {display_name:12}: {value}")
                    else:
                        print(f"  {display_name:12}: {value}")
                
                print()
                if editing:
                    print("Type new value, Enter to confirm, Esc to cancel")
                else:
                    print("Press Enter to edit field, Ctrl+S to save all changes")
            
            def get_char():
                tty.setraw(sys.stdin.fileno())
                char = sys.stdin.read(1)
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                return char
            
            def save_changes():
                nonlocal fields, task
                
                # Update task with new values
                for field_name, _, value in fields:
                    if field_name == 'title':
                        task.title = value or task.title
                    elif field_name == 'description':
                        task.description = value if value else None
                    elif field_name == 'priority':
                        if value in ['low', 'medium', 'high', 'urgent']:
                            task.priority = value
                    elif field_name == 'status':
                        if value in ['pending', 'in-progress', 'completed', 'cancelled']:
                            task.status = value
                    elif field_name == 'due_date':
                        if value:
                            try:
                                from dateutil.parser import parse as parse_date
                                task.due_date = parse_date(value)
                            except:
                                pass  # Keep original if parse fails
                        else:
                            task.due_date = None
                    elif field_name == 'tags':
                        if value:
                            task.tags = [tag.strip() for tag in value.split(',') if tag.strip()]
                        else:
                            task.tags = []
                
                task.updated_at = datetime.now()
                self.db.update_task(task)
                return True
            
            # Main interaction loop
            while True:
                draw_screen()
                
                if editing:
                    # In edit mode - handle text input
                    tty.setraw(sys.stdin.fileno())
                    char = sys.stdin.read(1)
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                    
                    if ord(char) == 13:  # Enter - confirm edit
                        # Update the field value
                        fields[current_field] = (fields[current_field][0], fields[current_field][1], edit_value)
                        editing = False
                        edit_value = ""
                    elif ord(char) == 27:  # Escape - cancel edit
                        editing = False
                        edit_value = ""
                    elif ord(char) == 127:  # Backspace
                        edit_value = edit_value[:-1]
                    elif ord(char) >= 32 and ord(char) < 127:  # Printable characters
                        edit_value += char
                else:
                    # Navigation mode
                    char = get_char()
                    
                    if ord(char) == 27:  # Escape sequence (arrow keys)
                        char = get_char()
                        if char == '[':
                            char = get_char()
                            if char == 'A':  # Up arrow
                                current_field = max(0, current_field - 1)
                            elif char == 'B':  # Down arrow
                                current_field = min(len(fields) - 1, current_field + 1)
                    elif ord(char) == 13:  # Enter - start editing
                        editing = True
                        edit_value = fields[current_field][2]
                    elif ord(char) == 19:  # Ctrl+S - save
                        if save_changes():
                            print("\nTask updated successfully!")
                            break
                    elif ord(char) == 3:  # Ctrl+C - cancel
                        print("\nEdit cancelled.")
                        break
        
        except KeyboardInterrupt:
            print("\nEdit cancelled.")
        finally:
            # Restore terminal settings
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    
    def _edit_task_simple(self, task):
        """Simple line-based task editor for systems without termios."""
        print("=" * 60)
        print(f"   EDITING TASK: {task.title}")
        print("=" * 60)
        print("Enter new values (press Enter to keep current value):")
        print()
        
        # Edit title
        current = task.title
        new_value = input(f"Title [{current}]: ").strip()
        if new_value:
            task.title = new_value
        
        # Edit description
        current = task.description or ''
        new_value = input(f"Description [{current}]: ").strip()
        task.description = new_value if new_value else None
        
        # Edit priority
        current = task.priority
        print(f"Priority options: low, medium, high, urgent")
        new_value = input(f"Priority [{current}]: ").strip().lower()
        if new_value in ['low', 'medium', 'high', 'urgent']:
            task.priority = new_value
        
        # Edit status
        current = task.status
        print(f"Status options: pending, in-progress, completed, cancelled")
        new_value = input(f"Status [{current}]: ").strip().lower()
        if new_value in ['pending', 'in-progress', 'completed', 'cancelled']:
            task.status = new_value
        
        # Edit due date
        current = task.due_date.strftime('%Y-%m-%d') if task.due_date else ''
        new_value = input(f"Due date (YYYY-MM-DD) [{current}]: ").strip()
        if new_value:
            try:
                from dateutil.parser import parse as parse_date
                task.due_date = parse_date(new_value)
            except:
                print("Invalid date format, keeping original value")
        elif new_value == '':
            # Empty input, ask if they want to clear the date
            if current and input("Clear due date? (y/N): ").strip().lower() == 'y':
                task.due_date = None
        
        # Edit tags
        current = ', '.join(task.tags) if task.tags else ''
        new_value = input(f"Tags (comma-separated) [{current}]: ").strip()
        if new_value:
            task.tags = [tag.strip() for tag in new_value.split(',') if tag.strip()]
        elif new_value == '' and current:
            if input("Clear all tags? (y/N): ").strip().lower() == 'y':
                task.tags = []
        
        # Save changes
        task.updated_at = datetime.now()
        self.db.update_task(task)
        print("\nTask updated successfully!")
    
    def remove_task(self, identifier: str):
        """Remove (delete) a task."""
        task = self.db.get_task(identifier) or self.find_task_by_partial_identifier(identifier)
        if not task:
            print(f"Task '{identifier}' not found.")
            return
        
        confirm = input(f"Delete task '{task.title}'? (y/N): ").strip().lower()
        if confirm in ['y', 'yes']:
            self.db.delete_task(task.id)
            print(f"Task '{task.title}' deleted.")
        else:
            print("Deletion cancelled.")
    
    def archive_task(self, identifier: str):
        """Archive a task (mark as cancelled)."""
        task = self.db.get_task(identifier) or self.find_task_by_partial_identifier(identifier)
        if not task:
            print(f"Task '{identifier}' not found.")
            return
        
        task.update_status("cancelled")
        self.db.update_task(task)
        print(f"Task '{task.title}' archived.")
    
    def remove_package(self, identifier: str):
        """Remove (delete) a package and all its contents."""
        packages = self.db.list_packages()
        matching = [p for p in packages if p.id.startswith(identifier) or identifier.lower() in p.name.lower()]
        
        if len(matching) == 1:
            package = matching[0]
        elif len(matching) > 1:
            print(f"Multiple packages match '{identifier}':")
            for pkg in matching:
                print(f"  {pkg.id[:8]} - {pkg.name}")
            return
        else:
            print(f"Package '{identifier}' not found.")
            return
        
        # Check for contents
        package_tasks = self.db.list_tasks({'package_id': package.id})
        package_notes = self.db.list_notes({'package_id': package.id})
        
        if package_tasks or package_notes:
            print(f"WARNING: Package '{package.name}' contains:")
            if package_tasks:
                print(f"  {len(package_tasks)} tasks")
            if package_notes:
                print(f"  {len(package_notes)} notes")
            print("  All contents will be deleted as well!")
        
        confirm = input(f"Delete package '{package.name}' and all its contents? (y/N): ").strip().lower()
        if confirm in ['y', 'yes']:
            # Delete all tasks and notes in the package
            for task in package_tasks:
                self.db.delete_task(task.id)
            for note in package_notes:
                self.db.delete_note(note.id)
            
            # Delete the package
            self.db.delete_package(package.id)
            
            # If this was the current package, clear it
            if self.current_package and self.current_package.id == package.id:
                self.current_package = None
            
            print(f"Package '{package.name}' and all its contents deleted.")
        else:
            print("Deletion cancelled.")
    
    def archive_package(self, identifier: str):
        """Archive a package (mark as archived)."""
        packages = self.db.list_packages()
        matching = [p for p in packages if p.id.startswith(identifier) or identifier.lower() in p.name.lower()]
        
        if len(matching) == 1:
            package = matching[0]
        elif len(matching) > 1:
            print(f"Multiple packages match '{identifier}':")
            for pkg in matching:
                print(f"  {pkg.id[:8]} - {pkg.name}")
            return
        else:
            print(f"Package '{identifier}' not found.")
            return
        
        package.archive()
        self.db.update_package(package)
        print(f"Package '{package.name}' archived.")
    
    def list_notes(self):
        """List notes (filtered by current package if set)."""
        filters = {}
        if self.current_package:
            filters['package_id'] = self.current_package.id
            
        notes = self.db.list_notes(filters)
        
        if not notes:
            context = f" in package '{self.current_package.name}'" if self.current_package else ""
            print(f"No notes found{context}.")
            return
        
        context = f" in {self.current_package.name}" if self.current_package else ""
        print(f"Notes{context}:")
        format_notes_table(notes)
        print()
    
    def show_note(self, identifier: str):
        """Show detailed note information."""
        note = self.db.get_note(identifier) or self.find_note_by_partial_identifier(identifier)
        if not note:
            print(f"Note '{identifier}' not found.")
            return
        
        print(f"Note: {note.title}")
        print(f"ID: {note.id}")
        if note.tags:
            print(f"Tags: {', '.join(note.tags)}")
        print(f"Created: {note.created_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"Updated: {note.updated_at.strftime('%Y-%m-%d %H:%M')}")
        print("-" * 50)
        print(note.content)
        print("-" * 50)
        print()
    
    def create_note(self, title: str):
        """Create a new note interactively."""
        print(f"Creating note: {title}")
        print("Enter note content (end with Ctrl+D on empty line):")
        
        content_lines = []
        try:
            while True:
                line = input()
                content_lines.append(line)
        except EOFError:
            pass
        
        content = '\n'.join(content_lines)
        
        tags_str = input("Tags (comma-separated): ").strip()
        tags = [tag.strip() for tag in tags_str.split(',')] if tags_str else []
        
        note = Note(
            title=title,
            content=content,
            package_id=self.current_package.id if self.current_package else None,
            tags=tags
        )
        
        created_note = self.db.create_note(note)
        print(f"Note '{created_note.title}' created successfully! (ID: {created_note.id[:8]})")
    
    def remove_note(self, identifier: str):
        """Remove (delete) a note."""
        note = self.db.get_note(identifier) or self.find_note_by_partial_identifier(identifier)
        if not note:
            print(f"Note '{identifier}' not found.")
            return
        
        confirm = input(f"Delete note '{note.title}'? (y/N): ").strip().lower()
        if confirm in ['y', 'yes']:
            self.db.delete_note(note.id)
            print(f"Note '{note.title}' deleted.")
        else:
            print("Deletion cancelled.")
    
    def search(self, query: str):
        """Search across all content."""
        results = self.db.search(query)
        total_results = len(results['tasks']) + len(results['notes']) + len(results['packages'])
        
        if total_results == 0:
            print(f"No results found for '{query}'")
            return
        
        print(f"Search results for '{query}' ({total_results} results):\n")
        
        if results['tasks']:
            print("=== TASKS ===")
            format_tasks_table(results['tasks'])
            print()
        
        if results['notes']:
            print("=== NOTES ===")
            format_notes_table(results['notes'])
            print()
        
        if results['packages']:
            print("=== PACKAGES ===")
            format_packages_table(results['packages'])
            print()
    
    def parse_command(self, command_line: str):
        """Parse and execute a command."""
        import shlex
        
        try:
            # Use shlex to properly handle quoted strings
            parts = shlex.split(command_line.strip())
        except ValueError:
            # Fall back to simple split if shlex fails
            parts = command_line.strip().split()
            
        if not parts:
            return
        
        cmd = parts[0].lower()
        args = parts[1:]
        
        try:
            if cmd in ['quit', 'exit', 'q']:
                self.running = False
                print("Goodbye!")
                
            elif cmd == 'help':
                self.show_help()
                
            elif cmd == 'status':
                self.show_status()
                
            elif cmd == 'clear':
                os.system('clear' if os.name == 'posix' else 'cls')
                self.show_banner()
                
            elif cmd == 'gui':
                self.launch_gui()
                
            elif cmd in ['list', 'ls']:
                show_all = '-a' in args or '--all' in args
                self.list_active_items(show_all)
                
            elif cmd in ['packages', 'p']:
                self.list_packages()
                
            elif cmd == 'package':
                if args:
                    self.switch_package(' '.join(args))
                else:
                    print("Usage: package <name>")
                    
            elif cmd == 'create-package':
                if args:
                    self.create_package(' '.join(args))
                else:
                    print("Usage: create-package <name>")
                    
            elif cmd == 'package-info':
                self.show_package_info()
                
            elif cmd in ['tasks', 't']:
                self.list_tasks()
                
            elif cmd == 'task':
                if args:
                    self.show_task(args[0])
                else:
                    print("Usage: task <id>")
                    
            elif cmd == 'create-task':
                if args:
                    self.create_task(' '.join(args))
                else:
                    print("Usage: create-task <title>")
                    
            elif cmd == 'edit':
                if args:
                    self.edit_task_interactive(' '.join(args))
                else:
                    print("Usage: edit <id_or_title>")
                    
            elif cmd == 'complete':
                if args:
                    self.complete_task(' '.join(args))
                else:
                    print("Usage: complete <id_or_title>")
                    
            elif cmd in ['rm', 'remove']:
                if args:
                    # Determine if it's a task, note, or package based on context or explicit type
                    identifier = ' '.join(args)
                    
                    # Try to find as task first
                    task = self.db.get_task(identifier) or self.find_task_by_partial_identifier(identifier)
                    if task:
                        self.remove_task(identifier)
                        return
                    
                    # Try to find as note
                    note = self.db.get_note(identifier) or self.find_note_by_partial_identifier(identifier)
                    if note:
                        self.remove_note(identifier)
                        return
                    
                    # Try to find as package
                    packages = self.db.list_packages()
                    matching_packages = [p for p in packages if p.id.startswith(identifier) or identifier.lower() in p.name.lower()]
                    if matching_packages:
                        self.remove_package(identifier)
                        return
                    
                    print(f"No task, note, or package found matching '{identifier}'")
                else:
                    print("Usage: rm <id_or_title>")
                    
            elif cmd == 'archive':
                if args:
                    identifier = ' '.join(args)
                    
                    # Try to find as task first
                    task = self.db.get_task(identifier) or self.find_task_by_partial_identifier(identifier)
                    if task:
                        self.archive_task(identifier)
                        return
                    
                    # Try to find as package
                    packages = self.db.list_packages()
                    matching_packages = [p for p in packages if p.id.startswith(identifier) or identifier.lower() in p.name.lower()]
                    if matching_packages:
                        self.archive_package(identifier)
                        return
                    
                    print(f"No task or package found matching '{identifier}'")
                else:
                    print("Usage: archive <id_or_title>")
                    
            elif cmd in ['notes', 'n']:
                self.list_notes()
                
            elif cmd == 'note':
                if args:
                    self.show_note(' '.join(args))
                else:
                    print("Usage: note <id_or_title>")
                    
            elif cmd == 'create-note':
                if args:
                    self.create_note(' '.join(args))
                else:
                    print("Usage: create-note <title>")
                    
            elif cmd in ['search', 'find', 's']:
                if args:
                    self.search(' '.join(args))
                else:
                    print("Usage: search <query>")
                    
            else:
                print(f"Unknown command: {cmd}")
                print("Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
        except Exception as e:
            print(f"Error: {e}")
    
    def run(self):
        """Run the interactive application."""
        self.show_banner()
        self.show_status()
        
        try:
            while self.running:
                try:
                    prompt = f"notes:{self.current_package.name if self.current_package else ''} > "
                    command = input(prompt)
                    if command.strip():
                        self.parse_command(command)
                        
                except KeyboardInterrupt:
                    print("\nUse 'quit' to exit or Ctrl+D")
                except EOFError:
                    print("\nGoodbye!")
                    break
                    
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            self.db.close()


def start_interactive_mode():
    """Start the interactive mode."""
    with InteractiveApp() as app:
        app.run()