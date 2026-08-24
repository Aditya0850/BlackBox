"""Unit tests for UpdateCaseUseCase."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4
from datetime import datetime

from src.application.cases.update_case import UpdateCaseUseCase, UpdateCaseCommand, UpdateCaseResult
from src.domain.value_objects import CaseNumber, UserId, CaseStatus, CaseId
from src.domain.events import CaseTagAdded, CaseTagRemoved
from src.infrastructure.db.models import CaseModel


class TestUpdateCaseUseCase:
    """Tests for UpdateCaseUseCase."""

    @pytest.fixture
    def mock_repo(self):
        """Create a mock CaseRepository."""
        repo = MagicMock()
        repo.get = AsyncMock()
        repo.update = AsyncMock()
        return repo

    @pytest.fixture
    def use_case(self, mock_repo):
        """Create an UpdateCaseUseCase with mocked dependencies."""
        return UpdateCaseUseCase(case_repo=mock_repo)

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
            tags=["old_tag"],
        )

    @pytest.mark.asyncio
    async def test_execute_updates_title(self, use_case, mock_repo, mock_session_factory, sample_case_model):
        """Test that execute updates title."""
        mock_factory, mock_session = mock_session_factory
        mock_repo.get.return_value = sample_case_model
        mock_repo.update.return_value = sample_case_model

        with patch('src.infrastructure.db.database.get_async_session_factory', return_value=mock_factory):
            command = UpdateCaseCommand(
                case_id=sample_case_model.id,
                title="Updated Title",
                updated_by=uuid4(),
            )

            result = await use_case.execute(command)

            assert result.case.title == "Updated Title"
            assert sample_case_model.title == "Updated Title"

    @pytest.mark.asyncio
    async def test_execute_updates_description(self, use_case, mock_repo, mock_session_factory, sample_case_model):
        """Test that execute updates description."""
        mock_factory, mock_session = mock_session_factory
        mock_repo.get.return_value = sample_case_model
        mock_repo.update.return_value = sample_case_model

        with patch('src.infrastructure.db.database.get_async_session_factory', return_value=mock_factory):
            command = UpdateCaseCommand(
                case_id=sample_case_model.id,
                description="New description",
                updated_by=uuid4(),
            )

            result = await use_case.execute(command)

            assert result.case.description == "New description"
            assert sample_case_model.description == "New description"

    @pytest.mark.asyncio
    async def test_execute_updates_tags(self, use_case, mock_repo, mock_session_factory, sample_case_model):
        """Test that execute updates tags and emits events."""
        mock_factory, mock_session = mock_session_factory
        mock_repo.get.return_value = sample_case_model
        mock_repo.update.return_value = sample_case_model

        with patch('src.infrastructure.db.database.get_async_session_factory', return_value=mock_factory):
            command = UpdateCaseCommand(
                case_id=sample_case_model.id,
                tags=["new_tag1", "new_tag2"],
                updated_by=uuid4(),
            )

            result = await use_case.execute(command)

            assert result.case.tags == ["new_tag1", "new_tag2"]
            assert len(result.events) == 3  # Two added, one removed
            # Check events are of correct type
            event_types = [type(e).__name__ for e in result.events]
            assert "CaseTagAdded" in event_types
            assert "CaseTagRemoved" in event_types

    @pytest.mark.asyncio
    async def test_execute_does_not_update_status(self, use_case, mock_repo, mock_session_factory, sample_case_model):
        """Test that status field is not updatable in this slice."""
        mock_factory, mock_session = mock_session_factory
        mock_repo.get.return_value = sample_case_model
        mock_repo.update.return_value = sample_case_model

        with patch('src.infrastructure.db.database.get_async_session_factory', return_value=mock_factory):
            # The command doesn't even have a status field in this slice
            command = UpdateCaseCommand(
                case_id=sample_case_model.id,
                title="Updated Title",
                updated_by=uuid4(),
            )

            result = await use_case.execute(command)

            # Status should remain unchanged
            assert result.case.status.value == "open"
            assert sample_case_model.status == "open"

    @pytest.mark.asyncio
    async def test_execute_sets_updated_at(self, use_case, mock_repo, mock_session_factory, sample_case_model):
        """Test that execute sets updated_at timestamp."""
        mock_factory, mock_session = mock_session_factory
        original_updated_at = sample_case_model.updated_at
        mock_repo.get.return_value = sample_case_model
        mock_repo.update.return_value = sample_case_model

        with patch('src.infrastructure.db.database.get_async_session_factory', return_value=mock_factory):
            command = UpdateCaseCommand(
                case_id=sample_case_model.id,
                title="Updated Title",
                updated_by=uuid4(),
            )

            result = await use_case.execute(command)

            assert sample_case_model.updated_at is not None
            if original_updated_at:
                assert sample_case_model.updated_at > original_updated_at

    @pytest.mark.asyncio
    async def test_execute_raises_when_not_found(self, use_case, mock_repo, mock_session_factory):
        """Test that execute raises ValueError when case not found."""
        mock_factory, mock_session = mock_session_factory
        mock_repo.get.return_value = None

        with patch('src.infrastructure.db.database.get_async_session_factory', return_value=mock_factory):
            command = UpdateCaseCommand(
                case_id=uuid4(),
                title="Updated Title",
                updated_by=uuid4(),
            )

            with pytest.raises(ValueError, match="Case not found"):
                await use_case.execute(command)

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