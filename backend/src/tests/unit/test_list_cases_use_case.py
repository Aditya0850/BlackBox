"""Unit tests for ListCasesUseCase."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4
from datetime import datetime

from src.application.cases.list_cases import ListCasesUseCase, ListCasesQuery, ListCasesResult
from src.domain.value_objects import CaseStatus
from src.infrastructure.db.models import CaseModel


class TestListCasesUseCase:
    """Tests for ListCasesUseCase."""

    @pytest.fixture
    def mock_repo(self):
        """Create a mock CaseRepository."""
        repo = MagicMock()
        repo.list = AsyncMock()
        repo.count = AsyncMock()
        return repo

    @pytest.fixture
    def use_case(self, mock_repo):
        """Create a ListCasesUseCase with mocked dependencies."""
        return ListCasesUseCase(case_repo=mock_repo)

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
    def sample_case_models(self):
        """Create sample CaseModels."""
        return [
            CaseModel(
                id=uuid4(),
                title="Test Case 1",
                case_number="CASE-2026-00001",
                description="Test description 1",
                status="open",
                created_by=uuid4(),
                created_at=datetime.now(),
                updated_at=None,
                closed_at=None,
                archived_at=None,
                tags=["important"],
            ),
            CaseModel(
                id=uuid4(),
                title="Test Case 2",
                case_number="CASE-2026-00002",
                description="Test description 2",
                status="closed",
                created_by=uuid4(),
                created_at=datetime.now(),
                updated_at=None,
                closed_at=None,
                archived_at=None,
                tags=["urgent"],
            ),
        ]

    @pytest.mark.asyncio
    async def test_execute_returns_paginated_cases(self, use_case, mock_repo, mock_session_factory, sample_case_models):
        """Test that execute returns paginated cases."""
        mock_factory, mock_session = mock_session_factory
        mock_repo.list.return_value = sample_case_models
        mock_repo.count.return_value = 2

        with patch('src.infrastructure.db.database.get_async_session_factory', return_value=mock_factory):
            query = ListCasesQuery(offset=0, limit=10)
            result = await use_case.execute(query)

            assert isinstance(result, ListCasesResult)
            assert len(result.cases) == 2
            assert result.total == 2
            assert result.offset == 0
            assert result.limit == 10

    @pytest.mark.asyncio
    async def test_execute_filters_by_status(self, use_case, mock_repo, mock_session_factory, sample_case_models):
        """Test that execute filters by status."""
        mock_factory, mock_session = mock_session_factory
        mock_repo.list.return_value = [sample_case_models[0]]  # Only open case
        mock_repo.count.return_value = 1

        with patch('src.infrastructure.db.database.get_async_session_factory', return_value=mock_factory):
            query = ListCasesQuery(offset=0, limit=10, status="open")
            result = await use_case.execute(query)

            assert len(result.cases) == 1
            assert result.cases[0].status.value == "open"
            mock_repo.list.assert_called_once()
            mock_repo.count.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_filters_by_tag(self, use_case, mock_repo, mock_session_factory, sample_case_models):
        """Test that execute filters by tag."""
        mock_factory, mock_session = mock_session_factory
        mock_repo.list.return_value = [sample_case_models[0]]  # Only important tag
        mock_repo.count.return_value = 1

        with patch('src.infrastructure.db.database.get_async_session_factory', return_value=mock_factory):
            query = ListCasesQuery(offset=0, limit=10, tag="important")
            result = await use_case.execute(query)

            assert len(result.cases) == 1
            assert "important" in result.cases[0].tags
            mock_repo.list.assert_called_once()
            mock_repo.count.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_empty_results(self, use_case, mock_repo, mock_session_factory):
        """Test that execute handles empty results."""
        mock_factory, mock_session = mock_session_factory
        mock_repo.list.return_value = []
        mock_repo.count.return_value = 0

        with patch('src.infrastructure.db.database.get_async_session_factory', return_value=mock_factory):
            query = ListCasesQuery(offset=0, limit=10)
            result = await use_case.execute(query)

            assert len(result.cases) == 0
            assert result.total == 0

    @pytest.mark.asyncio
    async def test_execute_with_pagination(self, use_case, mock_repo, mock_session_factory, sample_case_models):
        """Test pagination with offset and limit."""
        mock_factory, mock_session = mock_session_factory
        mock_repo.list.return_value = [sample_case_models[1]]  # Second case
        mock_repo.count.return_value = 2

        with patch('src.infrastructure.db.database.get_async_session_factory', return_value=mock_factory):
            query = ListCasesQuery(offset=1, limit=1)
            result = await use_case.execute(query)

            assert len(result.cases) == 1
            assert result.offset == 1
            assert result.limit == 1
            assert result.total == 2
            # Check repo called with correct offset/limit
            args, kwargs = mock_repo.list.call_args
            assert kwargs.get("offset") == 1
            assert kwargs.get("limit") == 1

    def test_model_to_entity_converts_all_fields(self, use_case, sample_case_models):
        """Test that _model_to_entity correctly converts all fields."""
        model = sample_case_models[0]
        case = use_case._model_to_entity(model)

        assert case.id.value == model.id
        assert case.title == model.title
        assert case.case_number.value == model.case_number
        assert case.description == model.description
        assert case.status == CaseStatus.OPEN
        assert case.created_by.value == model.created_by
        assert case.created_at == model.created_at
        assert case.updated_at == model.updated_at
        assert case.closed_at == model.closed_at
        assert case.archived_at == model.archived_at
        assert case.tags == model.tags