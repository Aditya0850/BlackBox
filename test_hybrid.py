#!/usr/bin/env python3

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
import uuid

Base = declarative_base()

# Minimal reproducer of the pattern that should work
class FindingModel(Base):
    __tablename__ = 'findings'
    __table_args__ = {"schema": "intel"}

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_mentions: Mapped[list["EntityMentionModel"]] = relationship(back_populates="finding")
    relationship_evidence: Mapped[list["RelationshipEvidenceModel"]] = relationship(back_populates="finding")

class EntityMentionModel(Base):
    __tablename__ = 'entity_mentions'
    __table_args__ = {"schema": "intel"}

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    finding_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("intel.findings.id"))
    finding: Mapped["FindingModel"] = relationship(back_populates="entity_mentions")

class RelationshipEvidenceModel(Base):
    __tablename__ = 'relationship_evidence'
    __table_args__ = {"schema": "intel"}

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    finding_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("intel.findings.id"))
    finding: Mapped["FindingModel"] = relationship(back_populates="relationship_evidence")

if __name__ == "__main__":
    print("Success! Hybrid test imported.")