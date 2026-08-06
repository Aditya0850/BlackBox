"""Finding repository implementation."""
from typing import Sequence, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import FindingModel
from .base import BaseRepository


class FindingRepository(BaseRepository[FindingModel]):
    """Repository for Finding entities."""

    @property
    def _model_class(self) -> type[FindingModel]:
        return FindingModel

    async def get(self, session: AsyncSession, id: UUID) -> Optional[FindingModel]:
        """Get finding by ID."""
        return await self._get(session, id)

    async def list(
        self,
        session: AsyncSession,
        *,
        offset: int = 0,
        limit: int = 100,
        snapshot_id: Optional[UUID] = None,
        key: Optional[str] = None,
        confidence_level: Optional[str] = None,
    ) -> Sequence[FindingModel]:
        """List findings with optional filters."""
        stmt = select(FindingModel).order_by(FindingModel.created_at.desc())

        if snapshot_id:
            stmt = stmt.where(FindingModel.snapshot_id == snapshot_id)
        if key:
            stmt = stmt.where(FindingModel.key == key)
        if confidence_level:
            stmt = stmt.where(FindingModel.confidence_level == confidence_level)

        stmt = stmt.offset(offset).limit(limit)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def create(self, session: AsyncSession, entity: FindingModel) -> FindingModel:
        """Create a new finding."""
        return await self._create(session, entity)

    async def create_many(
        self, session: AsyncSession, entities: list[FindingModel]
    ) -> list[FindingModel]:
        """Create multiple findings in batch."""
        session.add_all(entities)
        await session.flush()
        for entity in entities:
            await session.refresh(entity)
        return entities

    async def update(self, session: AsyncSession, entity: FindingModel) -> FindingModel:
        """Update an existing finding."""
        return await self._update(session, entity)

    async def delete(self, session: AsyncSession, id: UUID) -> bool:
        """Delete a finding by ID."""
        return await self._delete(session, id)

    async def get_by_snapshot_and_key(
        self, session: AsyncSession, snapshot_id: UUID, key: str
    ) -> Sequence[FindingModel]:
        """Get all findings for a snapshot with a specific key."""
        stmt = (
            select(FindingModel)
            .where(
                FindingModel.snapshot_id == snapshot_id,
                FindingModel.key == key,
            )
            .order_by(FindingModel.created_at)
        )
        result = await session.execute(stmt)
        return result.scalars().all()