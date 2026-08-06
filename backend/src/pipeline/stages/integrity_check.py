"""Integrity Check pipeline stage - Verifies SHA256 hash matches."""
import hashlib
import logging
from dataclasses import dataclass

from ...pipeline.contracts import EvidenceContext, Finding, PipelineStage, StageExecutionRecord, StageStatus
from ...domain.value_objects import ConfidenceLevel

logger = logging.getLogger(__name__)


@dataclass
class IntegrityCheckStage(PipelineStage):
    """Stage that verifies evidence integrity via SHA256 hash."""
    name: str = "integrity_check"
    model_version: str = "sha256-v1"

    def run(self, context: EvidenceContext) -> EvidenceContext:
        """Verify the SHA256 hash of the evidence file."""
        import time
        started_at = time.time()

        record = StageExecutionRecord(
            stage_name=self.name,
            status=StageStatus.RETRYING,
            started_at=None,  # Will be set by orchestrator
            model_version=self.model_version,
        )

        try:
            if not context.file_bytes:
                raise ValueError("No file bytes provided in context")

            # Compute hash
            computed_hash = hashlib.sha256(context.file_bytes).hexdigest()

            # Check if we have expected hash in metadata
            expected_hash = context.metadata.get("expected_sha256")
            if not expected_hash:
                # Store computed hash for future reference
                context.metadata["computed_sha256"] = computed_hash
                record.status = StageStatus.SUCCESS
                record.reason = "Hash computed and stored (no expected hash to verify)"
                logger.info(f"Computed SHA256: {computed_hash}")
            else:
                if computed_hash == expected_hash:
                    record.status = StageStatus.SUCCESS
                    record.reason = "Hash verification passed"
                    logger.info("SHA256 hash verification PASSED")
                else:
                    record.status = StageStatus.FAILED
                    record.reason = "Hash verification FAILED"
                    record.error_details = f"Expected: {expected_hash}, Got: {computed_hash}"
                    logger.error(f"SHA256 hash verification FAILED. Expected: {expected_hash}, Got: {computed_hash}")

            # Add finding
            context.add_finding(Finding(
                key="integrity.sha256",
                value={
                    "computed_hash": computed_hash,
                    "expected_hash": expected_hash,
                    "verified": expected_hash is not None and computed_hash == expected_hash,
                },
                confidence_level=ConfidenceLevel.HIGH if (expected_hash is None or computed_hash == expected_hash) else ConfidenceLevel.LOW,
                confidence_score=1.0 if (expected_hash is None or computed_hash == expected_hash) else 0.0,
                extraction_method="sha256",
            ))

        except Exception as e:
            record.status = StageStatus.FAILED
            record.error_details = str(e)
            record.reason = f"Integrity check failed: {type(e).__name__}"
            logger.error(f"Integrity check failed: {e}", exc_info=True)

            context.add_finding(Finding(
                key="integrity.sha256",
                value={"error": str(e)},
                confidence_level=ConfidenceLevel.UNKNOWN,
                confidence_score=0.0,
                extraction_method="sha256",
            ))

        return context