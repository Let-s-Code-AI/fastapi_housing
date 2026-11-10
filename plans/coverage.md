# Coverage

Pomiar: `uv run --directory services/<serwis> pytest --cov=. --cov-report=term-missing -q` (bez plików `tests/`).

| Data | Serwis | % przed | % po |
|------|--------|---------|------|
| 2026-11-10 | api | 64.8 | 100.0 |

## Martwy kod

Brak — wszystkie niepokryte linie (`create_db.py:1-71`, `main.py:51, 72-80`) zostały pokryte testami.
