from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate


def get_book(db: Session, book_id: int) -> Book | None:
    return db.get(Book, book_id)


def get_books(db: Session, skip: int = 0, limit: int = 100) -> list[Book]:
    return list(db.scalars(select(Book).offset(skip).limit(limit)))


def create_book(db: Session, book_in: BookCreate) -> Book:
    book = Book(**book_in.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def update_book(db: Session, book: Book, book_in: BookUpdate) -> Book:
    for field, value in book_in.model_dump(exclude_unset=True).items():
        setattr(book, field, value)
    db.commit()
    db.refresh(book)
    return book


def delete_book(db: Session, book: Book) -> None:
    db.delete(book)
    db.commit()
