import enum

from sqlalchemy import Enum, ForeignKey, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CopyStatus(str, enum.Enum):
    AVAILABLE = "available"
    LOANED = "loaned"
    LOST = "lost"


class Copy(Base):
    __tablename__ = "copies"
    __table_args__ = (Index("ix_copies_book_id_status", "book_id", "status"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="RESTRICT"), nullable=False)
    status: Mapped[CopyStatus] = mapped_column(
        Enum(
            CopyStatus,
            name="copy_status",
            native_enum=False,
            validate_strings=True,
            # Without this, SQLAlchemy persists the Python enum *member name*
            # ("AVAILABLE") instead of its value ("available"), which then violates
            # the migration's CHECK constraint (its values are lowercase).
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=CopyStatus.AVAILABLE,
    )

    book: Mapped["Book"] = relationship("Book", back_populates="copies")  # noqa: F821
    loans: Mapped[list["Loan"]] = relationship("Loan", back_populates="copy")  # noqa: F821
