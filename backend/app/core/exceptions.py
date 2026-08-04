# Raised only from crud/loan.py, where a single function (create_loan/return_loan)
# can fail in several distinct ways that each need a different HTTP status (see the
# except chain in routers/loans.py). Everywhere else, a lookup only has one failure
# mode (not found), so routers just do an inline
# `if x is None: raise HTTPException(404, ...)` instead of raising one of these.


class NotFoundError(Exception):
    """Raised when a referenced entity (member/copy/loan) doesn't exist."""


class ConflictError(Exception):
    """Raised when the current state of a resource prevents the requested action."""


class UnprocessableError(Exception):
    """Raised when the request is well-formed but violates a business rule."""
