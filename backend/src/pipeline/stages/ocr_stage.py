"""OCR pipeline stage - Extracts text from images using Tesseract."""
import logging

from ...pipeline.contracts import EvidenceContext, Finding, PipelineStage, StageExecutionRecord, StageStatus
from ...domain.value_objects import ConfidenceLevel
from ...infrastructure.plugins.ocr import get_ocr_provider

logger = logging.getLogger(__name__)


class OCRStage(PipelineStage):
    """Stage that performs OCR on image evidence."""
    name: str = "ocr"
    model_version: str = "tesseract-5.3"

    def __init__(self):
        self.ocr_provider = get_ocr_provider()
        self.model_version = self.ocr_provider.model_version

    def run(self, context: EvidenceContext) -> EvidenceContext:
        """Run OCR extraction on image evidence."""
        record = StageExecutionRecord(
            stage_name=self.name,
            status=StageStatus.RETRYING,
            started_at=None,
            model_version=self.model_version,
        )

        try:
            if not context.file_bytes:
                raise ValueError("No file bytes provided in context")

            # Only run OCR on images and PDFs
            supported_types = {
                "image/jpeg", "image/png", "image/tiff", "image/bmp",
                "image/heic", "image/webp", "application/pdf",
            }

            if context.mime_type not in supported_types:
                record.status = StageStatus.SKIPPED
                record.reason = f"OCR not applicable for mime type: {context.mime_type}"
                logger.info(f"Skipping OCR for unsupported type: {context.mime_type}")
                return context

            # Run OCR
            findings = self.ocr_provider.extract_text(context.file_bytes, context.mime_type)

            # Add all findings
            for finding in findings:
                context.add_finding(finding)

            # Check if any finding was successful
            success_findings = [f for f in findings if f.confidence_level != ConfidenceLevel.UNKNOWN or f.confidence_score > 0]
            if success_findings:
                record.status = StageStatus.SUCCESS
                record.reason = f"OCR completed with {len(success_findings)} findings"
            else:
                record.status = StageStatus.FAILED
                record.reason = "OCR produced no valid findings"

        except Exception as e:
            record.status = StageStatus.FAILED
            record.error_details = str(e)
            record.reason = f"OCR failed: {type(e).__name__}"
            logger.error(f"OCR stage failed: {e}", exc_info=True)

            context.add_finding(Finding(
                key="ocr.text",
                value={"error": str(e)},
                confidence_level=ConfidenceLevel.UNKNOWN,
                confidence_score=0.0,
                extraction_method="tesseract_ocr",
            ))

        return context