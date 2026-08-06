"""Case repository implementation."""
from typing import Sequence, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import CaseModel
from ..database import Base
from .base import BaseRepository


class CaseRepository(BaseRepository[CaseModel]):
    """Repository for Case entities."""

    @property
    def _model_class(self) -> type[CaseModel]:
        return CaseModel

    async def get(self, session: AsyncSession, id: UUID) -> Optional[CaseModel]:
        """Get case by ID with relationships loaded."""
        stmt = (
            select(CaseModel)
            .where(CaseModel.id == id)
            .options(selectinload(CaseModel.evidence_links).selectinload(CaseEvidenceModel.evidence))
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        session: AsyncSession,
        *,
        offset: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> Sequence[CaseModel]:
        """List cases with optional filters."""
        stmt = select(CaseModel).order_by(CaseModel.created_at.desc())

        if status:
            stmt = stmt.where(CaseModel.status == status)
        if tag:
            # Filter by tag using array containment
            stmt = stmt.where(CaseModel.tags.contains([tag]))

        stmt = stmt.offset(offset).limit(limit)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def create(self, session: AsyncSession, entity: CaseModel) -> CaseModel:
        """Create a new case."""
        return await self._create(session, entity)

    async def update(self, session: AsyncSession, entity: CaseModel) -> CaseModel:
        """Update an existing case."""
        return await self._update(session, entity)

    async def delete(self, session: AsyncSession, id: UUID) -> bool:
        """Delete a case by ID."""
        return await self._delete(session, id)

    async def get_by_title(self, session: AsyncSession, title: str) -> Optional[CaseModel]:
        """Get case by exact title match."""
        stmt = select(CaseModel).where(CaseModel.title == title)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def count(self, session: AsyncSession, status: Optional[str] = None) -> int:
        """Count cases with optional status filter."""
        from sqlalchemy import func
        stmt = select(func.count()).select_from(CaseModel)
        if status:
            stmt = stmt.where(CaseModel.status == status)
        result = await session.execute(stmt)
        return result.scalar() or 0


from ..models import CaseEvidenceModel