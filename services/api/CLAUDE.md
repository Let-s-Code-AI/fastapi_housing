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
- `models.py` — SQLAlchemy `OfferDB` (table `offers`) and Pydantic v2 `Offer` (`from_attributes=True`), `OfferCreate`, `PricePrediction`. Input schemas validate `area_m2 > 0` and `rooms >= 1` (422 otherwise); `Offer` (response) is deliberately unconstrained so legacy rows can't 500.
- `main.py` — FastAPI app; `create_all` on import; `lifespan` warms up `ml.get_model()` (missing `model.pkl` fails at startup); `get_db` dependency; endpoints `/`, `POST /offers/`, `GET /offers/` (`response_model=List[Offer]`, no cache), `GET /offers/search` (optional filters combined with `and_`, `limit` ≤ 500), `POST /predict/`.
- `create_db.py` — creates tables and loads the CSV (`ml.CSV_PATH`), cleaned by `ml.clean_offers` with `locality` added to the required columns.

## Non-obvious behaviors

- `POST /offers/` does **not** accept a price — it stores the ML-predicted price in `price_total_zl`. User-added rows contain model output; CSV-loaded rows contain real prices.
- `create_db.py` appends rows without dedup — rerunning duplicates data. Delete `offers.db` first to reload.
- `tests/conftest.py` sets `DATABASE_URL` to a temp file **before** `main` is imported, because `main` runs `create_all` at import time. Use `TestClient(app)` as a context manager so `lifespan` runs.
- Routes are registered with `app.add_api_route(...)` at the bottom of `main.py`, not decorators — mutmut 3 skips decorated functions. Mutation testing: `cd services/api && uv run mutmut run` (results in `plans/mutation.md`).
