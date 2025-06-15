import sqlite3
import json
from typing import List, Optional, Dict, Any
from datetime import datetime

from .schema import initialize_database
from ..models import Task, Note, Package


class Database:
    def __init__(self):
        self.conn = initialize_database()

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # Task operations
    def create_task(self, task: Task) -> Task:
        """Create a new task in the database."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO tasks (id, title, description, status, priority, due_date, 
                             package_id, tags, created_at, updated_at, completed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task.id, task.title, task.description, task.status, task.priority,
            task.due_date.isoformat() if task.due_date else None,
            task.package_id, json.dumps(task.tags),
            task.created_at.isoformat(), task.updated_at.isoformat(),
            task.completed_at.isoformat() if task.completed_at else None
        ))
        self.conn.commit()
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        row = cursor.fetchone()
        if row:
            return self._row_to_task(row)
        return None

    def update_task(self, task: Task) -> Task:
        """Update an existing task."""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE tasks SET title = ?, description = ?, status = ?, priority = ?,
                           due_date = ?, package_id = ?, tags = ?, updated_at = ?, completed_at = ?
            WHERE id = ?
        ''', (
            task.title, task.description, task.status, task.priority,
            task.due_date.isoformat() if task.due_date else None,
            task.package_id, json.dumps(task.tags),
            task.updated_at.isoformat(),
            task.completed_at.isoformat() if task.completed_at else None,
            task.id
        ))
        self.conn.commit()
        return task

    def delete_task(self, task_id: str) -> bool:
        """Delete a task by ID."""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def list_tasks(self, filters: Optional[Dict[str, Any]] = None) -> List[Task]:
        """List tasks with optional filters."""
        query = 'SELECT * FROM tasks WHERE 1=1'
        params = []

        if filters:
            if filters.get('status'):
                query += ' AND status = ?'
                params.append(filters['status'])
            if filters.get('priority'):
                query += ' AND priority = ?'
                params.append(filters['priority'])
            if filters.get('package_id'):
                query += ' AND package_id = ?'
                params.append(filters['package_id'])

        query += ' ORDER BY created_at DESC'
        
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [self._row_to_task(row) for row in rows]

    def _row_to_task(self, row) -> Task:
        """Convert database row to Task object."""
        data = {
            'id': row['id'],
            'title': row['title'],
            'description': row['description'],
            'status': row['status'],
            'priority': row['priority'],
            'due_date': row['due_date'],
            'package_id': row['package_id'],
            'tags': json.loads(row['tags']) if row['tags'] else [],
            'created_at': row['created_at'],
            'updated_at': row['updated_at'],
            'completed_at': row['completed_at']
        }
        return Task.from_dict(data)

    # Note operations
    def create_note(self, note: Note) -> Note:
        """Create a new note in the database."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO notes (id, title, content, package_id, linked_tasks, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            note.id, note.title, note.content, note.package_id,
            json.dumps(note.linked_tasks), json.dumps(note.tags),
            note.created_at.isoformat(), note.updated_at.isoformat()
        ))
        self.conn.commit()
        return note

    def get_note(self, note_id: str) -> Optional[Note]:
        """Get a note by ID."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM notes WHERE id = ?', (note_id,))
        row = cursor.fetchone()
        if row:
            return self._row_to_note(row)
        return None

    def update_note(self, note: Note) -> Note:
        """Update an existing note."""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE notes SET title = ?, content = ?, package_id = ?, 
                           linked_tasks = ?, tags = ?, updated_at = ?
            WHERE id = ?
        ''', (
            note.title, note.content, note.package_id,
            json.dumps(note.linked_tasks), json.dumps(note.tags),
            note.updated_at.isoformat(), note.id
        ))
        self.conn.commit()
        return note

    def delete_note(self, note_id: str) -> bool:
        """Delete a note by ID."""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def list_notes(self, filters: Optional[Dict[str, Any]] = None) -> List[Note]:
        """List notes with optional filters."""
        query = 'SELECT * FROM notes WHERE 1=1'
        params = []

        if filters:
            if filters.get('package_id'):
                query += ' AND package_id = ?'
                params.append(filters['package_id'])

        query += ' ORDER BY updated_at DESC'
        
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [self._row_to_note(row) for row in rows]

    def _row_to_note(self, row) -> Note:
        """Convert database row to Note object."""
        data = {
            'id': row['id'],
            'title': row['title'],
            'content': row['content'],
            'package_id': row['package_id'],
            'linked_tasks': json.loads(row['linked_tasks']) if row['linked_tasks'] else [],
            'tags': json.loads(row['tags']) if row['tags'] else [],
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }
        return Note.from_dict(data)

    # Package operations
    def create_package(self, package: Package) -> Package:
        """Create a new package in the database."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO packages (id, name, description, parent_id, due_date, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            package.id, package.name, package.description, package.parent_id,
            package.due_date.isoformat() if package.due_date else None,
            package.status, package.created_at.isoformat(), package.updated_at.isoformat()
        ))
        self.conn.commit()
        return package

    def get_package(self, package_id: str) -> Optional[Package]:
        """Get a package by ID."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM packages WHERE id = ?', (package_id,))
        row = cursor.fetchone()
        if row:
            return self._row_to_package(row)
        return None

    def update_package(self, package: Package) -> Package:
        """Update an existing package."""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE packages SET name = ?, description = ?, parent_id = ?, 
                              due_date = ?, status = ?, updated_at = ?
            WHERE id = ?
        ''', (
            package.name, package.description, package.parent_id,
            package.due_date.isoformat() if package.due_date else None,
            package.status, package.updated_at.isoformat(), package.id
        ))
        self.conn.commit()
        return package

    def delete_package(self, package_id: str) -> bool:
        """Delete a package by ID."""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM packages WHERE id = ?', (package_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def list_packages(self, filters: Optional[Dict[str, Any]] = None) -> List[Package]:
        """List packages with optional filters."""
        query = 'SELECT * FROM packages WHERE 1=1'
        params = []

        if filters:
            if filters.get('status'):
                query += ' AND status = ?'
                params.append(filters['status'])
            if filters.get('parent_id'):
                query += ' AND parent_id = ?'
                params.append(filters['parent_id'])

        query += ' ORDER BY created_at DESC'
        
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [self._row_to_package(row) for row in rows]

    def _row_to_package(self, row) -> Package:
        """Convert database row to Package object."""
        data = {
            'id': row['id'],
            'name': row['name'],
            'description': row['description'],
            'parent_id': row['parent_id'],
            'due_date': row['due_date'],
            'status': row['status'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }
        return Package.from_dict(data)

    # Search operations
    def search(self, query: str) -> Dict[str, List]:
        """Search across tasks, notes, and packages."""
        results = {
            'tasks': [],
            'notes': [],
            'packages': []
        }

        # Search tasks
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM tasks 
            WHERE title LIKE ? OR description LIKE ?
            ORDER BY updated_at DESC
        ''', (f'%{query}%', f'%{query}%'))
        results['tasks'] = [self._row_to_task(row) for row in cursor.fetchall()]

        # Search notes
        cursor.execute('''
            SELECT * FROM notes 
            WHERE title LIKE ? OR content LIKE ?
            ORDER BY updated_at DESC
        ''', (f'%{query}%', f'%{query}%'))
        results['notes'] = [self._row_to_note(row) for row in cursor.fetchall()]

        # Search packages
        cursor.execute('''
            SELECT * FROM packages 
            WHERE name LIKE ? OR description LIKE ?
            ORDER BY updated_at DESC
        ''', (f'%{query}%', f'%{query}%'))
        results['packages'] = [self._row_to_package(row) for row in cursor.fetchall()]

        return results