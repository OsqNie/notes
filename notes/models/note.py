import uuid
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, field


@dataclass
class Note:
    title: str
    content: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    package_id: Optional[str] = None
    linked_tasks: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'package_id': self.package_id,
            'linked_tasks': self.linked_tasks,
            'tags': self.tags,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Note':
        note = cls(
            id=data.get('id', str(uuid.uuid4())),
            title=data['title'],
            content=data.get('content', ''),
            package_id=data.get('package_id'),
            linked_tasks=data.get('linked_tasks', []),
            tags=data.get('tags', [])
        )
        
        if data.get('created_at'):
            note.created_at = datetime.fromisoformat(data['created_at'])
        if data.get('updated_at'):
            note.updated_at = datetime.fromisoformat(data['updated_at'])
            
        return note

    def update_content(self, content: str):
        self.content = content
        self.updated_at = datetime.now()

    def add_linked_task(self, task_id: str):
        if task_id not in self.linked_tasks:
            self.linked_tasks.append(task_id)
            self.updated_at = datetime.now()

    def remove_linked_task(self, task_id: str):
        if task_id in self.linked_tasks:
            self.linked_tasks.remove(task_id)
            self.updated_at = datetime.now()