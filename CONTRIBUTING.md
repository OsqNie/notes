# Contributing to Notes Task Manager

Thank you for your interest in contributing to Notes Task Manager! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Style Guidelines](#style-guidelines)
- [Project Structure](#project-structure)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment
4. Make your changes
5. Test your changes
6. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

### Installation

1. Clone your fork:
```bash
git clone https://github.com/yourusername/notes-task-manager.git
cd notes-task-manager
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install -e .
```

4. Verify installation:
```bash
notes --help
python example_usage.py
```

## Making Changes

### Branch Naming

- Feature branches: `feature/description-of-feature`
- Bug fixes: `fix/description-of-bug`
- Documentation: `docs/description-of-change`

### Commit Messages

- Use clear, descriptive commit messages
- Start with a verb in present tense (Add, Fix, Update, etc.)
- Keep the first line under 50 characters
- Add detailed description if necessary

Example:
```
Add task filtering by priority level

- Implement priority-based filtering in CLI
- Add priority filter to web GUI
- Update API endpoints to support priority queries
- Add tests for new filtering functionality
```

## Testing

### Running Tests

```bash
# Run basic functionality tests
python test_basic.py

# Test CLI commands
notes task list
notes --help

# Test web server
notes server start --port 8080
```

### Test Coverage

When adding new features, please include:
- Unit tests for core functionality
- Integration tests for CLI commands
- API endpoint tests
- Web GUI functionality tests (when applicable)

### Manual Testing Checklist

Before submitting changes, verify:
- [ ] CLI commands work as expected
- [ ] Web GUI loads and functions properly
- [ ] Database operations complete successfully
- [ ] No errors in console/logs
- [ ] Cross-platform compatibility (if applicable)

## Submitting Changes

### Pull Request Process

1. Ensure your fork is up to date with the main repository
2. Create a feature branch from `main`
3. Make your changes and commit them
4. Push your branch to your fork
5. Open a pull request with a clear title and description

### Pull Request Template

```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing
- [ ] Tested locally
- [ ] Added/updated tests
- [ ] All existing tests pass

## Screenshots (if applicable)
Add screenshots for UI changes.

## Additional Notes
Any additional information or context.
```

## Style Guidelines

### Python Code Style

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings for functions and classes
- Keep functions focused and single-purpose
- Use type hints where appropriate

### Example:

```python
def create_task(title: str, description: str = None, priority: str = "medium") -> Task:
    """Create a new task with the given parameters.
    
    Args:
        title: The task title (required)
        description: Optional task description
        priority: Task priority level (default: medium)
        
    Returns:
        Task: The created task object
        
    Raises:
        ValueError: If title is empty or priority is invalid
    """
    if not title.strip():
        raise ValueError("Task title cannot be empty")
    
    # Implementation here
    pass
```

### CLI Guidelines

- Use consistent command naming
- Provide helpful error messages
- Include `--help` documentation for all commands
- Support both short and long option names where appropriate

### Web GUI Guidelines

- Maintain responsive design principles
- Use semantic HTML elements
- Follow accessibility best practices
- Keep JavaScript vanilla or use minimal dependencies

## Project Structure

```
notes-task-manager/
├── notes/                  # Main package
│   ├── api/               # Flask web API
│   ├── cli/               # Command-line interface
│   ├── database/          # Database layer
│   ├── gui/               # Web GUI files
│   ├── models/            # Data models
│   └── utils/             # Utility functions
├── tests/                 # Test files (to be added)
├── docs/                  # Documentation (future)
├── example_usage.py       # Usage examples
├── requirements.txt       # Python dependencies
├── setup.py              # Package configuration
├── README.md             # Main documentation
├── CHANGELOG.md          # Version history
└── CONTRIBUTING.md       # This file
```

### Key Components

- **Models**: Define data structures (Task, Note, Package)
- **Database**: Handle SQLite operations and schema
- **CLI**: Command-line interface using Click framework
- **API**: RESTful API using Flask
- **GUI**: Web interface with HTML/CSS/JavaScript

## Feature Requests and Bug Reports

### Reporting Bugs

When reporting bugs, please include:
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- System information (OS, Python version)
- Error messages or logs

### Suggesting Features

For feature requests, please describe:
- The problem you're trying to solve
- Your proposed solution
- Any alternative solutions considered
- How this would benefit other users

## Getting Help

- Check existing issues and documentation first
- Open an issue for questions or problems
- Join discussions in existing issues
- Be patient and respectful when asking for help

## Recognition

Contributors will be recognized in:
- The project's contributors list
- Release notes for significant contributions
- Special thanks in documentation

Thank you for contributing to Notes Task Manager!