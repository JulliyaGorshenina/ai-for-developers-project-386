"""Application configuration, sourced from environment variables."""

import os
from pathlib import Path

BOOKING_TZ: str = os.getenv("BOOKING_TZ", "Europe/Moscow")
DEFAULT_AVAILABILITY_DAYS: int = int(os.getenv("AVAILABILITY_DAYS", "14"))

BACKEND_DIR: Path = Path(__file__).resolve().parent.parent
DB_PATH: Path = Path(os.getenv("DB_PATH", str(BACKEND_DIR / "bookings.db")))
FRONTEND_DIST: Path = BACKEND_DIR.parent / "frontend" / "dist"
