"""List Evidence Use Case."""
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from ....domain.entities import Evidence
from ....domain.value_objects import EvidenceId
from ....infrastructure.db.repositories import EvidenceRepository
from ....infrastructure.db.database import get_async_session_factory


@dataclass
class ListEvidenceQuery:
    """Query to list evidence with pagination and filters."""
    offset: int = 0
    limit: int = 100
    mime_type: Optional[str] = None
    case_id: Optional[UUID] = None


@dataclass
class ListEvidenceResult:
    """Result of list evidence operation."""
    evidence: list[Evidence]
    total: int
    offset: int
    limit: int


class ListEvidenceUseCase:
    """Use case for listing evidence with pagination and filters."""

    def __init__(self, evidence_repo: EvidenceRepository = None):
        self.evidence_repo = evidence_repo or EvidenceRepository()

    async def execute(self, query: ListEvidenceQuery) -> ListEvidenceResult:
        """Execute the list evidence use case."""
        async_session_factory = get_async_session_factory()
        async with async_session_factory() as session:
            evidence_models = await self.evidence_repo.list(
                session,
                offset=query.offset,
                limit=query.limit,
                mime_type=query.mime_type,
                case_id=query.case_id,
            )

            total = await self.evidence_repo.count_by_case(session, query.case_id) if query.case_id else len(evidence_models)

            evidence = [self._model_to_entity(model) for model in evidence_models]

            return ListEvidenceResult(
                evidence=evidence,
                total=total,
                offset=query.offset,
                limit=query.limit,
            )

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
        evidence.case_ids = [link.case_id for link in model.case_links]
        return evidence