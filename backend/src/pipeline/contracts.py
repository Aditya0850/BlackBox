"""Pipeline contracts - Core interfaces for the evidence processing pipeline."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Protocol, Optional


class StageStatus(str, Enum):
    """Pipeline stage execution status."""
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


@dataclass
class StageExecutionRecord:
    """Record of a pipeline stage execution."""
    stage_name: str
    status: StageStatus
    started_at: datetime
    finished_at: Optional[datetime] = None
    model_version: Optional[str] = None
    reason: Optional[str] = None
    error_details: Optional[str] = None


@dataclass
class Finding:
    """A finding extracted by a pipeline stage."""
    key: str
    value: Any
    confidence_level: str  # high, medium, low, unknown
    confidence_score: float
    extraction_method: str


@dataclass
class EvidenceContext:
    """Context passed through the pipeline stages."""
    evidence_id: str
    snapshot_id: str
    file_bytes: bytes = field(default=None, repr=False)  # Raw evidence bytes
    mime_type: str = ""
    findings: list[Finding] = field(default_factory=list)
    execution_history: list[StageExecutionRecord] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)  # Arbitrary stage metadata

    def add_finding(self, finding: Finding) -> None:
        """Add a finding to the context."""
        self.findings.append(finding)

    def record_execution(self, record: StageExecutionRecord) -> None:
        """Record a stage execution."""
        self.execution_history.append(record)

    def get_findings_by_key(self, key: str) -> list[Finding]:
        """Get all findings with a specific key."""
        return [f for f in self.findings if f.key == key]

    def get_latest_finding(self, key: str) -> Optional[Finding]:
        """Get the most recent finding with a specific key."""
        findings = self.get_findings_by_key(key)
        return findings[-1] if findings else None


class PipelineStage(Protocol):
    """Protocol for pipeline stages.

    A stage must NEVER fail silently — if it cannot complete, it still
    returns a context with a FAILED/SKIPPED StageExecutionRecord.
    """
    name: str

    def run(self, context: EvidenceContext) -> EvidenceContext: ...


class OCRProvider(Protocol):
    """Protocol for OCR providers."""
    def extract_text(self, file_bytes: bytes, mime_type: str) -> list[Finding]: ...