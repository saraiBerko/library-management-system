from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas.book import BookCreate, BookRead, BookUpdate

router = APIRouter(prefix="/books", tags=["books"])


@router.get("", response_model=list[BookRead])
def list_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.book.get_books(db, skip=skip, limit=limit)


@router.post("", response_model=BookRead, status_code=201)
def create_book(book_in: BookCreate, db: Session = Depends(get_db)):
    return crud.book.create_book(db, book_in)


@router.get("/{book_id}", response_model=BookRead)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = crud.book.get_book(db, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.put("/{book_id}", response_model=BookRead)
def update_book(book_id: int, book_in: BookUpdate, db: Session = Depends(get_db)):
    book = crud.book.get_book(db, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return crud.book.update_book(db, book, book_in)


@router.delete("/{book_id}", status_code=204)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = crud.book.get_book(db, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    crud.book.delete_book(db, book)
