"""Case entity."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID

from ..value_objects import CaseId, CaseStatus, UserId


@dataclass
class Case:
    """Case entity representing an investigation case."""
    id: CaseId
    title: str
    status: CaseStatus
    created_by: UserId
    created_at: datetime
    tags: list[str] = field(default_factory=list)
    updated_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None

    @classmethod
    def create(cls, title: str, created_by: UserId, tags: list[str] = None) -> "Case":
        """Create a new case."""
        return cls(
            id=CaseId.generate(),
            title=title,
            status=CaseStatus.OPEN,
            created_by=created_by,
            created_at=datetime.utcnow(),
            tags=tags or [],
        )

    def close(self) -> None:
        """Close the case."""
        if self.status != CaseStatus.OPEN:
            raise ValueError("Only open cases can be closed")
        self.status = CaseStatus.CLOSED
        self.closed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def archive(self) -> None:
        """Archive the case."""
        if self.status != CaseStatus.CLOSED:
            raise ValueError("Only closed cases can be archived")
        self.status = CaseStatus.ARCHIVED
        self.archived_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def reopen(self) -> None:
        """Reopen an archived or closed case."""
        if self.status == CaseStatus.OPEN:
            raise ValueError("Case is already open")
        self.status = CaseStatus.OPEN
        self.closed_at = None
        self.archived_at = None
        self.updated_at = datetime.utcnow()

    def add_tag(self, tag: str) -> None:
        """Add a tag to the case."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.utcnow()

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the case."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.utcnow()