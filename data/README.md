# Dane

Katalog na dane wejściowe. Wszystko poza tym plikiem jest w `.gitignore` – CSV trzeba dostarczyć lokalnie.

## Wymagany plik

`data/adresowo_wroclaw_all.csv` – oferty mieszkań we Wrocławiu zescrapowane z portalu [Adresowo.pl](https://adresowo.pl).

Wymagane kolumny:

| kolumna          | typ    | uwagi                                              |
|------------------|--------|----------------------------------------------------|
| `locality`       | tekst  | dzielnica / lokalizacja                            |
| `rooms`          | liczba | liczba pokoi                                       |
| `area_m2`        | liczba | powierzchnia w m²                                  |
| `price_total_zl` | tekst  | cena całkowita, może zawierać spacje (`"800 000"`) |

Podczas ładowania wiersze są filtrowane: powierzchnia 10–500 m², cena 100 tys.–5 mln zł, 1–10 pokoi.

## Jak zdobyć

Plik nie jest publikowany w repo. Poproś autora projektu o aktualny eksport albo przygotuj własny scrap ofert z Adresowo.pl z powyższymi kolumnami (zgodnie z regulaminem serwisu).

## Inna lokalizacja

Ścieżkę można nadpisać zmienną środowiskową:

```bash
HOUSING_CSV_PATH=/sciezka/do/pliku.csv uv run --directory services/ml python ml.py
```

## Do czego jest potrzebny

- `services/ml/ml.py` / `ml_flow.py` – trening modelu (`model.pkl`).
- `services/api/create_db.py` – zasilenie `offers.db`.

Samo API (`POST /predict/`) działa bez CSV, dopóki istnieje `services/ml/model.pkl`.
