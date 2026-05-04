from pydantic import BaseModel
from typing import Optional
from enum import Enum


class CharacterRole(str, Enum):
    warrior = "Warrior"
    sage = "Sage"
    statesman = "Statesman"
    king = "King"
    queen = "Queen"
    avatar = "Avatar / Divine"
    demon = "Demon / Asura"
    other = "Other"


class CharacterBase(BaseModel):
    name: str
    role: Optional[CharacterRole] = CharacterRole.other
    side: Optional[str] = None          # e.g. "Pandava", "Kaurava", "Neutral"
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    weapon: Optional[str] = None        # e.g. "Gandiva (bow)"
    lineage: Optional[str] = None       # e.g. "Son of Kunti and Indra"


class CharacterCreate(CharacterBase):
    pass


class Character(CharacterBase):
    id: str

    model_config = {"from_attributes": True}
