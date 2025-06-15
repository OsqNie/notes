import uuid
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, field


@dataclass
class Task:
    title: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: Optional[str] = None
    status: str = "pending"  # pending, in-progress, completed, cancelled
    priority: str = "medium"  # low, medium, high, urgent
    due_date: Optional[datetime] = None
    package_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'package_id': self.package_id,
            'tags': self.tags,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        task = cls(
            id=data.get('id', str(uuid.uuid4())),
            title=data['title'],
            description=data.get('description'),
            status=data.get('status', 'pending'),
            priority=data.get('priority', 'medium'),
            package_id=data.get('package_id'),
            tags=data.get('tags', [])
        )
        
        if data.get('due_date'):
            task.due_date = datetime.fromisoformat(data['due_date'])
        if data.get('created_at'):
            task.created_at = datetime.fromisoformat(data['created_at'])
        if data.get('updated_at'):
            task.updated_at = datetime.fromisoformat(data['updated_at'])
        if data.get('completed_at'):
            task.completed_at = datetime.fromisoformat(data['completed_at'])
            
        return task

    def mark_completed(self):
        self.status = "completed"
        self.completed_at = datetime.now()
        self.updated_at = datetime.now()

    def update_status(self, status: str):
        valid_statuses = ["pending", "in-progress", "completed", "cancelled"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
        
        self.status = status
        self.updated_at = datetime.now()
        
        if status == "completed" and not self.completed_at:
            self.completed_at = datetime.now()