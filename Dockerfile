# syntax=docker/dockerfile:1

# ---------------------------------------------------------------------------
# Call-booking service image.
#
# Builds the Vite SPA and serves it together with the FastAPI backend from a
# single uvicorn process. The app listens on $PORT (default 8000).
#
#   docker build -t calendar-slot-code:local .
#   docker run --rm -e PORT=8000 -p 8000:8000 calendar-slot-code:local
# ---------------------------------------------------------------------------

# --- Stage 1: build the frontend (Vite -> frontend/dist) --------------------
FROM node:22-slim AS frontend

WORKDIR /build/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# --- Stage 2: runtime (FastAPI + built SPA) ---------------------------------
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    BOOKING_TZ=Europe/Moscow \
    AVAILABILITY_DAYS=14 \
    DB_PATH=/data/bookings.db \
    PORT=8000

WORKDIR /app

COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt \
    && mkdir -p /data

COPY backend/ ./backend/
COPY --from=frontend /build/frontend/dist ./frontend/dist

EXPOSE 8000

# Serve API + SPA on all interfaces; honour the PORT environment variable.
CMD ["sh", "-c", "exec uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port \"${PORT:-8000}\""]
