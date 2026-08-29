#!/usr/bin/env python3

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class FindingModel(Base):
    __tablename__ = 'findings'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

class RelationshipEvidenceModel(Base):
    __tablename__ = 'relationship_evidence'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    finding_id: Mapped[int] = mapped_column(ForeignKey("findings.id"))
    finding: Mapped["FindingModel"] = relationship()

if __name__ == "__main__":
    print("Success! Simple model imported.")