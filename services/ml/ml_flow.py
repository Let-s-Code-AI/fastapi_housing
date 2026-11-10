import pickle

import mlflow
import mlflow.sklearn
from sklearn.linear_model import LinearRegression
from ml import MODEL_PATH, load_data

def train_model():
    """Train the linear regression model on real data, track with MLflow, and save it"""
    # Load real data from CSV
    df = load_data()
    
    # Prepare features (X) and target (y)
    X = df[['area_m2', 'rooms']].values
    y = df['price_total_zl'].values
    
    # Start MLflow run
    with mlflow.start_run():
        # Log parameters (np. feature names, liczba próbek)
        mlflow.log_param("features", ["area_m2", "rooms"])
        mlflow.log_param("num_samples", len(X))
        
        # Train the model
        model = LinearRegression().fit(X, y)
        
        # Calculate performance
        score = model.score(X, y)
        print(f"Model R² score: {score:.4f}")
        print(f"Model coefficients: area_m2={model.coef_[0]:.2f}, rooms={model.coef_[1]:.2f}")
        print(f"Model intercept: {model.intercept_:.2f}")
        
        # Log metrics
        mlflow.log_metric("r2", score)
        mlflow.log_metric("coef_area_m2", model.coef_[0])
        mlflow.log_metric("coef_rooms", model.coef_[1])
        mlflow.log_metric("intercept", model.intercept_)
        
        # Save model with MLflow
        mlflow.sklearn.log_model(model, "model")
        
        # (Opcjonalnie: nadal zapisujemy pickle lokalnie)
        model_path = MODEL_PATH
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
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


def predict_price(area_m2: float, rooms: int):
    """Predict price using the trained model"""
    model = load_model()
    return model.predict([[area_m2, rooms]])[0]


def test_model():
    """Test the trained model with sample predictions"""
    model = load_model()
    
    test_cases = [
        (50, 2),
        (70, 3),
        (30, 1),
        (100, 4),
    ]
    
    print("\n=== Model Predictions ===")
    for area, rooms in test_cases:
        predicted_price = predict_price(area, rooms)
        price_per_m2 = predicted_price / area
        print(f"Area: {area} m², Rooms: {rooms} → "
              f"Price: {predicted_price:,.0f} PLN "
              f"({price_per_m2:,.0f} PLN/m²)")


if __name__ == "__main__":
    train_model()
    test_model()
