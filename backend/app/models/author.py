from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.book import book_authors


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    books: Mapped[list["Book"]] = relationship(  # noqa: F821
        "Book", secondary=book_authors, back_populates="authors"
    )
