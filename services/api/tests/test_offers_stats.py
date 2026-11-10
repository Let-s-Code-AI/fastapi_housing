"""Testy GET /offers/stats – statystyki dzielnicy."""
import pytest
from fastapi.testclient import TestClient

import models
from database import SessionLocal
from main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def _seed(locality, offers):
    """Wstawia oferty (cena, powierzchnia) bezpośrednio do bazy – z dokładnymi cenami."""
    db = SessionLocal()
    try:
        for price, area in offers:
            db.add(models.OfferDB(locality=locality, rooms=2, area_m2=area, price_total_zl=price))
        db.commit()
    finally:
        db.close()


def _stats(client, locality):
    return client.get("/offers/stats", params={"locality": locality})


def test_stats_odd_count(client):
    _seed("Statowo Nieparzyste", [(300000, 50.0), (100000, 50.0), (200000, 50.0)])
    body = _stats(client, "Statowo Nieparzyste").json()
    assert body["offers_count"] == 3
    assert body["median_price_zl"] == 200000.0


def test_stats_even_count(client):
    _seed("Statowo Parzyste", [(100000, 50.0), (200000, 50.0), (300000, 50.0), (500000, 50.0)])
    body = _stats(client, "Statowo Parzyste").json()
    assert body["offers_count"] == 4
    assert body["median_price_zl"] == 250000.0


def test_stats_single_offer(client):
    _seed("Statowo Jedna", [(420000, 40.0)])
    body = _stats(client, "Statowo Jedna").json()
    assert body["offers_count"] == 1
    assert body["median_price_zl"] == 420000.0


def test_stats_median_rounded_two_decimals(client):
    _seed("Statowo Grosze", [(100001, 50.0), (100002, 50.0)])
    assert _stats(client, "Statowo Grosze").json()["median_price_zl"] == 100001.5


def test_stats_response_shape(client):
    _seed("Statowo Kształt", [(500000, 50.0)])
    resp = _stats(client, "Statowo Kształt")
    assert resp.status_code == 200
    assert resp.json() == {
        "locality": "Statowo Kształt",
        "offers_count": 1,
        "median_price_zl": 500000.0,
        "median_price_per_m2_zl": 10000.0,
    }


def test_stats_unknown_locality_404(client):
    resp = _stats(client, "Nieistniejąca Dzielnica")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Brak ofert dla dzielnicy: Nieistniejąca Dzielnica"


def test_stats_exact_match_not_partial(client):
    _seed("Statowo Exact", [(100000, 50.0)])
    _seed("Statowo Exact Park", [(900000, 50.0), (900000, 50.0)])
    body = _stats(client, "Statowo Exact").json()
    assert body["offers_count"] == 1
    assert body["median_price_zl"] == 100000.0
    assert _stats(client, "Statowo Ex").status_code == 404


def test_stats_ignores_invalid_rows(client):
    _seed("Statowo Brudne", [(300000, 50.0), (999999, 0.0), (None, 50.0)])
    body = _stats(client, "Statowo Brudne").json()
    assert body["offers_count"] == 1
    assert body["median_price_zl"] == 300000.0


def test_stats_only_invalid_rows_404(client):
    _seed("Statowo Puste", [(999999, 0.0)])
    assert _stats(client, "Statowo Puste").status_code == 404


def test_stats_strips_whitespace(client):
    _seed("Statowo Spacje", [(250000, 50.0)])
    resp = _stats(client, "  Statowo Spacje  ")
    assert resp.status_code == 200
    assert resp.json()["locality"] == "Statowo Spacje"


def test_stats_missing_locality_422(client):
    assert client.get("/offers/stats").status_code == 422


def test_stats_empty_locality_422(client):
    assert _stats(client, "").status_code == 422


def test_stats_per_m2_is_median_of_ratios(client):
    # ceny za m²: 10000, 5000, 15000 → mediana 10000 (iloraz median dałby 5000)
    _seed("Statowo Metraż", [(200000, 20.0), (300000, 60.0), (900000, 60.0)])
    assert _stats(client, "Statowo Metraż").json()["median_price_per_m2_zl"] == 10000.0


def test_stats_per_m2_even_count(client):
    _seed("Statowo Metraż Parzyste", [(500000, 50.0), (600000, 50.0)])
    assert _stats(client, "Statowo Metraż Parzyste").json()["median_price_per_m2_zl"] == 11000.0


def test_stats_per_m2_rounded_two_decimals(client):
    _seed("Statowo Metraż Grosze", [(100000, 30.0)])
    assert _stats(client, "Statowo Metraż Grosze").json()["median_price_per_m2_zl"] == 3333.33
