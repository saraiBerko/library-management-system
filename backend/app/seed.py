"""Populate the database with sample library data for local development.

Run inside the backend container (or any environment with DATABASE_URL
pointing at the target Postgres): `python -m app.seed`. Safe to re-run —
it clears the 5 tables (in FK-safe order) before inserting.
"""
from datetime import date

import sqlalchemy as sa

from app.database import SessionLocal
from app.models import Author, Book, Copy, Loan, Member
from app.models.book import book_authors
from app.models.copy import CopyStatus


def clear(db):
    db.execute(sa.delete(Loan))
    db.execute(sa.delete(Copy))
    db.execute(sa.delete(book_authors))
    db.execute(sa.delete(Book))
    db.execute(sa.delete(Author))
    db.execute(sa.delete(Member))
    db.commit()


def seed_authors_and_books(db):
    authors = {
        name: Author(name=name)
        for name in [
            "Frank Herbert",
            "J.R.R. Tolkien",
            "George R.R. Martin",
            "Isaac Asimov",
            "Agatha Christie",
            "Ursula K. Le Guin",
            "Neil Gaiman",
            "Terry Pratchett",
            "Yuval Noah Harari",
            "Amos Oz",
            "Etgar Keret",
            "David Grossman",
            "Liu Cixin",
        ]
    }
    db.add_all(authors.values())

    # (title, publication_year, genre, [author names]) — index in this list is the
    # "book index" referenced by seed_copies() below.
    book_defs = [
        ("Dune", 1965, "Science Fiction", ["Frank Herbert"]),
        ("The Hobbit", 1937, "Fantasy", ["J.R.R. Tolkien"]),
        ("A Game of Thrones", 1996, "Fantasy", ["George R.R. Martin"]),
        ("Foundation", 1951, "Science Fiction", ["Isaac Asimov"]),
        ("Murder on the Orient Express", 1934, "Mystery", ["Agatha Christie"]),
        ("The Left Hand of Darkness", 1969, "Science Fiction", ["Ursula K. Le Guin"]),
        ("Good Omens", 1990, "Fantasy", ["Neil Gaiman", "Terry Pratchett"]),
        ("Sapiens", 2011, "Non-Fiction", ["Yuval Noah Harari"]),
        ("Hebrew Voices: An Anthology", 2015, "Literature", ["Amos Oz", "Etgar Keret", "David Grossman"]),
        ("The Three-Body Problem", 2008, "Science Fiction", ["Liu Cixin"]),
    ]

    books = []
    for title, year, genre, author_names in book_defs:
        book = Book(title=title, publication_year=year, genre=genre)
        book.authors = [authors[name] for name in author_names]
        books.append(book)
    db.add_all(books)
    db.flush()
    return books


def seed_copies(db, books):
    # (book index, [statuses]) — flattened, insertion order becomes the "copy index"
    # referenced by seed_loans() below.
    copy_plan = [
        (0, [CopyStatus.AVAILABLE, CopyStatus.LOANED, CopyStatus.AVAILABLE]),  # Dune
        (1, [CopyStatus.AVAILABLE, CopyStatus.AVAILABLE]),  # The Hobbit
        (2, [CopyStatus.LOANED, CopyStatus.LOANED, CopyStatus.LOST]),  # A Game of Thrones
        (3, [CopyStatus.AVAILABLE, CopyStatus.LOANED]),  # Foundation
        (4, [CopyStatus.AVAILABLE]),  # Murder on the Orient Express
        (5, [CopyStatus.LOANED, CopyStatus.AVAILABLE]),  # The Left Hand of Darkness
        (6, [CopyStatus.AVAILABLE, CopyStatus.LOST]),  # Good Omens
        (7, [CopyStatus.AVAILABLE, CopyStatus.AVAILABLE]),  # Sapiens
        (8, [CopyStatus.LOANED]),  # Hebrew Voices
        (9, [CopyStatus.AVAILABLE, CopyStatus.LOANED]),  # The Three-Body Problem
    ]

    copies = []
    for book_index, statuses in copy_plan:
        for status in statuses:
            copies.append(Copy(book=books[book_index], status=status))
    db.add_all(copies)
    db.flush()
    return copies


def seed_members(db):
    member_defs = [
        ("Noa Levi", "noa.levi@example.com", date(2023, 3, 14), True),
        ("Yossi Cohen", "yossi.cohen@example.com", date(2022, 11, 2), True),
        ("Maya Ben-David", "maya.bendavid@example.com", date(2024, 1, 20), True),
        ("Avi Mizrahi", "avi.mizrahi@example.com", date(2021, 6, 10), False),
        ("Tamar Shani", "tamar.shani@example.com", date(2023, 9, 5), True),
        ("Ronen Peretz", "ronen.peretz@example.com", date(2024, 5, 18), True),
        ("Dana Avraham", "dana.avraham@example.com", date(2020, 12, 1), False),
        ("Eitan Katz", "eitan.katz@example.com", date(2023, 2, 27), True),
        ("Michal Golan", "michal.golan@example.com", date(2022, 7, 15), True),
        ("Omer Barak", "omer.barak@example.com", date(2024, 3, 9), True),
        ("Shira Adler", "shira.adler@example.com", date(2021, 10, 22), False),
        ("Lior Segal", "lior.segal@example.com", date(2023, 8, 30), True),
        ("Gil Nahum", "gil.nahum@example.com", date(2024, 6, 1), True),
        ("Hila Rosen", "hila.rosen@example.com", date(2022, 4, 17), True),
        ("Amit Sasson", "amit.sasson@example.com", date(2023, 12, 12), True),
    ]
    members = [
        Member(name=name, email=email, join_date=join_date, is_active=is_active)
        for name, email, join_date, is_active in member_defs
    ]
    db.add_all(members)
    db.flush()
    return members


