# FastAPI Housing Price Predictor

Projekt FastAPI do przewidywania cen mieszkań we Wrocławiu na podstawie powierzchni i liczby pokoi, wykorzystujący dane z portalu Adresowo.pl.

## Funkcjonalności

- 🏠 **API do przewidywania cen mieszkań** - na podstawie powierzchni i liczby pokoi
- 🤖 **Model Machine Learning** - Linear Regression wytrenowany na rzeczywistych danych z Wrocławia
- 📊 **Baza danych SQLite** - przechowuje dane o mieszkaniach
- 🔄 **Automatyczne trenowanie modelu** - model jest zapisywany w formacie pickle

## Wymagania

- Python 3.9+
- [uv](https://docs.astral.sh/uv/)

## Instalacja

Repo to monorepo – **uv workspace** z dwoma serwisami i jednym środowiskiem (`.venv` + `uv.lock` w katalogu głównym).

1. **Sklonuj repozytorium i zainstaluj zależności:**
```bash
git clone <repository-url>
cd fastapi_housing
uv sync --all-packages
```

2. **Dostarcz dane CSV** – patrz [data/README.md](data/README.md).

3. **Utwórz bazę danych:**
```bash
uv run --directory services/api python create_db.py
```

4. **(Opcjonalnie) przetrenuj model ML** – `model.pkl` jest w repo:
```bash
uv run --directory services/ml python ml.py
```

## Uruchomienie

1. **Uruchom serwer FastAPI:**
```bash
uv run --directory services/api uvicorn main:app --reload
```

2. **Otwórz dokumentację API:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testy

```bash
uv run --directory services/ml pytest
uv run --directory services/api pytest
```

## Struktura projektu

```
fastapi_housing/
├── pyproject.toml                 # Root uv workspace (członkowie: services/*)
├── uv.lock                        # Wspólny lock zależności
├── data/
│   ├── README.md                  # Skąd wziąć CSV
│   └── adresowo_wroclaw_all.csv   # Dane (poza gitem)
└── services/
    ├── api/                       # Pakiet housing-api
    │   ├── main.py                # Aplikacja FastAPI
    │   ├── models.py              # Modele SQLAlchemy i Pydantic
    │   ├── database.py            # Konfiguracja bazy (offers.db obok pliku)
    │   ├── create_db.py           # Tworzenie i zasilanie bazy z CSV
    │   ├── curl_requests.sh       # Smoke-test endpointów
    │   └── tests/
    └── ml/                        # Pakiet housing-ml
        ├── ml.py                  # Ładowanie danych, trening, predict_price
        ├── ml_flow.py             # Trening śledzony w MLflow
        ├── model.pkl              # Wytrenowany model
        └── tests/
```

## API Endpoints

### Przewidywanie ceny mieszkania
```http
POST /predict
Content-Type: application/json

{
    "area_m2": 50.0,
    "rooms": 2
}
```

**Odpowiedź:**
```json
{
    "area_m2": 50.0,
    "rooms": 2,
    "predicted_price": 450000,
    "price_per_m2": 9000
}
```

### Pobieranie wszystkich ofert
```http
GET /offers
```

### Dodawanie nowej oferty
```http
POST /offers
Content-Type: application/json

{
    "locality": "Wrocław Śródmieście",
    "rooms": 3,
    "area_m2": 65.0
}
```

## Model Machine Learning

Model wykorzystuje **Linear Regression** do przewidywania cen mieszkań na podstawie:
- **Powierzchni** (area_m2)
- **Liczby pokoi** (rooms)

Model jest wytrenowany na rzeczywistych danych z portalu Adresowo.pl zawierających ponad 1500 ofert mieszkań z Wrocławia.

### Przykład użycia modelu:
```python
from ml import predict_price

# Przewidywanie ceny dla mieszkania 50m², 2 pokoje
price = predict_price(50.0, 2)
print(f"Przewidywana cena: {price:,.0f} PLN")
```

## Dane

Projekt wykorzystuje dane z portalu Adresowo.pl zawierające:
- Lokalizację mieszkania
- Liczbę pokoi
- Powierzchnię w m²
- Cenę całkowitą w PLN
- Dodatkowe informacje (opis, zdjęcia, etc.)

## Rozwój

### Dodawanie nowych funkcji ML:
1. Zmodyfikuj `services/ml/ml.py` aby dodać nowe cechy
2. Zaktualizuj `services/api/models.py` jeśli potrzebne
3. Przetrenuj model: `uv run --directory services/ml python ml.py`

### Dodawanie nowych endpointów API:
1. Dodaj nowe funkcje w `services/api/main.py`
2. Zaktualizuj modele w `services/api/models.py` jeśli potrzebne
3. Dodaj testy w `services/api/tests/` i przetestuj endpointy w Swagger UI

## Licencja

MIT License
