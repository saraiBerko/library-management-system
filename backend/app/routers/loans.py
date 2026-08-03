from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.core.exceptions import ConflictError, NotFoundError, UnprocessableError
from app.database import get_db
from app.schemas.loan import LoanCreate, LoanRead

router = APIRouter(prefix="/loans", tags=["loans"])


@router.post("", response_model=LoanRead, status_code=201)
def create_loan(loan_in: LoanCreate, db: Session = Depends(get_db)):
    try:
        return crud.loan.create_loan(db, loan_in)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except UnprocessableError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.put("/{loan_id}/return", response_model=LoanRead)
def return_loan(loan_id: int, db: Session = Depends(get_db)):
    try:
        return crud.loan.return_loan(db, loan_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
