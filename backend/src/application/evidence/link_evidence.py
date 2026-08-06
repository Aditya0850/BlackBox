"""Link Evidence to Case Use Case."""
from dataclasses import dataclass
from uuid import UUID
from datetime import datetime

from ....domain.events import EvidenceLinkedToCase
from ....infrastructure.db.repositories import EvidenceRepository, CaseRepository
from ....infrastructure.db.database import get_async_session_factory


@dataclass
class LinkEvidenceCommand:
    """Command to link evidence to a case."""
    evidence_id: UUID
    case_id: UUID
    linked_by: UUID


@dataclass
class LinkEvidenceResult:
    """Result of link evidence operation."""
    event: EvidenceLinkedToCase


class LinkEvidenceToCaseUseCase:
    """Use case for linking evidence to a case."""

    def __init__(
        self,
        evidence_repo: EvidenceRepository = None,
        case_repo: CaseRepository = None,
    ):
        self.evidence_repo = evidence_repo or EvidenceRepository()
        self.case_repo = case_repo or CaseRepository()

    async def execute(self, command: LinkEvidenceCommand) -> LinkEvidenceResult:
        """Execute the link evidence to case use case."""
        async_session_factory = get_async_session_factory()
        async with async_session_factory() as session:
            evidence = await self.evidence_repo.get(session, command.evidence_id)
            if not evidence:
                raise ValueError(f"Evidence not found: {command.evidence_id}")

            case = await self.case_repo.get(session, command.case_id)
            if not case:
                raise ValueError(f"Case not found: {command.case_id}")

            # Check if already linked
            existing_link = any(link.case_id == command.case_id for link in evidence.case_links)
            if existing_link:
                raise ValueError("Evidence already linked to this case")

            # Create link
            from ....infrastructure.db.models import CaseEvidenceModel
            link = CaseEvidenceModel(
                case_id=command.case_id,
                evidence_id=command.evidence_id,
                linked_by=command.linked_by,
            )
            session.add(link)
            await session.commit()

            # Create domain event
            event = EvidenceLinkedToCase(
                evidence_id=command.evidence_id,
                case_id=command.case_id,
                linked_by=command.linked_by,
            )

            return LinkEvidenceResult(event=event)