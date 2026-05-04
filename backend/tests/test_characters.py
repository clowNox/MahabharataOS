"""
tests/test_characters.py
Pytest suite for the Characters Knowledge API.
Run with: pytest tests/ -v
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module", autouse=True)
def startup():
    """Trigger startup event so DBs are initialised before tests run."""
    with client:
        yield


# ---------------------------------------------------------------------------
# GET /api/characters/
# ---------------------------------------------------------------------------

class TestListCharacters:
    def test_returns_200(self):
        res = client.get("/api/characters/")
        assert res.status_code == 200

    def test_returns_list(self):
        res = client.get("/api/characters/")
        data = res.json()
        assert isinstance(data, list)

    def test_seeded_characters_present(self):
        res = client.get("/api/characters/")
        names = [c["name"] for c in res.json()]
        for expected in ["Arjuna", "Krishna", "Karna", "Draupadi"]:
            assert expected in names, f"{expected} missing from characters list"

    def test_pagination_limit(self):
        res = client.get("/api/characters/?limit=2")
        assert res.status_code == 200
        assert len(res.json()) <= 2

    def test_pagination_skip(self):
        all_res = client.get("/api/characters/?limit=100")
        skip_res = client.get("/api/characters/?skip=1&limit=100")
        all_names = [c["name"] for c in all_res.json()]
        skip_names = [c["name"] for c in skip_res.json()]
        # Skipping 1 should drop the first result
        assert skip_names == all_names[1:]

    def test_invalid_limit_rejected(self):
        res = client.get("/api/characters/?limit=0")
        assert res.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/characters/{id}
# ---------------------------------------------------------------------------

class TestGetCharacterById:
    def test_known_character(self):
        all_res = client.get("/api/characters/")
        char = all_res.json()[0]
        res = client.get(f"/api/characters/{char['id']}")
        assert res.status_code == 200
        assert res.json()["name"] == char["name"]

    def test_unknown_id_returns_404(self):
        res = client.get("/api/characters/does-not-exist")
        assert res.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/characters/search
# ---------------------------------------------------------------------------

class TestSearchCharacters:
    def test_search_known_name(self):
        res = client.get("/api/characters/search?name=Arjuna")
        assert res.status_code == 200
        data = res.json()
        assert any(c["name"] == "Arjuna" for c in data)

    def test_partial_match(self):
        res = client.get("/api/characters/search?name=kri")
        assert res.status_code == 200
        names = [c["name"].lower() for c in res.json()]
        assert any("kri" in n for n in names)

    def test_no_match_returns_200_empty(self):
        res = client.get("/api/characters/search?name=ZZZNoMatch999")
        assert res.status_code == 200
        assert res.json() == []

    def test_missing_name_param_returns_422(self):
        res = client.get("/api/characters/search")
        assert res.status_code == 422

    def test_empty_name_returns_422(self):
        res = client.get("/api/characters/search?name=")
        assert res.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/characters/count
# ---------------------------------------------------------------------------

class TestCharacterCount:
    def test_returns_count(self):
        res = client.get("/api/characters/count")
        assert res.status_code == 200
        data = res.json()
        assert "count" in data
        assert data["count"] >= 8  # at least the 8 seed characters

    def test_count_matches_list_length(self):
        count_res = client.get("/api/characters/count")
        list_res = client.get("/api/characters/?limit=100")
        assert count_res.json()["count"] == len(list_res.json())


# ---------------------------------------------------------------------------
# Seed idempotency
# ---------------------------------------------------------------------------

class TestSeedIdempotency:
    def test_double_init_does_not_duplicate(self):
        from app.db.character_repo import init_db
        init_db()  # run again
        init_db()  # and again
        count_res = client.get("/api/characters/count")
        list_res = client.get("/api/characters/?limit=100")
        assert count_res.json()["count"] == len(list_res.json())
        # Should still be exactly 8 seed characters (no duplicates)
        assert count_res.json()["count"] == 8
