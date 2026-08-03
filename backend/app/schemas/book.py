from pydantic import BaseModel, ConfigDict

from app.schemas.author import AuthorRead
from app.schemas.copy import CopyRead


class BookSearchResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    publication_year: int
    genre: str
    authors: list[AuthorRead]
    available_copies: int


class BookDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    publication_year: int
    genre: str
    authors: list[AuthorRead]
    copies: list[CopyRead]
