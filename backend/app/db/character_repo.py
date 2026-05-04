"""
character_repo.py
Thin SQLite data‑access layer for the 'characters' table.
"""

import sqlite3
import uuid
from typing import List, Optional
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "mahabharata.db"

# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS characters (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    role        TEXT,
    side        TEXT,
    description TEXT,
    avatar_url  TEXT,
    weapon      TEXT,
    lineage     TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_characters_name ON characters(name);
"""

# ---------------------------------------------------------------------------
# Seed data (sample Mahabharata characters)
# ---------------------------------------------------------------------------

SEED_CHARACTERS = [
    {
        "id": str(uuid.uuid4()),
        "name": "Arjuna",
        "role": "Warrior",
        "side": "Pandava",
        "description": (
            "Third of the Pandava brothers, peerless archer and devoted student of "
            "Dronacharya. Recipient of the Bhagavad Gita teachings from Krishna on "
            "the battlefield of Kurukshetra."
        ),
        "avatar_url": "",
        "weapon": "Gandiva (bow) + Pashupatastra",
        "lineage": "Son of Kunti and Indra (divine father)",
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Krishna",
        "role": "Avatar / Divine",
        "side": "Pandava",
        "description": (
            "Eighth avatar of Vishnu, charioteer and divine guide of Arjuna. "
            "King of Dwarka, master strategist, and embodiment of dharma."
        ),
        "avatar_url": "",
        "weapon": "Sudarshana Chakra (discus)",
        "lineage": "Son of Vasudeva and Devaki, raised by Nanda and Yashoda",
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Draupadi",
        "role": "Queen",
        "side": "Pandava",
        "description": (
            "Born from the sacred fire of King Drupada's yajna, wife of all five "
            "Pandava brothers, and a central figure whose humiliation in the Kuru "
            "court ignites the Kurukshetra War."
        ),
        "avatar_url": "",
        "weapon": None,
        "lineage": "Daughter of King Drupada of Panchala",
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Yudhisthira",
        "role": "King",
        "side": "Pandava",
        "description": (
            "Eldest Pandava, son of Dharma (Yama), known for his unwavering "
            "commitment to truth and righteousness. Becomes Emperor of Hastinapura "
            "after the Kurukshetra War."
        ),
        "avatar_url": "",
        "weapon": "Spear",
        "lineage": "Son of Kunti and Yama, the god of righteousness",
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Karna",
        "role": "Warrior",
        "side": "Kaurava",
        "description": (
            "Greatest tragic hero of the Mahabharata. Born of Kunti and the Sun god "
            "Surya, raised as a charioteer's son. Loyal friend of Duryodhana, "
            "rival of Arjuna, and warrior of unmatched generosity."
        ),
        "avatar_url": "",
        "weapon": "Vijaya (bow) + Vasavi Shakti",
        "lineage": "Son of Kunti and Surya (Sun god), raised by Adhiratha",
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Duryodhana",
        "role": "King",
        "side": "Kaurava",
        "description": (
            "Eldest of the 100 Kaurava brothers, crown prince of Hastinapura. "
            "His jealousy of the Pandavas and refusal to share the kingdom leads "
            "to the catastrophic Kurukshetra War."
        ),
        "avatar_url": "",
        "weapon": "Mace (gadā)",
        "lineage": "Son of blind King Dhritarashtra and Gandhari",
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Bhishma",
        "role": "Warrior",
        "side": "Kaurava",
        "description": (
            "Born Devavrata, grandson of King Shantanu. Took the terrible vow of "
            "lifelong celibacy (Bhishma Pratigya) and commanded the Kaurava army "
            "for the first 10 days of Kurukshetra. Possessed the boon to choose "
            "the time of his own death."
        ),
        "avatar_url": "",
        "weapon": "Bow + Brahmastra",
        "lineage": "Son of King Shantanu and the goddess Ganga",
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Drona",
        "role": "Sage",
        "side": "Kaurava",
        "description": (
            "Supreme preceptor of both Pandavas and Kauravas in the military arts. "
            "Commander of the Kaurava army after Bhishma's fall. Creator of the "
            "Chakravyuha formation that killed young Abhimanyu."
        ),
        "avatar_url": "",
        "weapon": "Brahmastra",
        "lineage": "Son of sage Bharadvaja, father of Ashwatthama",
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Vidura",
        "role": "Statesman",
        "side": "Kaurava",
        "description": (
            "Half-brother of Dhritarashtra and Pandu, renowned for his wisdom and "
            "ethical counsel. Advisor to the Kuru court, known as the embodiment of "
            "dharma and strategic integrity."
        ),
        "avatar_url": "",
        "weapon": None,
        "lineage": "Son of Vyasa and a maidservant of Ambika",
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Sahadeva",
        "role": "Warrior",
        "side": "Pandava",
        "description": (
            "Youngest of the five Pandava brothers, son of Madri and the Ashvins. "
            "Renowned for his mastery of astrology and intelligence, often credited "
            "as the most knowledgeable of the Pandavas."
        ),
        "avatar_url": "",
        "weapon": "Sword",
        "lineage": "Son of Madri and the Ashvins (divine twin physicians)",
    },
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the characters table and seed / migrate it."""
    with _get_conn() as conn:
        conn.executescript(_CREATE_TABLE)

        # Normalize legacy names so DB matches the backend character_risk_params keys.
        conn.execute("UPDATE characters SET name = 'Drona' WHERE name = 'Dronacharya'")
        conn.execute("UPDATE characters SET name = 'Yudhisthira' WHERE name = 'Yudhishthira'")

        # Fresh seed if completely empty, otherwise upsert only missing characters.
        count = conn.execute("SELECT COUNT(*) FROM characters").fetchone()[0]
        if count == 0:
            conn.executemany(
                """
                INSERT INTO characters
                    (id, name, role, side, description, avatar_url, weapon, lineage)
                VALUES
                    (:id, :name, :role, :side, :description, :avatar_url, :weapon, :lineage)
                """,
                SEED_CHARACTERS,
            )
        else:
            for char in SEED_CHARACTERS:
                conn.execute(
                    """
                    INSERT INTO characters
                        (id, name, role, side, description, avatar_url, weapon, lineage)
                    SELECT :id, :name, :role, :side, :description, :avatar_url, :weapon, :lineage
                    WHERE NOT EXISTS (SELECT 1 FROM characters WHERE name = :name)
                    """,
                    char,
                )
        conn.commit()


# ---------------------------------------------------------------------------
# Query functions
# ---------------------------------------------------------------------------

def get_all_characters(skip: int = 0, limit: int = 50) -> List[dict]:
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM characters ORDER BY name LIMIT ? OFFSET ?",
            (limit, skip),
        ).fetchall()
    return [dict(r) for r in rows]


def get_character_by_id(character_id: str) -> Optional[dict]:
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM characters WHERE id = ?", (character_id,)
        ).fetchone()
    return dict(row) if row else None


def search_characters(name: str) -> List[dict]:
    pattern = f"%{name}%"
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM characters WHERE name LIKE ? ORDER BY name",
            (pattern,),
        ).fetchall()
    return [dict(r) for r in rows]


def get_characters_count() -> int:
    with _get_conn() as conn:
        return conn.execute("SELECT COUNT(*) FROM characters").fetchone()[0]
