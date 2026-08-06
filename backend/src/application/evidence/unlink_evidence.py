"""Unlink Evidence from Case Use Case."""
from dataclasses import dataclass
from uuid import UUID

from ....domain.events import EvidenceUnlinkedFromCase
from ....infrastructure.db.repositories import EvidenceRepository
from ....infrastructure.db.database import get_async_session_factory


@dataclass
class UnlinkEvidenceCommand:
    """Command to unlink evidence from a case."""
    evidence_id: UUID
    case_id: UUID
    unlinked_by: UUID


@dataclass
class UnlinkEvidenceResult:
    """Result of unlink evidence operation."""
    event: EvidenceUnlinkedFromCase


class UnlinkEvidenceFromCaseUseCase:
    """Use case for unlinking evidence from a case."""

    def __init__(self, evidence_repo: EvidenceRepository = None):
        self.evidence_repo = evidence_repo or EvidenceRepository()

    async def execute(self, command: UnlinkEvidenceCommand) -> UnlinkEvidenceResult:
        """Execute the unlink evidence from case use case."""
        from ....infrastructure.db.models import CaseEvidenceModel
        from sqlalchemy import delete

        async_session_factory = get_async_session_factory()
        async with async_session_factory() as session:
            evidence = await self.evidence_repo.get(session, command.evidence_id)
            if not evidence:
                raise ValueError(f"Evidence not found: {command.evidence_id}")

            # Delete the link
            stmt = delete(CaseEvidenceModel).where(
                CaseEvidenceModel.case_id == command.case_id,
                CaseEvidenceModel.evidence_id == command.evidence_id,
            )
            result = await session.execute(stmt)

            if result.rowcount == 0:
                raise ValueError("Evidence not linked to this case")

            await session.commit()

            # Create domain event
            event = EvidenceUnlinkedFromCase(
                evidence_id=command.evidence_id,
                case_id=command.case_id,
                unlinked_by=command.unlinked_by,
            )

            return UnlinkEvidenceResult(event=event)