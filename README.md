# Notes

A dual-interface task and note management application featuring both a command-line interface and a local web-based GUI.

## Features

- **Task Management**: Create, edit, delete, and track tasks with priorities, due dates, and status
- **Note-Taking**: Markdown-supported notes with linking to tasks
- **Project Organization**: Hierarchical packages to organize tasks and notes
- **Dual Interface**: Both CLI and web GUI for different workflows
- **Search**: Full-text search across all content
- **Local Storage**: SQLite database for fast, reliable local storage

## Installation

1. Install the package:
```bash
pip install -e .
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Uninstallation

To remove the application:
```bash
pip uninstall notes
```

To completely remove all data:
```bash
rm -rf ~/.notes
```

## Quick Start

### Interactive Mode (Recommended)

Simply run `notes` without any commands to enter interactive mode:

```bash
notes
```

This opens an interactive command-line application where you can:
- Use shorter commands (`t` for tasks, `p` for packages, `n` for notes, `ls` for active items)
- Switch between packages and work within their context
- Get immediate feedback and status updates
- View context-aware active task lists with priority and due date indicators
- Launch the web GUI directly from the CLI (`gui` command)
- Support for partial ID matching (use first 8 characters of IDs)
- **Tab completion** for commands and task/note/package identifiers
- **Interactive editing** with arrow keys (`edit` command)
- **Partial title matching** for all commands (`complete "wireframes"`, `edit "meeting"`)

Example interactive session:
```
notes: > ls                           # Show context-aware active tasks
notes: > package Website Redesign
notes:Website Redesign > ls           # Now shows only tasks in this package
notes:Website Redesign > comp[TAB]    # Tab completion → 'complete'
notes:Website Redesign > complete "wireframes"  # Complete by partial title
notes:Website Redesign > edit "mockups"         # Edit by partial title
notes:Website Redesign > create-task "Review final designs"
notes:Website Redesign > gui          # Launch web interface
notes:Website Redesign > quit
```

### CLI Usage (Direct Commands)

You can also use direct commands for scripting and automation:

```bash
# Create a package (project)
notes package create "My Project" --description "A sample project"

# Create tasks
notes task create "Setup development environment" --priority high --package "My Project"
notes task create "Write documentation" --due "2024-01-15" --tags "docs,writing"

# List tasks
notes task list
notes task list --status pending --priority high

# Create notes
notes note create "Meeting Notes" --content "Discussion about project timeline"

# Search everything
notes search "documentation"

# Start web server
notes server start --port 8080
```

### Web GUI

Start the web server and open your browser:

```bash
notes server start
# Open http://localhost:8080 in your browser
```

## CLI Commands

### Interactive Mode Commands

When in interactive mode (`notes` without arguments), you can use these commands:

#### General Commands
- `help` - Show all available commands
- `status` - Show current statistics and status
- `quit` or `exit` - Exit the application
- `clear` - Clear the screen
- `gui` - Launch web GUI in browser

#### Quick Views
- `list` or `ls` - Context-aware list of active tasks with priority indicators
  - Shows overdue tasks with warnings
  - Displays due dates and priorities with icons
  - Filtered by current package if one is selected
  - Sorted by priority and due date

#### Package Commands
- `packages` or `p` - List all packages
- `package <name>` - Switch to a specific package
- `create-package <name>` - Create a new package
- `package-info` - Show current package details

#### Task Commands
- `tasks` or `t` - List tasks (filtered by current package)
- `task <id>` - Show detailed task information
- `create-task <title>` - Create a new task interactively
- `edit <id>` - Interactive edit task with arrow keys
- `complete <id>` - Mark a task as completed
- `rm <id>, remove <id>` - Delete a task
- `archive <id>` - Archive a task

#### Note Commands
- `notes` or `n` - List notes (filtered by current package)
- `note <id>` - Show detailed note information
- `create-note <title>` - Create a new note interactively
- `delete-note <id>` - Delete a note

#### Search Commands
- `search <query>` or `s <query>` - Search across all content
- `find <query>` - Alias for search

### Direct CLI Commands

### Task Commands
- `notes task create <title> [options]` - Create a new task
- `notes task list [filters]` - List tasks
- `notes task update <id> [options]` - Update a task
- `notes task complete <id>` - Mark task as completed
- `notes task delete <id>` - Delete a task

### Note Commands
- `notes note create <title> [options]` - Create a new note
- `notes note list [filters]` - List notes
- `notes note edit <id>` - Edit a note
- `notes note delete <id>` - Delete a note

### Package Commands
- `notes package create <name> [options]` - Create a new package
- `notes package list` - List packages
- `notes package archive <id>` - Archive a package

### Global Commands
- `notes search <query>` - Search across all content
- `notes server start [--port PORT]` - Start web server

## Command Options

### Task Options
- `--due <date>` - Set due date (YYYY-MM-DD, "tomorrow", "next week")
- `--priority <level>` - Set priority (low, medium, high, urgent)
- `--package <name>` - Assign to package
- `--tags <tag1,tag2>` - Add comma-separated tags
- `--status <status>` - Set status (pending, in-progress, completed, cancelled)

### Output Options
- `--format <format>` - Output format (table, json, markdown)

## Data Storage

All data is stored locally in `~/.notes/`:
- `database.sqlite` - Main SQLite database
- `config.json` - User preferences (future feature)

## Development

### Run Tests
```bash
python test_basic.py
```

### Project Structure
```
taskmanager/
├── models/          # Data models (Task, Note, Package)
├── database/        # Database layer and schema
├── cli/             # Command-line interface
├── api/             # Flask web API
├── gui/             # Web GUI (embedded in API)
└── utils/           # Utility functions
```

## API Endpoints

The web server provides a RESTful API:

- `GET /api/tasks` - List tasks
- `POST /api/tasks` - Create task
- `GET /api/tasks/:id` - Get specific task
- `PUT /api/tasks/:id` - Update task
- `DELETE /api/tasks/:id` - Delete task
- Similar endpoints for notes (`/api/notes`) and packages (`/api/packages`)
- `GET /api/search?q=query` - Global search
- `GET /api/stats` - Dashboard statistics

## License

MIT License