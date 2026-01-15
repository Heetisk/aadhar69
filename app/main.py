from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from dotenv import load_dotenv

load_dotenv()
from sqlalchemy.orm import Session
from . import models, database, schemas
from .services import ingestion, analytics, api_fetcher
from typing import List, Optional
from typing import List, Optional

import os

# Create DB tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Aadhar Hackathon API")

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...), 
    dataset_type: str = "enrolment",
    db: Session = Depends(database.get_db)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV.")
    
    content = await file.read()
    try:
        count = ingestion.process_csv_and_ingest(content, db, dataset_type=dataset_type)
        return {"message": f"Successfully processed {count} records."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sync-local")
def sync_local_data(
    dataset_type: str = "enrolment",
    db: Session = Depends(database.get_db)
):
    """
    Sync data from local CSV files in the dataset folder.
    """
    base_path = r"c:\Users\Heet\Desktop\dataset"
    if dataset_type == "enrolment":
        folder = "api_data_aadhar_enrolment"
    elif dataset_type == "demographic":
        folder = "api_data_aadhar_demographic"
    elif dataset_type == "biometric":
        folder = "api_data_aadhar_biometric"
    else:
        raise HTTPException(status_code=400, detail="Invalid dataset type")
        
    dir_path = os.path.join(base_path, folder)
    if not os.path.exists(dir_path):
        raise HTTPException(status_code=404, detail=f"Folder not found: {dir_path}")
        
    total_count = 0
    try:
        for filename in os.listdir(dir_path):
            if filename.endswith(".csv"):
                file_path = os.path.join(dir_path, filename)
                with open(file_path, "rb") as f:
                    content = f.read()
                    count = ingestion.process_csv_and_ingest(content, db, dataset_type=dataset_type)
                    total_count += count
        return {"message": f"Successfully synced {total_count} records from local {dataset_type} data."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sync-api")
def sync_from_api(
    limit: int = 100, 
    offset: int = 0, 
    state: str = None, 
    district: str = None, 
    fetch_all: bool = False,
    dataset_type: str = "enrolment", # Currently only enrolment supported via API resource ID
    db: Session = Depends(database.get_db)
):
    try:
        if dataset_type != "enrolment":
             raise HTTPException(status_code=400, detail="Only enrolment dataset is currently supported for API sync.")
             
        count = api_fetcher.fetch_and_sync_data(db, limit=limit, offset=offset, state=state, district=district, fetch_all=fetch_all)
        return {"message": f"Successfully synced {count} records from API."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/options/states")
def get_state_options(dataset_type: str = "enrolment", db: Session = Depends(database.get_db)):
    """Get list of available states"""
    return analytics.get_unique_states(db, dataset_type=dataset_type)

@app.get("/options/districts")
def get_district_options(state: Optional[str] = None, dataset_type: str = "enrolment", db: Session = Depends(database.get_db)):
    """Get list of available districts (optionally filtered by state)"""
    return analytics.get_unique_districts(db, state, dataset_type=dataset_type)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Aadhar Hackathon API"}

# Analytics Endpoints

@app.get("/summary")
@app.get("/summary")
def get_summary(state: Optional[str] = None, district: Optional[str] = None, dataset_type: str = "enrolment", db: Session = Depends(database.get_db)):
    return analytics.get_overall_summary(db, dataset_type=dataset_type, state=state, district=district)

@app.get("/trends/state")
def get_trends_state(state: Optional[str] = None, dataset_type: str = "enrolment", db: Session = Depends(database.get_db)):
    return analytics.get_trends_by_state(db, state, dataset_type=dataset_type)

@app.get("/trends/district")
def get_trends_district(district: Optional[str] = None, dataset_type: str = "enrolment", db: Session = Depends(database.get_db)):
    return analytics.get_trends_by_district(db, district, dataset_type=dataset_type)

@app.get("/age-comparison")
def get_age_comparison(state: Optional[str] = None, district: Optional[str] = None, dataset_type: str = "enrolment", db: Session = Depends(database.get_db)):
    return analytics.get_age_comparison(db, dataset_type=dataset_type, state=state, district=district)

@app.get("/anomalies")
def get_anomalies(state: Optional[str] = None, district: Optional[str] = None, dataset_type: str = "enrolment", db: Session = Depends(database.get_db)):
    return analytics.get_anomalies(db, dataset_type=dataset_type, state=state, district=district)

@app.delete("/clear-data")
def clear_all_data(dataset_type: str = "enrolment", db: Session = Depends(database.get_db)):
    """Clear all data of specified type from the database"""
    try:
        model, _ = analytics.get_model(dataset_type)
        count = db.query(model).delete()
        db.commit()
        return {"message": f"Successfully deleted {count} records from {dataset_type}."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
