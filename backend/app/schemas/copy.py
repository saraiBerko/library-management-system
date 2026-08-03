from pydantic import BaseModel, ConfigDict

from app.models.copy import CopyStatus


class CopyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: CopyStatus
