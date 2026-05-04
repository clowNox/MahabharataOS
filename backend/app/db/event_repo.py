"""
event_repo.py
SQLite data-access layer for the 'events' table.
"""

import sqlite3
import uuid
from typing import List, Optional
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "mahabharata.db"

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS events (
    id                  TEXT PRIMARY KEY,
    title               TEXT NOT NULL,
    event_type          TEXT,
    day                 INTEGER,
    location            TEXT,
    sides_involved      TEXT,
    outcome             TEXT,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS event_characters (
    event_id            TEXT,
    character_id        TEXT,
    PRIMARY KEY(event_id, character_id),
    FOREIGN KEY(event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY(character_id) REFERENCES characters(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_events_day ON events(day);
CREATE INDEX IF NOT EXISTS idx_events_title ON events(title);
"""

SEED_EVENTS = [
    {
        "id": str(uuid.uuid4()),
        "title": "The Dice Game",
        "event_type": "Council",
        "day": None,
        "location": "Hastinapura — Assembly Hall",
        "summary": (
            "Yudhishthira, enticed by Shakuni's loaded dice, gambles away the Pandava "
            "kingdom, wealth, brothers, himself, and finally Draupadi. Draupadi's public "
            "humiliation by Dushasana and Karna ignites the vow of revenge that will "
            "culminate in the Kurukshetra War."
        ),
        "sides_involved": "Pandava vs Kaurava",
        "outcome": "Pandavas lose everything; sentenced to 12 years forest exile + 1 year incognito",
        "key_character_names": "Yudhishthira, Shakuni, Draupadi, Duryodhana, Dushasana",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Bhishma Falls — Day 10 of Kurukshetra",
        "event_type": "Battle",
        "day": 10,
        "location": "Kurukshetra Battlefield",
        "summary": (
            "Arjuna, guided by Krishna and using Shikhandi as a shield (Bhishma had "
            "vowed never to fight a woman or one born female), unleashes a volley of "
            "arrows that brings the great patriarch down. Bhishma falls on a bed of "
            "arrows but, possessing the boon of iccha-mrityu, waits for the auspicious "
            "Uttarayana to depart."
        ),
        "sides_involved": "Pandava vs Kaurava",
        "outcome": "Bhishma incapacitated; Drona appointed new Kaurava commander",
        "key_character_names": "Arjuna, Bhishma, Shikhandi, Krishna",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Death of Abhimanyu — Day 13",
        "event_type": "Battle",
        "day": 13,
        "location": "Kurukshetra Battlefield",
        "summary": (
            "Drona forms the deadly Chakravyuha (spinning discus formation). Only "
            "Arjuna and Krishna know how to break it; Abhimanyu knows how to enter but "
            "not exit. Trapped inside, the sixteen-year-old hero is overwhelmed and "
            "killed by multiple Kaurava warriors simultaneously — a violation of the "
            "rules of war that enrages Arjuna."
        ),
        "sides_involved": "Pandava vs Kaurava",
        "outcome": "Abhimanyu killed; Arjuna vows to kill Jayadratha by sunset next day",
        "key_character_names": "Abhimanyu, Dronacharya, Karna, Jayadratha",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Karna vs Arjuna — Final Duel, Day 17",
        "event_type": "Battle",
        "day": 17,
        "location": "Kurukshetra Battlefield",
        "summary": (
            "The long-anticipated duel between the two greatest archers of the age. "
            "Karna's chariot wheel sinks in the mud at the crucial moment; he steps "
            "down to free it, invoking the rules of war — but Krishna urges Arjuna "
            "to strike. Arjuna's Anjalikastra severs Karna's head, fulfilling the "
            "prophecy and the vow made at Draupadi's humiliation."
        ),
        "sides_involved": "Pandava vs Kaurava",
        "outcome": "Karna slain; Kaurava forces devastated",
        "key_character_names": "Karna, Arjuna, Krishna, Shalya",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Duryodhana's Last Stand — Day 18",
        "event_type": "Battle",
        "day": 18,
        "location": "Kurukshetra — Lake Dvaipayana",
        "summary": (
            "After the fall of all his allies, Duryodhana hides in the lake using "
            "a water-breathing technique. Yudhishthira taunts him out; Bhima and "
            "Duryodhana fight a mace duel. Bhima strikes below the navel (against "
            "the rules) to shatter Duryodhana's thigh — fulfilling his vow made "
            "after the dice game. Duryodhana dies at sunset."
        ),
        "sides_involved": "Pandava vs Kaurava",
        "outcome": "Duryodhana slain; Pandavas win the Kurukshetra War",
        "key_character_names": "Duryodhana, Bhima, Yudhishthira, Ashwatthama",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "The Bhagavad Gita — Before Battle",
        "event_type": "Revelation",
        "day": 1,
        "location": "Kurukshetra Battlefield — between the two armies",
        "summary": (
            "As both armies stand ready on the first day, Arjuna's resolve crumbles "
            "at the sight of relatives, teachers, and loved ones on the opposing side. "
            "Krishna then delivers the 18-chapter Bhagavad Gita — a discourse on duty, "
            "the nature of the self, devotion, and the path to liberation — which "
            "becomes the spiritual core of the entire epic."
        ),
        "sides_involved": "N/A (dialogue between Arjuna and Krishna)",
        "outcome": "Arjuna regains his resolve; the war begins",
        "key_character_names": "Krishna, Arjuna",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Draupadi's Swayamvara",
        "event_type": "Ceremony",
        "day": None,
        "location": "Panchala — King Drupada's court",
        "summary": (
            "King Drupada arranges a swayamvara (self-choice ceremony) for Draupadi, "
            "setting an impossible archery task. Arjuna, disguised as a brahmin, "
            "strings the massive bow and shoots five arrows through a rotating target "
            "to win Draupadi's hand. The Pandavas' true identities are soon revealed."
        ),
        "sides_involved": "All kingdoms of Bharata (as suitors)",
        "outcome": "Draupadi marries Arjuna (and subsequently all five Pandavas)",
        "key_character_names": "Draupadi, Arjuna, Karna, Drupada, Krishna",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Night Raid — Ashwatthama's Revenge",
        "event_type": "Battle",
        "day": 18,
        "location": "Pandava Camp",
        "summary": (
            "After Duryodhana's death, Ashwatthama, Kripacharya, and Kritavarma "
            "infiltrate the sleeping Pandava camp at night. Ashwatthama massacres "
            "the Upapandavas (Draupadi's five sons) and other Pandava warriors, "
            "mistaking them for the Pandava brothers themselves. He also uses the "
            "Brahmastra against Uttara's womb, which Krishna neutralises."
        ),
        "sides_involved": "Kaurava remnants vs Pandava camp",
        "outcome": "Pandava heirs wiped out; Ashwatthama cursed by Krishna to roam Earth in agony",
        "key_character_names": "Ashwatthama, Draupadi, Arjuna, Krishna",
    },
]


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_events_db() -> None:
    """Create the events table and seed it if empty."""
    with _get_conn() as conn:
        conn.executescript(_CREATE_TABLE)
        count = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        if count == 0:
            for seed in SEED_EVENTS:
                conn.execute(
                    """
                    INSERT INTO events
                        (id, title, event_type, day, location, summary,
                         sides_involved, outcome)
                    VALUES
                        (:id, :title, :event_type, :day, :location, :summary,
                         :sides_involved, :outcome)
                    """,
                    seed
                )
                if seed.get("key_character_names"):
                    names = [n.strip() for n in seed["key_character_names"].split(",")]
                    for name in names:
                        char_row = conn.execute("SELECT id FROM characters WHERE name = ?", (name,)).fetchone()
                        if char_row:
                            conn.execute(
                                "INSERT INTO event_characters (event_id, character_id) VALUES (?, ?)",
                                (seed["id"], char_row["id"])
                            )
        conn.commit()


def get_all_events(skip: int = 0, limit: int = 50) -> List[dict]:
    query = """
        SELECT e.*, GROUP_CONCAT(c.name, ', ') AS key_character_names
        FROM events e
        LEFT JOIN event_characters ec ON e.id = ec.event_id
        LEFT JOIN characters c ON ec.character_id = c.id
        GROUP BY e.id
        ORDER BY e.day NULLS LAST, e.title
        LIMIT ? OFFSET ?
    """
    with _get_conn() as conn:
        rows = conn.execute(query, (limit, skip)).fetchall()
    return [dict(r) for r in rows]


def get_event_by_id(event_id: str) -> Optional[dict]:
    query = """
        SELECT e.*, GROUP_CONCAT(c.name, ', ') AS key_character_names
        FROM events e
        LEFT JOIN event_characters ec ON e.id = ec.event_id
        LEFT JOIN characters c ON ec.character_id = c.id
        WHERE e.id = ?
        GROUP BY e.id
    """
    with _get_conn() as conn:
        row = conn.execute(query, (event_id,)).fetchone()
    return dict(row) if row else None


def search_events(title: str) -> List[dict]:
    pattern = f"%{title}%"
    query = """
        SELECT e.*, GROUP_CONCAT(c.name, ', ') AS key_character_names
        FROM events e
        LEFT JOIN event_characters ec ON e.id = ec.event_id
        LEFT JOIN characters c ON ec.character_id = c.id
        WHERE e.title LIKE ?
        GROUP BY e.id
        ORDER BY e.day NULLS LAST
    """
    with _get_conn() as conn:
        rows = conn.execute(query, (pattern,)).fetchall()
    return [dict(r) for r in rows]


def get_events_by_day(day: int) -> List[dict]:
    query = """
        SELECT e.*, GROUP_CONCAT(c.name, ', ') AS key_character_names
        FROM events e
        LEFT JOIN event_characters ec ON e.id = ec.event_id
        LEFT JOIN characters c ON ec.character_id = c.id
        WHERE e.day = ?
        GROUP BY e.id
        ORDER BY e.title
    """
    with _get_conn() as conn:
        rows = conn.execute(query, (day,)).fetchall()
    return [dict(r) for r in rows]


def get_events_count() -> int:
    with _get_conn() as conn:
        return conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
