"""Pydantic schemas shared by the API routers."""

import re

from pydantic import BaseModel, Field, field_validator

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
HHMM_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


class Slot(BaseModel):
    start: str
    end: str


class DaySlots(BaseModel):
    date: str
    weekday: int
    slots: list[Slot]


class BookingCreate(BaseModel):
    slot_start: str
    name: str = Field(min_length=1, max_length=200)
    email: str = Field(min_length=3, max_length=200)
    comment: str = Field(default="", max_length=1000)

    @field_validator("name", "comment")
    @classmethod
    def _strip(cls, value: str) -> str:
        return value.strip()

    @field_validator("email")
    @classmethod
    def _valid_email(cls, value: str) -> str:
        value = value.strip()
        if not EMAIL_RE.match(value):
            raise ValueError("invalid email address")
        return value


class Booking(BaseModel):
    id: int
    slot_start: str
    slot_end: str
    name: str
    email: str
    comment: str
    status: str
    created_at: str


class Window(BaseModel):
    weekday: int = Field(ge=0, le=6)
    start_time: str
    end_time: str

    @field_validator("start_time", "end_time")
    @classmethod
    def _valid_time(cls, value: str) -> str:
        if not HHMM_RE.match(value):
            raise ValueError("time must be HH:MM")
        return value


class ScheduleUpdate(BaseModel):
    windows: list[Window]
