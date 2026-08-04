from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.core.exceptions import ConflictError, NotFoundError, UnprocessableError
from app.database import get_db
from app.schemas.loan import LoanCreate, LoanRead

router = APIRouter(prefix="/loans", tags=["loans"])


@router.get("", response_model=list[LoanRead])
def list_loans(open: bool | None = None, db: Session = Depends(get_db)):
    return crud.loan.list_loans(db, open=open)


@router.post("", response_model=LoanRead, status_code=201)
def create_loan(loan_in: LoanCreate, db: Session = Depends(get_db)):
    try:
        return crud.loan.create_loan(db, loan_in)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except UnprocessableError as exc:
        # Well-formed request, but it fails a business rule (member must be active) —
        # 422 rather than 409, since nothing about the *targeted resource's* state
        # conflicts with the request; the member itself is just ineligible.
        raise HTTPException(status_code=422, detail=str(exc))
    except ConflictError as exc:
        # The copy's current state (already loaned/lost) conflicts with the request.
        raise HTTPException(status_code=409, detail=str(exc))


@router.put("/{loan_id}/return", response_model=LoanRead)
def return_loan(loan_id: int, db: Session = Depends(get_db)):
    try:
        return crud.loan.return_loan(db, loan_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ConflictError as exc:
        # Already-returned loan — its state conflicts with returning it again.
        raise HTTPException(status_code=409, detail=str(exc))
