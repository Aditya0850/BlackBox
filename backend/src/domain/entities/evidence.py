"""Evidence entity."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from ..value_objects import CaseId, EvidenceId, MimeType, UserId


@dataclass
class Evidence:
    """Evidence entity representing a piece of forensic evidence."""
    id: EvidenceId
    original_filename: str
    mime_type: MimeType
    file_size_bytes: int
    sha256_hash: str
    storage_location: str
    uploaded_by: UserId
    uploaded_at: datetime
    case_ids: list[CaseId] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        original_filename: str,
        mime_type: MimeType,
        file_size_bytes: int,
        sha256_hash: str,
        storage_location: str,
        uploaded_by: UserId,
    ) -> "Evidence":
        """Create a new evidence record."""
        return cls(
            id=EvidenceId.generate(),
            original_filename=original_filename,
            mime_type=mime_type,
            file_size_bytes=file_size_bytes,
            sha256_hash=sha256_hash,
            storage_location=storage_location,
            uploaded_by=uploaded_by,
            uploaded_at=datetime.utcnow(),
        )

    def link_to_case(self, case_id: "CaseId") -> None:
        """Link evidence to a case."""
        if case_id not in self.case_ids:
            self.case_ids.append(case_id)

    def unlink_from_case(self, case_id: "CaseId") -> None:
        """Unlink evidence from a case."""
        if case_id in self.case_ids:
            self.case_ids.remove(case_id)