"""ID value objects for the BlackBox domain."""
from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class CaseId:
    """Case identifier."""
    value: UUID

    @classmethod
    def generate(cls) -> "CaseId":
        return cls(uuid4())

    @classmethod
    def from_string(cls, value: str) -> "CaseId":
        return cls(UUID(value))

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class EvidenceId:
    """Evidence identifier."""
    value: UUID

    @classmethod
    def generate(cls) -> "EvidenceId":
        return cls(uuid4())

    @classmethod
    def from_string(cls, value: str) -> "EvidenceId":
        return cls(UUID(value))

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class UserId:
    """User identifier."""
    value: UUID

    @classmethod
    def generate(cls) -> "UserId":
        return cls(uuid4())

    @classmethod
    def from_string(cls, value: str) -> "UserId":
        return cls(UUID(value))

    def __str__(self) -> str:
        return str(self.value)