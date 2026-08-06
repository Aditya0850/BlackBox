"""Unit tests for domain value objects."""
import pytest
from uuid import UUID

from src.domain.value_objects import (
    CaseId, EvidenceId, UserId,
    CaseStatus, EvidenceType, MimeType, ConfidenceLevel
)


class TestCaseId:
    """Tests for CaseId value object."""

    def test_generate_creates_unique_id(self):
        id1 = CaseId.generate()
        id2 = CaseId.generate()
        assert id1 != id2
        assert isinstance(id1.value, UUID)

    def test_from_string_parses_uuid(self):
        uuid_str = "123e4567-e89b-12d3-a456-426614174000"
        case_id = CaseId.from_string(uuid_str)
        assert str(case_id.value) == uuid_str

    def test_str_returns_uuid_string(self):
        case_id = CaseId.generate()
        assert str(case_id) == str(case_id.value)

    def test_equality(self):
        uuid_str = "123e4567-e89b-12d3-a456-426614174000"
        id1 = CaseId.from_string(uuid_str)
        id2 = CaseId.from_string(uuid_str)
        assert id1 == id2

    def test_hashable(self):
        case_id = CaseId.generate()
        # Should be usable as dict key
        d = {case_id: "value"}
        assert d[case_id] == "value"


class TestEvidenceId:
    """Tests for EvidenceId value object."""

    def test_generate_creates_unique_id(self):
        id1 = EvidenceId.generate()
        id2 = EvidenceId.generate()
        assert id1 != id2

    def test_from_string_parses_uuid(self):
        uuid_str = "123e4567-e89b-12d3-a456-426614174000"
        evidence_id = EvidenceId.from_string(uuid_str)
        assert str(evidence_id.value) == uuid_str


class TestUserId:
    """Tests for UserId value object."""

    def test_generate_creates_unique_id(self):
        id1 = UserId.generate()
        id2 = UserId.generate()
        assert id1 != id2

    def test_from_string_parses_uuid(self):
        uuid_str = "123e4567-e89b-12d3-a456-426614174000"
        user_id = UserId.from_string(uuid_str)
        assert str(user_id.value) == uuid_str


class TestCaseStatus:
    """Tests for CaseStatus enum."""

    def test_values(self):
        assert CaseStatus.OPEN.value == "open"
        assert CaseStatus.CLOSED.value == "closed"
        assert CaseStatus.ARCHIVED.value == "archived"


class TestEvidenceType:
    """Tests for EvidenceType enum."""

    def test_common_types(self):
        assert EvidenceType.IMAGE.value == "image"
        assert EvidenceType.VIDEO.value == "video"
        assert EvidenceType.DOCUMENT.value == "document"
        assert EvidenceType.PDF.value == "pdf"
        assert EvidenceType.OTHER.value == "other"


class TestMimeType:
    """Tests for MimeType enum."""

    def test_image_types(self):
        assert MimeType.JPEG.value == "image/jpeg"
        assert MimeType.PNG.value == "image/png"
        assert MimeType.PDF.value == "application/pdf"

    def test_document_types(self):
        assert MimeType.DOCX.value == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        assert MimeType.TXT.value == "text/plain"