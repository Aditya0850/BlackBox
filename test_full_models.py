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

from sqlalchemy.orm import declarative_base

Base = declarative_base()


class CaseModel(Base):
    """SQLAlchemy model for intel.cases table."""
    __tablename__ = "cases"
    __table_args__ = (
        Index("idx_cases_status", "status"),
        Index("idx_cases_tags", "tags", postgresql_using="gin"),
        Index("idx_cases_case_number", "case_number", unique=True),
        {"schema": "intel"},
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    case_number: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[String(20), nullable=False]  # open, closed, archived
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
    mime_type: Mapped[String(100), nullable=False]
    file_size_bytes: Mapped[Integer] = mapped_column(nullable=False)
    sha256_hash: Mapped[String(64), nullable=False, unique=True]
    storage_location: Mapped[String] = mapped_column(Text, nullable=False)
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
    case_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("intel.cases.id", ondelete="CASCADE"),
        nullable=False,
    )
    evidence_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("intel.evidence.id", ondelete="CASCADE"),
        nullable=False,
    )
    pipeline_version: Mapped[String(50), nullable=False]
    plugin_versions: Mapped[dict[str, String]] = mapped_column(JSON, nullable=False, default=dict)
    trigger: Mapped[String(30), nullable=False]  # upload, manual_reanalysis, scheduled_reanalysis
    triggered_by: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    is_current: Mapped[Boolean] = mapped_column(nullable=False, default=True)
    superseded_by: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    investigator_approval: Mapped[String(20), nullable=True]  # pending, approved, rejected
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    case: Mapped["CaseModel"] = relationship(back_populates="snapshots")
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
    key: Mapped[String(255), nullable=False]
    value: Mapped[dict[String, Any]] = mapped_column(JSON, nullable=False)
    confidence_level: Mapped[String(20), nullable=False]  # high, medium, low, unknown
    confidence_score: Mapped[Float] = mapped_column(nullable=False)
    extraction_method: Mapped[String(100), nullable=False]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    snapshot: Mapped["AnalysisSnapshotModel"] = relationship(back_populates="findings")
    entity_mentions: Mapped[list["EntityMentionModel"]] = relationship(back_populates="finding", cascade="all, delete-orphan")
    relationship_evidence: Mapped[list["RelationshipEvidenceModel"]] = relationship(back_populates="finding", cascade="all, delete-orphan")


class EntityModel(Base):
    """SQLAlchemy model for intel.entities table."""
    __tablename__ = "entities"
    __table_args__ = (
        Index("idx_entities_case_type", "case_id", "entity_type"),
        Index("idx_entities_normalized_key", "normalized_key"),
        UniqueConstraint("case_id", "entity_type", "normalized_key", name="uq_entities_case_type_normalized_key"),
        {"schema": "intel"},
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=uuid4)
    case_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("intel.cases.id", ondelete="CASCADE"),
        nullable=False,
    )
    entity_type: Mapped[String(20), nullable=False]
    canonical_value: Mapped[Text, nullable=False]
    normalized_key: Mapped[String(255), nullable=False]
    entity_metadata: Mapped[dict[String, Any]] = mapped_column(JSON, nullable=True)
    resolution_confidence: Mapped[Float] = mapped_column(nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    mentions: Mapped[list["EntityMentionModel"]] = relationship(back_populates="entity", cascade="all, delete-orphan")
    relationships_as_subject: Mapped[list["RelationshipModel"]] = relationship(
        back_populates="subject_entity",
        foreign_keys="[RelationshipModel.subject_entity_id]",
        cascade="all, delete-orphan"
    )
    relationships_as_object: Mapped[list["RelationshipModel"]] = relationship(
        back_populates="object_entity",
        foreign_keys="[RelationshipModel.object_entity_id]",
        cascade="all, delete-orphan"
    )


class EntityMentionModel(Base):
    """SQLAlchemy model for intel.entity_mentions table."""
    __tablename__ = "entity_mentions"
    __table_args__ = (
        Index("idx_mentions_entity", "entity_id"),
        Index("idx_mentions_finding", "finding_id"),
        {"schema": "intel"},
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=uuid4)
    entity_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("intel.entities.id", ondelete="CASCADE"),
        nullable=False,
    )
    finding_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("intel.findings.id", ondelete="CASCADE"),
        nullable=False,
    )
    source_text: Mapped[String] = mapped_column(Text, nullable=False)
    text_start_offset: Mapped[Integer] = mapped_column(nullable=False)
    text_end_offset: Mapped[Integer] = mapped_column(nullable=False)
    confidence_score: Mapped[Float] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    entity: Mapped["EntityModel"] = relationship(back_populates="mentions")
    finding: Mapped["FindingModel"] = relationship(back_populates="entity_mentions")


