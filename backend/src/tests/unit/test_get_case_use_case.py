"""Unit tests for GetCaseUseCase."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4
from datetime import datetime

from src.application.cases.get_case import GetCaseUseCase, GetCaseQuery, GetCaseByNumberQuery, GetCaseResult
from src.domain.value_objects import CaseNumber, UserId, CaseStatus, CaseId
from src.infrastructure.db.models import CaseModel


class TestGetCaseUseCase:
    """Tests for GetCaseUseCase."""

    @pytest.fixture
    def mock_repo(self):
        """Create a mock CaseRepository."""
        repo = MagicMock()
        repo.get = AsyncMock()
        repo.get_by_case_number = AsyncMock()
        return repo

    @pytest.fixture
    def use_case(self, mock_repo):
        """Create a GetCaseUseCase with mocked dependencies."""
        return GetCaseUseCase(case_repo=mock_repo)

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

    @pytest.fixture
    def sample_case_model(self):
        """Create a sample CaseModel."""
        return CaseModel(
            id=uuid4(),
            title="Test Case",
            case_number="CASE-2026-00001",
            description="Test description",
            status="open",
            created_by=uuid4(),
            created_at=datetime.now(),
            updated_at=None,
            closed_at=None,
            archived_at=None,
            tags=["important"],
        )

    @pytest.mark.asyncio
    async def test_execute_by_id_returns_case(self, use_case, mock_repo, mock_session_factory, sample_case_model):
        """Test that execute by ID returns the case."""
        mock_factory, mock_session = mock_session_factory
        mock_repo.get.return_value = sample_case_model

        with patch('src.infrastructure.db.database.get_async_session_factory', return_value=mock_factory):
            query = GetCaseQuery(case_id=sample_case_model.id)
            result = await use_case.execute(query)

            assert isinstance(result, GetCaseResult)
            assert result.case is not None
            assert result.case.id.value == sample_case_model.id
            assert result.case.title == "Test Case"
            assert result.case.case_number.value == "CASE-2026-00001"
            assert result.case.description == "Test description"
            assert result.case.status.value == "open"
            assert result.case.tags == ["important"]

    @pytest.mark.asyncio
    async def test_execute_by_id_returns_none_when_not_found(self, use_case, mock_repo, mock_session_factory):
        """Test that execute returns None when case not found."""
        mock_factory, mock_session = mock_session_factory
        mock_repo.get.return_value = None

        with patch('src.infrastructure.db.database.get_async_session_factory', return_value=mock_factory):
            query = GetCaseQuery(case_id=uuid4())
            result = await use_case.execute(query)

            assert result.case is None

    @pytest.mark.asyncio
    async def test_execute_by_number_returns_case(self, use_case, mock_repo, mock_session_factory, sample_case_model):
        """Test that execute_by_number returns the case."""
        mock_factory, mock_session = mock_session_factory
        mock_repo.get_by_case_number.return_value = sample_case_model

        with patch('src.infrastructure.db.database.get_async_session_factory', return_value=mock_factory):
            query = GetCaseByNumberQuery(case_number="CASE-2026-00001")
            result = await use_case.execute_by_number(query)

            assert isinstance(result, GetCaseResult)
            assert result.case is not None
            assert result.case.case_number.value == "CASE-2026-00001"
            assert result.case.title == "Test Case"

    @pytest.mark.asyncio
    async def test_execute_by_number_returns_none_when_not_found(self, use_case, mock_repo, mock_session_factory):
        """Test that execute_by_number returns None when case not found."""
        mock_factory, mock_session = mock_session_factory
        mock_repo.get_by_case_number.return_value = None

        with patch('src.infrastructure.db.database.get_async_session_factory', return_value=mock_factory):
            query = GetCaseByNumberQuery(case_number="CASE-2026-99999")
            result = await use_case.execute_by_number(query)

            assert result.case is None

    @pytest.mark.asyncio
    async def test_model_to_entity_converts_all_fields(self, use_case, sample_case_model):
        """Test that _model_to_entity correctly converts all fields."""
        case = use_case._model_to_entity(sample_case_model)

        assert case.id.value == sample_case_model.id
        assert case.title == sample_case_model.title
        assert case.case_number.value == sample_case_model.case_number
        assert case.description == sample_case_model.description
        assert case.status == CaseStatus.OPEN
        assert case.created_by.value == sample_case_model.created_by
        assert case.created_at == sample_case_model.created_at
        assert case.updated_at == sample_case_model.updated_at
        assert case.closed_at == sample_case_model.closed_at
        assert case.archived_at == sample_case_model.archived_at
        assert case.tags == sample_case_model.tags