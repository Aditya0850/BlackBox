"""Unit tests for pipeline contracts."""
import pytest
from datetime import datetime
from uuid import uuid4

from src.pipeline.contracts import (
    EvidenceContext,
    Finding,
    StageExecutionRecord,
    StageStatus,
    OCRProvider,
    PipelineStage,
)


class TestStageExecutionRecord:
    """Tests for StageExecutionRecord."""

    def test_create_record(self):
        record = StageExecutionRecord(
            stage_name="test_stage",
            status=StageStatus.SUCCESS,
            started_at=datetime.utcnow(),
        )

        assert record.stage_name == "test_stage"
        assert record.status == StageStatus.SUCCESS
        assert record.started_at is not None
        assert record.finished_at is None
        assert record.model_version is None
        assert record.reason is None
        assert record.error_details is None


class TestFinding:
    """Tests for Finding."""

    def test_create_finding(self):
        finding = Finding(
            key="test.key",
            value={"data": "value"},
            confidence_level="high",
            confidence_score=0.9,
            extraction_method="test_method",
        )

        assert finding.key == "test.key"
        assert finding.value == {"data": "value"}
        assert finding.confidence_level == "high"
        assert finding.confidence_score == 0.9
        assert finding.extraction_method == "test_method"


class TestEvidenceContext:
    """Tests for EvidenceContext."""

    def test_create_context(self):
        context = EvidenceContext(
            evidence_id="evidence-123",
            snapshot_id="snapshot-456",
        )

        assert context.evidence_id == "evidence-123"
        assert context.snapshot_id == "snapshot-456"
        assert context.file_bytes is None
        assert context.mime_type == ""
        assert context.findings == []
        assert context.execution_history == []
        assert context.metadata == {}

    def test_add_finding(self):
        context = EvidenceContext(
            evidence_id="evidence-123",
            snapshot_id="snapshot-456",
        )

        finding = Finding(
            key="test.key",
            value={"data": "value"},
            confidence_level="high",
            confidence_score=0.9,
            extraction_method="test_method",
        )

        context.add_finding(finding)

        assert len(context.findings) == 1
        assert context.findings[0] == finding

    def test_record_execution(self):
        context = EvidenceContext(
            evidence_id="evidence-123",
            snapshot_id="snapshot-456",
        )

        record = StageExecutionRecord(
            stage_name="test_stage",
            status=StageStatus.SUCCESS,
            started_at=datetime.utcnow(),
        )

        context.record_execution(record)

        assert len(context.execution_history) == 1
        assert context.execution_history[0] == record

    def test_get_findings_by_key(self):
        context = EvidenceContext(
            evidence_id="evidence-123",
            snapshot_id="snapshot-456",
        )

        finding1 = Finding(
            key="ocr.text",
            value={"text": "first"},
            confidence_level="high",
            confidence_score=0.9,
            extraction_method="test",
        )
        finding2 = Finding(
            key="ocr.text",
            value={"text": "second"},
            confidence_level="medium",
            confidence_score=0.7,
            extraction_method="test",
        )
        finding3 = Finding(
            key="metadata.extracted",
            value={"width": 100},
            confidence_level="high",
            confidence_score=0.95,
            extraction_method="test",
        )

        context.add_finding(finding1)
        context.add_finding(finding2)
        context.add_finding(finding3)

        ocr_findings = context.get_findings_by_key("ocr.text")
        assert len(ocr_findings) == 2
        assert ocr_findings[0].value["text"] == "first"
        assert ocr_findings[1].value["text"] == "second"

        metadata_findings = context.get_findings_by_key("metadata.extracted")
        assert len(metadata_findings) == 1

        empty_findings = context.get_findings_by_key("nonexistent")
        assert len(empty_findings) == 0

    def test_get_latest_finding(self):
        context = EvidenceContext(
            evidence_id="evidence-123",
            snapshot_id="snapshot-456",
        )

        finding1 = Finding(
            key="ocr.text",
            value={"text": "first"},
            confidence_level="high",
            confidence_score=0.9,
            extraction_method="test",
        )
        finding2 = Finding(
            key="ocr.text",
            value={"text": "second"},
            confidence_level="medium",
            confidence_score=0.7,
            extraction_method="test",
        )

        context.add_finding(finding1)
        context.add_finding(finding2)

        latest = context.get_latest_finding("ocr.text")
        assert latest is not None
        assert latest.value["text"] == "second"

        none = context.get_latest_finding("nonexistent")
        assert none is None


class MockStage:
    """Mock pipeline stage for testing."""

    def __init__(self, name: str, should_fail: bool = False):
        self.name = name
        self.should_fail = should_fail

    def run(self, context: EvidenceContext) -> EvidenceContext:
        if self.should_fail:
            raise ValueError("Stage failed")
        context.add_finding(Finding(
            key=f"{self.name}.result",
            value={"processed": True},
            confidence_level="high",
            confidence_score=1.0,
            extraction_method="mock",
        ))
        return context


class TestPipelineIntegration:
    """Integration tests for pipeline."""

    def test_pipeline_contracts_can_be_imported(self):
        """Verify all pipeline contracts can be imported."""
        assert PipelineStage
        assert OCRProvider
        assert EvidenceContext
        assert Finding
        assert StageExecutionRecord
        assert StageStatus