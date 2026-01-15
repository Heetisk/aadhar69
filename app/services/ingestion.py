import pandas as pd
from sqlalchemy.orm import Session
from .. import models
from datetime import datetime
import io

def process_csv_and_ingest(file_content: bytes, db: Session, dataset_type: str = "enrolment"):
    try:
        # Read CSV
        df = pd.read_csv(io.BytesIO(file_content))
        
        # Standardize column names (stripping spaces, lowercase)
        df.columns = df.columns.str.strip()
        
        # Mapping CSV columns to DB columns
        column_map = {
            "date": "date",
            "state": "state",
            "district": "district",
            "pincode": "pincode",
            # Enrolment
            "age_0_5": "age_0_5",
            "age_5_17": "age_5_17",
            "age_18_greater": "age_17_plus",
            # Demographic
            "demo_age_5_17": "demo_age_5_17",
            "demo_age_17_": "demo_age_17_plus",
            # Biometric
            "bio_age_5_17": "bio_age_5_17",
            "bio_age_17_": "bio_age_17_plus"
        }
        
        df = df.rename(columns=column_map)
        
        # Drop rows where critical fields are null
        df = df.dropna(subset=['date', 'state', 'district'])
        
        # Determine model and numeric columns based on dataset_type
        if dataset_type == "enrolment":
            model = models.EnrolmentData
            numeric_cols = ['age_0_5', 'age_5_17', 'age_17_plus']
        elif dataset_type == "demographic":
            model = models.DemographicUpdate
            numeric_cols = ['demo_age_5_17', 'demo_age_17_plus']
        elif dataset_type == "biometric":
            model = models.BiometricUpdate
            numeric_cols = ['bio_age_5_17', 'bio_age_17_plus']
        else:
            raise ValueError(f"Invalid dataset type: {dataset_type}")
            
        # Fill numeric nulls with 0
        for col in numeric_cols:
            if col not in df.columns:
                df[col] = 0
            df[col] = df[col].fillna(0)
        
        # Date parsing
        df['date'] = pd.to_datetime(df['date'], errors='coerce', dayfirst=True)
        df = df.dropna(subset=['date']) 
        
        # Convert to dictionary records
        records = df.to_dict(orient='records')
        
        # Bulk Insert
        db.bulk_insert_mappings(model, records)
        db.commit()
        
        return len(records)
        
    except Exception as e:
        db.rollback()
        raise e
