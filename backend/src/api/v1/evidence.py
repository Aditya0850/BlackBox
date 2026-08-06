"""Evidence API endpoints."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ....infrastructure.db.database import get_async_session_factory
from ....infrastructure.db.repositories import EvidenceRepository, CaseRepository
from ....infrastructure.storage import get_minio_client
from ....domain.value_objects import MimeType

router = APIRouter()


# Dependency
async def get_db() -> AsyncSession:
    async_session_factory = get_async_session_factory()
    async with async_session_factory() as session:
        yield session


# Pydantic schemas
class EvidenceResponse(BaseModel):
    id: UUID
    original_filename: str
    mime_type: str
    file_size_bytes: int
    sha256_hash: str
    storage_location: str
    uploaded_by: UUID
    uploaded_at: str
    case_ids: list[UUID] = []

    class Config:
        from_attributes = True


class EvidenceListResponse(BaseModel):
    evidence: list[EvidenceResponse]
    total: int
    offset: int
    limit: int


class EvidenceLinkRequest(BaseModel):
    case_id: UUID


# Endpoints
@router.post(
    "",
    response_model=EvidenceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload new evidence",
)
async def upload_evidence(
    file: UploadFile = File(...),
    case_ids: Optional[list[UUID]] = Form(default=None),
    session: AsyncSession = Depends(get_db),
    # TODO: Add auth dependency
    uploaded_by: UUID = UUID("00000000-0000-0000-0000-000000000001"),  # Placeholder
) -> EvidenceResponse:
    """Upload a new evidence file."""
    import hashlib
    from datetime import datetime

    # Read file content
    file_content = await file.read()
    file_size = len(file_content)

    # Compute SHA256 hash
    sha256_hash = hashlib.sha256(file_content).hexdigest()

    # Check for duplicate
    evidence_repo = EvidenceRepository()
    existing = await evidence_repo.get_by_hash(session, sha256_hash)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "DUPLICATE_EVIDENCE",
                    "message": "Evidence with this hash already exists",
                    "details": {"existing_evidence_id": str(existing.id)},
                }
            },
        )

    # Determine MIME type
    mime_type = file.content_type or "application/octet-stream"
    try:
        mime_type = MimeType(mime_type)
    except ValueError:
        mime_type = MimeType.OCTET_STREAM

    # Upload to MinIO
    minio_client = get_minio_client()
    minio_client.ensure_bucket_exists()

    # Generate storage location
    storage_location = f"evidence/{sha256_hash[:2]}/{sha256_hash[2:4]}/{sha256_hash}"

    uploaded = minio_client.upload_file(
        object_name=storage_location,
        file_data=file_content,
        content_type=mime_type.value,
    )

    if not uploaded:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "STORAGE_ERROR", "message": "Failed to store evidence file"}},
        )

    # Create evidence record
    from ....domain.entities import Evidence
    from ....domain.value_objects import UserId

    evidence = Evidence.create(
        original_filename=file.filename or "unknown",
        mime_type=mime_type,
        file_size_bytes=file_size,
        sha256_hash=sha256_hash,
        storage_location=storage_location,
        uploaded_by=UserId(uploaded_by),
    )

    # Convert to model
    from ....infrastructure.db.models import EvidenceModel
    evidence_model = EvidenceModel(
        id=evidence.id.value,
        original_filename=evidence.original_filename,
        mime_type=evidence.mime_type.value,
        file_size_bytes=evidence.file_size_bytes,
        sha256_hash=evidence.sha256_hash,
        storage_location=evidence.storage_location,
        uploaded_by=evidence.uploaded_by.value,
        uploaded_at=evidence.uploaded_at,
    )

    created_evidence = await evidence_repo.create(session, evidence_model)

    # Link to cases if provided
    if case_ids:
        case_repo = CaseRepository()
        for case_id in case_ids:
            case = await case_repo.get(session, case_id)
            if case:
                from ....infrastructure.db.models import CaseEvidenceModel
                link = CaseEvidenceModel(
                    case_id=case_id,
                    evidence_id=created_evidence.id,
                    linked_by=uploaded_by,
                )
                session.add(link)
                created_evidence.case_links.append(type('obj', (object,), {'case': case})())

    await session.commit()
    await session.refresh(created_evidence)

    return EvidenceResponse(
        id=created_evidence.id,
        original_filename=created_evidence.original_filename,
        mime_type=created_evidence.mime_type,
        file_size_bytes=created_evidence.file_size_bytes,
        sha256_hash=created_evidence.sha256_hash,
        storage_location=created_evidence.storage_location,
        uploaded_by=created_evidence.uploaded_by,
        uploaded_at=created_evidence.uploaded_at.isoformat(),
        case_ids=[link.case_id for link in created_evidence.case_links],
    )


@router.get(
    "",
    response_model=EvidenceListResponse,
    summary="List evidence with pagination and filters",
)
async def list_evidence(
    session: AsyncSession = Depends(get_db),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    mime_type: Optional[str] = Query(None, description="Filter by MIME type"),
    case_id: Optional[UUID] = Query(None, description="Filter by case ID"),
) -> EvidenceListResponse:
    """List evidence with optional filters."""
    repo = EvidenceRepository()

    evidence_list = await repo.list(
        session,
        offset=offset,
        limit=limit,
        mime_type=mime_type,
        case_id=case_id,
    )

    total = await repo.count_by_case(session, case_id) if case_id else len(evidence_list)

    return EvidenceListResponse(
        evidence=[
            EvidenceResponse(
                id=e.id,
                original_filename=e.original_filename,
                mime_type=e.mime_type,
                file_size_bytes=e.file_size_bytes,
                sha256_hash=e.sha256_hash,
                storage_location=e.storage_location,
                uploaded_by=e.uploaded_by,
                uploaded_at=e.uploaded_at.isoformat(),
                case_ids=[link.case_id for link in e.case_links],
            )
            for e in evidence_list
        ],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/{evidence_id}",
    response_model=EvidenceResponse,
    summary="Get evidence by ID",
)
async def get_evidence(
    evidence_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> EvidenceResponse:
    """Get evidence by its ID."""
    repo = EvidenceRepository()

    evidence = await repo.get(session, evidence_id)
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Evidence not found"}},
        )

    return EvidenceResponse(
        id=evidence.id,
        original_filename=evidence.original_filename,
        mime_type=evidence.mime_type,
        file_size_bytes=evidence.file_size_bytes,
        sha256_hash=evidence.sha256_hash,
        storage_location=evidence.storage_location,
        uploaded_by=evidence.uploaded_by,
        uploaded_at=evidence.uploaded_at.isoformat(),
        case_ids=[link.case_id for link in evidence.case_links],
    )


@router.post(
    "/{evidence_id}/link",
    response_model=EvidenceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Link evidence to a case",
)
async def link_evidence_to_case(
    evidence_id: UUID,
    link_request: EvidenceLinkRequest,
    session: AsyncSession = Depends(get_db),
    # TODO: Add auth dependency
    linked_by: UUID = UUID("00000000-0000-0000-0000-000000000001"),  # Placeholder
) -> EvidenceResponse:
    """Link evidence to a case."""
    evidence_repo = EvidenceRepository()
    case_repo = CaseRepository()

    evidence = await evidence_repo.get(session, evidence_id)
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Evidence not found"}},
        )

    case = await case_repo.get(session, link_request.case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Case not found"}},
        )

    # Check if already linked
    existing_link = any(link.case_id == link_request.case_id for link in evidence.case_links)
    if existing_link:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": {"code": "ALREADY_LINKED", "message": "Evidence already linked to this case"}},
        )

    # Create link
    from ....infrastructure.db.models import CaseEvidenceModel
    link = CaseEvidenceModel(
        case_id=link_request.case_id,
        evidence_id=evidence_id,
        linked_by=linked_by,
    )
    session.add(link)
    evidence.case_links.append(type('obj', (object,), {'case': case})())
    await session.commit()
    await session.refresh(evidence)

    return EvidenceResponse(
        id=evidence.id,
        original_filename=evidence.original_filename,
        mime_type=evidence.mime_type,
        file_size_bytes=evidence.file_size_bytes,
        sha256_hash=evidence.sha256_hash,
        storage_location=evidence.storage_location,
        uploaded_by=evidence.uploaded_by,
        uploaded_at=evidence.uploaded_at.isoformat(),
        case_ids=[link.case_id for link in evidence.case_links],
    )


@router.delete(
    "/{evidence_id}/link/{case_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unlink evidence from a case",
)
async def unlink_evidence_from_case(
    evidence_id: UUID,
    case_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> None:
    """Unlink evidence from a case."""
    from ....infrastructure.db.models import CaseEvidenceModel
    from sqlalchemy import delete

    evidence_repo = EvidenceRepository()

    evidence = await evidence_repo.get(session, evidence_id)
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Evidence not found"}},
        )

    # Delete the link
    stmt = delete(CaseEvidenceModel).where(
        CaseEvidenceModel.case_id == case_id,
        CaseEvidenceModel.evidence_id == evidence_id,
    )
    result = await session.execute(stmt)

    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_LINKED", "message": "Evidence not linked to this case"}},
        )

    await session.commit()


@router.get(
    "/{evidence_id}/download",
    summary="Get download URL for evidence",
)
async def get_evidence_download_url(
    evidence_id: UUID,
    session: AsyncSession = Depends(get_db),
    expires: int = Query(3600, ge=60, le=86400),
) -> dict[str, str]:
    """Get a presigned URL for downloading evidence."""
    repo = EvidenceRepository()

    evidence = await repo.get(session, evidence_id)
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Evidence not found"}},
        )

    minio_client = get_minio_client()
    url = minio_client.get_file_url(evidence.storage_location, expires=expires)

    if not url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "STORAGE_ERROR", "message": "Failed to generate download URL"}},
        )

    return {"download_url": url, "expires_in": expires}


@router.delete(
    "/{evidence_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete evidence",
)
async def delete_evidence(
    evidence_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> None:
    """Delete evidence and its file from storage."""
    repo = EvidenceRepository()

    evidence = await repo.get(session, evidence_id)
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Evidence not found"}},
        )

    # Delete from MinIO
    minio_client = get_minio_client()
    minio_client.delete_file(evidence.storage_location)

    # Delete from database
    await repo.delete(session, evidence_id)
    await session.commit()