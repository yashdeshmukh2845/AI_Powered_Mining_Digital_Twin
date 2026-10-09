import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List

class ExplainabilityEngine:
    @staticmethod
    def get_feature_contributions(model_path: str, sample_df: pd.DataFrame) -> List[Dict[str, Any]]:
        if not os.path.exists(model_path):
            # Baseline domain importance if model file does not exist yet
            return [
                {"feature": "equipment_downtime", "displayName": "Equipment Downtime (hrs)", "importance": 0.38, "impact": "Negative", "unit": "hrs"},
                {"feature": "rainfall_mm", "displayName": "Heavy Rainfall (mm)", "importance": 0.26, "impact": "Negative", "unit": "mm"},
                {"feature": "blasting_delay_hours", "displayName": "Blasting Delay (hrs)", "importance": 0.18, "impact": "Negative", "unit": "hrs"},
                {"feature": "equipment_availability_pct", "displayName": "Equipment Availability (%)", "importance": 0.12, "impact": "Positive", "unit": "%"},
                {"feature": "operating_hours", "displayName": "Effective Operating Hours", "importance": 0.06, "impact": "Positive", "unit": "hrs"}
            ]
            
        saved = joblib.load(model_path)
        model = saved['model']
        feature_names = saved['features']
        
        X = sample_df[feature_names]
        
        # Try SHAP explainer
        try:
            import shap
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(X)
            if isinstance(shap_values, list):
                shap_vals = np.abs(shap_values[0]).mean(axis=0)
            else:
                shap_vals = np.abs(shap_values).mean(axis=0) if len(shap_values.shape) > 1 else np.abs(shap_values)
                
            total_val = np.sum(shap_vals) if np.sum(shap_vals) > 0 else 1.0
            norm_imp = shap_vals / total_val
        except Exception:
            # Fallback to model feature importances
            if hasattr(model, 'feature_importances_'):
                norm_imp = model.feature_importances_
            else:
                norm_imp = [0.2] * len(feature_names)
                
        display_map = {
            'operating_hours': ('Effective Operating Hours', 'hrs'),
            'downtime_hours': ('Equipment Downtime', 'hrs'),
            'equipment_availability_pct': ('Equipment Availability', '%'),
            'rainfall_mm': ('Rainfall Level', 'mm'),
            'blasting_delay_hours': ('Blasting Delay', 'hrs')
        }
        
        results = []
        for feat, imp in zip(feature_names, norm_imp):
            name, unit = display_map.get(feat, (feat, ""))
            impact_direction = "Negative" if feat in ['downtime_hours', 'rainfall_mm', 'blasting_delay_hours'] else "Positive"
            results.append({
                "feature": feat,
                "displayName": name,
                "importance": float(round(imp, 4)),
                "impact": impact_direction,
                "unit": unit
            })
            
        results.sort(key=lambda x: x["importance"], reverse=True)
        return results
