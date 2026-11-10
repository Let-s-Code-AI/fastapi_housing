import os
import pickle
from functools import lru_cache
from pathlib import Path

import pandas as pd
from sklearn.linear_model import LinearRegression

# Ścieżki liczone względem pliku, a nie CWD
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model.pkl"
CSV_PATH = Path(os.environ.get(
    "HOUSING_CSV_PATH",
    BASE_DIR.parents[1] / "data" / "adresowo_wroclaw_all.csv",
))


# Kolumny wymagane do treningu oraz progi odrzucające nierealistyczne oferty
REQUIRED_COLUMNS = ("rooms", "area_m2", "price_total_zl")
AREA_MIN, AREA_MAX = 10, 500             # m², przedział otwarty
PRICE_MIN, PRICE_MAX = 100_000, 5_000_000  # PLN, przedział otwarty
ROOMS_MIN, ROOMS_MAX = 1, 10              # przedział domknięty


def clean_offers(df: pd.DataFrame, required=REQUIRED_COLUMNS) -> pd.DataFrame:
    """Wspólne czyszczenie ofert z CSV (trening modelu i import do bazy).

    Usuwa wiersze z brakami w kolumnach `required`, zamienia cenę zapisaną
    jako tekst ("800 000", "650,000") na liczbę i odfiltrowuje wartości
    spoza realistycznych przedziałów.
    """
    df_clean = df.dropna(subset=list(required)).copy()

    df_clean["price_total_zl"] = pd.to_numeric(
        df_clean["price_total_zl"].astype(str).str.replace(" ", "").str.replace(",", ""),
        errors="coerce",
    )
    df_clean = df_clean.dropna(subset=["price_total_zl"])

    return df_clean[
        (df_clean["area_m2"] > AREA_MIN)
        & (df_clean["area_m2"] < AREA_MAX)
        & (df_clean["price_total_zl"] > PRICE_MIN)
        & (df_clean["price_total_zl"] < PRICE_MAX)
        & (df_clean["rooms"] >= ROOMS_MIN)
        & (df_clean["rooms"] <= ROOMS_MAX)
    ]


def load_data(csv_path: Path = CSV_PATH):
    """Wczytaj CSV i oczyść dane do treningu (patrz `clean_offers`)."""
    csv_path = Path(csv_path)

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found at {csv_path}")

    return clean_offers(pd.read_csv(csv_path))


def train_model():
    """Train the linear regression model on real data and save it to pickle file"""
    # Load real data from CSV
    df = load_data()
    
    # Prepare features (X) and target (y)
    X = df[['area_m2', 'rooms']].values  # [area, rooms]
    y = df['price_total_zl'].values
    
    # Train the model
    model = LinearRegression().fit(X, y)
    
    # Calculate and print model performance
    score = model.score(X, y)
    print(f"Model R² score: {score:.4f}")
    print(f"Model coefficients: area_m2={model.coef_[0]:.2f}, rooms={model.coef_[1]:.2f}")
    print(f"Model intercept: {model.intercept_:.2f}")
    
    # Save model to pickle file
    model_path = MODEL_PATH
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    # Po retrainie kolejne predykcje mają użyć nowego modelu
    get_model.cache_clear()
    
    print(f"Model trained on {len(X)} samples and saved to {model_path}")
    return model


def load_model():
    """Load the trained model from pickle file"""
    model_path = MODEL_PATH
    if model_path.exists():
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        return model
    else:
        print("Model file not found. Training new model...")
        return train_model()


@lru_cache(maxsize=1)
def get_model():
    """Model wczytany raz na proces (cache); `get_model.cache_clear()` wymusza ponowne wczytanie."""
    return load_model()


def predict_price(area_m2: float, rooms: int):
    """Predict price using the trained model"""
    model = get_model()
    return model.predict([[area_m2, rooms]])[0]


def test_model():
    """Test the trained model with sample predictions"""
    # Test with some sample apartments
    test_cases = [
        (50, 2),   # 50 m², 2 rooms
        (70, 3),   # 70 m², 3 rooms  
        (30, 1),   # 30 m², 1 room
        (100, 4),  # 100 m², 4 rooms
    ]
    
    print("\n=== Model Predictions ===")
    for area, rooms in test_cases:
        predicted_price = predict_price(area, rooms)
        price_per_m2 = predicted_price / area
        print(f"Area: {area} m², Rooms: {rooms} → Price: {predicted_price:,.0f} PLN ({price_per_m2:,.0f} PLN/m²)")


# Train and save the model when this module is imported
if __name__ == "__main__":
    train_model()
    test_model()