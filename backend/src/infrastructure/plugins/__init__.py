"""Plugins infrastructure exports."""
from .ocr import TesseractOCRProvider, get_ocr_provider

__all__ = ["TesseractOCRProvider", "get_ocr_provider"]