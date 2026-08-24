"""Case number value object."""
import re
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CaseNumber:
    """Case number value object.

    Format: CASE-YYYY-NNNNN (e.g., CASE-2026-00001)
    - YYYY: 4-digit year
    - NNNNN: 5-digit sequence number
    """
    value: str

    @classmethod
    def generate(cls, year: int | None = None, sequence: int | None = None) -> "CaseNumber":
        """Generate a case number.

        Args:
            year: The year (defaults to current year)
            sequence: The sequence number (defaults to next from DB)

        Returns:
            CaseNumber instance
        """
        if year is None:
            year = datetime.now().year

        if sequence is None:
            raise ValueError("Sequence must be provided for generation")

        return cls(f"CASE-{year:04d}-{sequence:05d}")

    @classmethod
    def parse(cls, value: str) -> "CaseNumber":
        """Parse and validate a case number string.

        Args:
            value: The case number string to parse

        Returns:
            CaseNumber instance

        Raises:
            ValueError: If the format is invalid
        """
        if not cls.is_valid(value):
            raise ValueError(f"Invalid case number format: {value}. Expected format: CASE-YYYY-NNNNN")
        return cls(value)

    @classmethod
    def is_valid(cls, value: str | None) -> bool:
        """Check if a string is a valid case number format.

        Args:
            value: The string to validate

        Returns:
            True if valid, False otherwise
        """
        if value is None:
            return False
        return bool(re.match(r"^CASE-\d{4}-\d{5}$", value))

    @property
    def year(self) -> int:
        """Extract the year from the case number."""
        return int(self.value.split("-")[1])

    @property
    def sequence(self) -> int:
        """Extract the sequence number from the case number."""
        return int(self.value.split("-")[2])

    def __str__(self) -> str:
        return self.value