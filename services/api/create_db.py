from database import engine, Base
from models import OfferDB
import pandas as pd
from pathlib import Path

def create_database():
    """Create database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

def populate_database():
    """Populate database with data from CSV file"""
    from sqlalchemy.orm import sessionmaker
    from database import engine
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Load CSV data
        csv_path = Path("data/adresowo_wroclaw_all.csv")
        if not csv_path.exists():
            print(f"CSV file not found at {csv_path}")
            return
        
        print("Loading data from CSV...")
        df = pd.read_csv(csv_path)
        
        # Clean the data
        df_clean = df.dropna(subset=['rooms', 'area_m2', 'price_total_zl', 'locality'])
        
        # Convert price from string to numeric
        df_clean['price_total_zl'] = df_clean['price_total_zl'].astype(str).str.replace(' ', '').str.replace(',', '')
        df_clean['price_total_zl'] = pd.to_numeric(df_clean['price_total_zl'], errors='coerce')
        df_clean = df_clean.dropna(subset=['price_total_zl'])
        
        # Filter realistic values
        df_clean = df_clean[
            (df_clean['area_m2'] > 10) &
            (df_clean['area_m2'] < 500) &
            (df_clean['price_total_zl'] > 100000) &
            (df_clean['price_total_zl'] < 5000000) &
            (df_clean['rooms'] > 0) &
            (df_clean['rooms'] <= 10)
        ]
        
        print(f"Processing {len(df_clean)} apartments...")
        
        # Insert data into database
        for index, row in df_clean.iterrows():
            offer = OfferDB(
                locality=row['locality'],
                rooms=int(row['rooms']),
                area_m2=float(row['area_m2']),
                price_total_zl=int(row['price_total_zl'])
            )
            db.add(offer)
        
        db.commit()
        print(f"Successfully inserted {len(df_clean)} apartments into database!")
        
    except Exception as e:
        print(f"Error populating database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_database()
    populate_database()
