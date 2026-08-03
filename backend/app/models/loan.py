from datetime import date

from sqlalchemy import CheckConstraint, Date, ForeignKey, Index, Integer, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

_open_loan_clause = text("returned_date IS NULL")


class Loan(Base):
    __tablename__ = "loans"
    __table_args__ = (
        CheckConstraint(
            "returned_date IS NULL OR returned_date >= loan_date",
            name="ck_loans_returned_after_loan",
        ),
        Index("ix_loans_member_id", "member_id"),
        Index("ix_loans_loan_date", "loan_date"),
        Index("ix_loans_one_open_per_copy", "copy_id", unique=True, postgresql_where=_open_loan_clause),
        Index("ix_loans_open_due_date", "due_date", postgresql_where=_open_loan_clause),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id", ondelete="RESTRICT"), nullable=False)
    copy_id: Mapped[int] = mapped_column(ForeignKey("copies.id", ondelete="RESTRICT"), nullable=False)
    loan_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    returned_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    member: Mapped["Member"] = relationship("Member", back_populates="loans")  # noqa: F821
    copy: Mapped["Copy"] = relationship("Copy", back_populates="loans")  # noqa: F821

    @property
    def book(self):
        """Convenience accessor so LoanRead (schemas/loan.py) can read `.book`
        directly via from_attributes, instead of every call site reaching
        through `.copy.book`."""
        return self.copy.book
