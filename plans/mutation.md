# Mutation testing

Narzędzie: mutmut 3.8.1, konfiguracja w `services/api/pyproject.toml` (`[tool.mutmut]`, `paths_to_mutate = ["main.py"]`).
Pomiar: `cd services/api && uv run mutmut run && uv run mutmut results` (szczegóły mutanta: `uv run mutmut show <nazwa>`).

| Data | Plik | Mutanty | Zabite przed | Score przed | Zabite po | Score po |
|------|------|---------|--------------|-------------|-----------|----------|
| 2026-11-10 | `services/api/main.py` | 73 | 67 | 91.8% | 73 | 100.0% |

## Przygotowanie

- **Funkcje z dekoratorami.** mutmut 3 pomija funkcje z dekoratorami, więc przy `@app.get/@app.post` zmutował tylko `get_db` (1 mutant). Dlatego trasy są rejestrowane przez `app.add_api_route(...)` na końcu `main.py`. API działa tak samo; `lifespan` (`@asynccontextmanager`) nadal nie jest mutowany.
- **Wiele przebiegów w jednym procesie.** mutmut wywołuje `pytest.main()` kilka razy w jednym procesie, a baza testowa z poprzedniego przebiegu zostawała i psuła asercje na liczbę wierszy. Teraz `tests/conftest.py` czyści tabele na starcie każdej sesji (`_fresh_db`).

## Przeżyte mutanty (przebieg „przed”)

| Mutant | Zmiana | Status | Test zabijający |
|--------|--------|--------|-----------------|
| `main.x_root__mutmut_4` | komunikat w `root` małymi literami | zabity | `test_root_message_exact` |
| `main.x_root__mutmut_5` | komunikat w `root` WIELKIMI literami | zabity | `test_root_message_exact` |
| `main.x_predict__mutmut_17` | `round(predicted_price, 2)` → `round(predicted_price)` | zabity | `test_predict_rounds_to_two_decimals` |
| `main.x_predict__mutmut_22` | `round(price_per_m2, 2)` → `round(price_per_m2, None)` | zabity | `test_predict_rounds_to_two_decimals` |
| `main.x_predict__mutmut_24` | `round(price_per_m2, 2)` → `round(price_per_m2)` | zabity | `test_predict_rounds_to_two_decimals` |
| `main.x_predict__mutmut_25` | `round(price_per_m2, 2)` → `round(price_per_m2, 3)` | zabity | `test_predict_rounds_to_two_decimals` |

Mutanty równoważne: brak.

Przyczyny przeżycia:
- `test_root` sprawdzał tylko, czy klucz `message` istnieje, a nie jego treść.
- `test_predict` porównywał wynik z tolerancją `approx(rel=1e-3)` na prawdziwym modelu, więc nie odróżniał zaokrąglenia do 0, 2 i 3 miejsc. Nowy test podmienia `main.predict_price` na stałą `123456.789` i sprawdza dokładne wartości.
