import sqlite3
import os
from pathlib import Path


def get_database_path():
    """Get the path to the SQLite database file."""
    home_dir = Path.home()
    notes_dir = home_dir / '.notes'
    notes_dir.mkdir(exist_ok=True)
    return notes_dir / 'database.sqlite'


def create_tables(conn: sqlite3.Connection):
    """Create all necessary tables in the database."""
    
    # Create tasks table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL DEFAULT 'pending',
            priority TEXT NOT NULL DEFAULT 'medium',
            due_date TEXT,
            package_id TEXT,
            tags TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            completed_at TEXT,
            FOREIGN KEY (package_id) REFERENCES packages (id)
        )
    ''')
    
    # Create notes table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT,
            package_id TEXT,
            linked_tasks TEXT,
            tags TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (package_id) REFERENCES packages (id)
        )
    ''')
    
    # Create packages table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS packages (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            parent_id TEXT,
            due_date TEXT,
            status TEXT NOT NULL DEFAULT 'active',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (parent_id) REFERENCES packages (id)
        )
    ''')
    
    # Create indexes for better performance
    conn.execute('CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_tasks_package_id ON tasks(package_id)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_notes_package_id ON notes(package_id)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_packages_parent_id ON packages(parent_id)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_packages_status ON packages(status)')
    
    conn.commit()


def initialize_database():
    """Initialize the database with tables and return the connection."""
    db_path = get_database_path()
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row  # Enable column access by name
    create_tables(conn)
    return conn