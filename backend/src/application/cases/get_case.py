"""Get Case Use Case."""
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from src.domain.entities import Case
from src.domain.value_objects import CaseId, CaseNumber, CaseStatus, UserId
from src.infrastructure.db.repositories import CaseRepository
from src.infrastructure.db.database import get_async_session_factory


@dataclass
class GetCaseQuery:
    """Query to get a case by ID."""
    case_id: UUID


@dataclass
class GetCaseByNumberQuery:
    """Query to get a case by case number."""
    case_number: str


@dataclass
class GetCaseResult:
    """Result of get case operation."""
    case: Optional[Case]


class GetCaseUseCase:
    """Use case for retrieving a case by ID or case number."""

    def __init__(self, case_repo: CaseRepository = None):
        self.case_repo = case_repo or CaseRepository()

    async def execute(self, query: GetCaseQuery) -> GetCaseResult:
        """Execute the get case use case by ID."""
        async_session_factory = get_async_session_factory()
        async with async_session_factory() as session:
            case_model = await self.case_repo.get(session, query.case_id)
            if not case_model:
                return GetCaseResult(case=None)

            # Convert back to domain entity
            case = self._model_to_entity(case_model)
            return GetCaseResult(case=case)

    async def execute_by_number(self, query: GetCaseByNumberQuery) -> GetCaseResult:
        """Execute the get case use case by case number."""
        async_session_factory = get_async_session_factory()
        async with async_session_factory() as session:
            case_model = await self.case_repo.get_by_case_number(session, query.case_number)
            if not case_model:
                return GetCaseResult(case=None)

            # Convert back to domain entity
            case = self._model_to_entity(case_model)
            return GetCaseResult(case=case)

    def _model_to_entity(self, model) -> Case:
        """Convert persistence model to domain entity."""
        from src.domain.value_objects import CaseStatus, UserId
        from datetime import datetime

        case = Case(
            id=CaseId(model.id),
            title=model.title,
            case_number=CaseNumber.parse(model.case_number),
            description=model.description,
            status=CaseStatus(model.status),
            created_by=UserId(model.created_by),
            created_at=model.created_at,
            tags=model.tags,
        )
        case.updated_at = model.updated_at
        case.closed_at = model.closed_at
        case.archived_at = model.archived_at
        return case