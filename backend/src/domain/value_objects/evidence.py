"""Evidence value objects."""
from enum import Enum


class EvidenceType(str, Enum):
    """Evidence type enumeration."""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    PDF = "pdf"
    EMAIL = "email"
    CHAT = "chat"
    MOBILE_EXTRACTION = "mobile_extraction"
    CCTV = "cctv"
    GPS = "gps"
    FINGERPRINT = "fingerprint"
    DNA = "dna"
    WEAPON_REPORT = "weapon_report"
    FINANCIAL = "financial"
    BROWSER_HISTORY = "browser_history"
    CLOUD_EXPORT = "cloud_export"
    OTHER = "other"


class MimeType(str, Enum):
    """Common MIME types for evidence files."""
    # Images
    JPEG = "image/jpeg"
    PNG = "image/png"
    TIFF = "image/tiff"
    BMP = "image/bmp"
    HEIC = "image/heic"

    # Videos
    MP4 = "video/mp4"
    AVI = "video/x-msvideo"
    MOV = "video/quicktime"
    MKV = "video/x-matroska"

    # Audio
    MP3 = "audio/mpeg"
    WAV = "audio/wav"
    OGG = "audio/ogg"
    M4A = "audio/mp4"

    # Documents
    PDF = "application/pdf"
    DOC = "application/msword"
    DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    TXT = "text/plain"
    RTF = "application/rtf"

    # Data
    JSON = "application/json"
    CSV = "text/csv"
    XML = "application/xml"
    ZIP = "application/zip"

    # Email
    EML = "message/rfc822"
    MSG = "application/vnd.ms-outlook"

    # Forensic
    E01 = "application/x-enCase"
    AFF = "application/x-aff"

    # Other
    OCTET_STREAM = "application/octet-stream"


class ConfidenceLevel(str, Enum):
    """Confidence level enumeration."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"