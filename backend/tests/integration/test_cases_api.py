"""Integration tests for Cases API endpoints."""
import pytest
from uuid import UUID, uuid4
from httpx import AsyncClient, ASGITransport

from src.main import app


@pytest.fixture
def async_client():
    """Create an async test client."""
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.fixture
def sample_case_data():
    """Sample case data for testing."""
    return {
        "title": "API Test Case",
        "description": "Test case created via API",
        "tags": ["api", "test"],
    }


class TestCasesAPI:
    """Integration tests for Cases API endpoints."""

    @pytest.mark.asyncio
    async def test_create_case(self, async_client, sample_case_data):
        """Test POST /api/v1/cases creates a case."""
        response = await async_client.post("/api/v1/cases", json=sample_case_data)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_case_data["title"]
        assert data["description"] == sample_case_data["description"]
        assert data["tags"] == sample_case_data["tags"]
        assert data["status"] == "open"
        assert data["case_number"].startswith("CASE-2026-")
        assert "id" in data
        assert "created_at" in data
        assert "created_by" in data

    @pytest.mark.asyncio
    async def test_create_case_minimal(self, async_client):
        """Test creating a case with only required fields."""
        response = await async_client.post("/api/v1/cases", json={"title": "Minimal Case"})

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Minimal Case"
        assert data["description"] == ""
        assert data["tags"] == []

    @pytest.mark.asyncio
    async def test_create_case_invalid_empty_title(self, async_client):
        """Test creating a case with empty title fails."""
        response = await async_client.post("/api/v1/cases", json={"title": ""})

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_case_invalid_long_title(self, async_client):
        """Test creating a case with too long title fails."""
        response = await async_client.post("/api/v1/cases", json={"title": "x" * 256})

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_case_invalid_long_description(self, async_client):
        """Test creating a case with too long description fails."""
        response = await async_client.post("/api/v1/cases", json={
            "title": "Test",
            "description": "x" * 10001,
        })

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_case_invalid_too_many_tags(self, async_client):
        """Test creating a case with too many tags fails."""
        response = await async_client.post("/api/v1/cases", json={
            "title": "Test",
            "tags": [f"tag{i}" for i in range(21)],  # 21 tags, max is 20
        })

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_create_case_invalid_long_tag(self, async_client):
        """Test creating a case with too long tag fails."""
        response = await async_client.post("/api/v1/cases", json={
            "title": "Test",
            "tags": ["a" * 51],  # 51 chars, max is 50
        })

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_list_cases(self, async_client):
        """Test GET /api/v1/cases returns paginated list."""
        # First create a case
        await async_client.post("/api/v1/cases", json={"title": "List Test Case"})

        response = await async_client.get("/api/v1/cases")

        assert response.status_code == 200
        data = response.json()
        assert "cases" in data
        assert "total" in data
        assert "offset" in data
        assert "limit" in data
        assert isinstance(data["cases"], list)
        assert len(data["cases"]) >= 1

    @pytest.mark.asyncio
    async def test_list_cases_pagination(self, async_client):
        """Test pagination on list cases."""
        response = await async_client.get("/api/v1/cases?offset=0&limit=1")

        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 1
        assert len(data["cases"]) <= 1

    @pytest.mark.asyncio
    async def test_list_cases_filter_by_status(self, async_client):
        """Test filtering by status."""
        response = await async_client.get("/api/v1/cases?status=open")

        assert response.status_code == 200
        data = response.json()
        assert all(c["status"] == "open" for c in data["cases"])

    @pytest.mark.asyncio
    async def test_list_cases_filter_by_tag(self, async_client):
        """Test filtering by tag."""
        # Create a case with a specific tag
        await async_client.post("/api/v1/cases", json={
            "title": "Tagged Case",
            "tags": ["specific-tag-for-test"],
        })

        response = await async_client.get("/api/v1/cases?tag=specific-tag-for-test")

        assert response.status_code == 200
        data = response.json()
        assert all("specific-tag-for-test" in c["tags"] for c in data["cases"])

    @pytest.mark.asyncio
    async def test_get_case_by_id(self, async_client):
        """Test GET /api/v1/cases/{id} returns the case."""
        create_response = await async_client.post("/api/v1/cases", json={
            "title": "Get By ID Test",
        })
        case_id = create_response.json()["id"]

        response = await async_client.get(f"/api/v1/cases/{case_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == case_id
        assert data["title"] == "Get By ID Test"
        assert data["case_number"].startswith("CASE-2026-")

    @pytest.mark.asyncio
    async def test_get_case_by_id_not_found(self, async_client):
        """Test GET /api/v1/cases/{id} returns 404 for nonexistent case."""
        fake_id = str(uuid4())
        response = await async_client.get(f"/api/v1/cases/{fake_id}")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_case_by_case_number(self, async_client):
        """Test GET /api/v1/cases/number/{case_number} returns the case."""
        create_response = await async_client.post("/api/v1/cases", json={
            "title": "Get By Number Test",
        })
        case_number = create_response.json()["case_number"]

        response = await async_client.get(f"/api/v1/cases/number/{case_number}")

        assert response.status_code == 200
        data = response.json()
        assert data["case_number"] == case_number
        assert data["title"] == "Get By Number Test"

    @pytest.mark.asyncio
    async def test_get_case_by_case_number_not_found(self, async_client):
        """Test GET /api/v1/cases/number/{case_number} returns 404 for nonexistent."""
        response = await async_client.get("/api/v1/cases/number/CASE-2026-99999")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_case(self, async_client):
        """Test PATCH /api/v1/cases/{id} updates the case."""
        create_response = await async_client.post("/api/v1/cases", json={
            "title": "Original Title",
            "description": "Original description",
            "tags": ["original"],
        })
        case_id = create_response.json()["id"]

        response = await async_client.patch(f"/api/v1/cases/{case_id}", json={
            "title": "Updated Title",
            "description": "Updated description",
            "tags": ["updated", "new"],
        })

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "Updated description"
        assert data["tags"] == ["updated", "new"]
        assert data["case_number"] == create_response.json()["case_number"]  # Unchanged

    @pytest.mark.asyncio
    async def test_update_case_partial(self, async_client):
        """Test partial update of a case."""
        create_response = await async_client.post("/api/v1/cases", json={
            "title": "Partial Update Test",
            "description": "Original",
            "tags": ["original"],
        })
        case_id = create_response.json()["id"]

        # Only update title
        response = await async_client.patch(f"/api/v1/cases/{case_id}", json={
            "title": "New Title Only",
        })

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Title Only"
        assert data["description"] == "Original"  # Unchanged
        assert data["tags"] == ["original"]  # Unchanged

    @pytest.mark.asyncio
    async def test_update_case_not_found(self, async_client):
        """Test PATCH /api/v1/cases/{id} returns 404 for nonexistent case."""
        fake_id = str(uuid4())
        response = await async_client.patch(f"/api/v1/cases/{fake_id}", json={
            "title": "Updated",
        })

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_case_does_not_allow_status(self, async_client):
        """Test that status cannot be updated via PATCH."""
        create_response = await async_client.post("/api/v1/cases", json={
            "title": "Status Test",
        })
        case_id = create_response.json()["id"]

        response = await async_client.patch(f"/api/v1/cases/{case_id}", json={
            "title": "Updated",
            "status": "closed",  # Should be ignored/rejected
        })

        # The API should either ignore status or reject it
        assert response.status_code in (200, 400, 422)
        if response.status_code == 200:
            data = response.json()
            assert data["status"] == "open"  # Status should remain open

    @pytest.mark.asyncio
    async def test_delete_case_not_allowed(self, async_client):
        """Test that DELETE endpoint is not implemented in Slice 2.1."""
        create_response = await async_client.post("/api/v1/cases", json={
            "title": "Delete Test",
        })
        case_id = create_response.json()["id"]

        response = await async_client.delete(f"/api/v1/cases/{case_id}")

        # DELETE should return 404 or 405 (not implemented)
        assert response.status_code in (404, 405)