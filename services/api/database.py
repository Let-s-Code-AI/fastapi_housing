import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Domyślnie offers.db obok tego pliku; DATABASE_URL pozwala podmienić bazę (np. w testach)
SQLALCHEMY_DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    f"sqlite:///{Path(__file__).resolve().parent / 'offers.db'}",
)

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()