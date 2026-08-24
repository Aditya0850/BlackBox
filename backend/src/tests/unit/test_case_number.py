"""Unit tests for CaseNumber value object."""
import pytest
from datetime import datetime

from src.domain.value_objects import CaseNumber


class TestCaseNumber:
    """Tests for CaseNumber value object."""

    def test_generate_creates_valid_format(self):
        """Test that generate creates valid case number format."""
        case_number = CaseNumber.generate(year=2026, sequence=1)
        assert case_number.value == "CASE-2026-00001"

    def test_generate_with_different_sequences(self):
        """Test generation with various sequence numbers."""
        assert CaseNumber.generate(2026, 1).value == "CASE-2026-00001"
        assert CaseNumber.generate(2026, 42).value == "CASE-2026-00042"
        assert CaseNumber.generate(2026, 99999).value == "CASE-2026-99999"

    def test_generate_with_different_years(self):
        """Test generation with different years."""
        assert CaseNumber.generate(2025, 1).value == "CASE-2025-00001"
        assert CaseNumber.generate(2030, 1).value == "CASE-2030-00001"

    def test_parse_valid_case_number(self):
        """Test parsing a valid case number string."""
        case_number = CaseNumber.parse("CASE-2026-00001")
        assert case_number.value == "CASE-2026-00001"

    def test_parse_invalid_format_raises(self):
        """Test that parsing invalid format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid case number format"):
            CaseNumber.parse("INVALID")

        with pytest.raises(ValueError, match="Invalid case number format"):
            CaseNumber.parse("CASE-2026-1")  # Too few digits

        with pytest.raises(ValueError, match="Invalid case number format"):
            CaseNumber.parse("CASE-26-00001")  # Too few year digits

        with pytest.raises(ValueError, match="Invalid case number format"):
            CaseNumber.parse("case-2026-00001")  # Wrong case

        with pytest.raises(ValueError, match="Invalid case number format"):
            CaseNumber.parse("CASE-2026-ABCDE")  # Non-numeric sequence

    def test_is_valid(self):
        """Test is_valid method."""
        assert CaseNumber.is_valid("CASE-2026-00001") is True
        assert CaseNumber.is_valid("CASE-2025-99999") is True
        assert CaseNumber.is_valid("INVALID") is False
        assert CaseNumber.is_valid("CASE-2026-1") is False
        assert CaseNumber.is_valid("") is False
        assert CaseNumber.is_valid(None) is False

    def test_year_property(self):
        """Test year property extraction."""
        assert CaseNumber.parse("CASE-2026-00001").year == 2026
        assert CaseNumber.parse("CASE-2025-99999").year == 2025
        assert CaseNumber.parse("CASE-2030-00042").year == 2030

    def test_sequence_property(self):
        """Test sequence property extraction."""
        assert CaseNumber.parse("CASE-2026-00001").sequence == 1
        assert CaseNumber.parse("CASE-2026-00042").sequence == 42
        assert CaseNumber.parse("CASE-2026-99999").sequence == 99999

    def test_str_returns_value(self):
        """Test string representation."""
        cn = CaseNumber.parse("CASE-2026-00001")
        assert str(cn) == "CASE-2026-00001"

    def test_equality(self):
        """Test equality comparison."""
        cn1 = CaseNumber.parse("CASE-2026-00001")
        cn2 = CaseNumber.parse("CASE-2026-00001")
        cn3 = CaseNumber.parse("CASE-2026-00002")
        assert cn1 == cn2
        assert cn1 != cn3

    def test_hashable(self):
        """Test that CaseNumber is hashable (can be used in sets/dicts)."""
        cn1 = CaseNumber.parse("CASE-2026-00001")
        cn2 = CaseNumber.parse("CASE-2026-00002")
        s = {cn1, cn2}
        assert len(s) == 2
        d = {cn1: "first"}
        assert d[cn1] == "first"