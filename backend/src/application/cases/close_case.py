"""Close Case Use Case."""
from dataclasses import dataclass
from uuid import UUID
from datetime import datetime

from ....domain.entities import Case
from ....domain.value_objects import CaseId, UserId, CaseStatus
from ....infrastructure.db.repositories import CaseRepository
from ....infrastructure.db.database import get_async_session_factory


@dataclass
class CloseCaseCommand:
    """Command to close a case."""
    case_id: UUID
    closed_by: UUID


@dataclass
class CloseCaseResult:
    """Result of close case operation."""
    case: Case


class CloseCaseUseCase:
    """Use case for closing a case."""

    def __init__(self, case_repo: CaseRepository = None):
        self.case_repo = case_repo or CaseRepository()

    async def execute(self, command: CloseCaseCommand) -> CloseCaseResult:
        """Execute the close case use case."""
        async_session_factory = get_async_session_factory()
        async with async_session_factory() as session:
            case_model = await self.case_repo.get(session, command.case_id)
            if not case_model:
                raise ValueError(f"Case not found: {command.case_id}")

            if case_model.status == CaseStatus.CLOSED.value:
                raise ValueError("Case is already closed")

            if case_model.status == CaseStatus.ARCHIVED.value:
                raise ValueError("Cannot close an archived case; reopen it first")

            case_model.status = CaseStatus.CLOSED.value
            case_model.closed_at = datetime.utcnow()
            case_model.updated_at = datetime.utcnow()

            updated_case_model = await self.case_repo.update(session, case_model)
            await session.commit()

            case = self._model_to_entity(updated_case_model)

            return CloseCaseResult(case=case)

    def _model_to_entity(self, model) -> Case:
        """Convert persistence model to domain entity."""
        case = Case(
            id=CaseId(model.id),
            title=model.title,
            status=CaseStatus(model.status),
            created_by=UserId(model.created_by),
            created_at=model.created_at,
            tags=model.tags,
        )
        case.updated_at = model.updated_at
        case.closed_at = model.closed_at
        case.archived_at = model.archived_at
        return case