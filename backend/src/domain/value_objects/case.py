"""Case value objects."""
from enum import Enum


class CaseStatus(str, Enum):
    """Case status enumeration."""
    OPEN = "open"
    CLOSED = "closed"
    ARCHIVED = "archived"