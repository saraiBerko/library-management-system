from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas.book import BookDetail, BookSearchResult

router = APIRouter(prefix="/books", tags=["books"])


@router.get("", response_model=list[BookSearchResult])
def search_books(
    title: str | None = None,
    genre: str | None = None,
    author: str | None = None,
    available: bool | None = None,
    db: Session = Depends(get_db),
):
    results = crud.book.search_books(db, title=title, genre=genre, author=author, available=available)
    return [
        BookSearchResult(
            id=book.id,
            title=book.title,
            publication_year=book.publication_year,
            genre=book.genre,
            authors=book.authors,
            available_copies=available_copies,
        )
        for book, available_copies in results
    ]


@router.get("/{book_id}", response_model=BookDetail)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = crud.book.get_book(db, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book
