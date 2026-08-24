"""Unit tests for CreateCaseUseCase."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4
from datetime import datetime

from src.application.cases.create_case import CreateCaseUseCase, CreateCaseCommand, CreateCaseResult
from src.domain.value_objects import CaseNumber, UserId
from src.infrastructure.db.models import CaseModel


class TestCreateCaseUseCase:
    """Tests for CreateCaseUseCase."""

    @pytest.fixture
    def mock_repo(self):
        """Create a mock CaseRepository."""
        repo = MagicMock()
        repo.create = AsyncMock()
        return repo

    @pytest.fixture
    def use_case(self, mock_repo):
        """Create a CreateCaseUseCase with mocked dependencies."""
        return CreateCaseUseCase(case_repo=mock_repo)

    @pytest.fixture
    def mock_session_factory(self):
        """Create a mock async session factory with context manager support."""
        mock_session = AsyncMock()
        # Mock the async context manager (async with)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        mock_factory = MagicMock()
        mock_factory.return_value = mock_session
        return mock_factory, mock_session

    @pytest.mark.asyncio
    async def test_execute_creates_case_with_case_number(self, use_case, mock_repo, mock_session_factory):
        """Test that execute creates a case with auto-generated case number."""
        from src.domain.entities import Case
        from src.infrastructure.db.models import CaseModel

        mock_factory, mock_session = mock_session_factory

        # Mock the DB sequence call
        mock_result = MagicMock()
        mock_result.scalar.return_value = "CASE-2026-00001"
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Mock repo.create to return a CaseModel
        created_model = CaseModel(
            id=uuid4(),
            title="Test Case",
            case_number="CASE-2026-00001",
            description="Test description",
            status="open",
            created_by=uuid4(),
            created_at=datetime.now(),
            tags=["important"],
        )
        mock_repo.create.return_value = created_model

        with patch('src.application.cases.create_case.get_async_session_factory', return_value=mock_factory):
            command = CreateCaseCommand(
                title="Test Case",
                created_by=uuid4(),
                tags=["important"],
                description="Test description",
            )

            result = await use_case.execute(command)

            assert isinstance(result, CreateCaseResult)
            assert result.case.title == "Test Case"
            assert result.case.description == "Test description"
            assert result.case.case_number.value == "CASE-2026-00001"
            assert result.case.status.value == "open"
            assert result.case.tags == ["important"]
            assert result.event.case_number == "CASE-2026-00001"

    @pytest.mark.asyncio
    async def test_execute_without_description(self, use_case, mock_repo, mock_session_factory):
        """Test that execute works without description."""
        from src.domain.entities import Case
        from src.infrastructure.db.models import CaseModel

        mock_factory, mock_session = mock_session_factory

        mock_session.execute = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar.return_value = "CASE-2026-00002"
        mock_session.execute.return_value = mock_result

        created_model = CaseModel(
            id=uuid4(),
            title="Test Case",
            case_number="CASE-2026-00002",
            description="",
            status="open",
            created_by=uuid4(),
            created_at=datetime.now(),
            tags=[],
        )
        mock_repo.create.return_value = created_model

        with patch('src.application.cases.create_case.get_async_session_factory', return_value=mock_factory):
            command = CreateCaseCommand(
                title="Test Case",
                created_by=uuid4(),
                tags=[],
                description="",
            )

            result = await use_case.execute(command)

            assert result.case.description == ""

    @pytest.mark.asyncio
    async def test_execute_with_empty_tags(self, use_case, mock_repo, mock_session_factory):
        """Test that execute works with empty tags list."""
        from src.infrastructure.db.models import CaseModel

        mock_factory, mock_session = mock_session_factory

        mock_session.execute = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar.return_value = "CASE-2026-00003"
        mock_session.execute.return_value = mock_result

        created_model = CaseModel(
            id=uuid4(),
            title="Test Case",
            case_number="CASE-2026-00003",
            description="Test",
            status="open",
            created_by=uuid4(),
            created_at=datetime.now(),
            tags=[],
        )
        mock_repo.create.return_value = created_model

        with patch('src.application.cases.create_case.get_async_session_factory', return_value=mock_factory):
            command = CreateCaseCommand(
                title="Test Case",
                created_by=uuid4(),
                tags=[],
                description="Test",
            )

            result = await use_case.execute(command)

            assert result.case.tags == []