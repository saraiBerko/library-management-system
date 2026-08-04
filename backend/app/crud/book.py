from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.author import Author
from app.models.book import Book
from app.models.copy import Copy, CopyStatus


def _count_available(book: Book) -> int:
    return sum(1 for copy in book.copies if copy.status == CopyStatus.AVAILABLE)


def search_books(
    db: Session,
    q: str | None = None,
    genre: str | None = None,
    available: bool | None = None,
) -> list[tuple[Book, int]]:
    query = select(Book).options(selectinload(Book.authors), selectinload(Book.copies))

    if q:
        # Single free-text field matches title OR author name (see Part ג plan) —
        # separate ANDed title/author params couldn't express "either field".
        query = query.where(
            Book.title.ilike(f"%{q}%") | Book.authors.any(Author.name.ilike(f"%{q}%"))
        )
    if genre:
        query = query.where(func.lower(Book.genre) == genre.lower())
    if available is not None:
        has_available_copy = Book.copies.any(Copy.status == CopyStatus.AVAILABLE)
        query = query.where(has_available_copy if available else ~has_available_copy)

    books = list(db.scalars(query.order_by(Book.title)))
    return [(book, _count_available(book)) for book in books]


def get_book(db: Session, book_id: int) -> Book | None:
    query = (
        select(Book)
        .options(selectinload(Book.authors), selectinload(Book.copies))
        .where(Book.id == book_id)
    )
    return db.scalars(query).first()
