"""Upload Evidence Use Case."""
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from ....domain.entities import Evidence
from ....domain.value_objects import UserId, MimeType, EvidenceId
from ....domain.events import EvidenceUploaded
from ....infrastructure.db.repositories import EvidenceRepository, CaseRepository
from ....infrastructure.db.database import get_async_session_factory
from ....infrastructure.storage import get_minio_client


@dataclass
class UploadEvidenceCommand:
    """Command to upload evidence."""
    file_bytes: bytes
    original_filename: str
    mime_type: MimeType
    uploaded_by: UUID
    case_ids: list[UUID] = None


@dataclass
class UploadEvidenceResult:
    """Result of upload evidence operation."""
    evidence: Evidence
    event: EvidenceUploaded


class UploadEvidenceUseCase:
    """Use case for uploading evidence."""

    def __init__(
        self,
        evidence_repo: EvidenceRepository = None,
        case_repo: CaseRepository = None,
        storage_client = None,
    ):
        self.evidence_repo = evidence_repo or EvidenceRepository()
        self.case_repo = case_repo or CaseRepository()
        self.storage_client = storage_client or get_minio_client()

    async def execute(self, command: UploadEvidenceCommand) -> UploadEvidenceResult:
        """Execute the upload evidence use case."""
        import hashlib
        from datetime import datetime

        # Compute SHA256 hash
        sha256_hash = hashlib.sha256(command.file_bytes).hexdigest()

        # Check for duplicate
        async_session_factory = get_async_session_factory()
        async with async_session_factory() as session:
            existing = await self.evidence_repo.get_by_hash(session, sha256_hash)
            if existing:
                raise ValueError(f"Evidence with hash {sha256_hash} already exists")

            # Upload to MinIO
            self.storage_client.ensure_bucket_exists()
            storage_location = f"evidence/{sha256_hash[:2]}/{sha256_hash[2:4]}/{sha256_hash}"

            uploaded = self.storage_client.upload_file(
                object_name=storage_location,
                file_data=command.file_bytes,
                content_type=command.mime_type.value,
            )

            if not uploaded:
                raise RuntimeError("Failed to store evidence file in MinIO")

            # Create domain entity
            evidence = Evidence.create(
                original_filename=command.original_filename,
                mime_type=command.mime_type,
                file_size_bytes=len(command.file_bytes),
                sha256_hash=sha256_hash,
                storage_location=storage_location,
                uploaded_by=UserId(command.uploaded_by),
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

            # Persist
            created_evidence_model = await self.evidence_repo.create(session, evidence_model)

            # Link to cases if provided
            if command.case_ids:
                from ....infrastructure.db.models import CaseEvidenceModel
                for case_id in command.case_ids:
                    case = await self.case_repo.get(session, case_id)
                    if case:
                        link = CaseEvidenceModel(
                            case_id=case_id,
                            evidence_id=created_evidence_model.id,
                            linked_by=command.uploaded_by,
                        )
                        session.add(link)

            await session.commit()
            await session.refresh(created_evidence_model)

            # Create domain event
            event = EvidenceUploaded(
                evidence_id=EvidenceId(created_evidence_model.id),
                original_filename=created_evidence_model.original_filename,
                mime_type=MimeType(created_evidence_model.mime_type),
                file_size_bytes=created_evidence_model.file_size_bytes,
                sha256_hash=created_evidence_model.sha256_hash,
                storage_location=created_evidence_model.storage_location,
                uploaded_by=UserId(created_evidence_model.uploaded_by),
                case_ids=command.case_ids or [],
            )

            evidence = self._model_to_entity(created_evidence_model)

            return UploadEvidenceResult(evidence=evidence, event=event)

    def _model_to_entity(self, model) -> Evidence:
        """Convert persistence model to domain entity."""
        evidence = Evidence(
            id=EvidenceId(model.id),
            original_filename=model.original_filename,
            mime_type=MimeType(model.mime_type),
            file_size_bytes=model.file_size_bytes,
            sha256_hash=model.sha256_hash,
            storage_location=model.storage_location,
            uploaded_by=UserId(model.uploaded_by),
            uploaded_at=model.uploaded_at,
        )
        return evidence