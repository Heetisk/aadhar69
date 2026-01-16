from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from .. import models
import pandas as pd

def get_model(dataset_type: str):
    if dataset_type == "enrolment":
        return models.EnrolmentData, [models.EnrolmentData.age_0_5, models.EnrolmentData.age_5_17, models.EnrolmentData.age_17_plus]
    elif dataset_type == "demographic":
        return models.DemographicUpdate, [models.DemographicUpdate.demo_age_5_17, models.DemographicUpdate.demo_age_17_plus]
    elif dataset_type == "biometric":
        return models.BiometricUpdate, [models.BiometricUpdate.bio_age_5_17, models.BiometricUpdate.bio_age_17_plus]
    else:
        raise ValueError(f"Invalid dataset type: {dataset_type}")

def get_overall_summary(db: Session, dataset_type: str = "enrolment", state: str = None, district: str = None):
    model, age_cols = get_model(dataset_type)
    
    # Create the aggregation list
    aggregations = [func.sum(col) for col in age_cols]
    
    # Base query for all age groups at once
    query = db.query(*aggregations)
    if state:
        query = query.filter(model.state == state)
    if district:
        query = query.filter(model.district == district)
        
    results = query.first() or [0] * len(age_cols)
    results = [r or 0 for r in results] # Handle None results from sum()
    
    total_sum = sum(results)
    
    summary = {
        "total_enrolments": total_sum,
        "top_state": "N/A"
    }
    
    if dataset_type == "enrolment":
        summary["total_0_5"] = results[0]
        summary["total_5_17"] = results[1]
        summary["total_17_plus"] = results[2]
    else:
        # Demographic and Biometric
        summary["total_0_5"] = 0
        summary["total_5_17"] = results[0]
        summary["total_17_plus"] = results[1]
        
    # Top location logic
    if state:
        if district:
            # If district is selected, it IS the top location
            summary["top_location"] = district
            summary["location_label"] = "Selected District"
        else:
            # If state is selected, show top district
            top_district_query = db.query(
                model.district,
                func.sum(total_val).label("total")
            ).filter(model.state == state)
            
            top_district = top_district_query.group_by(model.district).order_by(desc("total")).first()
            summary["top_location"] = top_district[0] if top_district else "N/A"
            summary["location_label"] = "Top District"
    else:
        top_state_query = db.query(
            model.state,
            func.sum(total_val).label("total")
        )
        top_state = top_state_query.group_by(model.state).order_by(desc("total")).first()
        summary["top_location"] = top_state[0] if top_state else "N/A"
        summary["location_label"] = "Top State"
    
    return summary

def get_trends_by_state(db: Session, state: str = None, dataset_type: str = "enrolment", limit: int = 500):
    model, age_cols = get_model(dataset_type)
    total_val = sum(age_cols)
    
    query = db.query(
        model.date,
        model.state,
        func.sum(total_val).label("count")
    )
    if state:
        query = query.filter(model.state == state)
        
    results = query.group_by(model.date, model.state).order_by(desc(model.date)).limit(limit).all()
    return [{"date": r.date, "state": r.state, "enrolments": r.count} for r in results]

def get_trends_by_district(db: Session, district: str = None, dataset_type: str = "enrolment", limit: int = 500):
    model, age_cols = get_model(dataset_type)
    total_val = sum(age_cols)
    
    query = db.query(
        model.date,
        model.district,
        func.sum(total_val).label("count")
    )
    if district:
        query = query.filter(model.district == district)
        
    results = query.group_by(model.date, model.district).order_by(desc(model.date)).limit(limit).all()
    return [{"date": r.date, "district": r.district, "enrolments": r.count} for r in results]

def get_age_comparison(db: Session, dataset_type: str = "enrolment", state: str = None, district: str = None):
    model, age_cols = get_model(dataset_type)
    
    def get_filtered_sum(col):
        q = db.query(func.sum(col))
        if state:
            q = q.filter(model.state == state)
        if district:
            q = q.filter(model.district == district)
        return q.scalar() or 0
    
    if dataset_type == "enrolment":
        return {
            "age_0_5": get_filtered_sum(model.age_0_5),
            "age_5_17": get_filtered_sum(model.age_5_17),
            "age_17_plus": get_filtered_sum(model.age_17_plus)
        }
    else:
        # Demographic and Biometric only have 5-17 and 17+
        prefix = "demo" if dataset_type == "demographic" else "bio"
        return {
            "age_0_5": 0,
            "age_5_17": get_filtered_sum(getattr(model, f"{prefix}_age_5_17")),
            "age_17_plus": get_filtered_sum(getattr(model, f"{prefix}_age_17_plus"))
        }

def get_anomalies(db: Session, threshold: int = 10, dataset_type: str = "enrolment", state: str = None, district: str = None, limit: int = 100):
    model, age_cols = get_model(dataset_type)
    total_val = sum(age_cols)
    
    query = db.query(
        model.date,
        model.district,
        total_val.label("total")
    )
    
    # Apply filters
    if state:
        query = query.filter(model.state == state)
    if district:
        query = query.filter(model.district == district)
        
    results = query.filter(
        total_val < threshold
    ).order_by(desc(model.date)).limit(limit).all()
    
    return [{"date": r.date, "district": r.district, "total_enrolment": r.total, "type": "Low Activity"} for r in results]

def get_unique_states(db: Session, dataset_type: str = "enrolment"):
    model, _ = get_model(dataset_type)
    results = db.query(model.state).distinct().filter(model.state != None).order_by(model.state).all()
    return [r[0] for r in results]

def get_unique_districts(db: Session, state: str = None, dataset_type: str = "enrolment"):
    model, _ = get_model(dataset_type)
    query = db.query(model.district).distinct().filter(model.district != None)
    if state:
        query = query.filter(model.state == state)
    results = query.order_by(model.district).all()
    return [r[0] for r in results]
