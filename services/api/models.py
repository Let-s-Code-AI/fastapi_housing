from sqlalchemy import Column, Integer, String, Float
from pydantic import BaseModel, ConfigDict, Field
from database import Base


# SQLAlchemy model
class OfferDB(Base):
    __tablename__ = "offers"
    id = Column(Integer, primary_key=True, index=True)
    locality = Column(String, index=True)
    rooms = Column(Integer)
    area_m2 = Column(Float)
    price_total_zl = Column(Integer)


# Pydantic schemas
class Offer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    locality: str
    rooms: int
    area_m2: float
    price_total_zl: int


class OfferCreate(BaseModel):
    locality: str
    rooms: int = Field(ge=1, description="Liczba pokoi (co najmniej 1)")
    area_m2: float = Field(gt=0, description="Powierzchnia w m² (większa od 0)")


class PricePrediction(BaseModel):
    area_m2: float = Field(gt=0, description="Powierzchnia w m² (większa od 0)")
    rooms: int = Field(ge=1, description="Liczba pokoi (co najmniej 1)")


class OfferStats(BaseModel):
    locality: str
    offers_count: int
    median_price_zl: float
