"""
event_router.py
FastAPI router exposing Event / Battle endpoints.

NOTE: Frontend wiring intentionally deferred.
These endpoints are ready and tested but the events UI was removed because
the data has no functional role in the current orchestration pipeline.
Wire this up when one of the following is built:
  - Campaign days themed around specific Kurukshetra battles
  - Context injection: event used as strategic metaphor in task execution
  - Analytics view mapping task types to war-day archetypes
Until then, the backend serves this data but no frontend surface exists.
"""

from typing import List
from fastapi import APIRouter, HTTPException, Query, Path

from app.models.event import Event
from app.db.event_repo import (
    get_all_events,
    get_event_by_id,
    search_events,
    get_events_by_day,
    get_events_count,
)

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("/", response_model=List[Event], summary="List all events / battles")
def list_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """Returns all events ordered by war day then title."""
    return get_all_events(skip=skip, limit=limit)


@router.get("/search", response_model=List[Event], summary="Search events by title")
def search_by_title(
    title: str = Query(..., min_length=1, description="Partial or full event title"),
):
    results = search_events(title)
    return results  # 200 [] for no matches


@router.get("/day/{day}", response_model=List[Event], summary="Get events by Kurukshetra war day")
def events_by_day(day: int = Path(..., ge=1, le=18, description="War day (1–18)")):
    """Returns all events that occurred on the given war day (1–18)."""
    results = get_events_by_day(day)
    if not results:
        raise HTTPException(status_code=404, detail=f"No events recorded for war day {day}")
    return results


@router.get("/count", summary="Total event count")
def event_count():
    return {"count": get_events_count()}


@router.get("/{event_id}", response_model=Event, summary="Get a single event by ID")
def get_event(event_id: str):
    event = get_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail=f"Event '{event_id}' not found")
    return event
