from datetime import date

from pydantic import BaseModel, ConfigDict


class MemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    join_date: date
    is_active: bool
