from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas.loan import LoanRead

router = APIRouter(prefix="/members", tags=["members"])


@router.get("/{member_id}/loans", response_model=list[LoanRead])
def get_member_loans(member_id: int, db: Session = Depends(get_db)):
    member = crud.member.get_member(db, member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return crud.member.get_member_loans(db, member_id)
