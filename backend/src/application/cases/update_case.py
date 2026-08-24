"""Update Case Use Case."""
from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from datetime import datetime

from src.domain.entities import Case
from src.domain.value_objects import CaseId, CaseNumber, UserId, CaseStatus
from src.domain.events import CaseTagAdded, CaseTagRemoved
from src.infrastructure.db.repositories import CaseRepository
from src.infrastructure.db.database import get_async_session_factory


@dataclass
class UpdateCaseCommand:
    """Command to update a case."""
    case_id: UUID
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[list[str]] = None
    updated_by: UUID = None


@dataclass
class UpdateCaseResult:
    """Result of update case operation."""
    case: Case
    events: list


class UpdateCaseUseCase:
    """Use case for updating a case. Only title, description, and tags can be updated in this slice."""

    def __init__(self, case_repo: CaseRepository = None):
        self.case_repo = case_repo or CaseRepository()

    async def execute(self, command: UpdateCaseCommand) -> UpdateCaseResult:
        """Execute the update case use case."""
        async_session_factory = get_async_session_factory()
        async with async_session_factory() as session:
            case_model = await self.case_repo.get(session, command.case_id)
            if not case_model:
                raise ValueError(f"Case not found: {command.case_id}")

            events = []

            # Update fields - only title, description, tags allowed in this slice
            if command.title is not None:
                case_model.title = command.title

            if command.description is not None:
                case_model.description = command.description

            if command.tags is not None:
                # Track added/removed tags
                old_tags = set(case_model.tags)
                new_tags = set(command.tags)

                for added_tag in new_tags - old_tags:
                    events.append(CaseTagAdded(
                        case_id=CaseId(command.case_id),
                        tag=added_tag,
                        added_by=UserId(command.updated_by),
                    ))

                for removed_tag in old_tags - new_tags:
                    events.append(CaseTagRemoved(
                        case_id=CaseId(command.case_id),
                        tag=removed_tag,
                        removed_by=UserId(command.updated_by),
                    ))

                case_model.tags = command.tags

            case_model.updated_at = datetime.utcnow()

            updated_case_model = await self.case_repo.update(session, case_model)
            await session.commit()

            case = self._model_to_entity(updated_case_model)

            return UpdateCaseResult(case=case, events=events)

    def _model_to_entity(self, model) -> Case:
        """Convert persistence model to domain entity."""
        from src.domain.value_objects import CaseStatus, UserId

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