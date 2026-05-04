"""
tests/test_events.py
Pytest suite for the Events / War Timeline API.
Run with: pytest tests/ -v
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def startup():
    with client:
        yield


# ---------------------------------------------------------------------------
# GET /api/events/
# ---------------------------------------------------------------------------

class TestListEvents:
    def test_returns_200(self):
        res = client.get("/api/events/")
        assert res.status_code == 200

    def test_returns_list(self):
        assert isinstance(client.get("/api/events/").json(), list)

    def test_seeded_events_present(self):
        res = client.get("/api/events/?limit=100")
        titles = [e["title"] for e in res.json()]
        assert any("Bhagavad Gita" in t for t in titles)
        assert any("Abhimanyu" in t for t in titles)

    def test_pagination_limit(self):
        res = client.get("/api/events/?limit=2")
        assert len(res.json()) <= 2

    def test_invalid_limit_rejected(self):
        assert client.get("/api/events/?limit=0").status_code == 422

    def test_limit_over_100_rejected(self):
        assert client.get("/api/events/?limit=101").status_code == 422


# ---------------------------------------------------------------------------
# GET /api/events/{id}
# ---------------------------------------------------------------------------

class TestGetEventById:
    def test_known_event(self):
        first = client.get("/api/events/?limit=1").json()[0]
        res = client.get(f"/api/events/{first['id']}")
        assert res.status_code == 200
        assert res.json()["id"] == first["id"]

    def test_unknown_id_returns_404(self):
        assert client.get("/api/events/does-not-exist").status_code == 404


# ---------------------------------------------------------------------------
# GET /api/events/search
# ---------------------------------------------------------------------------

class TestSearchEvents:
    def test_search_known_title(self):
        res = client.get("/api/events/search?title=Bhagavad")
        assert res.status_code == 200
        data = res.json()
        assert len(data) >= 1
        assert any("Bhagavad" in e["title"] for e in data)

    def test_no_match_returns_200_empty(self):
        res = client.get("/api/events/search?title=ZZZNoMatch999")
        assert res.status_code == 200
        assert res.json() == []

    def test_missing_param_returns_422(self):
        assert client.get("/api/events/search").status_code == 422


# ---------------------------------------------------------------------------
# GET /api/events/day/{day}
# ---------------------------------------------------------------------------

class TestEventsByDay:
    def test_day_1_returns_events(self):
        res = client.get("/api/events/day/1")
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        assert all(e["day"] == 1 for e in data)

    def test_day_0_rejected(self):
        assert client.get("/api/events/day/0").status_code == 422

    def test_day_19_rejected(self):
        assert client.get("/api/events/day/19").status_code == 422

    def test_day_minus_1_rejected(self):
        assert client.get("/api/events/day/-1").status_code == 422

    def test_day_with_no_events_returns_404(self):
        # Day 15 has no seeded events
        res = client.get("/api/events/day/15")
        assert res.status_code == 404

    def test_day_18_returns_events(self):
        res = client.get("/api/events/day/18")
        assert res.status_code == 200


# ---------------------------------------------------------------------------
# GET /api/events/count
# ---------------------------------------------------------------------------

class TestEventCount:
    def test_returns_count(self):
        res = client.get("/api/events/count")
        assert res.status_code == 200
        assert "count" in res.json()
        assert res.json()["count"] >= 8

    def test_count_matches_list(self):
        count = client.get("/api/events/count").json()["count"]
        total = len(client.get("/api/events/?limit=100").json())
        assert count == total


# ---------------------------------------------------------------------------
# Seed idempotency
# ---------------------------------------------------------------------------

class TestEventSeedIdempotency:
    def test_double_init_no_duplicates(self):
        from app.db.event_repo import init_events_db
        init_events_db()
        init_events_db()
        count = client.get("/api/events/count").json()["count"]
        assert count == 8
