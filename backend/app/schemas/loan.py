from datetime import date

from pydantic import BaseModel, ConfigDict, field_validator

from app.schemas.member import MemberRead


class LoanCreate(BaseModel):
    member_id: int
    copy_id: int
    due_date: date

    @field_validator("due_date")
    @classmethod
    def due_date_not_in_past(cls, value: date) -> date:
        if value < date.today():
            raise ValueError("due_date cannot be in the past")
        return value


class LoanBookSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str


class LoanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    copy_id: int
    book: LoanBookSummary
    member: MemberRead
    loan_date: date
    due_date: date
    returned_date: date | None
