from database import engine, Base, SessionLocal
from models import OfferDB
import pandas as pd
from ml import CSV_PATH, REQUIRED_COLUMNS, clean_offers

def create_database():
    """Create database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

def populate_database():
    """Populate database with data from CSV file"""
    db = SessionLocal()
    
    try:
        # Load CSV data
        csv_path = CSV_PATH
        if not csv_path.exists():
            print(f"CSV file not found at {csv_path}")
            return
        
        print("Loading data from CSV...")
        # Wspólne czyszczenie z ml; do bazy dodatkowo wymagamy locality
        df_clean = clean_offers(pd.read_csv(csv_path), required=(*REQUIRED_COLUMNS, "locality"))
        
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
