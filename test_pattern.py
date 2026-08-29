#!/usr/bin/env python3

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class FindingModel(Base):
    __tablename__ = 'findings'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    entity_mentions: Mapped[list["EntityMentionModel"]] = relationship(back_populates="finding")
    relationship_evidence: Mapped[list["RelationshipEvidenceModel"]] = relationship(back_populates="finding")

class EntityMentionModel(Base):
    __tablename__ = 'entity_mentions'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    finding_id: Mapped[int] = mapped_column(Integer, ForeignKey("findings.id"))
    finding: Mapped["FindingModel"] = relationship(back_populates="entity_mentions")

class RelationshipEvidenceModel(Base):
    __tablename__ = 'relationship_evidence'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    finding_id: Mapped[int] = mapped_column(Integer, ForeignKey("findings.id"))
    finding: Mapped["FindingModel"] = relationship(back_populates="finding")

if __name__ == "__main__":
    print("Success! All models imported.")