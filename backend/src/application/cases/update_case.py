"""Update Case Use Case."""
from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from datetime import datetime

from ....domain.entities import Case
from ....domain.value_objects import CaseId, UserId, CaseStatus
from ....domain.events import CaseTagAdded, CaseTagRemoved
from ....infrastructure.db.repositories import CaseRepository
from ....infrastructure.db.database import get_async_session_factory


@dataclass
class UpdateCaseCommand:
    """Command to update a case."""
    case_id: UUID
    title: Optional[str] = None
    status: Optional[CaseStatus] = None
    tags: Optional[list[str]] = None
    updated_by: UUID = None


@dataclass
class UpdateCaseResult:
    """Result of update case operation."""
    case: Case
    events: list


class UpdateCaseUseCase:
    """Use case for updating a case."""

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

            # Update fields
            if command.title is not None:
                case_model.title = command.title

            if command.status is not None:
                old_status = case_model.status
                new_status = command.status.value

                if new_status == CaseStatus.CLOSED.value and old_status != CaseStatus.CLOSED.value:
                    case_model.status = new_status
                    case_model.closed_at = datetime.utcnow()
                elif new_status == CaseStatus.ARCHIVED.value and old_status == CaseStatus.CLOSED.value:
                    case_model.status = new_status
                    case_model.archived_at = datetime.utcnow()
                elif new_status == CaseStatus.OPEN.value:
                    case_model.status = new_status
                    case_model.closed_at = None
                    case_model.archived_at = None

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