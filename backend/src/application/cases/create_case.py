"""Create Case Use Case."""
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from sqlalchemy import text

from src.domain.entities import Case
from src.domain.value_objects import UserId, CaseStatus, CaseId, CaseNumber
from src.domain.events import CaseCreated
from src.infrastructure.db.repositories import CaseRepository
from src.infrastructure.db.database import get_async_session_factory


@dataclass
class CreateCaseCommand:
    """Command to create a new case."""
    title: str
    created_by: UUID
    tags: list[str] = None
    description: str = ""


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
            # Get next case number from DB sequence
            result = await session.execute(text("SELECT intel.next_case_number()"))
            case_number_str = result.scalar()

            case_number = CaseNumber.parse(case_number_str)

            # Create domain entity
            case = Case.create(
                title=command.title,
                created_by=UserId(command.created_by),
                tags=command.tags or [],
                case_number=case_number,
                description=command.description or "",
            )

            # Convert to persistence model
            from src.infrastructure.db.models import CaseModel
            case_model = CaseModel(
                id=case.id.value,
                title=case.title,
                case_number=case.case_number.value,
                description=case.description,
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
                case_number=created_case_model.case_number,
                title=created_case_model.title,
                description=created_case_model.description,
                created_by=UserId(created_case_model.created_by),
            )

            return CreateCaseResult(
                case=case,
                event=event,
            )