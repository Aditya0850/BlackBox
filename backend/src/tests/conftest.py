"""Test configuration and fixtures."""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from uuid import uuid4

from src.infrastructure.db.database import Base
from src.config import get_settings

pytest_plugins = ["pytest_asyncio"]


@pytest.fixture(scope="session")
def settings():
    """Get application settings."""
    return get_settings()


@pytest.fixture(scope="session")
def engine() -> AsyncEngine:
    """Create test database engine."""
    settings = get_settings()
    # Use a test database or in-memory SQLite for unit tests
    return create_async_engine(
        f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}_test",
        echo=False,
    )


@pytest_asyncio.fixture
async def db_session(engine):
    """Create a database session for each test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def sample_case_data():
    """Sample case data for testing."""
    return {
        "title": "Test Case",
        "created_by": uuid4(),
        "tags": ["test", "sample"],
    }


@pytest.fixture
def sample_evidence_data():
    """Sample evidence data for testing."""
    return {
        "original_filename": "test.jpg",
        "mime_type": "image/jpeg",
        "file_size_bytes": 1024,
        "uploaded_by": uuid4(),
    }