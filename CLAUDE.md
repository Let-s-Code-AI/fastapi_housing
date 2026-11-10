# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

FastAPI service that predicts Wrocław apartment prices (Linear Regression on `area_m2` + `rooms`) and stores offers in SQLite. Data source: Adresowo.pl scrape. Code comments, docstrings, API messages and README are in Polish — keep that convention.

## Commands

```bash
pip install -e .
python create_db.py          # create tables + load CSV into offers.db
python ml.py                 # train LinearRegression -> model.pkl, print sample predictions
python ml_flow.py            # same training, but tracked in MLflow (writes mlruns/)
uvicorn main:app --reload    # dev server; docs at http://localhost:8000/docs
./curl_requests.sh           # smoke-test endpoints against a running server
```

There is no test suite, linter, or formatter configured. `test_model()` in `ml.py` is a print-based sanity check, not a pytest test.

All scripts use paths relative to the CWD (`data/adresowo_wroclaw_all.csv`, `model.pkl`, `./offers.db`), so run everything from the repo root.

Dependencies live only in `pyproject.toml`, which uses a flat `py-modules` list, so a new top-level module must be added there.

## Architecture

- `database.py` — SQLAlchemy engine/`SessionLocal`/`Base` for `sqlite:///./offers.db`.
- `models.py` — both the SQLAlchemy table (`OfferDB`, table `offers`) and the Pydantic schemas (`Offer`, `OfferCreate`, `PricePrediction`). `Offer` uses Pydantic v1-style `Config.orm_mode`.
- `ml.py` — `load_data()` (CSV cleaning + outlier filters), `train_model()`, `load_model()`, `predict_price()`. `ml_flow.py` imports `load_data` from here and duplicates the rest with MLflow logging; both write the same `model.pkl`.
- `main.py` — FastAPI app; calls `create_all` on import; `get_db` dependency; endpoints `/`, `POST /offers/`, `GET /offers/`, `GET /offers/search` (optional filters combined with `and_`, `limit` ≤ 500), `POST /predict/`.

Non-obvious behaviors to be aware of:
- `POST /offers/` does **not** accept a price — it stores the ML-predicted price in `price_total_zl`. So user-added rows contain model output, while CSV-loaded rows contain real prices.
- `predict_price()` unpickles `model.pkl` on every call; if the file is missing it trains a new model, which requires the CSV.
- The CSV cleaning/filter logic (price string → int, area 10–500 m², price 100k–5M PLN, rooms 1–10) is duplicated in `ml.py:load_data` and `create_db.py:populate_database`; change both together.
- `create_db.py` appends rows without dedup — rerunning it duplicates the data. Delete `offers.db` first to reload.
- `GET /offers/` is wrapped in `functools.lru_cache` keyed on the per-request `Session`, so it effectively never hits and retains sessions — don't rely on it as a cache.

## Commits

Use [Conventional Commits](https://www.conventionalcommits.org/): `<type>(<optional scope>): <description>`.

- Types: `feat`, `fix`, `docs`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `style`, `revert`.
- Useful scopes here: `api` (main.py), `db` (database.py, models.py, create_db.py), `ml` (ml.py, ml_flow.py, model.pkl), `deps` (pyproject.toml, uv.lock).
- Description in imperative mood, lowercase, no trailing period, ≤72 chars. Breaking changes: `!` after type/scope (e.g. `feat(api)!: ...`) and a `BREAKING CHANGE:` footer.
- Examples: `feat(api): add /offers/search filters`, `build(deps): add pyproject.toml and uv`, `chore(ml): retrain model.pkl`.

## Untracked artifacts

`data/`, `*.csv`, `*.db` and `mlruns/` are gitignored; the CSV must be supplied locally. `model.pkl` **is** committed — retraining changes a tracked file.
