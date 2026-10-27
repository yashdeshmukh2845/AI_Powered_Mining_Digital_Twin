import os
import json
import math
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score, recall_score, f1_score
from backend.app.core.config import settings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
MODEL_DIR = os.path.join(BASE_DIR, 'models')
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_DIR, 'prospectivity_model.joblib')

class SurfaceExplorationPriorityModel:
    """
    Surface Exploration Priority Model.
    
    NON-NEGOTIABLE DESIGN RULE (The Subsurface Trap):
    This model ranks exploration grid cells to guide WHERE TO DRILL NEXT based on:
    1. Proximity to regional geological structural lineaments / faults.
    2. Drill coverage gaps (distance from existing drilled boreholes).
    3. Surface environmental accessibility (slope, vegetation buffer).
    
    CRITICAL DISCLAIMER:
    Guides where to drill next. Does not indicate ore at depth.
    Subsurface manganese reserve estimation must be derived from drillhole cores and assays only.
    """

    def __init__(self):
        self.model = None
        self.feature_names = ['dist_to_fault_km', 'drill_coverage_gap_m', 'accessibility_score']
        self.metrics = {}
        self.algorithm = "MultiCriteriaExplorationRanking"
        self.disclaimer = settings.SURFACE_MAP_DISCLAIMER

    @staticmethod
    def calculate_drill_coverage_gap(grid_lat: float, grid_lon: float, boreholes: List[Dict[str, float]]) -> float:
        """Calculates distance in meters to nearest existing exploratory borehole."""
        if not boreholes:
            return 500.0  # Default maximum gap if no boreholes present
        
        min_dist_m = float('inf')
        cos_lat = math.cos(math.radians(grid_lat))
        for b in boreholes:
            blat = b.get('latitude', b.get('lat', grid_lat))
            blon = b.get('longitude', b.get('lon', grid_lon))
            dx = (grid_lon - blon) * 111320.0 * cos_lat
            dy = (grid_lat - blat) * 110540.0
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < min_dist_m:
                min_dist_m = dist
        return round(min_dist_m, 1)

    def compute_priority_scores(self, features_df: pd.DataFrame, boreholes: List[Dict[str, float]] = None) -> pd.DataFrame:
        """
        Computes drill prioritization score combining structural lineament proximity
        and drill coverage information gap.
        """
        df = features_df.copy()
        
        # Calculate coverage gap if not provided
        if 'drill_coverage_gap_m' not in df.columns:
            if boreholes:
                gaps = [
                    self.calculate_drill_coverage_gap(row.get('center_lat', 21.534), row.get('center_lon', 79.691), boreholes)
                    for _, row in df.iterrows()
                ]
                df['drill_coverage_gap_m'] = gaps
            else:
                df['drill_coverage_gap_m'] = 250.0

        # Structural factor: closer to regional strike fault is more prospective for hosting host-rock contact
        fault_dist = df.get('dist_to_fault_km', pd.Series([1.0] * len(df)))
        struct_score = np.clip(1.0 - (fault_dist / 2.5), 0.05, 0.98)
        
        # Drill gap factor: larger gap means higher exploratory information gain
        gap_score = np.clip(df['drill_coverage_gap_m'] / 400.0, 0.1, 1.0)
        
        # Surface exploration priority score (0.0 to 1.0)
        priority_scores = np.round(0.55 * struct_score + 0.45 * gap_score, 3)
        df['exploration_priority_score'] = priority_scores
        
        # Drill gap category
        def categorize_gap(g):
            if g > 300.0:
                return "High Gap (>300m - Priority Info Gain)"
            elif g > 150.0:
                return "Moderate Gap (150-300m)"
            else:
                return "Well Drilled (<150m)"
                
        df['drill_gap_category'] = df['drill_coverage_gap_m'].apply(categorize_gap)
        
        # Overall exploration priority category
        def categorize_priority(s):
            if s >= 0.70:
                return "High Priority Drilling"
            elif s >= 0.45:
                return "Medium Priority"
            elif s >= 0.25:
                return "Low Priority"
            else:
                return "Adequately Explored"
                
        df['exploration_priority_category'] = df['exploration_priority_score'].apply(categorize_priority)
        return df

    def train_from_geojson(self, geojson_path: str, algorithm: str = "RandomForest"):
        """Maintains backward compatibility with training endpoint while enforcing honest exploration ranking."""
        with open(geojson_path, 'r') as f:
            data = json.load(f)
            
        records = []
        for feat in data['features']:
            props = feat['properties']
            records.append({
                'dist_to_fault_km': props.get('dist_to_fault_km', 0.5),
                'drill_coverage_gap_m': props.get('drill_coverage_gap_m', 220.0),
                'accessibility_score': props.get('accessibility_score', 0.8),
                'target': 1 if props.get('exploration_priority_score', 0.5) >= 0.65 else 0
            })
            
        df = pd.DataFrame(records)
        X = df[['dist_to_fault_km', 'drill_coverage_gap_m', 'accessibility_score']]
        y = df['target']
        
        clf = RandomForestClassifier(n_estimators=50, max_depth=4, random_state=42)
        clf.fit(X, y)
        preds = clf.predict(X)
        
        self.model = clf
        self.algorithm = "RandomForest (Drill Prioritization)"
        self.metrics = {
            "precision": float(round(precision_score(y, preds, zero_division=0), 4)),
            "recall": float(round(recall_score(y, preds, zero_division=0), 4)),
            "f1_score": float(round(f1_score(y, preds, zero_division=0), 4)),
            "ranking_methodology": "Structural proximity + Drillhole coverage gap spacing",
            "disclaimer": self.disclaimer
        }
        
        joblib.dump({
            'model': self.model,
            'metrics': self.metrics,
            'features': self.feature_names,
            'algorithm': self.algorithm,
            'disclaimer': self.disclaimer
        }, MODEL_PATH)
        return self.metrics

    def predict_grid(self, features_df: pd.DataFrame):
        df_ranked = self.compute_priority_scores(features_df)
        return df_ranked['exploration_priority_score'].values


# Backwards compatibility alias
ProspectivityModel = SurfaceExplorationPriorityModel
