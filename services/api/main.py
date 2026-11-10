from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List

import models
from database import engine, SessionLocal
from ml import get_model, predict_price

# Utwórz tabele
models.Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Wczytaj model ML raz przy starcie – brak model.pkl wyjdzie od razu, nie w pierwszym requeście
    get_model()
    yield


app = FastAPI(title="Housing API", lifespan=lifespan)

# Dependency – sesja DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Root
def root():
    return {"message": "API do mieszkań we Wrocławiu"}

# Dodawanie oferty
def create_offer(offer: models.OfferCreate, db: Session = Depends(get_db)):
    # Przewiduj cenę używając modelu ML
    predicted_price = predict_price(offer.area_m2, offer.rooms)
    
    # Utwórz obiekt bazy danych z przewidywaną ceną
    db_offer = models.OfferDB(
        locality=offer.locality,
        rooms=offer.rooms,
        area_m2=offer.area_m2,
        price_total_zl=int(predicted_price)
    )
    db.add(db_offer)
    db.commit()
    db.refresh(db_offer)
    return db_offer

# Pobieranie wszystkich ofert
def read_offers(db: Session = Depends(get_db)):
    return db.query(models.OfferDB).all()

# Wyszukiwanie ofert
def search_offers(
    locality: Optional[str] = Query(None, description="Nazwa miejscowości (częściowe dopasowanie)"),
    rooms_min: Optional[int] = Query(None, ge=1, description="Minimalna liczba pokoi"),
    rooms_max: Optional[int] = Query(None, ge=1, description="Maksymalna liczba pokoi"),
    area_min: Optional[float] = Query(None, gt=0, description="Minimalna powierzchnia (m²)"),
    area_max: Optional[float] = Query(None, gt=0, description="Maksymalna powierzchnia (m²)"),
    price_min: Optional[int] = Query(None, ge=0, description="Minimalna cena (zł)"),
    price_max: Optional[int] = Query(None, ge=0, description="Maksymalna cena (zł)"),
    limit: int = Query(50, ge=1, le=500, description="Maksymalna liczba wyników"),
    db: Session = Depends(get_db),
):
    filters = []
    if locality:
        filters.append(models.OfferDB.locality.ilike(f"%{locality}%"))
    if rooms_min is not None:
        filters.append(models.OfferDB.rooms >= rooms_min)
    if rooms_max is not None:
        filters.append(models.OfferDB.rooms <= rooms_max)
    if area_min is not None:
        filters.append(models.OfferDB.area_m2 >= area_min)
    if area_max is not None:
        filters.append(models.OfferDB.area_m2 <= area_max)
    if price_min is not None:
        filters.append(models.OfferDB.price_total_zl >= price_min)
    if price_max is not None:
        filters.append(models.OfferDB.price_total_zl <= price_max)

    return db.query(models.OfferDB).filter(and_(*filters)).limit(limit).all()


# Predykcja ceny
def predict(offer: models.PricePrediction):
    predicted_price = predict_price(offer.area_m2, offer.rooms)
    price_per_m2 = predicted_price / offer.area_m2
    return {
        "area_m2": offer.area_m2,
        "rooms": offer.rooms,
        "predicted_price": round(predicted_price, 2),
        "price_per_m2": round(price_per_m2, 2)
    }


# Rejestracja tras bez dekoratorów – mutmut 3 pomija funkcje z dekoratorami,
# więc dzięki add_api_route endpointy podlegają testom mutacyjnym.
app.add_api_route("/", root, methods=["GET"])
app.add_api_route("/offers/", create_offer, methods=["POST"], response_model=models.Offer)
app.add_api_route("/offers/", read_offers, methods=["GET"], response_model=List[models.Offer])
app.add_api_route("/offers/search", search_offers, methods=["GET"], response_model=List[models.Offer])
app.add_api_route("/predict/", predict, methods=["POST"])
