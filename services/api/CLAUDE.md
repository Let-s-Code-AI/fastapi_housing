# services/api

Package `housing-api` (uv workspace member). Depends on `housing-ml` (workspace source) for `predict_price`.

## Commands (from repo root)

```bash
uv run --directory services/api uvicorn main:app --reload   # docs at http://localhost:8000/docs
uv run --directory services/api python create_db.py         # create tables + load CSV
uv run --directory services/api pytest
./services/api/curl_requests.sh                             # smoke-test a running server
```

## Modules

- `database.py` — engine/`SessionLocal`/`Base`; URL from `DATABASE_URL`, default `sqlite:///<this dir>/offers.db`.
- `models.py` — SQLAlchemy `OfferDB` (table `offers`) and Pydantic `Offer`, `OfferCreate`, `PricePrediction`. `Offer` uses Pydantic v1-style `Config.orm_mode` (warns under v2).
- `main.py` — FastAPI app; `create_all` on import; `get_db` dependency; endpoints `/`, `POST /offers/`, `GET /offers/`, `GET /offers/search` (optional filters combined with `and_`, `limit` ≤ 500), `POST /predict/`.
- `create_db.py` — creates tables and loads the CSV (`ml.CSV_PATH`).

## Non-obvious behaviors

- `POST /offers/` does **not** accept a price — it stores the ML-predicted price in `price_total_zl`. User-added rows contain model output; CSV-loaded rows contain real prices.
- `create_db.py` appends rows without dedup — rerunning duplicates data. Delete `offers.db` first to reload.
- CSV cleaning in `create_db.py` duplicates `ml.load_data` (plus drops missing `locality`); change both together.
- `GET /offers/` is wrapped in `functools.lru_cache` keyed on the per-request `Session`, so it effectively never hits and retains sessions — don't rely on it as a cache.
- `tests/conftest.py` sets `DATABASE_URL` to a temp file **before** `main` is imported, because `main` runs `create_all` at import time.
