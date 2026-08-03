from datetime import date

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import ConflictError, NotFoundError, UnprocessableError
from app.models.copy import Copy, CopyStatus
from app.models.loan import Loan
from app.models.member import Member
from app.schemas.loan import LoanCreate


def create_loan(db: Session, loan_in: LoanCreate) -> Loan:
    member = db.get(Member, loan_in.member_id)
    if member is None:
        raise NotFoundError("member not found")
    if not member.is_active:
        raise UnprocessableError("member is not active")

    copy = db.get(Copy, loan_in.copy_id)
    if copy is None:
        raise NotFoundError("copy not found")
    if copy.status != CopyStatus.AVAILABLE:
        raise ConflictError("copy is not available")

    loan = Loan(
        member_id=loan_in.member_id,
        copy_id=loan_in.copy_id,
        loan_date=date.today(),
        due_date=loan_in.due_date,
        returned_date=None,
    )
    copy.status = CopyStatus.LOANED
    db.add(loan)
    try:
        # Two requests can both pass the `copy.status == AVAILABLE` check above
        # before either commits (check-then-act race). The real guarantee is the
        # partial unique index on loans(copy_id) WHERE returned_date IS NULL — a
        # concurrent second insert for the same copy fails here with a unique
        # violation, which we surface as a 409 instead of silently double-booking.
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError("copy was just loaned to someone else")

    db.refresh(loan)
    return loan


def return_loan(db: Session, loan_id: int) -> Loan:
    loan = db.get(Loan, loan_id)
    if loan is None:
        raise NotFoundError("loan not found")
    if loan.returned_date is not None:
        raise ConflictError("loan was already returned")

    loan.returned_date = date.today()
    loan.copy.status = CopyStatus.AVAILABLE
    db.commit()
    db.refresh(loan)
    return loan


def get_overdue_loans(db: Session) -> list[Loan]:
    query = (
        select(Loan)
        .where(Loan.returned_date.is_(None), Loan.due_date < date.today())
        .options(selectinload(Loan.copy).selectinload(Copy.book), selectinload(Loan.member))
        .order_by(Loan.due_date)
    )
    return list(db.scalars(query))
