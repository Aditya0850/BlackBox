"""Case domain events."""
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from ..value_objects import CaseId, UserId


@dataclass(frozen=True)
class CaseCreated:
    """Event fired when a case is created."""
    case_id: CaseId
    title: str
    created_by: UserId
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class CaseClosed:
    """Event fired when a case is closed."""
    case_id: CaseId
    closed_by: UserId
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class CaseArchived:
    """Event fired when a case is archived."""
    case_id: CaseId
    archived_by: UserId
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class CaseReopened:
    """Event fired when a case is reopened."""
    case_id: CaseId
    reopened_by: UserId
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class CaseTagAdded:
    """Event fired when a tag is added to a case."""
    case_id: CaseId
    tag: str
    added_by: UserId
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class CaseTagRemoved:
    """Event fired when a tag is removed from a case."""
    case_id: CaseId
    tag: str
    removed_by: UserId
    occurred_at: datetime = field(default_factory=datetime.utcnow)