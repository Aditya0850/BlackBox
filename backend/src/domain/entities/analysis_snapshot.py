"""AnalysisSnapshot entity."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from ..value_objects import EvidenceId


class PipelineTrigger(str, Enum):
    """Pipeline trigger types."""
    UPLOAD = "upload"
    MANUAL_REANALYSIS = "manual_reanalysis"
    SCHEDULED_REANALYSIS = "scheduled_reanalysis"


class InvestigatorApproval(str, Enum):
    """Investigator approval status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class AnalysisSnapshot:
    """Analysis snapshot representing a pipeline run result."""
    id: UUID
    evidence_id: EvidenceId
    pipeline_version: str
    plugin_versions: dict[str, str] = field(default_factory=dict)
    trigger: PipelineTrigger = PipelineTrigger.UPLOAD
    triggered_by: Optional[UUID] = None  # UserId
    is_current: bool = True
    superseded_by: Optional[UUID] = None
    investigator_approval: InvestigatorApproval = InvestigatorApproval.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(
        cls,
        evidence_id: EvidenceId,
        pipeline_version: str,
        plugin_versions: dict[str, str],
        trigger: PipelineTrigger = PipelineTrigger.UPLOAD,
        triggered_by: Optional[UUID] = None,
    ) -> "AnalysisSnapshot":
        """Create a new analysis snapshot."""
        from uuid import uuid4
        return cls(
            id=uuid4(),
            evidence_id=evidence_id,
            pipeline_version=pipeline_version,
            plugin_versions=plugin_versions,
            trigger=trigger,
            triggered_by=triggered_by,
        )

    def supersede(self, new_snapshot_id: UUID) -> None:
        """Mark this snapshot as superseded by another."""
        self.is_current = False
        self.superseded_by = new_snapshot_id

    def approve(self) -> None:
        """Approve the snapshot."""
        self.investigator_approval = InvestigatorApproval.APPROVED

    def reject(self) -> None:
        """Reject the snapshot."""
        self.investigator_approval = InvestigatorApproval.REJECTED