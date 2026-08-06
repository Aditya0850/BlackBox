"""Unit tests for domain entities."""
import pytest
from datetime import datetime
from uuid import uuid4, UUID

from src.domain.entities import Case, Evidence, CaseEvidence, AnalysisSnapshot, Finding
from src.domain.value_objects import CaseId, EvidenceId, UserId, CaseStatus, MimeType, ConfidenceLevel
from src.domain.events import CaseCreated, CaseClosed


class TestCase:
    """Tests for Case entity."""

    def test_create_case(self):
        case = Case.create(
            title="Test Case",
            created_by=UserId.generate(),
            tags=["tag1", "tag2"],
        )

        assert case.id is not None
        assert case.title == "Test Case"
        assert case.status == CaseStatus.OPEN
        assert case.created_by is not None
        assert case.created_at is not None
        assert case.tags == ["tag1", "tag2"]
        assert case.updated_at is None
        assert case.closed_at is None
        assert case.archived_at is None

    def test_close_case(self):
        case = Case.create(
            title="Test Case",
            created_by=UserId.generate(),
        )

        case.close()

        assert case.status == CaseStatus.CLOSED
        assert case.closed_at is not None
        assert case.updated_at is not None

    def test_close_already_closed_raises(self):
        case = Case.create(
            title="Test Case",
            created_by=UserId.generate(),
        )
        case.close()

        with pytest.raises(ValueError, match="Only open cases can be closed"):
            case.close()

    def test_archive_case(self):
        case = Case.create(
            title="Test Case",
            created_by=UserId.generate(),
        )
        case.close()
        case.archive()

        assert case.status == CaseStatus.ARCHIVED
        assert case.archived_at is not None

    def test_archive_non_closed_raises(self):
        case = Case.create(
            title="Test Case",
            created_by=UserId.generate(),
        )

        with pytest.raises(ValueError, match="Only closed cases can be archived"):
            case.archive()

    def test_reopen_case(self):
        case = Case.create(
            title="Test Case",
            created_by=UserId.generate(),
        )
        case.close()
        case.archive()
        case.reopen()

        assert case.status == CaseStatus.OPEN
        assert case.closed_at is None
        assert case.archived_at is None

    def test_add_tag(self):
        case = Case.create(
            title="Test Case",
            created_by=UserId.generate(),
            tags=["tag1"],
        )

        case.add_tag("tag2")
        assert case.tags == ["tag1", "tag2"]

        # Adding duplicate should not create duplicate
        case.add_tag("tag2")
        assert case.tags == ["tag1", "tag2"]

    def test_remove_tag(self):
        case = Case.create(
            title="Test Case",
            created_by=UserId.generate(),
            tags=["tag1", "tag2"],
        )

        case.remove_tag("tag1")
        assert case.tags == ["tag2"]

        # Removing non-existent should not raise
        case.remove_tag("nonexistent")
        assert case.tags == ["tag2"]


class TestEvidence:
    """Tests for Evidence entity."""

    def test_create_evidence(self):
        evidence = Evidence.create(
            original_filename="test.jpg",
            mime_type=MimeType.JPEG,
            file_size_bytes=1024,
            sha256_hash="a" * 64,
            storage_location="evidence/00/test.jpg",
            uploaded_by=UserId.generate(),
        )

        assert evidence.id is not None
        assert evidence.original_filename == "test.jpg"
        assert evidence.mime_type == MimeType.JPEG
        assert evidence.file_size_bytes == 1024
        assert evidence.sha256_hash == "a" * 64
        assert evidence.storage_location == "evidence/00/test.jpg"
        assert evidence.uploaded_by is not None
        assert evidence.uploaded_at is not None
        assert evidence.case_ids == []

    def test_link_to_case(self):
        evidence = Evidence.create(
            original_filename="test.jpg",
            mime_type=MimeType.JPEG,
            file_size_bytes=1024,
            sha256_hash="a" * 64,
            storage_location="evidence/00/test.jpg",
            uploaded_by=UserId.generate(),
        )

        case_id = CaseId.generate()
        evidence.link_to_case(case_id)
        assert case_id in evidence.case_ids

        # Duplicate link should not create duplicate
        evidence.link_to_case(case_id)
        assert evidence.case_ids.count(case_id) == 1

    def test_unlink_from_case(self):
        evidence = Evidence.create(
            original_filename="test.jpg",
            mime_type=MimeType.JPEG,
            file_size_bytes=1024,
            sha256_hash="a" * 64,
            storage_location="evidence/00/test.jpg",
            uploaded_by=UserId.generate(),
        )

        case_id = CaseId.generate()
        evidence.link_to_case(case_id)
        evidence.unlink_from_case(case_id)
        assert case_id not in evidence.case_ids

        # Unlinking non-existent should not raise
        evidence.unlink_from_case(case_id)
        assert case_id not in evidence.case_ids


