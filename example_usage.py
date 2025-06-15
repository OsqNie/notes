#!/usr/bin/env python3
"""
Example usage of the Notes Task Manager CLI and API.
This script demonstrates how to use the Notes Task Manager programmatically.
"""

import os
import sys

# Add the notes module to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from notes.database import Database
from notes.models import Task, Note, Package
from datetime import datetime, timedelta


def create_example_data():
    """Create some example data to demonstrate the Notes Task Manager."""
    print("Creating example data for Notes Task Manager demonstration...\n")
    
    with Database() as db:
        # Create a work project
        work_project = Package(
            name="Website Redesign",
            description="Complete redesign of company website",
            due_date=datetime.now() + timedelta(days=30)
        )
        work_project = db.create_package(work_project)
        print(f"📁 Created project: {work_project.name}")
        
        # Create a personal project
        personal_project = Package(
            name="Personal Organization",
            description="Organize and declutter office space"
        )
        personal_project = db.create_package(personal_project)
        print(f"📁 Created project: {personal_project.name}")
        
        # Create work tasks
        work_tasks = [
            Task(
                title="Research design trends",
                description="Look into current web design trends and best practices",
                priority="high",
                package_id=work_project.id,
                tags=["research", "design"]
            ),
            Task(
                title="Create wireframes",
                description="Design wireframes for main pages",
                priority="high",
                due_date=datetime.now() + timedelta(days=7),
                package_id=work_project.id,
                tags=["design", "wireframes"]
            ),
            Task(
                title="Develop homepage",
                description="Implement the new homepage design",
                priority="medium",
                due_date=datetime.now() + timedelta(days=14),
                package_id=work_project.id,
                tags=["development", "frontend"]
            ),
            Task(
                title="User testing",
                description="Conduct user testing sessions",
                priority="medium",
                due_date=datetime.now() + timedelta(days=21),
                package_id=work_project.id,
                tags=["testing", "ux"]
            )
        ]
        
        # Create personal tasks
        personal_tasks = [
            Task(
                title="Organize desk area",
                description="Clear and organize the main work desk",
                priority="medium",
                package_id=personal_project.id,
                tags=["organization", "workspace"]
            ),
            Task(
                title="File important documents",
                description="Sort and file all loose documents",
                priority="low",
                package_id=personal_project.id,
                tags=["organization", "documents"]
            )
        ]
        
        # Create tasks in database
        created_tasks = []
        for task in work_tasks + personal_tasks:
            created_task = db.create_task(task)
            created_tasks.append(created_task)
            print(f"✅ Created task: {created_task.title}")
        
        # Create some notes
        notes = [
            Note(
                title="Design Inspiration",
                content="""# Design Inspiration Collection

## Modern Website Trends
- Minimalist layouts
- Bold typography
- Subtle animations
- Mobile-first approach

## Color Schemes
- Monochromatic palettes
- High contrast combinations
- Nature-inspired colors

## Reference Sites
- example-design-site.com
- inspiration-gallery.net
- modern-web-showcase.org
""",
                package_id=work_project.id,
                tags=["design", "inspiration", "reference"]
            ),
            Note(
                title="Meeting Notes - Design Review",
                content="""# Design Review Meeting - 2024-01-10

**Attendees:** Team Lead, Designer, Developer

## Key Points
- Homepage should emphasize company values
- Need clear call-to-action buttons
- Mobile responsiveness is critical
- Brand colors must be consistent

## Action Items
- Update color palette
- Create mobile mockups
- Review competitor sites

## Follow-up
Schedule next review for wireframe presentation.
""",
                package_id=work_project.id,
                tags=["meeting", "review", "action-items"]
            ),
            Note(
                title="Organization Tips",
                content="""# Workspace Organization Tips

## Daily Habits
- Clear desk at end of each day
- File documents immediately
- Use inbox system for new items

## Weekly Tasks
- Review and archive completed projects
- Update task priorities
- Clean workspace thoroughly

## Tools
- Label maker for filing
- Desktop organizer
- Digital task manager (this app!)
""",
                package_id=personal_project.id,
                tags=["organization", "productivity", "tips"]
            )
        ]
        
        # Create notes in database
        created_notes = []
        for note in notes:
            created_note = db.create_note(note)
            created_notes.append(created_note)
            print(f"📝 Created note: {created_note.title}")
        
        print(f"\n🎉 Example data created successfully!")
        print(f"   Projects: {len([work_project, personal_project])}")
        print(f"   Tasks: {len(created_tasks)}")
        print(f"   Notes: {len(created_notes)}")
        
        return work_project, personal_project, created_tasks, created_notes


def demonstrate_cli_usage():
    """Demonstrate programmatic usage of the CLI functionality."""
    print("\n" + "="*50)
    print("DEMONSTRATION: Programmatic Usage")
    print("="*50)
    
    with Database() as db:
        # Show all tasks
        print("\n📋 All Tasks:")
        tasks = db.get_tasks()
        for task in tasks[:5]:  # Show first 5
            status_icon = "✅" if task.status == "completed" else "🔄" if task.status == "in-progress" else "⏳"
            priority_icon = "🔴" if task.priority == "urgent" else "🟠" if task.priority == "high" else "🟡" if task.priority == "medium" else "🟢"
            print(f"  {status_icon} {priority_icon} {task.title}")
        
        # Show all packages
        print("\n📁 All Packages:")
        packages = db.get_packages()
        for package in packages:
            task_count = len(db.get_tasks(package_id=package.id))
            print(f"  📦 {package.name} ({task_count} tasks)")
        
        # Demonstrate search
        print("\n🔍 Search Results for 'design':")
        search_results = db.search("design")
        for result in search_results[:3]:  # Show first 3
            print(f"  🎯 {result['title']} ({result['type']})")


def main():
    """Main demonstration function."""
    print("🚀 Notes Task Manager - Example Usage Demonstration")
    print("=" * 55)
    
    # Create example data
    create_example_data()
    
    # Demonstrate usage
    demonstrate_cli_usage()
    
    print(f"\n💡 Try these commands:")
    print(f"   notes                    # Start interactive mode")
    print(f"   notes task list          # List all tasks")
    print(f"   notes package list       # List all packages")
    print(f"   notes search design      # Search for 'design'")
    print(f"   notes server start       # Start web GUI")
    
    print(f"\n🎯 Database location: ~/.notes/database.sqlite")
    print(f"✨ Ready to use! Run 'notes' to get started.")


if __name__ == "__main__":
    main()