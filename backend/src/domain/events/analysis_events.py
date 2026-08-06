"""Analysis domain events."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID

from ..value_objects import EvidenceId


@dataclass(frozen=True)
class AnalysisSnapshotCreated:
    """Event fired when an analysis snapshot is created."""
    snapshot_id: UUID
    evidence_id: EvidenceId
    pipeline_version: str
    plugin_versions: dict[str, str] = field(default_factory=dict)
    trigger: str = "upload"
    triggered_by: Optional[UUID] = None
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class AnalysisSnapshotSuperseded:
    """Event fired when an analysis snapshot is superseded."""
    old_snapshot_id: UUID
    new_snapshot_id: UUID
    evidence_id: EvidenceId
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class AnalysisSnapshotApproved:
    """Event fired when an analysis snapshot is approved."""
    snapshot_id: UUID
    approved_by: UUID
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class AnalysisSnapshotRejected:
    """Event fired when an analysis snapshot is rejected."""
    snapshot_id: UUID
    rejected_by: UUID
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class FindingAdded:
    """Event fired when a finding is added to a snapshot."""
    finding_id: UUID
    snapshot_id: UUID
    key: str
    confidence_level: str
    confidence_score: float
    extraction_method: str
    occurred_at: datetime = field(default_factory=datetime.utcnow)