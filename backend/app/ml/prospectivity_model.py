import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, average_precision_score
from sklearn.model_selection import train_test_split

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
MODEL_DIR = os.path.join(BASE_DIR, 'models')
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_DIR, 'prospectivity_model.joblib')

class ProspectivityModel:
    def __init__(self):
        self.model = None
        self.feature_names = ['dist_to_fault_km', 'ndvi', 'lst_c', 'sar_coherence']
        self.metrics = {}
        self.algorithm = "RandomForest"
        
    def train_from_geojson(self, geojson_path: str, algorithm: str = "RandomForest"):
        with open(geojson_path, 'r') as f:
            data = json.load(f)
            
        records = []
        for feat in data['features']:
            props = feat['properties']
            records.append({
                'dist_to_fault_km': props.get('dist_to_fault_km', 0.0),
                'ndvi': props.get('ndvi', 0.5),
                'lst_c': props.get('lst_c', 30.0),
                'sar_coherence': props.get('sar_coherence', 0.7),
                'target': props.get('synthetic_training_label', 0)
            })
            
        df = pd.DataFrame(records)
        X = df[self.feature_names]
        y = df['target']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
        
        if algorithm == "XGBoost":
            try:
                from xgboost import XGBClassifier
                self.model = XGBClassifier(n_estimators=100, max_depth=4, random_state=42, eval_metric='logloss')
                self.algorithm = "XGBoost"
            except ImportError:
                self.model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42, class_weight='balanced')
                self.algorithm = "RandomForest (Fallback)"
        else:
            self.model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42, class_weight='balanced')
            self.algorithm = "RandomForest"
            
        self.model.fit(X_train, y_train)
        
        preds = self.model.predict(X_test)
        probs = self.model.predict_proba(X_test)[:, 1] if hasattr(self.model, "predict_proba") else preds
        
        self.metrics = {
            "precision": float(round(precision_score(y_test, preds, zero_division=0), 4)),
            "recall": float(round(recall_score(y_test, preds, zero_division=0), 4)),
            "f1_score": float(round(f1_score(y_test, preds, zero_division=0), 4)),
            "roc_auc": float(round(roc_auc_score(y_test, probs), 4)) if len(np.unique(y_test)) > 1 else 0.5,
            "pr_auc": float(round(average_precision_score(y_test, probs), 4)) if len(np.unique(y_test)) > 1 else 0.5
        }
        
        # Save model
        joblib.dump({'model': self.model, 'metrics': self.metrics, 'features': self.feature_names, 'algorithm': self.algorithm}, MODEL_PATH)
        return self.metrics

    def predict_grid(self, features_df: pd.DataFrame):
        if self.model is None and os.path.exists(MODEL_PATH):
            saved = joblib.load(MODEL_PATH)
            self.model = saved['model']
            self.metrics = saved.get('metrics', {})
            self.algorithm = saved.get('algorithm', 'RandomForest')
            
        if self.model is None:
            # Simple heuristic baseline score if uninitialized
            scores = (1.0 / (1.0 + features_df['dist_to_fault_km'])).clip(0.0, 1.0).values
            return scores
            
        X = features_df[self.feature_names]
        if hasattr(self.model, "predict_proba"):
            probs = self.model.predict_proba(X)[:, 1]
        else:
            probs = self.model.predict(X).astype(float)
        return np.round(probs, 3)
