"""Walidacja wejścia: area_m2 > 0 i rooms >= 1 dla POST /offers/ oraz POST /predict/."""
import pytest
from fastapi.testclient import TestClient

from main import app

ENDPOINTS = {
    "/offers/": {"locality": "Wrocław Walidacja"},
    "/predict/": {},
}


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.mark.parametrize("path", ENDPOINTS)
@pytest.mark.parametrize(
    "payload",
    [
        {"area_m2": 0, "rooms": 2},
        {"area_m2": -1, "rooms": 2},
        {"area_m2": 50.0, "rooms": 0},
        {"area_m2": 50.0, "rooms": -1},
    ],
)
def test_invalid_values_rejected(client, path, payload):
    resp = client.post(path, json={**ENDPOINTS[path], **payload})
    assert resp.status_code == 422


@pytest.mark.parametrize("path", ENDPOINTS)
@pytest.mark.parametrize("payload", [{"area_m2": 0.1, "rooms": 1}, {"area_m2": 50.0, "rooms": 1}])
def test_boundary_values_accepted(client, path, payload):
    resp = client.post(path, json={**ENDPOINTS[path], **payload})
    assert resp.status_code == 200
