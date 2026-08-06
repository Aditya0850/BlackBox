"""Evidence domain events."""
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from ..value_objects import CaseId, EvidenceId, MimeType, UserId


@dataclass(frozen=True)
class EvidenceUploaded:
    """Event fired when evidence is uploaded."""
    evidence_id: EvidenceId
    original_filename: str
    mime_type: MimeType
    file_size_bytes: int
    sha256_hash: str
    storage_location: str
    uploaded_by: UserId
    case_ids: list[CaseId] = field(default_factory=list)
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class EvidenceLinkedToCase:
    """Event fired when evidence is linked to a case."""
    evidence_id: EvidenceId
    case_id: CaseId
    linked_by: UserId
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class EvidenceUnlinkedFromCase:
    """Event fired when evidence is unlinked from a case."""
    evidence_id: EvidenceId
    case_id: CaseId
    unlinked_by: UserId
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class EvidenceDeleted:
    """Event fired when evidence is deleted."""
    evidence_id: EvidenceId
    deleted_by: UserId
    occurred_at: datetime = field(default_factory=datetime.utcnow)