"""Meeting-type management endpoints."""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from .. import db
from ..generated.models import EventType, EventTypeCreate
from ..repository import get_event_type, load_event_types

router = APIRouter(prefix="/api", tags=["event-types"])


@router.get("/event-types", response_model=list[EventType])
def list_event_types(conn: sqlite3.Connection = Depends(db.get_db)) -> list[EventType]:
    """List every published meeting type."""
    return load_event_types(conn)


@router.post("/event-types", response_model=EventType, status_code=201)
def create_event_type(
    payload: EventTypeCreate,
    conn: sqlite3.Connection = Depends(db.get_db),
) -> EventType:
    """Publish a new meeting type."""
    if get_event_type(conn, payload.id) is not None:
        raise HTTPException(status_code=409, detail="Event type already exists")
    conn.execute(
        "INSERT INTO event_types (id, name, description, duration_minutes) VALUES (?, ?, ?, ?)",
        (payload.id, payload.name, payload.description, payload.duration_minutes),
    )
    conn.commit()
    created = get_event_type(conn, payload.id)
    assert created is not None
    return created


@router.put("/event-types/{id}", response_model=EventType)
def update_event_type(
    id: str,
    payload: EventTypeCreate,
    conn: sqlite3.Connection = Depends(db.get_db),
) -> EventType:
    """Replace an existing meeting type."""
    if get_event_type(conn, id) is None:
        raise HTTPException(status_code=404, detail="Event type not found")
    conn.execute(
        "UPDATE event_types SET name = ?, description = ?, duration_minutes = ? WHERE id = ?",
        (payload.name, payload.description, payload.duration_minutes, id),
    )
    conn.commit()
    updated = get_event_type(conn, id)
    assert updated is not None
    return updated


@router.delete("/event-types/{id}", status_code=204)
def delete_event_type(id: str, conn: sqlite3.Connection = Depends(db.get_db)) -> None:
    """Remove a meeting type."""
    if get_event_type(conn, id) is None:
        raise HTTPException(status_code=404, detail="Event type not found")
    conn.execute("DELETE FROM event_types WHERE id = ?", (id,))
    conn.commit()
