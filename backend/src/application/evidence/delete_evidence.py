"""Delete Evidence Use Case."""
from dataclasses import dataclass
from uuid import UUID

from ....domain.events import EvidenceDeleted
from ....infrastructure.db.repositories import EvidenceRepository
from ....infrastructure.db.database import get_async_session_factory
from ....infrastructure.storage import get_minio_client


@dataclass
class DeleteEvidenceCommand:
    """Command to delete evidence."""
    evidence_id: UUID
    deleted_by: UUID


@dataclass
class DeleteEvidenceResult:
    """Result of delete evidence operation."""
    event: EvidenceDeleted


class DeleteEvidenceUseCase:
    """Use case for deleting evidence."""

    def __init__(
        self,
        evidence_repo: EvidenceRepository = None,
        storage_client = None,
    ):
        self.evidence_repo = evidence_repo or EvidenceRepository()
        self.storage_client = storage_client or get_minio_client()

    async def execute(self, command: DeleteEvidenceCommand) -> DeleteEvidenceResult:
        """Execute the delete evidence use case."""
        async_session_factory = get_async_session_factory()
        async with async_session_factory() as session:
            evidence = await self.evidence_repo.get(session, command.evidence_id)
            if not evidence:
                raise ValueError(f"Evidence not found: {command.evidence_id}")

            # Delete from MinIO
            self.storage_client.delete_file(evidence.storage_location)

            # Delete from database
            await self.evidence_repo.delete(session, command.evidence_id)
            await session.commit()

            # Create domain event
            event = EvidenceDeleted(
                evidence_id=command.evidence_id,
                deleted_by=command.deleted_by,
            )

            return DeleteEvidenceResult(event=event)