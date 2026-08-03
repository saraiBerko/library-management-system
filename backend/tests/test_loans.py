from datetime import date, timedelta

from app.models import Book, Copy, Member
from app.models.copy import CopyStatus
from app.models.loan import Loan

_member_counter = 0


def _make_member(db_session, is_active=True):
    global _member_counter
    _member_counter += 1
    member = Member(
        name="Test Member",
        email=f"member{_member_counter}@example.com",
        join_date=date(2023, 1, 1),
        is_active=is_active,
    )
    db_session.add(member)
    db_session.commit()
    return member


def _make_copy(db_session, status=CopyStatus.AVAILABLE):
    book = Book(title="Test Book", publication_year=2000, genre="Fiction")
    db_session.add(book)
    db_session.flush()
    copy = Copy(book=book, status=status)
    db_session.add(copy)
    db_session.commit()
    return copy


def test_create_and_return_loan_happy_path(client, db_session):
    member = _make_member(db_session)
    copy = _make_copy(db_session, CopyStatus.AVAILABLE)
    due_date = (date.today() + timedelta(days=14)).isoformat()

    response = client.post("/loans", json={"member_id": member.id, "copy_id": copy.id, "due_date": due_date})
    assert response.status_code == 201
    loan = response.json()
    assert loan["returned_date"] is None

    db_session.refresh(copy)
    assert copy.status == CopyStatus.LOANED

    response = client.put(f"/loans/{loan['id']}/return")
    assert response.status_code == 200
    assert response.json()["returned_date"] is not None

    db_session.refresh(copy)
    assert copy.status == CopyStatus.AVAILABLE


def test_loan_copy_not_available_returns_409(client, db_session):
    member = _make_member(db_session)
    copy = _make_copy(db_session, CopyStatus.LOANED)
    due_date = (date.today() + timedelta(days=14)).isoformat()

    response = client.post("/loans", json={"member_id": member.id, "copy_id": copy.id, "due_date": due_date})
    assert response.status_code == 409


def test_loan_inactive_member_returns_422(client, db_session):
    member = _make_member(db_session, is_active=False)
    copy = _make_copy(db_session, CopyStatus.AVAILABLE)
    due_date = (date.today() + timedelta(days=14)).isoformat()

    response = client.post("/loans", json={"member_id": member.id, "copy_id": copy.id, "due_date": due_date})
    assert response.status_code == 422


def test_loan_missing_member_returns_404(client, db_session):
    copy = _make_copy(db_session, CopyStatus.AVAILABLE)
    due_date = (date.today() + timedelta(days=14)).isoformat()

    response = client.post("/loans", json={"member_id": 999, "copy_id": copy.id, "due_date": due_date})
    assert response.status_code == 404


def test_loan_missing_copy_returns_404(client, db_session):
    member = _make_member(db_session)
    due_date = (date.today() + timedelta(days=14)).isoformat()

    response = client.post("/loans", json={"member_id": member.id, "copy_id": 999, "due_date": due_date})
    assert response.status_code == 404


def test_return_already_returned_loan_returns_409(client, db_session):
    member = _make_member(db_session)
    copy = _make_copy(db_session, CopyStatus.AVAILABLE)
    due_date = (date.today() + timedelta(days=14)).isoformat()

    loan_id = client.post(
        "/loans", json={"member_id": member.id, "copy_id": copy.id, "due_date": due_date}
    ).json()["id"]
    client.put(f"/loans/{loan_id}/return")

    response = client.put(f"/loans/{loan_id}/return")
    assert response.status_code == 409


def test_return_missing_loan_returns_404(client):
    response = client.put("/loans/999/return")
    assert response.status_code == 404


def test_due_date_in_past_returns_422(client, db_session):
    member = _make_member(db_session)
    copy = _make_copy(db_session, CopyStatus.AVAILABLE)
    past_date = (date.today() - timedelta(days=1)).isoformat()

    response = client.post("/loans", json={"member_id": member.id, "copy_id": copy.id, "due_date": past_date})
    assert response.status_code == 422


def test_overdue_report_includes_only_overdue_open_loans(client, db_session):
    member = _make_member(db_session)
    overdue_copy = _make_copy(db_session, CopyStatus.AVAILABLE)
    ontime_copy = _make_copy(db_session, CopyStatus.AVAILABLE)

    # Inserted directly (not via POST /loans) since the create endpoint's
    # validator rejects a due_date that's already in the past.
    overdue_copy.status = CopyStatus.LOANED
    db_session.add(
        Loan(
            member=member,
            copy=overdue_copy,
            loan_date=date.today() - timedelta(days=30),
            due_date=date.today() - timedelta(days=10),
            returned_date=None,
        )
    )
    db_session.commit()

    due_date = (date.today() + timedelta(days=14)).isoformat()
    client.post("/loans", json={"member_id": member.id, "copy_id": ontime_copy.id, "due_date": due_date})

    response = client.get("/reports/overdue")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["copy_id"] == overdue_copy.id
