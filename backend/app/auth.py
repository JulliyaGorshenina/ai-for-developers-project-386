"""Admin authentication dependency."""

from fastapi import Header, HTTPException, status

from . import config


def require_admin(x_admin_token: str | None = Header(default=None)) -> None:
    """Reject requests without a valid ``X-Admin-Token`` header."""
    if not x_admin_token or x_admin_token != config.ADMIN_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing admin token",
        )
