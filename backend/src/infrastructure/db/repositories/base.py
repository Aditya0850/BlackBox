"""Base repository with common CRUD operations."""
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository."""

    @abstractmethod
    async def get(self, session: AsyncSession, id: UUID) -> Optional[T]:
        """Get entity by ID."""
        pass

    @abstractmethod
    async def list(
        self,
        session: AsyncSession,
        *,
        offset: int = 0,
        limit: int = 100,
        **filters,
    ) -> Sequence[T]:
        """List entities with pagination and filters."""
        pass

    @abstractmethod
    async def create(self, session: AsyncSession, entity: T) -> T:
        """Create a new entity."""
        pass

    @abstractmethod
    async def update(self, session: AsyncSession, entity: T) -> T:
        """Update an existing entity."""
        pass

    @abstractmethod
    async def delete(self, session: AsyncSession, id: UUID) -> bool:
        """Delete an entity by ID."""
        pass

    async def _get(self, session: AsyncSession, id: UUID) -> Optional[T]:
        """Get entity by ID using primary key lookup."""
        return await session.get(self._model_class, id)

    async def _list(
        self,
        session: AsyncSession,
        *,
        offset: int = 0,
        limit: int = 100,
        **filters,
    ) -> Sequence[T]:
        """List entities with pagination and filters."""
        stmt = select(self._model_class)
        for key, value in filters.items():
            if hasattr(self._model_class, key):
                stmt = stmt.where(getattr(self._model_class, key) == value)
        stmt = stmt.offset(offset).limit(limit)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def _create(self, session: AsyncSession, entity: T) -> T:
        """Create a new entity."""
        session.add(entity)
        await session.flush()
        await session.refresh(entity)
        return entity

    async def _update(self, session: AsyncSession, entity: T) -> T:
        """Update an existing entity."""
        await session.flush()
        await session.refresh(entity)
        return entity

    async def _delete(self, session: AsyncSession, id: UUID) -> bool:
        """Delete an entity by ID."""
        entity = await self._get(session, id)
        if entity is None:
            return False
        await session.delete(entity)
        await session.flush()
        return True

    @property
    @abstractmethod
    def _model_class(self) -> type[T]:
        """Return the SQLAlchemy model class."""
        pass