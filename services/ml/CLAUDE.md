# services/ml

Package `housing-ml` (uv workspace member). Flat modules `ml`, `ml_flow`; consumed by `services/api` via `from ml import predict_price`.

## Commands (from repo root)

```bash
uv run --directory services/ml pytest
uv run --directory services/ml python ml.py        # retrain -> model.pkl + sample predictions
uv run --directory services/ml python ml_flow.py   # same, tracked in MLflow (mlruns/ in CWD)
```

## Modules

- `ml.py` — `BASE_DIR`, `MODEL_PATH`, `CSV_PATH` constants; `clean_offers(df, required=REQUIRED_COLUMNS)` (shared CSV cleaning + outlier filters, thresholds as module constants; also used by `services/api/create_db.py`), `load_data(csv_path=CSV_PATH)` (read CSV + `clean_offers`), `train_model()`, `load_model()` (raw unpickle from disk), `get_model()` (`lru_cache(maxsize=1)` over `load_model`), `predict_price()`. `test_model()` is a print-based sanity check, not a pytest test.
- `ml_flow.py` — imports `MODEL_PATH`, `load_data`, `get_model`, `predict_price` from `ml`; only `train_model` differs (MLflow logging); writes the same `model.pkl`.

## Non-obvious behaviors

- `MODEL_PATH` is `Path(__file__).parent / "model.pkl"`; works because the workspace installs this package editable. A non-editable wheel would not ship `model.pkl`.
- `predict_price()` uses the cached `get_model()` — the pickle is read once per process. Both `train_model()`s call `get_model.cache_clear()` after writing. If `model.pkl` is missing, `load_model()` silently trains a new one (via `ml.train_model`, without MLflow), which requires the CSV.
- `model.pkl` was pickled with an older scikit-learn — unpickling emits `InconsistentVersionWarning`. Retraining fixes it but changes a tracked file.
- CSV cleaning/filter logic (price string → int, area 10–500 m², price 100k–5M PLN, rooms 1–10) lives only in `clean_offers`; changing it affects both training and the DB import.
- Tests that count model loads must `get_model.cache_clear()` before/after (see `count_loads` fixture).
- `tests/` use the committed `model.pkl` and a tiny CSV in `tmp_path` — they never need the real data.
