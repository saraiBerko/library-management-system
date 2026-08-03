"""initial schema: authors, books, book_authors, copies, members, loans

Revision ID: 0001
Revises:
Create Date: 2026-08-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "authors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
    )
    op.create_index("ix_authors_name", "authors", ["name"])

    op.create_table(
        "books",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("publication_year", sa.Integer(), nullable=False),
        sa.Column("genre", sa.String(length=100), nullable=False),
    )
    op.create_index("ix_books_title", "books", ["title"])
    op.create_index("ix_books_genre", "books", ["genre"])

    op.create_table(
        "book_authors",
        sa.Column("book_id", sa.Integer(), sa.ForeignKey("books.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("author_id", sa.Integer(), sa.ForeignKey("authors.id", ondelete="CASCADE"), primary_key=True),
    )
    op.create_index("ix_book_authors_author_id", "book_authors", ["author_id"])

    op.create_table(
        "copies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("book_id", sa.Integer(), sa.ForeignKey("books.id", ondelete="RESTRICT"), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="available",
        ),
        sa.CheckConstraint(
            "status IN ('available', 'loaned', 'lost')",
            name="ck_copies_status_valid",
        ),
    )
    op.create_index("ix_copies_book_id_status", "copies", ["book_id", "status"])

    op.create_table(
        "members",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("join_date", sa.Date(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_members_email", "members", ["email"], unique=True)

    op.create_table(
        "loans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("member_id", sa.Integer(), sa.ForeignKey("members.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("copy_id", sa.Integer(), sa.ForeignKey("copies.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("loan_date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("returned_date", sa.Date(), nullable=True),
        sa.CheckConstraint(
            "returned_date IS NULL OR returned_date >= loan_date",
            name="ck_loans_returned_after_loan",
        ),
    )
    op.create_index("ix_loans_member_id", "loans", ["member_id"])
    op.create_index("ix_loans_loan_date", "loans", ["loan_date"])
    op.create_index(
        "ix_loans_one_open_per_copy",
        "loans",
        ["copy_id"],
        unique=True,
        postgresql_where=sa.text("returned_date IS NULL"),
    )
    op.create_index(
        "ix_loans_open_due_date",
        "loans",
        ["due_date"],
        postgresql_where=sa.text("returned_date IS NULL"),
    )


def downgrade() -> None:
    op.drop_table("loans")
    op.drop_table("members")
    op.drop_table("copies")
    op.drop_table("book_authors")
    op.drop_table("books")
    op.drop_table("authors")
