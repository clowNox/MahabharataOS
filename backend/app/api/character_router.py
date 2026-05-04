"""
character_router.py
FastAPI router exposing Character endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from app.models.character import Character
from app.db.character_repo import (
    get_all_characters,
    get_character_by_id,
    search_characters,
    get_characters_count,
)

router = APIRouter(prefix="/characters", tags=["Characters"])


@router.get("/", response_model=List[Character], summary="List all characters")
def list_characters(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Max records to return"),
):
    """
    Returns a paginated list of Mahabharata characters ordered by name.
    """
    return get_all_characters(skip=skip, limit=limit)


@router.get("/search", response_model=List[Character], summary="Search characters by name")
def search_by_name(
    name: str = Query(..., min_length=1, description="Partial or full character name"),
):
    """
    Returns all characters whose name contains the provided string (case-insensitive).
    """
    results = search_characters(name)
    return results  # Return 200 [] when no match — 404 is for unknown resources, not empty sets


@router.get("/count", summary="Total character count")
def character_count():
    """Returns the total number of characters in the database."""
    return {"count": get_characters_count()}


@router.get("/{character_id}", response_model=Character, summary="Get a character by ID")
def get_character(character_id: str):
    """
    Returns the full details of a single character by their UUID.
    """
    character = get_character_by_id(character_id)
    if not character:
        raise HTTPException(status_code=404, detail=f"Character '{character_id}' not found")
    return character
