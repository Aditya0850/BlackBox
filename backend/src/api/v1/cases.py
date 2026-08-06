"""Cases API endpoints."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ....infrastructure.db.database import get_async_session_factory
from ....infrastructure.db.repositories import CaseRepository
from ....domain.value_objects import CaseStatus

router = APIRouter()


# Dependency
async def get_db() -> AsyncSession:
    async_session_factory = get_async_session_factory()
    async with async_session_factory() as session:
        yield session


# Pydantic schemas
class CaseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    tags: list[str] = Field(default_factory=list)


class CaseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[CaseStatus] = None
    tags: Optional[list[str]] = None


class CaseResponse(BaseModel):
    id: UUID
    title: str
    status: str
    created_by: UUID
    created_at: str
    updated_at: Optional[str] = None
    closed_at: Optional[str] = None
    archived_at: Optional[str] = None
    tags: list[str] = []

    class Config:
        from_attributes = True


class CaseListResponse(BaseModel):
    cases: list[CaseResponse]
    total: int
    offset: int
    limit: int


# Endpoints
@router.post(
    "",
    response_model=CaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new case",
)
async def create_case(
    case_data: CaseCreate,
    session: AsyncSession = Depends(get_db),
    # TODO: Add auth dependency to get current user
    created_by: UUID = UUID("00000000-0000-0000-0000-000000000001"),  # Placeholder
) -> CaseResponse:
    """Create a new investigation case."""
    from ....domain.entities import Case
    from ....domain.value_objects import UserId, CaseStatus as DomainCaseStatus

    repo = CaseRepository()

    case = Case.create(
        title=case_data.title,
        created_by=UserId(created_by),
        tags=case_data.tags,
    )

    # Convert to model
    from ....infrastructure.db.models import CaseModel
    case_model = CaseModel(
        id=case.id.value,
        title=case.title,
        status=case.status.value,
        created_by=case.created_by.value,
        created_at=case.created_at,
        tags=case.tags,
    )

    created_case = await repo.create(session, case_model)
    await session.commit()

    return CaseResponse(
        id=created_case.id,
        title=created_case.title,
        status=created_case.status,
        created_by=created_case.created_by,
        created_at=created_case.created_at.isoformat(),
        updated_at=created_case.updated_at.isoformat() if created_case.updated_at else None,
        closed_at=created_case.closed_at.isoformat() if created_case.closed_at else None,
        archived_at=created_case.archived_at.isoformat() if created_case.archived_at else None,
        tags=created_case.tags,
    )


@router.get(
    "",
    response_model=CaseListResponse,
    summary="List cases with pagination and filters",
)
async def list_cases(
    session: AsyncSession = Depends(get_db),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None, description="Filter by case status"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
) -> CaseListResponse:
    """List cases with optional filters."""
    repo = CaseRepository()

    cases = await repo.list(
        session,
        offset=offset,
        limit=limit,
        status=status,
        tag=tag,
    )

    total = await repo.count(session, status=status)

    return CaseListResponse(
        cases=[
            CaseResponse(
                id=c.id,
                title=c.title,
                status=c.status,
                created_by=c.created_by,
                created_at=c.created_at.isoformat(),
                updated_at=c.updated_at.isoformat() if c.updated_at else None,
                closed_at=c.closed_at.isoformat() if c.closed_at else None,
                archived_at=c.archived_at.isoformat() if c.archived_at else None,
                tags=c.tags,
            )
            for c in cases
        ],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/{case_id}",
    response_model=CaseResponse,
    summary="Get a case by ID",
)
async def get_case(
    case_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> CaseResponse:
    """Get a case by its ID."""
    repo = CaseRepository()

    case = await repo.get(session, case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Case not found"}},
        )

    return CaseResponse(
        id=case.id,
        title=case.title,
        status=case.status,
        created_by=case.created_by,
        created_at=case.created_at.isoformat(),
        updated_at=case.updated_at.isoformat() if case.updated_at else None,
        closed_at=case.closed_at.isoformat() if case.closed_at else None,
        archived_at=case.archived_at.isoformat() if case.archived_at else None,
        tags=case.tags,
    )


@router.patch(
    "/{case_id}",
    response_model=CaseResponse,
    summary="Update a case",
)
async def update_case(
    case_id: UUID,
    case_update: CaseUpdate,
    session: AsyncSession = Depends(get_db),
    # TODO: Add auth dependency
    updated_by: UUID = UUID("00000000-0000-0000-0000-000000000001"),  # Placeholder
) -> CaseResponse:
    """Update a case. Requires reason for audit logging."""
    from ....domain.value_objects import UserId

    repo = CaseRepository()

    case = await repo.get(session, case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Case not found"}},
        )

    # Apply updates
    from datetime import datetime
    if case_update.title is not None:
        case.title = case_update.title
    if case_update.status is not None:
        if case_update.status == CaseStatus.CLOSED and case.status != CaseStatus.CLOSED:
            case.status = CaseStatus.CLOSED.value
            case.closed_at = datetime.utcnow()
        elif case_update.status == CaseStatus.ARCHIVED and case.status == CaseStatus.CLOSED:
            case.status = CaseStatus.ARCHIVED.value
            case.archived_at = datetime.utcnow()
        elif case_update.status == CaseStatus.OPEN:
            case.status = CaseStatus.OPEN.value
            case.closed_at = None
            case.archived_at = None
    if case_update.tags is not None:
        case.tags = case_update.tags

    case.updated_at = datetime.utcnow()

    updated_case = await repo.update(session, case)
    await session.commit()

    return CaseResponse(
        id=updated_case.id,
        title=updated_case.title,
        status=updated_case.status,
        created_by=updated_case.created_by,
        created_at=updated_case.created_at.isoformat(),
        updated_at=updated_case.updated_at.isoformat() if updated_case.updated_at else None,
        closed_at=updated_case.closed_at.isoformat() if updated_case.closed_at else None,
        archived_at=updated_case.archived_at.isoformat() if updated_case.archived_at else None,
        tags=updated_case.tags,
    )


@router.delete(
    "/{case_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a case",
)
async def delete_case(
    case_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> None:
    """Delete a case."""
    repo = CaseRepository()

    deleted = await repo.delete(session, case_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Case not found"}},
        )

    await session.commit()