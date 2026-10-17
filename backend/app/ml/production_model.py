import os
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
MODEL_DIR = os.path.join(BASE_DIR, 'models')
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_DIR, 'production_model.joblib')

class ProductionModel:
    def __init__(self):
        self.model = None
        self.feature_names = [
            'operating_hours', 'downtime_hours', 'equipment_availability_pct',
            'rainfall_mm', 'blasting_delay_hours', 'manpower', 'energy_consumption_kwh'
        ]
        self.metrics = {}
        self.algorithm = "RandomForestRegressor"
        
    def train(self, df_prod: pd.DataFrame, algorithm: str = "RandomForest") -> Dict[str, Any]:
        df = df_prod.sort_values("date").copy()
        
        # Ensure all required features exist in df with reasonable defaults
        for f in self.feature_names:
            if f not in df.columns:
                if f == 'manpower':
                    df[f] = 25
                elif f == 'energy_consumption_kwh':
                    df[f] = 2500.0
                elif f == 'blasting_delay_hours':
                    df[f] = 0.0
                elif f == 'rainfall_mm':
                    df[f] = 0.0
                elif f == 'operating_hours':
                    df[f] = 8.0 - df.get('downtime_hours', 0.0)
                elif f == 'equipment_availability_pct':
                    df[f] = 90.0
                else:
                    df[f] = 0.0
                    
        X = df[self.feature_names].fillna(0.0)
        y = df['actual_production_tonnes']
        
        # Chronological time-aware split (80% train, 20% test) to prevent future data leakage
        split_idx = int(len(df) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        # Calculate naive baseline (mean of training targets / moving average)
        baseline_pred = np.full(shape=len(y_test), fill_value=y_train.mean())
        base_mae = float(round(mean_absolute_error(y_test, baseline_pred), 2))
        base_rmse = float(round(np.sqrt(mean_squared_error(y_test, baseline_pred)), 2))
        base_wape = float(round(np.sum(np.abs(y_test - baseline_pred)) / np.sum(y_test) * 100.0, 2)) if np.sum(y_test) > 0 else 0.0
        
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
        
        improvement_pct = round(((base_mae - mae) / base_mae * 100.0), 1) if base_mae > 0 else 0.0
        
        train_start = str(df.iloc[0]['date'])
        train_end = str(df.iloc[split_idx-1]['date'])
        test_start = str(df.iloc[split_idx]['date'])
        test_end = str(df.iloc[-1]['date'])
        
        self.metrics = {
            "mae": mae,
            "rmse": rmse,
            "wape_pct": wape,
            "baseline_mae": base_mae,
            "baseline_rmse": base_rmse,
            "baseline_wape_pct": base_wape,
            "improvement_over_baseline_pct": improvement_pct,
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "train_period": f"{train_start} to {train_end}",
            "test_period": f"{test_start} to {test_end}",
            "evaluation_method": "Chronological Out-of-Time Validation Split (No future data leakage)",
            "is_synthetic_experiment": bool(df.get('is_synthetic', pd.Series([False])).any())
        }
        
        joblib.dump({
            'model': self.model,
            'metrics': self.metrics,
            'features': self.feature_names,
            'algorithm': self.algorithm,
            'updated_at': datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        }, MODEL_PATH)
        
        return self.metrics

    def predict(self, input_features: pd.DataFrame) -> np.ndarray:
        if self.model is None and os.path.exists(MODEL_PATH):
            saved = joblib.load(MODEL_PATH)
            self.model = saved['model']
            self.metrics = saved.get('metrics', {})
            self.algorithm = saved.get('algorithm', 'RandomForestRegressor')
            self.feature_names = saved.get('features', self.feature_names)
            
        # Ensure input_features has all required features
        input_copy = input_features.copy()
        for f in self.feature_names:
            if f not in input_copy.columns:
                if f == 'manpower':
                    input_copy[f] = 25
                elif f == 'energy_consumption_kwh':
                    input_copy[f] = 2500.0
                elif f == 'blasting_delay_hours':
                    input_copy[f] = 0.0
                elif f == 'rainfall_mm':
                    input_copy[f] = 0.0
                elif f == 'operating_hours':
                    input_copy[f] = 8.0 - input_copy.get('downtime_hours', 0.0)
                elif f == 'equipment_availability_pct':
                    input_copy[f] = 90.0
                else:
                    input_copy[f] = 0.0
                    
        if self.model is None:
            # Deterministic engineering capacity baseline if model not trained yet
            op_hrs = input_copy['operating_hours'] if 'operating_hours' in input_copy else 16.0
            avail = input_copy['equipment_availability_pct'] if 'equipment_availability_pct' in input_copy else 90.0
            return np.round((op_hrs * 155.0 * (avail / 100.0)).values, 1)
            
        X = input_copy[self.feature_names].fillna(0.0)
        preds = self.model.predict(X)
        return np.round(preds, 1)

    @staticmethod
    def calculate_shortfall_risk(target_tonnes: float, forecast_tonnes: float, low_thresh: float = 5.0, med_thresh: float = 10.0) -> dict:
        shortfall_tonnes = max(0.0, target_tonnes - forecast_tonnes) if target_tonnes > 0 else 0.0
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
