"""Testy modułu ml – predykcja na commitowanym model.pkl i czyszczenie CSV."""
import pandas as pd
import pytest

import ml


def test_model_file_is_found_next_to_module():
    assert ml.MODEL_PATH.exists()
    assert ml.MODEL_PATH.parent == ml.BASE_DIR


def test_predict_price_returns_positive_value():
    assert ml.predict_price(50.0, 2) > 0


def test_predict_price_grows_with_area():
    assert ml.predict_price(100.0, 3) > ml.predict_price(50.0, 3)


def test_load_data_cleans_and_filters(tmp_path):
    csv = tmp_path / "offers.csv"
    pd.DataFrame(
        {
            "locality": ["A", "B", "C", "D", "E", "F"],
            "rooms": [2, 3, 2, 0, 2, None],
            "area_m2": [50.0, 70.0, 5.0, 40.0, 60.0, 45.0],
            "price_total_zl": ["800 000", "650000", "300000", "400000", "6000000", "500000"],
        }
    ).to_csv(csv, index=False)

    df = ml.load_data(csv)

    # Zostają tylko A (cena ze spacją) i B; C: za mała powierzchnia,
    # D: 0 pokoi, E: cena > 5M, F: brak liczby pokoi
    assert sorted(df["locality"]) == ["A", "B"]
    assert df.loc[df["locality"] == "A", "price_total_zl"].item() == 800000


def test_load_data_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        ml.load_data(tmp_path / "brak.csv")


def _raw_offers():
    return pd.DataFrame(
        {
            "locality": ["A", None, "C", "D"],
            "rooms": [1, 2, 10, 11],
            "area_m2": [30.0, 50.0, 120.0, 150.0],
            "price_total_zl": ["300 000", "450,000", "1200000", "1500000"],
        }
    )


def test_clean_offers_default_keeps_missing_locality():
    df = ml.clean_offers(_raw_offers())
    # D odpada (11 pokoi); brak locality nie przeszkadza przy treningu
    assert list(df["price_total_zl"]) == [300000, 450000, 1200000]


def test_clean_offers_required_locality_drops_missing():
    df = ml.clean_offers(_raw_offers(), required=(*ml.REQUIRED_COLUMNS, "locality"))
    assert list(df["locality"]) == ["A", "C"]


def test_clean_offers_does_not_mutate_input():
    raw = _raw_offers()
    ml.clean_offers(raw)
    assert raw["price_total_zl"].iloc[0] == "300 000"


@pytest.fixture
def count_loads(monkeypatch):
    """Licznik wczytań modelu z dysku; czysty cache przed i po teście."""
    calls = []
    real_load = ml.load_model

    def fake_load():
        calls.append(1)
        return real_load()

    ml.get_model.cache_clear()
    monkeypatch.setattr(ml, "load_model", fake_load)
    yield calls
    ml.get_model.cache_clear()


def test_predict_price_loads_model_once(count_loads):
    ml.predict_price(50.0, 2)
    ml.predict_price(70.0, 3)
    assert len(count_loads) == 1


def test_cache_clear_forces_reload(count_loads):
    ml.predict_price(50.0, 2)
    ml.get_model.cache_clear()
    ml.predict_price(50.0, 2)
    assert len(count_loads) == 2
