"""List Cases Use Case."""
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from ....domain.entities import Case
from ....domain.value_objects import CaseId
from ....infrastructure.db.repositories import CaseRepository
from ....infrastructure.db.database import get_async_session_factory


@dataclass
class ListCasesQuery:
    """Query to list cases with pagination and filters."""
    offset: int = 0
    limit: int = 100
    status: Optional[str] = None
    tag: Optional[str] = None


@dataclass
class ListCasesResult:
    """Result of list cases operation."""
    cases: list[Case]
    total: int
    offset: int
    limit: int


class ListCasesUseCase:
    """Use case for listing cases with pagination and filters."""

    def __init__(self, case_repo: CaseRepository = None):
        self.case_repo = case_repo or CaseRepository()

    async def execute(self, query: ListCasesQuery) -> ListCasesResult:
        """Execute the list cases use case."""
        async_session_factory = get_async_session_factory()
        async with async_session_factory() as session:
            case_models = await self.case_repo.list(
                session,
                offset=query.offset,
                limit=query.limit,
                status=query.status,
                tag=query.tag,
            )

            total = await self.case_repo.count(session, status=query.status)

            cases = [self._model_to_entity(model) for model in case_models]

            return ListCasesResult(
                cases=cases,
                total=total,
                offset=query.offset,
                limit=query.limit,
            )

    def _model_to_entity(self, model) -> Case:
        """Convert persistence model to domain entity."""
        from ....domain.value_objects import CaseStatus, UserId

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