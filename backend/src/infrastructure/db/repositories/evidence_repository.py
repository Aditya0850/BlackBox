"""Evidence repository implementation."""
from typing import Sequence, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import EvidenceModel
from .base import BaseRepository


class EvidenceRepository(BaseRepository[EvidenceModel]):
    """Repository for Evidence entities."""

    @property
    def _model_class(self) -> type[EvidenceModel]:
        return EvidenceModel

    async def get(self, session: AsyncSession, id: UUID) -> Optional[EvidenceModel]:
        """Get evidence by ID with relationships loaded."""
        stmt = (
            select(EvidenceModel)
            .where(EvidenceModel.id == id)
            .options(selectinload(EvidenceModel.case_links).selectinload(CaseEvidenceModel.case))
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_hash(self, session: AsyncSession, sha256_hash: str) -> Optional[EvidenceModel]:
        """Get evidence by SHA256 hash (deduplication)."""
        stmt = select(EvidenceModel).where(EvidenceModel.sha256_hash == sha256_hash)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        session: AsyncSession,
        *,
        offset: int = 0,
        limit: int = 100,
        mime_type: Optional[str] = None,
        case_id: Optional[UUID] = None,
    ) -> Sequence[EvidenceModel]:
        """List evidence with optional filters."""
        stmt = select(EvidenceModel).order_by(EvidenceModel.uploaded_at.desc())

        if mime_type:
            stmt = stmt.where(EvidenceModel.mime_type == mime_type)

        if case_id:
            # Join through case_evidence
            stmt = stmt.join(CaseEvidenceModel).where(CaseEvidenceModel.case_id == case_id)

        stmt = stmt.offset(offset).limit(limit)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def create(self, session: AsyncSession, entity: EvidenceModel) -> EvidenceModel:
        """Create a new evidence record."""
        return await self._create(session, entity)

    async def update(self, session: AsyncSession, entity: EvidenceModel) -> EvidenceModel:
        """Update an existing evidence record."""
        return await self._update(session, entity)

    async def delete(self, session: AsyncSession, id: UUID) -> bool:
        """Delete evidence by ID."""
        return await self._delete(session, id)

    async def count_by_case(self, session: AsyncSession, case_id: UUID) -> int:
        """Count evidence linked to a case."""
        from sqlalchemy import func
        stmt = (
            select(func.count())
            .select_from(EvidenceModel)
            .join(CaseEvidenceModel)
            .where(CaseEvidenceModel.case_id == case_id)
        )
        result = await session.execute(stmt)
        return result.scalar() or 0


from ..models import CaseEvidenceModel