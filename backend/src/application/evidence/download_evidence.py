"""Download Evidence Use Case."""
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from ....domain.entities import Evidence
from ....domain.value_objects import EvidenceId
from ....infrastructure.db.repositories import EvidenceRepository
from ....infrastructure.db.database import get_async_session_factory
from ....infrastructure.storage import get_minio_client


@dataclass
class DownloadEvidenceQuery:
    """Query to download evidence."""
    evidence_id: UUID
    expires: int = 3600


@dataclass
class DownloadEvidenceResult:
    """Result of download evidence operation."""
    download_url: str
    expires_in: int
    evidence: Evidence


class DownloadEvidenceUseCase:
    """Use case for downloading evidence."""

    def __init__(
        self,
        evidence_repo: EvidenceRepository = None,
        storage_client = None,
    ):
        self.evidence_repo = evidence_repo or EvidenceRepository()
        self.storage_client = storage_client or get_minio_client()

    async def execute(self, query: DownloadEvidenceQuery) -> DownloadEvidenceResult:
        """Execute the download evidence use case."""
        async_session_factory = get_async_session_factory()
        async with async_session_factory() as session:
            evidence_model = await self.evidence_repo.get(session, query.evidence_id)
            if not evidence_model:
                raise ValueError(f"Evidence not found: {query.evidence_id}")

            # Generate presigned URL
            download_url = self.storage_client.get_file_url(
                evidence_model.storage_location,
                expires=query.expires,
            )

            if not download_url:
                raise RuntimeError("Failed to generate download URL")

            evidence = self._model_to_entity(evidence_model)

            return DownloadEvidenceResult(
                download_url=download_url,
                expires_in=query.expires,
                evidence=evidence,
            )

    def _model_to_entity(self, model) -> Evidence:
        """Convert persistence model to domain entity."""
        evidence = Evidence(
            id=EvidenceId(model.id),
            original_filename=model.original_filename,
            mime_type=model.mime_type,
            file_size_bytes=model.file_size_bytes,
            sha256_hash=model.sha256_hash,
            storage_location=model.storage_location,
            uploaded_by=model.uploaded_by,
            uploaded_at=model.uploaded_at,
        )
        evidence.case_ids = [link.case_id for link in model.case_links]
        return evidence