class RelationshipModel(Base):
    """SQLAlchemy model for intel.relationships table."""
    __tablename__ = "relationships"
    __table_args__ = (
        Index("idx_relationships_case", "case_id"),
        {"schema": "intel"},
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=uuid4)
    case_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("intel.cases.id", ondelete="CASCADE"),
        nullable=False,
    )
    subject_entity_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("intel.entities.id", ondelete="CASCADE"),
        nullable=False,
    )
    predicate: Mapped[String(50), nullable=False]
    object_entity_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("intel.entities.id", ondelete="CASCADE"),
        nullable=False,
    )
    confidence_score: Mapped[Float] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    subject_entity: Mapped["EntityModel"] = relationship(
        back_populates="relationships_as_subject",
        foreign_keys="[RelationshipModel.subject_entity_id]"
    )
    object_entity: Mapped["EntityModel"] = relationship(
        back_populates="relationships_as_object",
        foreign_keys="[RelationshipModel.object_entity_id]"
    )
    evidence: Mapped[list["RelationshipEvidenceModel"]] = relationship(back_populates="relationship", cascade="all, delete-orphan")


class RelationshipEvidenceModel(Base):
    """SQLAlchemy model for intel.relationship_evidence table."""
    __tablename__ = "relationship_evidence"
    __table_args__ = (
        Index("idx_relationship_evidence_rel", "relationship_id"),
        {"schema": "intel"},
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=UUID), primary_key=uuid4)
    relationship_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=UUID),
        ForeignKey("intel.relationships.id", ondelete="CASCADE"),
        nullable=False,
    )
    finding_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=UUID),
        ForeignKey("intel.findings.id", ondelete="CASCADE"),
        nullable=False,
    )
    source_text: Mapped[String] = mapped_column(Text, nullable=False)
    text_start_offset: Mapped[Integer] = mapped_column(nullable=False)
    text_end_offset: Mapped[Integer] = mapped_column(nullable=False)
    confidence_score: Mapped[Float] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=DateTime), nullable=False, server_default=func.now())

    # Relationships
    relationship: Mapped["RelationshipModel"] = relationship(back_populates="evidence")
    finding: Mapped["FindingModel"] = relationship(back_populates="relationship_evidence")


class PatternFindingModel(Base):
    """SQLAlchemy model for intel.pattern_findings table."""
    __tablename__ = "pattern_findings"
    __table_args__ = (
        Index("idx_pattern_findings_case", "case_id"),
        {"schema": "intel"},
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=UUID), primary_key=uuid4)
    case_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=UUID),
        ForeignKey("intel.cases.id", ondelete="CASCADE"),
        nullable=False,
    )
    pattern_type: Mapped[String(50), nullable=False]
    description: Mapped[String(50), nullable=False]
    entities_involved: Mapped[list[UUID]] = mapped_column(ARRAY(PGUUID(as_uuid=UUID)), nullable=False)
    evidence_trail: Mapped[list[dict[String, Any]]] = mapped_column(JSON, nullable=False)
    confidence_score: Mapped[Float] = mapped_column(nullable=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=DateTime), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=DateTime), nullable=False, server_default=func.now())

    # Relationships
    case: Mapped["CaseModel"] = relationship(back_populates="pattern_findings")

if __name__ == "__main__":
    print("Models imported successfully!")