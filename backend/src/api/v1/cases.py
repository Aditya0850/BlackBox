"""Cases API endpoints."""
from __future__ import annotations
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
import re

from src.infrastructure.db.database import get_async_session_factory
from src.infrastructure.db.repositories import CaseRepository
from src.domain.value_objects import CaseStatus

router = APIRouter()


# Dependency
async def get_db() -> AsyncSession:
    async_session_factory = get_async_session_factory()
    async with async_session_factory() as session:
        yield session


# Pydantic schemas
class CaseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=10000)
    tags: list[str] = Field(default_factory=list)


class CaseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=10000)
    tags: Optional[list[str]] = None


class CaseResponse(BaseModel):
    id: UUID
    case_number: str
    title: str
    description: str
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


# Validation helpers

CASE_NUMBER_PATTERN = re.compile(r"^CASE-\d{4}-\d{5}$")

def validate_case_number(case_number: str) -> str:
    """Validate case number format."""
    if not CASE_NUMBER_PATTERN.match(case_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "INVALID_CASE_NUMBER",
                    "message": "Invalid case number format. Expected format: CASE-YYYY-NNNNN",
                }
            },
        )
    return case_number


def validate_tags(tags: list[str]) -> list[str]:
    """Validate tags."""
    if len(tags) > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "TOO_MANY_TAGS", "message": "Maximum 20 tags allowed"}},
        )
    for tag in tags:
        if not tag or len(tag) > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": {"code": "INVALID_TAG", "message": "Tags must be 1-50 characters"}},
            )
    # Lowercase and deduplicate
    return list(dict.fromkeys(tag.lower() for tag in tags))


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
    """Create a new investigation case.

    Returns the case with auto-generated case_number (format: CASE-YYYY-NNNNN).
    """
    from src.domain.entities import Case
    from src.domain.value_objects import UserId
    from src.application.cases import CreateCaseUseCase, CreateCaseCommand

    # Validate tags
    validated_tags = validate_tags(case_data.tags)

    repo = CaseRepository()
    use_case = CreateCaseUseCase(repo)

    command = CreateCaseCommand(
        title=case_data.title,
        created_by=created_by,
        tags=validated_tags,
        description=case_data.description or "",
    )

    result = await use_case.execute(command)

    created_case = result.case

    return CaseResponse(
        id=created_case.id.value,
        case_number=created_case.case_number.value,
        title=created_case.title,
        description=created_case.description,
        status=created_case.status.value,
        created_by=created_case.created_by.value,
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
    from src.domain.entities import Case
    from src.application.cases import ListCasesUseCase, ListCasesQuery

    repo = CaseRepository()
    use_case = ListCasesUseCase(repo)

    query = ListCasesQuery(
        offset=offset,
        limit=limit,
        status=status,
        tag=tag,
    )

    result = await use_case.execute(query)

    return CaseListResponse(
        cases=[
            CaseResponse(
                id=c.id.value,
                case_number=c.case_number.value,
                title=c.title,
                description=c.description,
                status=c.status.value,
                created_by=c.created_by.value,
                created_at=c.created_at.isoformat(),
                updated_at=c.updated_at.isoformat() if c.updated_at else None,
                closed_at=c.closed_at.isoformat() if c.closed_at else None,
                archived_at=c.archived_at.isoformat() if c.archived_at else None,
                tags=c.tags,
            )
            for c in result.cases
        ],
        total=result.total,
        offset=result.offset,
        limit=result.limit,
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
    from src.domain.entities import Case
    from src.application.cases import GetCaseUseCase, GetCaseQuery

    use_case = GetCaseUseCase()

    query = GetCaseQuery(case_id=case_id)
    result = await use_case.execute(query)

    if not result.case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Case not found"}},
        )

    case = result.case
    return CaseResponse(
        id=case.id.value,
        case_number=case.case_number.value,
        title=case.title,
        description=case.description,
        status=case.status.value,
        created_by=case.created_by.value,
        created_at=case.created_at.isoformat(),
        updated_at=case.updated_at.isoformat() if case.updated_at else None,
        closed_at=case.closed_at.isoformat() if case.closed_at else None,
        archived_at=case.archived_at.isoformat() if case.archived_at else None,
        tags=case.tags,
    )


@router.get(
    "/number/{case_number}",
    response_model=CaseResponse,
    summary="Get a case by case number",
)
async def get_case_by_number(
    case_number: str,
    session: AsyncSession = Depends(get_db),
) -> CaseResponse:
    """Get a case by its case number (format: CASE-YYYY-NNNNN)."""
    from src.domain.entities import Case
    from src.application.cases import GetCaseUseCase, GetCaseByNumberQuery

    # Validate format
    validate_case_number(case_number)

    use_case = GetCaseUseCase()

    query = GetCaseByNumberQuery(case_number=case_number)
    result = await use_case.execute_by_number(query)

    if not result.case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Case not found"}},
        )

    case = result.case
    return CaseResponse(
        id=case.id.value,
        case_number=case.case_number.value,
        title=case.title,
        description=case.description,
        status=case.status.value,
        created_by=case.created_by.value,
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
    """Update a case. Only title, description, and tags can be updated.

    Status transitions are not available in this slice (will be added in Slice 2.3).
    """
    from src.domain.entities import Case
    from src.application.cases import UpdateCaseUseCase, UpdateCaseCommand

    # Validate tags if provided
    validated_tags = None
    if case_update.tags is not None:
        validated_tags = validate_tags(case_update.tags)

    repo = CaseRepository()
    use_case = UpdateCaseUseCase(repo)

    command = UpdateCaseCommand(
        case_id=case_id,
        title=case_update.title,
        description=case_update.description,
        tags=validated_tags,
        updated_by=updated_by,
    )

    try:
        result = await use_case.execute(command)
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "NOT_FOUND", "message": str(e)}},
            )
        raise

    updated_case = result.case
    return CaseResponse(
        id=updated_case.id.value,
        case_number=updated_case.case_number.value,
        title=updated_case.title,
        description=updated_case.description,
        status=updated_case.status.value,
        created_by=updated_case.created_by.value,
        created_at=updated_case.created_at.isoformat(),
        updated_at=updated_case.updated_at.isoformat() if updated_case.updated_at else None,
        closed_at=updated_case.closed_at.isoformat() if updated_case.closed_at else None,
        archived_at=updated_case.archived_at.isoformat() if updated_case.archived_at else None,
        tags=updated_case.tags,
    )