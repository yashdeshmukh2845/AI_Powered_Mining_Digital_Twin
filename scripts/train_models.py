import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from backend.app.ml.prospectivity_model import ProspectivityModel
from backend.app.ml.production_model import ProductionModel
from backend.app.database.db import SessionLocal
from backend.app.database.models import ProductionRecord

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DEMO_DIR = os.path.join(BASE_DIR, 'data', 'demo')

def train_all_models():
    print("Training Prospectivity Model...")
    pmodel = ProspectivityModel()
    geojson_path = os.path.join(DATA_DEMO_DIR, 'prospectivity_grid.geojson')
    p_metrics = pmodel.train_from_geojson(geojson_path, algorithm="RandomForest")
    print("Prospectivity Model Metrics:", p_metrics)
    
    print("\nTraining Production Forecasting Model...")
    db = SessionLocal()
    try:
        records = db.query(ProductionRecord).filter(ProductionRecord.mine_id == "MINE-001").all()
        if records:
            df = pd.DataFrame([{
                "date": r.date,
                "actual_production_tonnes": r.actual_production_tonnes,
                "operating_hours": r.operating_hours,
                "downtime_hours": r.downtime_hours,
                "equipment_availability_pct": r.equipment_availability_pct,
                "rainfall_mm": r.rainfall_mm,
                "blasting_delay_hours": r.blasting_delay_hours
            } for r in records])
            prod_model = ProductionModel()
            prod_metrics = prod_model.train(df, algorithm="RandomForest")
            print("Production Forecasting Model Metrics:", prod_metrics)
        else:
            print("No production records found to train model.")
    finally:
        db.close()
        
    print("\nModel training complete! Saved model artifacts to models/ directory.")

if __name__ == "__main__":
    train_all_models()
