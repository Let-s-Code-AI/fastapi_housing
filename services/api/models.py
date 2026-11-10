from sqlalchemy import Column, Integer, String, Float
from pydantic import BaseModel
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
    id: int
    locality: str
    rooms: int
    area_m2: float
    price_total_zl: int

    class Config:
        orm_mode = True


class OfferCreate(BaseModel):
    locality: str
    rooms: int
    area_m2: float


class PricePrediction(BaseModel):
    area_m2: float
    rooms: int