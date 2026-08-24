"""Integration tests for CaseRepository."""
import pytest
import time
from uuid import UUID, uuid4
from datetime import datetime

from src.infrastructure.db.repositories import CaseRepository
from src.infrastructure.db.models import CaseModel
from src.infrastructure.db.database import get_async_session_factory


def _unique_case_number():
    """Generate a unique case number based on current time."""
    unique_seq = int(time.time() * 1000) % 100000
    return f"CASE-2026-{unique_seq:05d}"


@pytest.fixture
def session_factory():
    """Get real async session factory."""
    return get_async_session_factory()


@pytest.fixture
async def session():
    """Get a real database session."""
    factory = get_async_session_factory()
    async with factory() as s:
        yield s
        await s.rollback()


@pytest.fixture
def case_repo():
    """Create a CaseRepository instance."""
    return CaseRepository()


@pytest.fixture
async def sample_case():
    """Create a sample case in the database."""
    factory = get_async_session_factory()
    async with factory() as s:
        case = CaseModel(
            id=uuid4(),
            title="Integration Test Case",
            case_number=_unique_case_number(),
            description="Test description for integration",
            status="open",
            created_by=uuid4(),
            created_at=datetime.now(),
            tags=["important", "integration"],
        )
        s.add(case)
        await s.commit()
        await s.refresh(case)
        yield case
        # Cleanup - not strictly needed since rollback happens


