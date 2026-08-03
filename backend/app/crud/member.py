from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.copy import Copy
from app.models.loan import Loan
from app.models.member import Member


def get_member(db: Session, member_id: int) -> Member | None:
    return db.get(Member, member_id)


def get_member_loans(db: Session, member_id: int) -> list[Loan]:
    query = (
        select(Loan)
        .where(Loan.member_id == member_id)
        .options(selectinload(Loan.copy).selectinload(Copy.book), selectinload(Loan.member))
        .order_by(Loan.loan_date.desc())
    )
    return list(db.scalars(query))
