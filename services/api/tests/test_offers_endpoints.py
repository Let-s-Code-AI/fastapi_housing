"""Testy GET /offers/ oraz wszystkich filtrów /offers/search."""
import pytest
from fastapi.testclient import TestClient

from main import app

LOCALITY = "Wrocław Filtrowo"


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def offers(client):
    """Dwie oferty o różnej liczbie pokoi i powierzchni (cena z modelu)."""
    small = client.post("/offers/", json={"locality": LOCALITY, "rooms": 1, "area_m2": 30.0}).json()
    big = client.post("/offers/", json={"locality": LOCALITY, "rooms": 4, "area_m2": 90.0}).json()
    return small, big


def _search_ids(client, **params):
    resp = client.get("/offers/search", params={"locality": "filtrowo", **params})
    assert resp.status_code == 200
    return {o["id"] for o in resp.json()}


def test_read_offers_returns_created(client, offers):
    resp = client.get("/offers/")
    assert resp.status_code == 200
    ids = {o["id"] for o in resp.json()}
    assert {offers[0]["id"], offers[1]["id"]} <= ids


def test_search_rooms_max(client, offers):
    small, big = offers
    assert _search_ids(client, rooms_max=2) == {small["id"]}


def test_search_area_range(client, offers):
    small, big = offers
    assert _search_ids(client, area_min=50) == {big["id"]}
    assert _search_ids(client, area_max=50) == {small["id"]}


def test_search_price_range(client, offers):
    small, big = offers
    lo, hi = sorted([small, big], key=lambda o: o["price_total_zl"])
    threshold = (lo["price_total_zl"] + hi["price_total_zl"]) // 2
    assert _search_ids(client, price_min=threshold) == {hi["id"]}
    assert _search_ids(client, price_max=threshold) == {lo["id"]}


def test_search_limit(client, offers):
    assert len(_search_ids(client, limit=1)) == 1
