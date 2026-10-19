"""Shared pytest fixtures and test environment setup."""

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

_TMP_DIR = Path(tempfile.mkdtemp(prefix="booking-test-"))
os.environ["DB_PATH"] = str(_TMP_DIR / "test.db")
os.environ.setdefault("ADMIN_TOKEN", "test-token")
os.environ.setdefault("BOOKING_TZ", "Europe/Moscow")
os.environ.setdefault("SLOT_MINUTES", "30")
