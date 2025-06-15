# Changelog

All notable changes to the Notes Task Manager project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-15

### Added
- Initial release of Notes Task Manager
- **Dual Interface**: Command-line interface and web GUI
- **Task Management**: Create, edit, delete, and track tasks with priorities, due dates, and status
- **Note-Taking System**: Markdown-supported notes with task linking capabilities
- **Project Organization**: Hierarchical packages to organize tasks and notes
- **Interactive CLI Mode**: Context-aware commands with tab completion
- **Web GUI**: Local browser-based interface with real-time updates
- **Search Functionality**: Full-text search across all content
- **Local Storage**: SQLite database for fast, reliable local storage
- **Export Capabilities**: Multiple output formats (table, JSON, markdown)
- **Cross-Platform Support**: Works on Windows, macOS, and Linux

### Features
#### CLI Interface
- Interactive mode with shortened commands (`t`, `n`, `p`, `s`)
- Direct commands for automation and scripting
- Tab completion for commands and identifiers
- Partial ID and title matching
- Context-aware package switching
- Priority and due date indicators

#### Web GUI
- Dashboard with overview statistics
- Drag-and-drop task organization
- Inline editing capabilities
- Responsive design
- Dark/light theme support
- Real-time updates without page refresh

#### Core Functionality
- Task status tracking (pending, in-progress, completed, cancelled)
- Priority levels (low, medium, high, urgent)
- Due date management with natural language support
- Tag-based categorization
- Package (project) hierarchies
- Bulk operations on multiple items
- Advanced filtering and sorting options

#### API
- RESTful API endpoints for all operations
- JSON data format support
- Statistics and dashboard data endpoints
- Global search API

### Technical Specifications
- **Backend**: Python 3.8+
- **Web Framework**: Flask 2.3.3
- **CLI Framework**: Click 8.1.7
- **Database**: SQLite (local storage)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Dependencies**: python-dateutil, markdown

### Documentation
- Comprehensive README with installation and usage instructions
- CLI command reference
- API endpoint documentation
- Example usage script
- Development and testing guidelines

## [Unreleased]

### Planned Features
- Data import/export functionality
- Backup and restore capabilities
- Plugin system for extensions
- Advanced reporting features
- Synchronization options
- Mobile-responsive improvements