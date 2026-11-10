# FastAPI Housing Price Predictor

Projekt FastAPI do przewidywania cen mieszkań we Wrocławiu na podstawie powierzchni i liczby pokoi, wykorzystujący dane z portalu Adresowo.pl.

## Funkcjonalności

- 🏠 **API do przewidywania cen mieszkań** - na podstawie powierzchni i liczby pokoi
- 🤖 **Model Machine Learning** - Linear Regression wytrenowany na rzeczywistych danych z Wrocławia
- 📊 **Baza danych SQLite** - przechowuje dane o mieszkaniach
- 🔄 **Automatyczne trenowanie modelu** - model jest zapisywany w formacie pickle

## Wymagania

- Python 3.8+
- pip (Python package manager)

## Instalacja

1. **Sklonuj repozytorium:**
```bash
git clone <repository-url>
cd FastAPIProject
```

2. **Zainstaluj zależności:**
```bash
pip install -e .
```

3. **Utwórz bazę danych:**
```bash
python create_db.py
```

4. **Wytrenuj model ML:**
```bash
python ml.py
```

## Uruchomienie

1. **Uruchom serwer FastAPI:**
```bash
uvicorn main:app --reload
```

2. **Otwórz dokumentację API:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Struktura projektu

```
FastAPIProject/
├── data/
│   └── adresowo_wroclaw_all.csv    # Dane mieszkań z Wrocławia
├── main.py                         # Główny plik FastAPI
├── models.py                       # Modele SQLAlchemy i Pydantic
├── database.py                     # Konfiguracja bazy danych
├── ml.py                          # Model Machine Learning
├── create_db.py                   # Skrypt do tworzenia bazy danych
├── pyproject.toml                 # Konfiguracja projektu i zależności
├── offers.db                      # Baza danych SQLite (generowana)
├── model.pkl                      # Wytrenowany model ML (generowany)
└── README.md                      # Ten plik
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
1. Zmodyfikuj `ml.py` aby dodać nowe cechy
2. Zaktualizuj `models.py` jeśli potrzebne
3. Przetrenuj model: `python ml.py`

### Dodawanie nowych endpointów API:
1. Dodaj nowe funkcje w `main.py`
2. Zaktualizuj modele w `models.py` jeśli potrzebne
3. Przetestuj endpointy w Swagger UI

## Licencja

MIT License
