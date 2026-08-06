"""Case-Evidence link entity."""
from dataclasses import dataclass
from datetime import datetime

from ..value_objects import CaseId, EvidenceId, UserId


@dataclass
class CaseEvidence:
    """Many-to-many link between cases and evidence."""
    case_id: CaseId
    evidence_id: EvidenceId
    linked_by: UserId
    linked_at: datetime

    @classmethod
    def create(cls, case_id: CaseId, evidence_id: EvidenceId, linked_by: UserId) -> "CaseEvidence":
        """Create a new case-evidence link."""
        return cls(
            case_id=case_id,
            evidence_id=evidence_id,
            linked_by=linked_by,
            linked_at=datetime.utcnow(),
        )