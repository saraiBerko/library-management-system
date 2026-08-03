class NotFoundError(Exception):
    """Raised when a referenced entity (member/copy/loan) doesn't exist."""


class ConflictError(Exception):
    """Raised when the current state of a resource prevents the requested action."""


class UnprocessableError(Exception):
    """Raised when the request is well-formed but violates a business rule."""
