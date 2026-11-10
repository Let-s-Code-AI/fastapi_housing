"""Testy skryptu create_db.py na tymczasowym CSV i testowej bazie z conftest.py."""
import runpy

import ml
import create_db
from database import SessionLocal
from models import OfferDB

LOCALITY = "Wrocław CsvTest"


def _count(locality):
    db = SessionLocal()
    try:
        return db.query(OfferDB).filter(OfferDB.locality == locality).count()
    finally:
        db.close()


def test_create_database(capsys):
    create_db.create_database()
    assert "created successfully" in capsys.readouterr().out


def test_populate_database_filters_and_inserts(tmp_path, monkeypatch, capsys):
    csv = tmp_path / "offers.csv"
    csv.write_text(
        "locality,rooms,area_m2,price_total_zl\n"
        f"{LOCALITY},2,50,\"450 000\"\n"      # poprawny – cena ze spacją
        f"{LOCALITY},3,70,\"650,000\"\n"      # poprawny – cena z przecinkiem
        f"{LOCALITY},2,5,300000\n"            # za mała powierzchnia
        f"{LOCALITY},2,50,abc\n"              # cena nienumeryczna
        f"{LOCALITY},,50,300000\n"            # brak liczby pokoi
        ",2,50,300000\n",                     # brak locality
        encoding="utf-8",
    )
    monkeypatch.setattr(create_db, "CSV_PATH", csv)

    create_db.populate_database()

    assert "Successfully inserted 2 apartments" in capsys.readouterr().out
    assert _count(LOCALITY) == 2


def test_populate_database_missing_csv(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(create_db, "CSV_PATH", tmp_path / "brak.csv")
    create_db.populate_database()
    assert "CSV file not found" in capsys.readouterr().out


def test_populate_database_error_rolls_back(tmp_path, monkeypatch, capsys):
    csv = tmp_path / "zle.csv"
    csv.write_text("foo,bar\n1,2\n", encoding="utf-8")  # brak wymaganych kolumn
    monkeypatch.setattr(create_db, "CSV_PATH", csv)

    create_db.populate_database()

    assert "Error populating database" in capsys.readouterr().out


def test_main_block(tmp_path, monkeypatch, capsys):
    # Uruchomienie jako skrypt importuje CSV_PATH z ml na nowo – podmieniamy go tam
    monkeypatch.setattr(ml, "CSV_PATH", tmp_path / "brak.csv")
    runpy.run_path(create_db.__file__, run_name="__main__")
    out = capsys.readouterr().out
    assert "created successfully" in out
    assert "CSV file not found" in out
