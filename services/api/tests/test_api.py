"""Testy endpointów API (TestClient + tymczasowa baza SQLite z conftest.py)."""
import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "message" in resp.json()


def test_predict(client):
    resp = client.post("/predict/", json={"area_m2": 50.0, "rooms": 2})
    assert resp.status_code == 200
    body = resp.json()
    assert body["area_m2"] == 50.0
    assert body["rooms"] == 2
    assert body["predicted_price"] > 0
    assert body["price_per_m2"] == pytest.approx(body["predicted_price"] / 50.0, rel=1e-3)


def test_predict_invalid_body(client):
    resp = client.post("/predict/", json={"area_m2": "dużo"})
    assert resp.status_code == 422


def test_create_offer_and_search(client):
    resp = client.post(
        "/offers/",
        json={"locality": "Wrocław Testowo", "rooms": 3, "area_m2": 65.0},
    )
    assert resp.status_code == 200
    offer = resp.json()
    # Cena oferty pochodzi z modelu, nie od użytkownika
    assert offer["price_total_zl"] > 0

    resp = client.get("/offers/search", params={"locality": "testowo", "rooms_min": 3})
    assert resp.status_code == 200
    ids = [o["id"] for o in resp.json()]
    assert offer["id"] in ids

    resp = client.get("/offers/search", params={"locality": "testowo", "rooms_min": 4})
    assert offer["id"] not in [o["id"] for o in resp.json()]
