# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

FastAPI service that predicts Wrocław apartment prices (Linear Regression on `area_m2` + `rooms`) and stores offers in SQLite. Data source: Adresowo.pl scrape. Code comments, docstrings, API messages and README are in Polish — keep that convention.

## Layout

Monorepo managed as a **uv workspace** — one `.venv` and one `uv.lock` at the root. No `requirements.txt`; dependencies live in each service's `pyproject.toml`.

- `pyproject.toml` (root) — virtual workspace root (no `[project]`): `members = ["services/api", "services/ml"]` + `dev` dependency group (pytest, httpx).
- `services/ml/` — package `housing-ml` (flat `py-modules`: `ml`, `ml_flow`) + committed `model.pkl`. See `services/ml/CLAUDE.md`.
- `services/api/` — package `housing-api` (`main`, `models`, `database`, `create_db`); depends on `housing-ml` via `[tool.uv.sources] housing-ml = { workspace = true }` and imports `from ml import predict_price`. See `services/api/CLAUDE.md`.
- `data/` — CSV input (gitignored except `data/README.md`).

New top-level modules must be added to the relevant service's `py-modules` list.

## Commands

```bash
uv sync --all-packages                                   # install both services (editable) + dev group
uv run --directory services/api uvicorn main:app --reload
uv run --directory services/api python create_db.py      # create tables + load CSV
uv run --directory services/ml python ml.py              # retrain model.pkl
uv run --directory services/ml python ml_flow.py         # retrain with MLflow (mlruns/ in CWD)
uv run --directory services/ml pytest
uv run --directory services/api pytest
```

Paths (`model.pkl`, CSV, `offers.db`) are resolved relative to module files, not CWD. The CSV defaults to `<repo>/data/adresowo_wroclaw_all.csv` (override: `HOUSING_CSV_PATH`); the DB defaults to `services/api/offers.db` (override: `DATABASE_URL`). This relies on editable installs — `ml.MODEL_PATH` points into the source tree.

No linter or formatter is configured.

## Commits

Use [Conventional Commits](https://www.conventionalcommits.org/): `<type>(<optional scope>): <description>`.

- Types: `feat`, `fix`, `docs`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `style`, `revert`.
- Scopes: `api` (`services/api`), `ml` (`services/ml`, incl. `model.pkl`), `deps` (any `pyproject.toml`, `uv.lock`), `data` (`data/README.md`).
- Description in imperative mood, lowercase, no trailing period, ≤72 chars. Breaking changes: `!` after type/scope (e.g. `feat(api)!: ...`) and a `BREAKING CHANGE:` footer.
- Examples: `feat(api): add /offers/search filters`, `build(deps): add httpx to dev group`, `chore(ml): retrain model.pkl`.

## Untracked artifacts

`data/*` (except `data/README.md`), `*.csv`, `*.db` and `mlruns/` are gitignored; the CSV must be supplied locally. `services/ml/model.pkl` **is** committed — retraining changes a tracked file.
