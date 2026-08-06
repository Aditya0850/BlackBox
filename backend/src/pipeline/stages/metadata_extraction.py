"""Metadata Extraction pipeline stage - Extracts file metadata."""
import json
import logging
from datetime import datetime
from typing import Any

from PIL import Image

from ...pipeline.contracts import EvidenceContext, Finding, PipelineStage, StageExecutionRecord, StageStatus
from ...domain.value_objects import ConfidenceLevel

logger = logging.getLogger(__name__)


class MetadataExtractionStage(PipelineStage):
    """Stage that extracts metadata from evidence files."""
    name: str = "metadata_extraction"
    model_version: str = "exif-v1"

    def run(self, context: EvidenceContext) -> EvidenceContext:
        """Extract metadata based on file type."""
        record = StageExecutionRecord(
            stage_name=self.name,
            status=StageStatus.RETRYING,
            started_at=None,
            model_version=self.model_version,
        )

        try:
            if not context.file_bytes:
                raise ValueError("No file bytes provided in context")

            mime_type = context.mime_type or "application/octet-stream"
            metadata = self._extract_metadata(context.file_bytes, mime_type)

            # Store metadata in context
            context.metadata["extracted_metadata"] = metadata

            # Add finding
            context.add_finding(Finding(
                key="metadata.extracted",
                value=metadata,
                confidence_level=ConfidenceLevel.HIGH,
                confidence_score=0.95,
                extraction_method="exif_pil",
            ))

            record.status = StageStatus.SUCCESS
            record.reason = f"Extracted metadata for {mime_type}"

        except Exception as e:
            record.status = StageStatus.FAILED
            record.error_details = str(e)
            record.reason = f"Metadata extraction failed: {type(e).__name__}"
            logger.error(f"Metadata extraction failed: {e}", exc_info=True)

            context.add_finding(Finding(
                key="metadata.extracted",
                value={"error": str(e)},
                confidence_level=ConfidenceLevel.UNKNOWN,
                confidence_score=0.0,
                extraction_method="exif_pil",
            ))

        return context

    def _extract_metadata(self, file_bytes: bytes, mime_type: str) -> dict[str, Any]:
        """Extract metadata based on MIME type."""
        metadata = {
            "file_size_bytes": len(file_bytes),
            "mime_type": mime_type,
            "extracted_at": datetime.utcnow().isoformat(),
        }

        if mime_type.startswith("image/"):
            metadata.update(self._extract_image_metadata(file_bytes))
        elif mime_type == "application/pdf":
            metadata.update(self._extract_pdf_metadata(file_bytes))
        elif mime_type.startswith("video/"):
            metadata.update(self._extract_video_metadata(file_bytes))
        elif mime_type.startswith("audio/"):
            metadata.update(self._extract_audio_metadata(file_bytes))

        return metadata

    def _extract_image_metadata(self, file_bytes: bytes) -> dict[str, Any]:
        """Extract EXIF and image metadata."""
        from io import BytesIO

        metadata = {}
        try:
            image = Image.open(BytesIO(file_bytes))

            # Basic image info
            metadata["width"] = image.width
            metadata["height"] = image.height
            metadata["format"] = image.format
            metadata["mode"] = image.mode

            # EXIF data
            exif = image.getexif()
            if exif:
                exif_data = {}
                for tag_id, value in exif.items():
                    tag = Image.ExifTags.TAGS.get(tag_id, tag_id)
                    # Convert non-serializable values
                    if hasattr(value, 'isoformat'):
                        value = value.isoformat()
                    elif isinstance(value, bytes):
                        value = value.hex()
                    exif_data[tag] = value
                metadata["exif"] = exif_data

            # GPS info if available
            if "GPSInfo" in exif_data:
                metadata["has_gps"] = True
                gps = exif_data["GPSInfo"]
                metadata["gps_raw"] = gps

        except Exception as e:
            logger.warning(f"Failed to extract image metadata: {e}")
            metadata["error"] = str(e)

        return metadata

    def _extract_pdf_metadata(self, file_bytes: bytes) -> dict[str, Any]:
        """Extract PDF metadata."""
        metadata = {}
        try:
            import pypdf
            from io import BytesIO

            pdf_file = BytesIO(file_bytes)
            reader = pypdf.PdfReader(pdf_file)

            if reader.metadata:
                meta = {k.lstrip('/'): str(v) for k, v in reader.metadata.items()}
                metadata["pdf_info"] = meta

            metadata["page_count"] = len(reader.pages)

        except Exception as e:
            logger.warning(f"Failed to extract PDF metadata: {e}")
            metadata["error"] = str(e)

        return metadata

    def _extract_video_metadata(self, file_bytes: bytes) -> dict[str, Any]:
        """Extract video metadata."""
        metadata = {}
        try:
            # Basic file info only - full video metadata requires ffprobe
            metadata["note"] = "Full video metadata requires ffprobe (not installed)"
        except Exception as e:
            logger.warning(f"Failed to extract video metadata: {e}")
            metadata["error"] = str(e)
        return metadata

    def _extract_audio_metadata(self, file_bytes: bytes) -> dict[str, Any]:
        """Extract audio metadata."""
        metadata = {}
        try:
            # Basic file info only - full audio metadata requires mutagen
            metadata["note"] = "Full audio metadata requires mutagen (not installed)"
        except Exception as e:
            logger.warning(f"Failed to extract audio metadata: {e}")
            metadata["error"] = str(e)
        return metadata