class TestCaseRepository:
    """Integration tests for CaseRepository."""

    @pytest.mark.asyncio
    async def test_create_case(self, case_repo):
        """Test creating a case."""
        factory = get_async_session_factory()
        async with factory() as session:
            case = CaseModel(
                id=uuid4(),
                title="New Test Case",
                case_number=_unique_case_number(),
                description="New test description",
                status="open",
                created_by=uuid4(),
                created_at=datetime.now(),
                tags=["test"],
            )

            created = await case_repo.create(session, case)
            await session.commit()

            assert created.id == case.id
            assert created.title == "New Test Case"
            assert created.case_number == case.case_number

    @pytest.mark.asyncio
    async def test_get_case(self, case_repo):
        """Test getting a case by ID."""
        factory = get_async_session_factory()
        async with factory() as session:
            # Create a case first
            case = CaseModel(
                id=uuid4(),
                title="Test Get Case",
                case_number=_unique_case_number(),
                description="Test",
                status="open",
                created_by=uuid4(),
                created_at=datetime.now(),
                tags=["test"],
            )
            session.add(case)
            await session.commit()
            await session.refresh(case)

            found = await case_repo.get(session, case.id)

            assert found is not None
            assert found.id == case.id
            assert found.title == case.title
            assert found.case_number == case.case_number

    @pytest.mark.asyncio
    async def test_get_nonexistent_case(self, case_repo):
        """Test getting a nonexistent case returns None."""
        factory = get_async_session_factory()
        async with factory() as session:
            found = await case_repo.get(session, uuid4())
            assert found is None

    @pytest.mark.asyncio
    async def test_get_by_case_number(self, case_repo):
        """Test getting a case by case_number."""
        factory = get_async_session_factory()
        async with factory() as session:
            # Create a case first
            case = CaseModel(
                id=uuid4(),
                title="Test Get By Number",
                case_number=_unique_case_number(),
                description="Test",
                status="open",
                created_by=uuid4(),
                created_at=datetime.now(),
                tags=["test"],
            )
            session.add(case)
            await session.commit()
            await session.refresh(case)

            found = await case_repo.get_by_case_number(session, case.case_number)

            assert found is not None
            assert found.id == case.id
            assert found.case_number == case.case_number

    @pytest.mark.asyncio
    async def test_get_by_case_number_not_found(self, case_repo):
        """Test getting a case by nonexistent case_number returns None."""
        factory = get_async_session_factory()
        async with factory() as session:
            found = await case_repo.get_by_case_number(session, "CASE-2026-99999")
            assert found is None

    @pytest.mark.asyncio
    async def test_list_cases(self, case_repo):
        """Test listing cases with pagination."""
        factory = get_async_session_factory()
        async with factory() as session:
            # Create a case first
            case = CaseModel(
                id=uuid4(),
                title="Test List Case",
                case_number=_unique_case_number(),
                description="Test",
                status="open",
                created_by=uuid4(),
                created_at=datetime.now(),
                tags=["list-test"],
            )
            session.add(case)
            await session.commit()

            cases = await case_repo.list(session, offset=0, limit=10)

            assert len(cases) >= 1
            assert any(c.id == case.id for c in cases)

    @pytest.mark.asyncio
    async def test_list_cases_with_status_filter(self, case_repo):
        """Test listing cases with status filter."""
        factory = get_async_session_factory()
        async with factory() as session:
            cases = await case_repo.list(session, offset=0, limit=10, status="open")

            assert len(cases) >= 1
            assert all(c.status == "open" for c in cases)

    @pytest.mark.asyncio
    async def test_list_cases_with_tag_filter(self, case_repo):
        """Test listing cases with tag filter."""
        factory = get_async_session_factory()
        async with factory() as session:
            # Create a tagged case
            case = CaseModel(
                id=uuid4(),
                title="Test Tag Case",
                case_number=_unique_case_number(),
                description="Test",
                status="open",
                created_by=uuid4(),
                created_at=datetime.now(),
                tags=["specific-tag-filter"],
            )
            session.add(case)
            await session.commit()

            cases = await case_repo.list(session, offset=0, limit=10, tag="specific-tag-filter")

            assert len(cases) >= 1
            assert all("specific-tag-filter" in c.tags for c in cases)

    @pytest.mark.asyncio
    async def test_update_case(self, case_repo):
        """Test updating a case."""
        factory = get_async_session_factory()
        async with factory() as session:
            case = CaseModel(
                id=uuid4(),
                title="Original Title",
                case_number=_unique_case_number(),
                description="Original description",
                status="open",
                created_by=uuid4(),
                created_at=datetime.now(),
                tags=["original"],
            )
            session.add(case)
            await session.commit()
            await session.refresh(case)

            case.title = "Updated Title"
            case.description = "Updated description"
            case.tags = ["updated"]

            updated = await case_repo.update(session, case)
            await session.commit()

            assert updated.title == "Updated Title"
            assert updated.description == "Updated description"
            assert updated.tags == ["updated"]

    @pytest.mark.asyncio
    async def test_count_cases(self, case_repo):
        """Test counting cases."""
        factory = get_async_session_factory()
        async with factory() as session:
            total = await case_repo.count(session)
            assert total >= 1

    @pytest.mark.asyncio
    async def test_count_cases_with_status_filter(self, case_repo):
        """Test counting cases with status filter."""
        factory = get_async_session_factory()
        async with factory() as session:
            total = await case_repo.count(session, status="open")
            assert total >= 1

    @pytest.mark.asyncio
    async def test_case_number_uniqueness(self, case_repo):
        """Test that case_number must be unique."""
        factory = get_async_session_factory()
        async with factory() as session:
            case_number = _unique_case_number()
            case1 = CaseModel(
                id=uuid4(),
                title="Case 1",
                case_number=case_number,
                description="Test",
                status="open",
                created_by=uuid4(),
                created_at=datetime.now(),
                tags=[],
            )
            await case_repo.create(session, case1)
            await session.commit()

            case2 = CaseModel(
                id=uuid4(),
                title="Case 2",
                case_number=case_number,  # Same case number
                description="Test",
                status="open",
                created_by=uuid4(),
                created_at=datetime.now(),
                tags=[],
            )

            with pytest.raises(Exception):  # Should raise integrity error
                await case_repo.create(session, case2)
                await session.commit()