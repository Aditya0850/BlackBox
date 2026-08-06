"""Get Evidence Use Case."""
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from ....domain.entities import Evidence
from ....domain.value_objects import EvidenceId
from ....infrastructure.db.repositories import EvidenceRepository
from ....infrastructure.db.database import get_async_session_factory


@dataclass
class GetEvidenceQuery:
    """Query to get evidence by ID."""
    evidence_id: UUID


@dataclass
class GetEvidenceResult:
    """Result of get evidence operation."""
    evidence: Optional[Evidence]


class GetEvidenceUseCase:
    """Use case for retrieving evidence by ID."""

    def __init__(self, evidence_repo: EvidenceRepository = None):
        self.evidence_repo = evidence_repo or EvidenceRepository()

    async def execute(self, query: GetEvidenceQuery) -> GetEvidenceResult:
        """Execute the get evidence use case."""
        async_session_factory = get_async_session_factory()
        async with async_session_factory() as session:
            evidence_model = await self.evidence_repo.get(session, query.evidence_id)
            if not evidence_model:
                return GetEvidenceResult(evidence=None)

            evidence = self._model_to_entity(evidence_model)
            return GetEvidenceResult(evidence=evidence)

    def _model_to_entity(self, model) -> Evidence:
        """Convert persistence model to domain entity."""
        evidence = Evidence(
            id=EvidenceId(model.id),
            original_filename=model.original_filename,
            mime_type=model.mime_type,
            file_size_bytes=model.file_size_bytes,
            sha256_hash=model.sha256_hash,
            storage_location=model.storage_location,
            uploaded_by=model.uploaded_by,
            uploaded_at=model.uploaded_at,
        )
        # Add case links
        evidence.case_ids = [link.case_id for link in model.case_links]
        return evidence