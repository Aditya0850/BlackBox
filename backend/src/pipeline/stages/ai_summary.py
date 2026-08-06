"""AI Summary pipeline stage - Generates AI-powered summary of evidence."""
import logging
from typing import Any

from ...pipeline.contracts import EvidenceContext, Finding, PipelineStage, StageExecutionRecord, StageStatus
from ...domain.value_objects import ConfidenceLevel

logger = logging.getLogger(__name__)


class AISummaryStage(PipelineStage):
    """Stage that generates an AI summary of the evidence."""
    name: str = "ai_summary"
    model_version: str = "llm-v1"

    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.model_version = "llm-v1"  # Would be actual model version in production

    def run(self, context: EvidenceContext) -> EvidenceContext:
        """Generate AI summary based on previous findings."""
        record = StageExecutionRecord(
            stage_name=self.name,
            status=StageStatus.RETRYING,
            started_at=None,
            model_version=self.model_version,
        )

        try:
            # Collect relevant findings from previous stages
            ocr_text = self._get_ocr_text(context)
            metadata = context.metadata.get("extracted_metadata", {})

            # Generate summary
            summary = self._generate_summary(ocr_text, metadata, context.mime_type)

            # Add finding
            context.add_finding(Finding(
                key="ai.summary",
                value={
                    "summary": summary,
                    "source_findings": {
                        "ocr_text_present": bool(ocr_text),
                        "metadata_keys": list(metadata.keys()),
                    },
                },
                confidence_level=ConfidenceLevel.MEDIUM,
                confidence_score=0.7,
                extraction_method="llm_summary",
            ))

            record.status = StageStatus.SUCCESS
            record.reason = "AI summary generated"

        except Exception as e:
            record.status = StageStatus.FAILED
            record.error_details = str(e)
            record.reason = f"AI summary failed: {type(e).__name__}"
            logger.error(f"AI summary stage failed: {e}", exc_info=True)

            context.add_finding(Finding(
                key="ai.summary",
                value={"error": str(e)},
                confidence_level=ConfidenceLevel.UNKNOWN,
                confidence_score=0.0,
                extraction_method="llm_summary",
            ))

        return context

    def _get_ocr_text(self, context: EvidenceContext) -> str:
        """Get OCR text from previous findings."""
        ocr_findings = context.get_findings_by_key("ocr.text")
        if ocr_findings:
            latest = ocr_findings[-1]
            return latest.value.get("text", "") if isinstance(latest.value, dict) else str(latest.value)
        return ""

    def _generate_summary(self, ocr_text: str, metadata: dict, mime_type: str) -> dict[str, Any]:
        """Generate a summary of the evidence."""
        # In production, this would call an LLM
        # For now, return a structured template

        summary = {
            "description": self._create_description(ocr_text, metadata, mime_type),
            "key_points": self._extract_key_points(ocr_text, metadata),
            "tags": self._suggest_tags(ocr_text, metadata, mime_type),
            "investigation_relevance": self._assess_relevance(ocr_text, metadata),
        }

        return summary

    def _create_description(self, ocr_text: str, metadata: dict, mime_type: str) -> str:
        """Create a natural language description."""
        parts = []

        if mime_type.startswith("image/"):
            parts.append(f"This is an image file ({metadata.get('width', '?')}x{metadata.get('height', '?')})")
        elif mime_type == "application/pdf":
            parts.append(f"This is a PDF document with {metadata.get('page_count', '?')} pages")
        else:
            parts.append(f"This is a {mime_type} file")

        if ocr_text:
            text_preview = ocr_text[:200] + ("..." if len(ocr_text) > 200 else "")
            parts.append(f"OCR extracted text: \"{text_preview}\"")
        else:
            parts.append("No text content extracted via OCR")

        if metadata.get("exif"):
            exif = metadata["exif"]
            if "DateTime" in exif:
                parts.append(f"Photo taken on: {exif['DateTime']}")
            if "Make" in exif and "Model" in exif:
                parts.append(f"Camera: {exif['Make']} {exif['Model']}")
            if exif.get("GPSInfo"):
                parts.append("GPS location data present")

        return ". ".join(parts) + "."

    def _extract_key_points(self, ocr_text: str, metadata: dict) -> list[str]:
        """Extract key investigation points."""
        points = []

        if ocr_text:
            # Check for common investigation keywords
            keywords = {
                "license plate": ["license", "plate", "registration"],
                "phone number": ["phone", "call", "number"],
                "address": ["address", "street", "avenue", "road"],
                "date/time": ["date", "time", "am", "pm", ":"],
                "name": ["name", "mr.", "mrs.", "dr."],
                "vehicle": ["car", "truck", "vehicle", "van", "suv"],
                "weapon": ["gun", "knife", "weapon", "firearm"],
            }

            text_lower = ocr_text.lower()
            for point, terms in keywords.items():
                if any(term in text_lower for term in terms):
                    points.append(f"Potential {point} mentioned in text")

        if metadata.get("exif", {}).get("GPSInfo"):
            points.append("GPS coordinates available in EXIF")

        if metadata.get("exif", {}).get("DateTime"):
            points.append("Timestamp available in EXIF")

        if not points:
            points.append("No specific investigation points identified")

        return points

    def _suggest_tags(self, ocr_text: str, metadata: dict, mime_type: str) -> list[str]:
        """Suggest tags for categorization."""
        tags = []

        if mime_type.startswith("image/"):
            tags.append("image")
        elif mime_type == "application/pdf":
            tags.append("document")

        if ocr_text:
            tags.append("ocr-text")

        if metadata.get("exif", {}).get("GPSInfo"):
            tags.append("geotagged")

        if metadata.get("exif", {}).get("DateTime"):
            tags.append("timestamped")

        return tags

    def _assess_relevance(self, ocr_text: str, metadata: dict) -> str:
        """Assess investigation relevance."""
        score = 0

        if ocr_text and len(ocr_text) > 50:
            score += 2
        if metadata.get("exif", {}).get("GPSInfo"):
            score += 2
        if metadata.get("exif", {}).get("DateTime"):
            score += 1

        if score >= 4:
            return "high"
        elif score >= 2:
            return "medium"
        return "low"