def seed_loans(db, copies, members):
    # Historical, already-returned loans: (copy_index, member_index, loan_date, due_date, returned_date).
    returned = [
        (0, 2, date(2025, 9, 1), date(2025, 9, 22), date(2025, 9, 20)),
        (0, 0, date(2026, 1, 10), date(2026, 1, 31), date(2026, 2, 5)),
        (2, 1, date(2025, 11, 5), date(2025, 11, 26), date(2025, 11, 24)),
        (3, 4, date(2024, 10, 1), date(2024, 10, 22), date(2024, 10, 20)),
        (4, 5, date(2025, 3, 15), date(2025, 4, 5), date(2025, 4, 10)),
        (8, 0, date(2026, 2, 1), date(2026, 2, 22), date(2026, 2, 20)),
        (8, 7, date(2025, 10, 10), date(2025, 10, 31), date(2025, 11, 5)),
        (10, 8, date(2024, 11, 12), date(2024, 12, 3), date(2024, 12, 1)),
        (12, 1, date(2026, 3, 1), date(2026, 3, 22), date(2026, 3, 19)),
        (12, 9, date(2025, 6, 1), date(2025, 6, 22), date(2025, 6, 30)),
        (13, 0, date(2026, 4, 1), date(2026, 4, 22), date(2026, 4, 19)),
        (15, 1, date(2026, 5, 5), date(2026, 5, 26), date(2026, 5, 24)),
        (16, 11, date(2025, 1, 10), date(2025, 1, 31), date(2025, 2, 5)),
        (18, 0, date(2026, 6, 1), date(2026, 6, 22), date(2026, 6, 25)),
        (18, 12, date(2025, 12, 1), date(2025, 12, 22), date(2025, 12, 20)),
        (0, 13, date(2025, 5, 1), date(2025, 5, 22), date(2025, 5, 30)),
        (2, 1, date(2026, 6, 10), date(2026, 7, 1), date(2026, 7, 2)),
        (8, 14, date(2024, 12, 1), date(2024, 12, 22), date(2024, 12, 18)),
        (12, 0, date(2025, 9, 15), date(2025, 10, 6), date(2025, 10, 10)),
        (16, 1, date(2026, 2, 15), date(2026, 3, 8), date(2026, 3, 5)),
        (13, 2, date(2025, 4, 1), date(2025, 4, 22), date(2025, 4, 28)),
        (17, 3, date(2024, 7, 1), date(2024, 7, 22), date(2024, 7, 20)),
    ]

    # Open loans (not yet returned): (copy_index, member_index, loan_date, due_date).
    # One per copy currently "loaned" or "lost" — keeps seed data internally consistent
    # with the copy.status values above, and also satisfies the one-open-loan-per-copy
    # partial unique index.
    open_loans = [
        (1, 0, date(2026, 7, 20), date(2026, 8, 10)),
        (5, 1, date(2026, 7, 1), date(2026, 7, 22)),
        (6, 2, date(2026, 7, 25), date(2026, 8, 8)),
        (9, 5, date(2026, 6, 15), date(2026, 7, 6)),
        (11, 7, date(2026, 7, 28), date(2026, 8, 11)),
        (17, 8, date(2026, 6, 1), date(2026, 6, 22)),
        (19, 9, date(2026, 7, 15), date(2026, 8, 5)),
        (7, 11, date(2025, 11, 1), date(2025, 11, 22)),
        (14, 12, date(2025, 9, 10), date(2025, 10, 1)),
    ]

    loans = [
        Loan(
            copy=copies[copy_index],
            member=members[member_index],
            loan_date=loan_date,
            due_date=due_date,
            returned_date=returned_date,
        )
        for copy_index, member_index, loan_date, due_date, returned_date in returned
    ]
    loans += [
        Loan(
            copy=copies[copy_index],
            member=members[member_index],
            loan_date=loan_date,
            due_date=due_date,
            returned_date=None,
        )
        for copy_index, member_index, loan_date, due_date in open_loans
    ]
    db.add_all(loans)
    return loans


def run():
    db = SessionLocal()
    try:
        clear(db)
        books = seed_authors_and_books(db)
        copies = seed_copies(db, books)
        members = seed_members(db)
        loans = seed_loans(db, copies, members)
        db.commit()
        print(f"Seeded {len(books)} books, {len(copies)} copies, {len(members)} members, {len(loans)} loans.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
