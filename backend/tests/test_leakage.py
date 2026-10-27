import os
import sys
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.app.ml.production_forecast_engine import ProductionForecastEngine
from backend.app.database.models import ProductionRecord

def test_forecast_features_have_no_same_day_actuals():
    """
    STRICT AUTOMATED LEAKAGE TEST:
    Verifies that the forecast feature set contains ZERO post-event actual values.
    Features must only be forecast-time inputs or strictly shifted historical lags.
    """
    engine = ProductionForecastEngine()
    features = engine.feature_names
    
    # Forbidden contemporaneous actuals
    forbidden_features = [
        'actual_production_tonnes',
        'actual_downtime_hours',
        'downtime_hours', # unshifted
        'operating_hours', # unshifted actual
        'actual_equipment_availability_pct',
        'equipment_availability_pct' # unshifted
    ]
    
    for f in forbidden_features:
        assert f not in features, f"DATA LEAKAGE DETECTED: {f} is used as a forecast feature!"

def test_lag_features_are_strictly_prior_to_target_day():
    """
    Verifies that lag features at index t are strictly derived from index <= t-1.
    """
    records = []
    base_prod = 2200.0
    for d in range(30):
        r = ProductionRecord(
            id=f"P-{d}",
            mine_id="MINE-001",
            date=f"2025-05-{d+1:02d}",
            actual_production_tonnes=base_prod + (d * 15.0), # Distinct strictly monotonic values
            planned_target_tonnes=2500.0,
            operating_hours=14.0,
            downtime_hours=1.5,
            equipment_availability_pct=92.0,
            rainfall_mm=0.0,
            blasting_delay_hours=0.0,
            manpower=25
        )
        records.append(r)
        
    df_feat = ProductionForecastEngine.build_feature_table(records)
    
    # Check for each day t >= 1 that lag_1d_production strictly equals actual_production_tonnes of day t-1
    for t in range(1, len(df_feat)):
        actual_prev = df_feat.iloc[t-1]['actual_production_tonnes']
        lag1_curr = df_feat.iloc[t]['lag_1d_production']
        actual_curr = df_feat.iloc[t]['actual_production_tonnes']
        
        # lag1 MUST match previous day
        assert lag1_curr == actual_prev, f"Lag leakage: lag_1d ({lag1_curr}) != previous actual ({actual_prev})"
        # lag1 MUST NOT match current day
        assert lag1_curr != actual_curr, f"Same-day leakage: lag_1d matches current day actual ({actual_curr})"

def test_altering_current_day_actual_does_not_affect_current_day_features():
    """
    Verifies that changing day t's actual production has 0 impact on day t's predictive feature vector.
    """
    records = []
    for d in range(25):
        records.append(ProductionRecord(
            id=f"P-{d}",
            mine_id="MINE-001",
            date=f"2025-06-{d+1:02d}",
            actual_production_tonnes=2300.0,
            planned_target_tonnes=2500.0,
            operating_hours=15.0,
            downtime_hours=1.0,
            equipment_availability_pct=94.0,
            rainfall_mm=5.0,
            blasting_delay_hours=0.5,
            manpower=25
        ))
        
    df1 = ProductionForecastEngine.build_feature_table(records)
    feat_vector_orig = df1.iloc[10][ProductionForecastEngine().feature_names].to_dict()
    
    # Now simulate altered post-event actual on day 10
    records[10].actual_production_tonnes = 99999.0
    records[10].downtime_hours = 12.0
    records[10].operating_hours = 2.0
    
    df2 = ProductionForecastEngine.build_feature_table(records)
    feat_vector_new = df2.iloc[10][ProductionForecastEngine().feature_names].to_dict()
    
    assert feat_vector_orig == feat_vector_new, "Leakage: same-day post-event actual altered same-day forecast feature vector!"
