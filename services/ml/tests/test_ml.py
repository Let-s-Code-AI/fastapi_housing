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
