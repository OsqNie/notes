from flask import Flask, request, jsonify, send_from_directory, send_file
from datetime import datetime
from dateutil.parser import parse as parse_date
import os

from ..database import Database
from ..models import Task, Note, Package


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config['JSON_SORT_KEYS'] = False

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500

    # Task endpoints
    @app.route('/api/tasks', methods=['GET'])
    def get_tasks():
        """Get list of tasks with optional filtering."""
        with Database() as db:
            filters = {}
            
            # Parse query parameters
            if request.args.get('status'):
                filters['status'] = request.args.get('status')
            if request.args.get('priority'):
                filters['priority'] = request.args.get('priority')
            if request.args.get('package_id'):
                filters['package_id'] = request.args.get('package_id')
            
            tasks = db.list_tasks(filters)
            return jsonify([task.to_dict() for task in tasks])

    @app.route('/api/tasks', methods=['POST'])
    def create_task():
        """Create a new task."""
        data = request.get_json()
        if not data or not data.get('title'):
            return jsonify({'error': 'Title is required'}), 400
            
        with Database() as db:
            try:
                # Parse due date if provided
                due_date = None
                if data.get('due_date'):
                    due_date = parse_date(data['due_date'])
                
                task = Task(
                    title=data['title'],
                    description=data.get('description'),
                    status=data.get('status', 'pending'),
                    priority=data.get('priority', 'medium'),
                    due_date=due_date,
                    package_id=data.get('package_id'),
                    tags=data.get('tags', [])
                )
                
                created_task = db.create_task(task)
                return jsonify(created_task.to_dict()), 201
                
            except Exception as e:
                return jsonify({'error': str(e)}), 400

    @app.route('/api/tasks/<task_id>', methods=['GET'])
    def get_task(task_id):
        """Get a specific task."""
        with Database() as db:
            task = db.get_task(task_id)
            if not task:
                return jsonify({'error': 'Task not found'}), 404
            return jsonify(task.to_dict())

    @app.route('/api/tasks/<task_id>', methods=['PUT'])
    def update_task(task_id):
        """Update an existing task."""
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        with Database() as db:
            task = db.get_task(task_id)
            if not task:
                return jsonify({'error': 'Task not found'}), 404
                
            try:
                # Update fields if provided
                if 'title' in data:
                    task.title = data['title']
                if 'description' in data:
                    task.description = data['description']
                if 'status' in data:
                    task.update_status(data['status'])
                if 'priority' in data:
                    task.priority = data['priority']
                if 'due_date' in data:
                    task.due_date = parse_date(data['due_date']) if data['due_date'] else None
                if 'package_id' in data:
                    task.package_id = data['package_id']
                if 'tags' in data:
                    task.tags = data['tags']
                    
                task.updated_at = datetime.now()
                updated_task = db.update_task(task)
                return jsonify(updated_task.to_dict())
                
            except Exception as e:
                return jsonify({'error': str(e)}), 400

    @app.route('/api/tasks/<task_id>', methods=['DELETE'])
    def delete_task(task_id):
        """Delete a task."""
        with Database() as db:
            if not db.get_task(task_id):
                return jsonify({'error': 'Task not found'}), 404
                
            if db.delete_task(task_id):
                return '', 204
            else:
                return jsonify({'error': 'Failed to delete task'}), 500

    # Note endpoints
    @app.route('/api/notes', methods=['GET'])
    def get_notes():
        """Get list of notes with optional filtering."""
        with Database() as db:
            filters = {}
            
            if request.args.get('package_id'):
                filters['package_id'] = request.args.get('package_id')
            
            notes = db.list_notes(filters)
            return jsonify([note.to_dict() for note in notes])

    @app.route('/api/notes', methods=['POST'])
    def create_note():
        """Create a new note."""
        data = request.get_json()
        if not data or not data.get('title'):
            return jsonify({'error': 'Title is required'}), 400
            
        with Database() as db:
            try:
                note = Note(
                    title=data['title'],
                    content=data.get('content', ''),
                    package_id=data.get('package_id'),
                    linked_tasks=data.get('linked_tasks', []),
                    tags=data.get('tags', [])
                )
                
                created_note = db.create_note(note)
                return jsonify(created_note.to_dict()), 201
                
            except Exception as e:
                return jsonify({'error': str(e)}), 400

    @app.route('/api/notes/<note_id>', methods=['GET'])
    def get_note(note_id):
        """Get a specific note."""
        with Database() as db:
            note = db.get_note(note_id)
            if not note:
                return jsonify({'error': 'Note not found'}), 404
            return jsonify(note.to_dict())

    @app.route('/api/notes/<note_id>', methods=['PUT'])
    def update_note(note_id):
        """Update an existing note."""
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        with Database() as db:
            note = db.get_note(note_id)
            if not note:
                return jsonify({'error': 'Note not found'}), 404
                
            try:
                # Update fields if provided
                if 'title' in data:
                    note.title = data['title']
                if 'content' in data:
                    note.content = data['content']
                if 'package_id' in data:
                    note.package_id = data['package_id']
                if 'linked_tasks' in data:
                    note.linked_tasks = data['linked_tasks']
                if 'tags' in data:
                    note.tags = data['tags']
                    
                note.updated_at = datetime.now()
                updated_note = db.update_note(note)
                return jsonify(updated_note.to_dict())
                
            except Exception as e:
                return jsonify({'error': str(e)}), 400

    @app.route('/api/notes/<note_id>', methods=['DELETE'])
    def delete_note(note_id):
        """Delete a note."""
        with Database() as db:
            if not db.get_note(note_id):
                return jsonify({'error': 'Note not found'}), 404
                
            if db.delete_note(note_id):
                return '', 204
            else:
                return jsonify({'error': 'Failed to delete note'}), 500

    # Package endpoints
    @app.route('/api/packages', methods=['GET'])
    def get_packages():
        """Get list of packages with optional filtering."""
        with Database() as db:
            filters = {}
            
            if request.args.get('status'):
                filters['status'] = request.args.get('status')
            if request.args.get('parent_id'):
                filters['parent_id'] = request.args.get('parent_id')
            
            packages = db.list_packages(filters)
            return jsonify([pkg.to_dict() for pkg in packages])

    @app.route('/api/packages', methods=['POST'])
    def create_package():
        """Create a new package."""
        data = request.get_json()
        if not data or not data.get('name'):
            return jsonify({'error': 'Name is required'}), 400
            
        with Database() as db:
            try:
                # Parse due date if provided
                due_date = None
                if data.get('due_date'):
                    due_date = parse_date(data['due_date'])
                
                package = Package(
                    name=data['name'],
                    description=data.get('description'),
                    parent_id=data.get('parent_id'),
                    due_date=due_date,
                    status=data.get('status', 'active')
                )
                
                created_package = db.create_package(package)
                return jsonify(created_package.to_dict()), 201
                
            except Exception as e:
                return jsonify({'error': str(e)}), 400

    @app.route('/api/packages/<package_id>', methods=['GET'])
    def get_package(package_id):
        """Get a specific package with its contents."""
        with Database() as db:
            package = db.get_package(package_id)
            if not package:
                return jsonify({'error': 'Package not found'}), 404
                
            # Get tasks and notes in this package
            tasks = db.list_tasks({'package_id': package_id})
            notes = db.list_notes({'package_id': package_id})
            child_packages = db.list_packages({'parent_id': package_id})
            
            result = package.to_dict()
            result['tasks'] = [task.to_dict() for task in tasks]
            result['notes'] = [note.to_dict() for note in notes]
            result['child_packages'] = [pkg.to_dict() for pkg in child_packages]
            
            return jsonify(result)

    @app.route('/api/packages/<package_id>', methods=['PUT'])
    def update_package(package_id):
        """Update an existing package."""
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        with Database() as db:
            package = db.get_package(package_id)
            if not package:
                return jsonify({'error': 'Package not found'}), 404
                
            try:
                # Update fields if provided
                if 'name' in data:
                    package.name = data['name']
                if 'description' in data:
                    package.description = data['description']
                if 'parent_id' in data:
                    package.parent_id = data['parent_id']
                if 'due_date' in data:
                    package.due_date = parse_date(data['due_date']) if data['due_date'] else None
                if 'status' in data:
                    package.update_status(data['status'])
                    
                package.updated_at = datetime.now()
                updated_package = db.update_package(package)
                return jsonify(updated_package.to_dict())
                
            except Exception as e:
                return jsonify({'error': str(e)}), 400

    @app.route('/api/packages/<package_id>', methods=['DELETE'])
    def delete_package(package_id):
        """Delete a package."""
        with Database() as db:
            if not db.get_package(package_id):
                return jsonify({'error': 'Package not found'}), 404
                
            if db.delete_package(package_id):
                return '', 204
            else:
                return jsonify({'error': 'Failed to delete package'}), 500

    # Search endpoint
    @app.route('/api/search', methods=['GET'])
    def search():
        """Global search across tasks, notes, and packages."""
        query = request.args.get('q')
        if not query:
            return jsonify({'error': 'Query parameter q is required'}), 400
            
        with Database() as db:
            results = db.search(query)
            
            # Convert objects to dictionaries
            return jsonify({
                'tasks': [task.to_dict() for task in results['tasks']],
                'notes': [note.to_dict() for note in results['notes']],
                'packages': [pkg.to_dict() for pkg in results['packages']]
            })

    # Stats endpoint for dashboard
    @app.route('/api/stats', methods=['GET'])
    def get_stats():
        """Get dashboard statistics."""
        with Database() as db:
            # Get counts by status
            all_tasks = db.list_tasks()
            all_notes = db.list_notes()
            all_packages = db.list_packages()
            
            task_stats = {
                'total': len(all_tasks),
                'pending': len([t for t in all_tasks if t.status == 'pending']),
                'in_progress': len([t for t in all_tasks if t.status == 'in-progress']),
                'completed': len([t for t in all_tasks if t.status == 'completed']),
                'cancelled': len([t for t in all_tasks if t.status == 'cancelled'])
            }
            
            note_stats = {
                'total': len(all_notes)
            }
            
            package_stats = {
                'total': len(all_packages),
                'active': len([p for p in all_packages if p.status == 'active']),
                'completed': len([p for p in all_packages if p.status == 'completed']),
                'archived': len([p for p in all_packages if p.status == 'archived'])
            }
            
            return jsonify({
                'tasks': task_stats,
                'notes': note_stats,
                'packages': package_stats
            })

    # Serve static files for GUI
    @app.route('/')
    def index():
        """Serve the main GUI page."""
        gui_dir = os.path.join(os.path.dirname(__file__), '..', 'gui')
        return send_file(os.path.join(gui_dir, 'index.html'))
    
    @app.route('/styles.css')
    def styles():
        """Serve the CSS file."""
        gui_dir = os.path.join(os.path.dirname(__file__), '..', 'gui')
        return send_file(os.path.join(gui_dir, 'styles.css'), mimetype='text/css')
    
    @app.route('/app.js')
    def javascript():
        """Serve the JavaScript file."""
        gui_dir = os.path.join(os.path.dirname(__file__), '..', 'gui')
        return send_file(os.path.join(gui_dir, 'app.js'), mimetype='application/javascript')

    return app