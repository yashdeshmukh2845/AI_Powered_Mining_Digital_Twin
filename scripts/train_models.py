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
    print("=== STARTING REPRODUCIBLE MODEL TRAINING ON INTEGRATED DATASETS ===")
    
    # 1. Production Forecasting Model
    print("\n1. Training Production Forecasting Model (Chronological Split on Downloaded Production Data)...")
    db = SessionLocal()
    try:
        records = db.query(ProductionRecord).order_by(ProductionRecord.date.asc()).all()
        if records:
            df = pd.DataFrame([{
                "date": r.date,
                "actual_production_tonnes": r.actual_production_tonnes,
                "operating_hours": r.operating_hours,
                "downtime_hours": r.downtime_hours,
                "equipment_availability_pct": r.equipment_availability_pct,
                "rainfall_mm": r.rainfall_mm,
                "blasting_delay_hours": r.blasting_delay_hours,
                "manpower": r.manpower if r.manpower else 25,
                "energy_consumption_kwh": r.energy_consumption_kwh if r.energy_consumption_kwh else 2500.0,
                "is_synthetic": r.is_synthetic
            } for r in records])
            
            prod_model = ProductionModel()
            prod_metrics = prod_model.train(df, algorithm="RandomForest")
            print("  Production Forecasting Model Metrics:")
            for k, v in prod_metrics.items():
                print(f"    {k}: {v}")

            # Also train Quantile Regressors (P10, P50, P90)
            from backend.app.ml.production_forecast_engine import ProductionForecastEngine
            df_feat = ProductionForecastEngine.build_feature_table(records)
            q_engine = ProductionForecastEngine()
            q_metrics = q_engine.train_models(df_feat)
            print("  Quantile Uncertainty Model (P10/P50/P90) Metrics:")
            for k, v in q_metrics.items():
                print(f"    {k}: {v}")
        else:
            print("  No production records found in database.")
    finally:

        db.close()
        
    # 2. Equipment Failure Risk Model (Calibrated Time-Series Classifier)
    print("\n2. Training Equipment Failure & Breakdown Risk Model (24h/48h/72h Horizons)...")
    db_eq = SessionLocal()
    try:
        from backend.app.ml.equipment_failure_model import EquipmentFailureModel
        eq_model = EquipmentFailureModel()
        eq_metrics = eq_model.train(db_eq)
        print("  Equipment Failure Risk Model Metrics:")
        for k, v in eq_metrics.items():
            print(f"    {k}: {v}")
    except Exception as e:
        print(f"  Equipment model training notice: {e}")
    finally:
        db_eq.close()

        
    # 3. Prospectivity Exploration Model
    print("\n3. Training Geological Prospectivity Model...")
    pmodel = ProspectivityModel()
    geojson_path = os.path.join(DATA_DEMO_DIR, 'prospectivity_grid.geojson')
    if os.path.exists(geojson_path):
        p_metrics = pmodel.train_from_geojson(geojson_path, algorithm="RandomForest")
        print("  Prospectivity Model Metrics:", p_metrics)
    else:
        print("  No prospectivity grid GeoJSON found.")
        
    print("\n=== Model training complete! Artifacts persisted in models/ directory. ===")

if __name__ == "__main__":
    train_all_models()
