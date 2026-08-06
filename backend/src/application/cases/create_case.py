"""Create Case Use Case."""
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from ....domain.entities import Case
from ....domain.value_objects import UserId, CaseStatus, CaseId
from ....domain.events import CaseCreated
from ....infrastructure.db.repositories import CaseRepository
from ....infrastructure.db.database import get_async_session_factory


@dataclass
class CreateCaseCommand:
    """Command to create a new case."""
    title: str
    created_by: UUID
    tags: list[str] = None


@dataclass
class CreateCaseResult:
    """Result of create case operation."""
    case: Case
    event: CaseCreated


class CreateCaseUseCase:
    """Use case for creating a new investigation case."""

    def __init__(self, case_repo: CaseRepository = None):
        self.case_repo = case_repo or CaseRepository()

    async def execute(self, command: CreateCaseCommand) -> CreateCaseResult:
        """Execute the create case use case."""
        async_session_factory = get_async_session_factory()
        async with async_session_factory() as session:
            # Create domain entity
            case = Case.create(
                title=command.title,
                created_by=UserId(command.created_by),
                tags=command.tags or [],
            )

            # Convert to persistence model
            from ....infrastructure.db.models import CaseModel
            case_model = CaseModel(
                id=case.id.value,
                title=case.title,
                status=case.status.value,
                created_by=case.created_by.value,
                created_at=case.created_at,
                tags=case.tags,
            )

            # Persist
            created_case_model = await self.case_repo.create(session, case_model)
            await session.commit()

            # Create domain event
            event = CaseCreated(
                case_id=CaseId(created_case_model.id),
                title=created_case_model.title,
                created_by=UserId(created_case_model.created_by),
            )

            return CreateCaseResult(
                case=case,
                event=event,
            )