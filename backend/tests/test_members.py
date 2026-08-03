from datetime import date, timedelta

from app.models import Book, Copy, Member
from app.models.copy import CopyStatus
from app.models.loan import Loan


def test_member_loan_history_includes_open_and_returned(client, db_session):
    member = Member(name="Test Member", email="member@example.com", join_date=date(2023, 1, 1), is_active=True)
    book = Book(title="Test Book", publication_year=2000, genre="Fiction")
    db_session.add_all([member, book])
    db_session.flush()

    copy1 = Copy(book=book, status=CopyStatus.AVAILABLE)
    copy2 = Copy(book=book, status=CopyStatus.LOANED)
    db_session.add_all([copy1, copy2])
    db_session.flush()

    db_session.add_all(
        [
            Loan(
                member=member,
                copy=copy1,
                loan_date=date(2025, 1, 1),
                due_date=date(2025, 1, 22),
                returned_date=date(2025, 1, 20),
            ),
            Loan(
                member=member,
                copy=copy2,
                loan_date=date.today() - timedelta(days=5),
                due_date=date.today() + timedelta(days=9),
                returned_date=None,
            ),
        ]
    )
    db_session.commit()

    response = client.get(f"/members/{member.id}/loans")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 2
    returned_flags = {loan["returned_date"] is None for loan in results}
    assert returned_flags == {True, False}


def test_member_loans_missing_member_returns_404(client):
    response = client.get("/members/999/loans")
    assert response.status_code == 404
