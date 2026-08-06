"""Analysis Snapshot repository implementation."""
from typing import Sequence, Optional
from uuid import UUID

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import AnalysisSnapshotModel
from .base import BaseRepository


class AnalysisSnapshotRepository(BaseRepository[AnalysisSnapshotModel]):
    """Repository for AnalysisSnapshot entities."""

    @property
    def _model_class(self) -> type[AnalysisSnapshotModel]:
        return AnalysisSnapshotModel

    async def get(self, session: AsyncSession, id: UUID) -> Optional[AnalysisSnapshotModel]:
        """Get snapshot by ID with findings loaded."""
        stmt = (
            select(AnalysisSnapshotModel)
            .where(AnalysisSnapshotModel.id == id)
            .options(selectinload(AnalysisSnapshotModel.findings))
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_current_for_evidence(
        self, session: AsyncSession, evidence_id: UUID
    ) -> Optional[AnalysisSnapshotModel]:
        """Get the current (is_current=True) snapshot for an evidence."""
        stmt = (
            select(AnalysisSnapshotModel)
            .where(
                AnalysisSnapshotModel.evidence_id == evidence_id,
                AnalysisSnapshotModel.is_current == True,
            )
            .options(selectinload(AnalysisSnapshotModel.findings))
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        session: AsyncSession,
        *,
        offset: int = 0,
        limit: int = 100,
        evidence_id: Optional[UUID] = None,
        is_current: Optional[bool] = None,
    ) -> Sequence[AnalysisSnapshotModel]:
        """List snapshots with optional filters."""
        stmt = select(AnalysisSnapshotModel).order_by(desc(AnalysisSnapshotModel.created_at))

        if evidence_id:
            stmt = stmt.where(AnalysisSnapshotModel.evidence_id == evidence_id)
        if is_current is not None:
            stmt = stmt.where(AnalysisSnapshotModel.is_current == is_current)

        stmt = stmt.offset(offset).limit(limit).options(selectinload(AnalysisSnapshotModel.findings))
        result = await session.execute(stmt)
        return result.scalars().all()

    async def create(self, session: AsyncSession, entity: AnalysisSnapshotModel) -> AnalysisSnapshotModel:
        """Create a new snapshot."""
        return await self._create(session, entity)

    async def update(self, session: AsyncSession, entity: AnalysisSnapshotModel) -> AnalysisSnapshotModel:
        """Update an existing snapshot."""
        return await self._update(session, entity)

    async def delete(self, session: AsyncSession, id: UUID) -> bool:
        """Delete a snapshot by ID."""
        return await self._delete(session, id)

    async def mark_superseded(
        self, session: AsyncSession, old_id: UUID, new_id: UUID
    ) -> bool:
        """Mark a snapshot as superseded by another."""
        old_snapshot = await self.get(session, old_id)
        if old_snapshot is None:
            return False
        old_snapshot.is_current = False
        old_snapshot.superseded_by = new_id
        await session.flush()
        return True