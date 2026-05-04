from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class EventType(str, Enum):
    battle = "Battle"
    council = "Council"
    ceremony = "Ceremony"
    exile = "Exile"
    revelation = "Revelation"
    other = "Other"


class EventBase(BaseModel):
    title: str
    event_type: Optional[EventType] = EventType.other
    day: Optional[int] = None               # Kurukshetra war day (1–18), None if pre-war
    location: Optional[str] = None
    summary: Optional[str] = None
    sides_involved: Optional[str] = None    # e.g. "Pandava vs Kaurava"
    outcome: Optional[str] = None
    key_character_names: Optional[str] = None  # comma-separated names


class EventCreate(EventBase):
    pass


class Event(EventBase):
    id: str

    model_config = {"from_attributes": True}
