"""SQLAlchemy ORM models for the intel schema."""
import json
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class CaseModel(Base):
    """SQLAlchemy model for intel.cases table."""
    __tablename__ = "cases"
    __table_args__ = (
        Index("idx_cases_status", "status"),
        Index("idx_cases_tags", "tags", postgresql_using="gin"),
        {"schema": "intel"},
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # open, closed, archived
    created_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)

    # Relationships
    evidence_links: Mapped[list["CaseEvidenceModel"]] = relationship(back_populates="case", cascade="all, delete-orphan")
    snapshots: Mapped[list["AnalysisSnapshotModel"]] = relationship(back_populates="case")


class EvidenceModel(Base):
    """SQLAlchemy model for intel.evidence table."""
    __tablename__ = "evidence"
    __table_args__ = (
        Index("idx_evidence_hash", "sha256_hash", unique=True),
        {"schema": "intel"},
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    original_filename: Mapped[str] = mapped_column(Text, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(nullable=False)
    sha256_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    storage_location: Mapped[str] = mapped_column(Text, nullable=False)
    uploaded_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    case_links: Mapped[list["CaseEvidenceModel"]] = relationship(back_populates="evidence", cascade="all, delete-orphan")
    snapshots: Mapped[list["AnalysisSnapshotModel"]] = relationship(back_populates="evidence")


class CaseEvidenceModel(Base):
    """SQLAlchemy model for intel.case_evidence table (many-to-many)."""
    __tablename__ = "case_evidence"
    __table_args__ = (
        UniqueConstraint("case_id", "evidence_id", name="uq_case_evidence"),
        {"schema": "intel"},
    )

    case_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("intel.cases.id", ondelete="CASCADE"),
        primary_key=True,
    )
    evidence_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("intel.evidence.id", ondelete="CASCADE"),
        primary_key=True,
    )
    linked_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    linked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    case: Mapped["CaseModel"] = relationship(back_populates="evidence_links")
    evidence: Mapped["EvidenceModel"] = relationship(back_populates="case_links")


class AnalysisSnapshotModel(Base):
    """SQLAlchemy model for intel.analysis_snapshots table."""
    __tablename__ = "analysis_snapshots"
    __table_args__ = (
        Index("idx_snapshot_evidence", "evidence_id"),
        Index("idx_snapshot_current", "evidence_id", unique=True, postgresql_where=Text("is_current")),
        {"schema": "intel"},
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    evidence_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("intel.evidence.id", ondelete="CASCADE"),
        nullable=False,
    )
    pipeline_version: Mapped[str] = mapped_column(String(50), nullable=False)
    plugin_versions: Mapped[dict[str, str]] = mapped_column(JSON, nullable=False, default=dict)
    trigger: Mapped[str] = mapped_column(String(30), nullable=False)  # upload, manual_reanalysis, scheduled_reanalysis
    triggered_by: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    is_current: Mapped[bool] = mapped_column(nullable=False, default=True)
    superseded_by: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    investigator_approval: Mapped[str | None] = mapped_column(String(20), nullable=True)  # pending, approved, rejected
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    evidence: Mapped["EvidenceModel"] = relationship(back_populates="snapshots")
    findings: Mapped[list["FindingModel"]] = relationship(back_populates="snapshot", cascade="all, delete-orphan")


class FindingModel(Base):
    """SQLAlchemy model for intel.findings table."""
    __tablename__ = "findings"
    __table_args__ = (
        Index("idx_findings_snapshot", "snapshot_id"),
        {"schema": "intel"},
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    snapshot_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("intel.analysis_snapshots.id", ondelete="CASCADE"),
        nullable=False,
    )
    key: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    confidence_level: Mapped[str] = mapped_column(String(20), nullable=False)  # high, medium, low, unknown
    confidence_score: Mapped[float] = mapped_column(nullable=False)
    extraction_method: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    snapshot: Mapped["AnalysisSnapshotModel"] = relationship(back_populates="findings")