---
description: Coverage serwisu + testy tylko dla niepokrytych linii
argument-hint: [api|ml]
allowed-tools: Bash(uv run:*), Bash(git add:*), Bash(git commit:*), Bash(git diff:*), Bash(date:*), Read, Edit, Write
---

Serwis: `$ARGUMENTS` (dozwolone tylko `api` albo `ml` — dla innej wartości przerwij i zgłoś błąd).

1. Zmierz coverage „przed”:
   `uv run --directory services/$ARGUMENTS pytest --cov=. --cov-report=term-missing -q`
   Zapamiętaj łączny % (TOTAL) i listę niepokrytych linii (`Missing`). Pomiń same pliki testów (`tests/`).

2. Dopisz wiersz do `plans/coverage.md` (utwórz plik z nagłówkiem tabeli, jeśli nie istnieje):
   `| <data YYYY-MM-DD> | $ARGUMENTS | <% przed> | <% po> |`
   Kolumnę „po” uzupełnij po kroku 3.

3. Dla każdej linii z `Missing`: dopisz test w `services/$ARGUMENTS/tests/` **albo** uzasadnij w `plans/coverage.md`, że to martwy kod (plik:linia + jedno zdanie dlaczego). Nie zmieniaj kodu produkcyjnego, żeby podbić wynik. Nie trenuj ponownie `model.pkl`. Następnie uruchom krok 1 ponownie i zapisz % „po”.

4. Ustaw w `services/$ARGUMENTS/pyproject.toml`:
   ```toml
   [tool.coverage.report]
   fail_under = <% po, zaokrąglone w dół do liczby całkowitej>
   ```

5. Commit (Conventional Commits, bez trailera Co-Authored-By):
   `git add services/$ARGUMENTS plans/coverage.md && git commit -m "test($ARGUMENTS): <opis, tryb rozkazujący, ≤72 znaki>"`
   Na koniec pokaż tabelę coverage przed/po (łącznie i per plik).
