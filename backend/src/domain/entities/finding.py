"""Finding entity."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

from ..value_objects import ConfidenceLevel


@dataclass
class Finding:
    """Finding entity representing extracted information from evidence."""
    id: UUID
    snapshot_id: UUID
    key: str
    value: dict[str, Any]  # JSONB
    confidence_level: ConfidenceLevel
    confidence_score: float
    extraction_method: str
    created_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(
        cls,
        snapshot_id: UUID,
        key: str,
        value: dict[str, Any],
        confidence_level: ConfidenceLevel,
        confidence_score: float,
        extraction_method: str,
    ) -> "Finding":
        """Create a new finding."""
        from uuid import uuid4
        return cls(
            id=uuid4(),
            snapshot_id=snapshot_id,
            key=key,
            value=value,
            confidence_level=confidence_level,
            confidence_score=confidence_score,
            extraction_method=extraction_method,
        )