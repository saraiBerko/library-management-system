from app.models import Author, Book, Copy
from app.models.copy import CopyStatus


def _make_book(db_session, title, year, genre, author_names, statuses):
    authors = [Author(name=name) for name in author_names]
    db_session.add_all(authors)
    book = Book(title=title, publication_year=year, genre=genre)
    book.authors = authors
    db_session.add(book)
    db_session.flush()
    for status in statuses:
        db_session.add(Copy(book=book, status=status))
    db_session.commit()
    return book


def test_search_by_title(client, db_session):
    _make_book(db_session, "Dune", 1965, "Science Fiction", ["Frank Herbert"], [CopyStatus.AVAILABLE])
    _make_book(db_session, "The Hobbit", 1937, "Fantasy", ["J.R.R. Tolkien"], [CopyStatus.AVAILABLE])

    response = client.get("/books", params={"title": "dune"})
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["title"] == "Dune"
    assert results[0]["available_copies"] == 1
    assert results[0]["authors"][0]["name"] == "Frank Herbert"


def test_search_by_genre(client, db_session):
    _make_book(db_session, "Dune", 1965, "Science Fiction", ["Frank Herbert"], [CopyStatus.AVAILABLE])
    _make_book(db_session, "The Hobbit", 1937, "Fantasy", ["J.R.R. Tolkien"], [CopyStatus.AVAILABLE])

    response = client.get("/books", params={"genre": "fantasy"})
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["title"] == "The Hobbit"


def test_search_by_author(client, db_session):
    _make_book(
        db_session, "Good Omens", 1990, "Fantasy", ["Neil Gaiman", "Terry Pratchett"], [CopyStatus.AVAILABLE]
    )

    response = client.get("/books", params={"author": "pratchett"})
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert len(results[0]["authors"]) == 2


def test_search_by_availability(client, db_session):
    _make_book(db_session, "Dune", 1965, "Science Fiction", ["Frank Herbert"], [CopyStatus.LOANED])
    _make_book(db_session, "The Hobbit", 1937, "Fantasy", ["J.R.R. Tolkien"], [CopyStatus.AVAILABLE])

    response = client.get("/books", params={"available": True})
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["title"] == "The Hobbit"


def test_get_book_detail(client, db_session):
    book = _make_book(
        db_session,
        "Dune",
        1965,
        "Science Fiction",
        ["Frank Herbert"],
        [CopyStatus.AVAILABLE, CopyStatus.LOANED],
    )

    response = client.get(f"/books/{book.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Dune"
    assert len(data["copies"]) == 2
    statuses = {copy["status"] for copy in data["copies"]}
    assert statuses == {"available", "loaned"}


def test_get_missing_book_returns_404(client):
    response = client.get("/books/999")
    assert response.status_code == 404
