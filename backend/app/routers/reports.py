from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas.loan import LoanRead

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/overdue", response_model=list[LoanRead])
def get_overdue_loans(db: Session = Depends(get_db)):
    return crud.loan.get_overdue_loans(db)
