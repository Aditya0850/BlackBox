"""Tesseract OCR provider implementation."""
import logging
from dataclasses import dataclass
from typing import Optional

from PIL import Image
import pytesseract

from ....pipeline.contracts import Finding, OCRProvider
from ....domain.value_objects import ConfidenceLevel

logger = logging.getLogger(__name__)


@dataclass
class OCRResult:
    """Result of OCR extraction."""
    text: str
    confidence: float
    language: str


class TesseractOCRProvider:
    """Tesseract-based OCR implementation."""

    def __init__(self, languages: str = "eng", config: str = ""):
        self.languages = languages
        self.config = config
        self.model_version = f"tesseract-{pytesseract.get_tesseract_version()}"

    def extract_text(self, file_bytes: bytes, mime_type: str) -> list[Finding]:
        """Extract text from image bytes using Tesseract OCR."""
        findings = []

        try:
            # Validate mime type
            if not self._is_supported_image(mime_type):
                logger.warning(f"Unsupported mime type for OCR: {mime_type}")
                return [Finding(
                    key="ocr.text",
                    value={"error": f"Unsupported image type: {mime_type}"},
                    confidence_level=ConfidenceLevel.UNKNOWN,
                    confidence_score=0.0,
                    extraction_method="tesseract_ocr",
                )]

            # Load image from bytes
            from io import BytesIO
            image = Image.open(BytesIO(file_bytes))

            # Run OCR
            result = self._run_ocr(image)

            # Create finding
            findings.append(Finding(
                key="ocr.text",
                value={
                    "text": result.text,
                    "language": result.language,
                    "word_count": len(result.text.split()) if result.text else 0,
                },
                confidence_level=self._confidence_level(result.confidence),
                confidence_score=result.confidence / 100.0,
                extraction_method="tesseract_ocr",
            ))

            # Also extract structured data if available
            if result.text:
                structured_findings = self._extract_structured_data(result.text)
                findings.extend(structured_findings)

        except Exception as e:
            logger.error(f"OCR extraction failed: {e}", exc_info=True)
            findings.append(Finding(
                key="ocr.text",
                value={"error": str(e)},
                confidence_level=ConfidenceLevel.UNKNOWN,
                confidence_score=0.0,
                extraction_method="tesseract_ocr",
            ))

        return findings

    def _is_supported_image(self, mime_type: str) -> bool:
        """Check if mime type is supported for OCR."""
        supported = {
            "image/jpeg", "image/png", "image/tiff", "image/bmp",
            "image/heic", "image/webp", "application/pdf",
        }
        return mime_type in supported

    def _run_ocr(self, image: Image.Image) -> OCRResult:
        """Run Tesseract OCR on image."""
        # Get detailed OCR data
        data = pytesseract.image_to_data(
            image,
            lang=self.languages,
            config=self.config,
            output_type=pytesseract.Output.DICT,
        )

        # Calculate average confidence
        confidences = [float(c) for c in data["conf"] if c != "-1"]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        # Get full text
        text = pytesseract.image_to_string(
            image,
            lang=self.languages,
            config=self.config,
        ).strip()

        return OCRResult(
            text=text,
            confidence=avg_confidence,
            language=self.languages,
        )

    def _confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Map confidence score to level."""
        if confidence >= 80:
            return ConfidenceLevel.HIGH
        elif confidence >= 50:
            return ConfidenceLevel.MEDIUM
        elif confidence > 0:
            return ConfidenceLevel.LOW
        return ConfidenceLevel.UNKNOWN

    def _extract_structured_data(self, text: str) -> list[Finding]:
        """Extract structured data from OCR text (dates, phones, emails, etc.)."""
        import re

        findings = []

        # Email extraction
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if emails:
            findings.append(Finding(
                key="ocr.emails",
                value={"emails": emails},
                confidence_level=ConfidenceLevel.HIGH,
                confidence_score=0.9,
                extraction_method="regex",
            ))

        # Phone numbers (basic pattern)
        phones = re.findall(r'(\+?\d{1,4}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}', text)
        if phones:
            findings.append(Finding(
                key="ocr.phones",
                value={"phones": [p for p in phones if p]},
                confidence_level=ConfidenceLevel.MEDIUM,
                confidence_score=0.7,
                extraction_method="regex",
            ))

        # Dates (basic patterns)
        date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # MM/DD/YYYY or DD/MM/YYYY
            r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',    # YYYY/MM/DD
        ]
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, text))
        if dates:
            findings.append(Finding(
                key="ocr.dates",
                value={"dates": dates},
                confidence_level=ConfidenceLevel.MEDIUM,
                confidence_score=0.6,
                extraction_method="regex",
            ))

        return findings


# Module-level provider instance
_ocr_provider: Optional[TesseractOCRProvider] = None


def get_ocr_provider() -> TesseractOCRProvider:
    """Get the singleton OCR provider instance."""
    global _ocr_provider
    if _ocr_provider is None:
        _ocr_provider = TesseractOCRProvider()
    return _ocr_provider