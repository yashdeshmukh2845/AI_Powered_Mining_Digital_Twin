import os
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
MODEL_DIR = os.path.join(BASE_DIR, 'models')
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_DIR, 'production_model.joblib')

class ProductionModel:
    def __init__(self):
        self.model = None
        self.feature_names = ['operating_hours', 'downtime_hours', 'equipment_availability_pct', 'rainfall_mm', 'blasting_delay_hours']
        self.metrics = {}
        self.algorithm = "RandomForestRegressor"
        
    def train(self, df_prod: pd.DataFrame, algorithm: str = "RandomForest"):
        df = df_prod.sort_values("date").copy()
        
        X = df[self.feature_names]
        y = df['actual_production_tonnes']
        
        # Time-aware split (80% past train, 20% recent test) - NO random shuffling
        split_idx = int(len(df) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        if algorithm == "XGBoost":
            try:
                from xgboost import XGBRegressor
                self.model = XGBRegressor(n_estimators=100, max_depth=5, random_state=42)
                self.algorithm = "XGBoost"
            except ImportError:
                self.model = RandomForestRegressor(n_estimators=100, max_depth=6, random_state=42)
                self.algorithm = "RandomForestRegressor (Fallback)"
        else:
            self.model = RandomForestRegressor(n_estimators=100, max_depth=6, random_state=42)
            self.algorithm = "RandomForestRegressor"
            
        self.model.fit(X_train, y_train)
        
        preds = self.model.predict(X_test)
        mae = float(round(mean_absolute_error(y_test, preds), 2))
        rmse = float(round(np.sqrt(mean_squared_error(y_test, preds)), 2))
        wape = float(round(np.sum(np.abs(y_test - preds)) / np.sum(y_test) * 100.0, 2)) if np.sum(y_test) > 0 else 0.0
        
        self.metrics = {
            "mae": mae,
            "rmse": rmse,
            "wape_pct": wape,
            "train_samples": len(X_train),
            "test_samples": len(X_test)
        }
        
        joblib.dump({'model': self.model, 'metrics': self.metrics, 'features': self.feature_names, 'algorithm': self.algorithm}, MODEL_PATH)
        return self.metrics

    def predict(self, input_features: pd.DataFrame) -> np.ndarray:
        if self.model is None and os.path.exists(MODEL_PATH):
            saved = joblib.load(MODEL_PATH)
            self.model = saved['model']
            self.metrics = saved.get('metrics', {})
            self.algorithm = saved.get('algorithm', 'RandomForestRegressor')
            
        if self.model is None:
            # Deterministic capacity baseline fallback if not trained yet
            op_hrs = input_features['operating_hours'] if 'operating_hours' in input_features else 16.0
            avail = input_features['equipment_availability_pct'] if 'equipment_availability_pct' in input_features else 90.0
            return (op_hrs * 155.0 * (avail / 100.0)).values
            
        X = input_features[self.feature_names]
        preds = self.model.predict(X)
        return np.round(preds, 1)

    @staticmethod
    def calculate_shortfall_risk(target_tonnes: float, forecast_tonnes: float, low_thresh: float = 5.0, med_thresh: float = 10.0) -> dict:
        shortfall_tonnes = max(0.0, target_tonnes - forecast_tonnes)
        shortfall_pct = (100.0 * shortfall_tonnes / target_tonnes) if target_tonnes > 0 else 0.0
        
        if shortfall_pct >= med_thresh:
            risk_category = "High"
        elif shortfall_pct >= low_thresh:
            risk_category = "Medium"
        else:
            risk_category = "Low"
            
        return {
            "target_tonnes": round(target_tonnes, 1),
            "forecast_tonnes": round(forecast_tonnes, 1),
            "shortfall_tonnes": round(shortfall_tonnes, 1),
            "shortfall_pct": round(shortfall_pct, 2),
            "risk_category": risk_category
        }
