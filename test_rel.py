#!/usr/bin/env python3

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class A(Base):
    __tablename__ = 'a'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # This should work
    b_list: Mapped[list["B"]] = relationship(back_populates="a")
    # Another relationship to test
    c_list: Mapped[list["C"]] = relationship(back_populates="a")

class B(Base):
    __tablename__ = 'b'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    a_id: Mapped[int] = mapped_column(Integer, ForeignKey("a.id"))
    # This is the pattern we're trying to replicate
    a: Mapped["A"] = relationship(back_populates="b_list")

class C(Base):
    __tablename__ = 'c'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    a_id: Mapped[int] = mapped_column(Integer, ForeignKey("a.id"))
    # This is the pattern we're trying to replicate for relationship_evidence
    a: Mapped["A"] = relationship(back_populates="c_list")

if __name__ == "__main__":
    print("Success!")