class TestCaseEvidence:
    """Tests for CaseEvidence entity."""

    def test_create_link(self):
        case_id = CaseId.generate()
        evidence_id = EvidenceId.generate()
        user_id = UserId.generate()

        link = CaseEvidence.create(case_id, evidence_id, user_id)

        assert link.case_id == case_id
        assert link.evidence_id == evidence_id
        assert link.linked_by == user_id
        assert link.linked_at is not None


class TestAnalysisSnapshot:
    """Tests for AnalysisSnapshot entity."""

    def test_create_snapshot(self):
        snapshot = AnalysisSnapshot.create(
            evidence_id=EvidenceId.generate(),
            pipeline_version="1.0.0",
            plugin_versions={"ocr": "tesseract-5.3", "ai": "gpt-4"},
            trigger="upload",
            triggered_by=UserId.generate(),
        )

        assert snapshot.id is not None
        assert snapshot.pipeline_version == "1.0.0"
        assert snapshot.plugin_versions == {"ocr": "tesseract-5.3", "ai": "gpt-4"}
        assert snapshot.trigger == "upload"
        assert snapshot.is_current is True
        assert snapshot.superseded_by is None
        assert snapshot.investigator_approval == "pending"

    def test_supersede_snapshot(self):
        snapshot = AnalysisSnapshot.create(
            evidence_id=EvidenceId.generate(),
            pipeline_version="1.0.0",
            plugin_versions={},
            trigger="upload",
        )

        new_snapshot_id = UUID("123e4567-e89b-12d3-a456-426614174001")
        snapshot.supersede(new_snapshot_id)

        assert snapshot.is_current is False
        assert snapshot.superseded_by == new_snapshot_id

    def test_approve_snapshot(self):
        snapshot = AnalysisSnapshot.create(
            evidence_id=EvidenceId.generate(),
            pipeline_version="1.0.0",
            plugin_versions={},
            trigger="upload",
        )

        snapshot.approve()
        assert snapshot.investigator_approval == "approved"

    def test_reject_snapshot(self):
        snapshot = AnalysisSnapshot.create(
            evidence_id=EvidenceId.generate(),
            pipeline_version="1.0.0",
            plugin_versions={},
            trigger="upload",
        )

        snapshot.reject()
        assert snapshot.investigator_approval == "rejected"


class TestFinding:
    """Tests for Finding entity."""

    def test_create_finding(self):
        snapshot_id = UUID("123e4567-e89b-12d3-a456-426614174000")

        finding = Finding.create(
            snapshot_id=snapshot_id,
            key="ocr.text",
            value={"text": "Sample text", "language": "eng"},
            confidence_level=ConfidenceLevel.HIGH,
            confidence_score=0.95,
            extraction_method="tesseract_ocr",
        )

        assert finding.id is not None
        assert finding.snapshot_id == snapshot_id
        assert finding.key == "ocr.text"
        assert finding.value == {"text": "Sample text", "language": "eng"}
        assert finding.confidence_level == ConfidenceLevel.HIGH
        assert finding.confidence_score == 0.95
        assert finding.extraction_method == "tesseract_ocr"