# services/ml

Package `housing-ml` (uv workspace member). Flat modules `ml`, `ml_flow`; consumed by `services/api` via `from ml import predict_price`.

## Commands (from repo root)

```bash
uv run --directory services/ml pytest
uv run --directory services/ml python ml.py        # retrain -> model.pkl + sample predictions
uv run --directory services/ml python ml_flow.py   # same, tracked in MLflow (mlruns/ in CWD)
```

## Modules

- `ml.py` — `BASE_DIR`, `MODEL_PATH`, `CSV_PATH` constants; `load_data(csv_path=CSV_PATH)` (CSV cleaning + outlier filters), `train_model()`, `load_model()`, `predict_price()`. `test_model()` is a print-based sanity check, not a pytest test.
- `ml_flow.py` — imports `MODEL_PATH`, `load_data` from `ml` and duplicates training with MLflow logging; writes the same `model.pkl`.

## Non-obvious behaviors

- `MODEL_PATH` is `Path(__file__).parent / "model.pkl"`; works because the workspace installs this package editable. A non-editable wheel would not ship `model.pkl`.
- `predict_price()` unpickles `model.pkl` on every call; if the file is missing it silently trains a new one, which requires the CSV.
- `model.pkl` was pickled with an older scikit-learn — unpickling emits `InconsistentVersionWarning`. Retraining fixes it but changes a tracked file.
- CSV cleaning/filter logic (price string → int, area 10–500 m², price 100k–5M PLN, rooms 1–10) is duplicated in `services/api/create_db.py:populate_database`; change both together.
- `tests/` use the committed `model.pkl` and a tiny CSV in `tmp_path` — they never need the real data.
