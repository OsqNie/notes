import uuid
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class Package:
    name: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: Optional[str] = None
    parent_id: Optional[str] = None
    due_date: Optional[datetime] = None
    status: str = "active"  # active, archived, completed
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'parent_id': self.parent_id,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Package':
        package = cls(
            id=data.get('id', str(uuid.uuid4())),
            name=data['name'],
            description=data.get('description'),
            parent_id=data.get('parent_id'),
            status=data.get('status', 'active')
        )
        
        if data.get('due_date'):
            package.due_date = datetime.fromisoformat(data['due_date'])
        if data.get('created_at'):
            package.created_at = datetime.fromisoformat(data['created_at'])
        if data.get('updated_at'):
            package.updated_at = datetime.fromisoformat(data['updated_at'])
            
        return package

    def archive(self):
        self.status = "archived"
        self.updated_at = datetime.now()

    def mark_completed(self):
        self.status = "completed"
        self.updated_at = datetime.now()

    def update_status(self, status: str):
        valid_statuses = ["active", "archived", "completed"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
        
        self.status = status
        self.updated_at = datetime.now()