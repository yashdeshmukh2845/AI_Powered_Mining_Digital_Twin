import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import precision_recall_curve, auc, brier_score_loss, recall_score, precision_score
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.database.models import Equipment, EquipmentDowntime, EnvironmentalObservation

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
MODEL_DIR = os.path.join(BASE_DIR, 'models')
os.makedirs(MODEL_DIR, exist_ok=True)
EQUIPMENT_MODEL_PATH = os.path.join(MODEL_DIR, 'equipment_failure_model.joblib')

class EquipmentFailureModel:
    """
    Predictive Equipment Health & Breakdown Risk Engine.
    Predicts probability of equipment breakdown within 24h, 48h, and 72h horizons.
    Calculates expected lost operating downtime hours for the next 1-7 days to feed
    directly into production forecasting as a PREDICTED variable rather than an after-the-fact input.
    """

    def __init__(self):
        self.model = None
        self.feature_names = [
            'engine_hours',
            'hours_since_last_maintenance',
            'past_failure_count_90d',
            'average_load_pct',
            'ambient_temp',
            'rainfall_3d_sum'
        ]
        self.metrics = {}

    def _generate_synthetic_telemetry_history(self, db: Session) -> pd.DataFrame:
        """
        Creates historical telemetry training dataset matching recorded downtime incidents.
        """
        downtimes = db.query(EquipmentDowntime).all()
        equipment_list = db.query(Equipment).all()
        env_obs = db.query(EnvironmentalObservation).order_by(EnvironmentalObservation.date.asc()).all()
        
        env_map = {e.date: e for e in env_obs}
        eq_map = {eq.id: eq for eq in equipment_list}
        
        # Build 365 daily machine telemetry rows
        rows = []
        if env_obs:
            for env in env_obs:
                d_str = env.date
                rain_3d = env.rainfall_mm
                temp_c = env.land_surface_temp_c if env.land_surface_temp_c else 30.0
                
                for eq in equipment_list:
                    # Synthetic feature state for day d
                    eng_hrs = eq.engine_hours + np.random.uniform(-500, 200)
                    maint_hrs = (hash(f"{d_str}_{eq.id}") % 260) + 10.0
                    load_pct = eq.average_load_pct + np.random.uniform(-10, 8)
                    past_fails = eq.past_failure_count_90d
                    
                    # Target 24h failure label: true if downtime incident occurred for this equipment on this day
                    failed_24h = 1 if any(dt.equipment_id == eq.id and d_str in str(dt.start_time) for dt in downtimes) else 0
                    
                    # Probabilistic failure simulation if sparse
                    if failed_24h == 0 and maint_hrs > 230 and load_pct > 88:
                        failed_24h = 1 if np.random.rand() < 0.25 else 0
                        
                    rows.append({
                        'date': d_str,
                        'equipment_id': eq.id,
                        'engine_hours': max(1000.0, eng_hrs),
                        'hours_since_last_maintenance': maint_hrs,
                        'past_failure_count_90d': past_fails,
                        'average_load_pct': np.clip(load_pct, 50.0, 100.0),
                        'ambient_temp': temp_c,
                        'rainfall_3d_sum': rain_3d,
                        'target_failed_24h': failed_24h
                    })
        else:
            # Baseline dummy rows
            for i in range(120):
                rows.append({
                    'date': f"2025-01-{i%28+1:02d}",
                    'equipment_id': f"EQ-0{i%7+1}",
                    'engine_hours': 4500.0 + i * 10,
                    'hours_since_last_maintenance': float(i % 250),
                    'past_failure_count_90d': i % 3,
                    'average_load_pct': 82.0,
                    'ambient_temp': 32.0,
                    'rainfall_3d_sum': 5.0,
                    'target_failed_24h': 1 if (i % 250 > 220) else 0
                })

        return pd.DataFrame(rows).sort_values('date')

    def train(self, db: Session) -> Dict[str, Any]:
        """
        Trains a calibrated Random Forest classifier with a chronological time-based split.
        Reports PR-AUC, Recall, Brier score, and baseline maintenance-interval rule comparison.
        """
        df = self._generate_synthetic_telemetry_history(db)
        X = df[self.feature_names]
        y = df['target_failed_24h']

        # Time-based chronological split (80% train, 20% test)
        split_idx = int(len(df) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

        # Train calibrated classifier
        base_clf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42, class_weight='balanced')
        base_clf.fit(X_train, y_train)

        # Calibrate probabilities using isotonic / sigmoid calibration
        calibrated_clf = CalibratedClassifierCV(estimator=base_clf, method='sigmoid', cv='prefit')
        calibrated_clf.fit(X_train, y_train)
        self.model = calibrated_clf

        probs = self.model.predict_proba(X_test)[:, 1]
        preds = (probs >= 0.35).astype(int)

        # Metrics
        precision_vals, recall_vals, _ = precision_recall_curve(y_test, probs)
        pr_auc = float(round(auc(recall_vals, precision_vals), 3))
        brier = float(round(brier_score_loss(y_test, probs), 3))
        rec = float(round(recall_score(y_test, preds, zero_division=0), 3))
        prec = float(round(precision_score(y_test, preds, zero_division=0), 3))

        # Baseline rule: Predict failure if hours_since_last_maintenance > 220
        rule_preds = (X_test['hours_since_last_maintenance'] > 220.0).astype(int)
        baseline_brier = float(round(brier_score_loss(y_test, rule_preds), 3))
        baseline_recall = float(round(recall_score(y_test, rule_preds, zero_division=0), 3))

        self.metrics = {
            "pr_auc": pr_auc,
            "recall": rec,
            "precision": prec,
            "brier_score": brier,
            "baseline_brier_score": baseline_brier,
            "baseline_rule": "Maintenance interval threshold (>220 hrs)",
            "baseline_recall": baseline_recall,
            "brier_improvement_pct": float(round((baseline_brier - brier) / max(0.01, baseline_brier) * 100.0, 1)),
            "evaluation_method": "Chronological Out-of-Time Test Split",
            "last_trained": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        }

        joblib.dump({
            "model": self.model,
            "metrics": self.metrics,
            "features": self.feature_names
        }, EQUIPMENT_MODEL_PATH)

        return self.metrics

    def predict_equipment_risks(self, db: Session, mine_id: str = "MINE-001") -> Dict[str, Any]:
        """
        Calculates per-machine 24h, 48h, and 72h failure risks and 7-day expected downtime hours.
        """
        if self.model is None and os.path.exists(EQUIPMENT_MODEL_PATH):
            saved = joblib.load(EQUIPMENT_MODEL_PATH)
            self.model = saved.get("model")
            self.metrics = saved.get("metrics", {})

        equipment_list = db.query(Equipment).filter(Equipment.mine_id == mine_id).all()
        if not equipment_list:
            equipment_list = db.query(Equipment).all()

        latest_env = db.query(EnvironmentalObservation).order_by(EnvironmentalObservation.date.desc()).first()
        amb_temp = latest_env.land_surface_temp_c if latest_env else 32.0
        rain_sum = latest_env.rainfall_mm if latest_env else 0.0

        items = []
        total_expected_downtime_7d = 0.0

        for eq in equipment_list:
            X_curr = pd.DataFrame([{
                'engine_hours': eq.engine_hours,
                'hours_since_last_maintenance': eq.hours_since_last_maintenance,
                'past_failure_count_90d': eq.past_failure_count_90d,
                'average_load_pct': eq.average_load_pct,
                'ambient_temp': amb_temp,
                'rainfall_3d_sum': rain_sum
            }])

            if self.model is not None:
                p_24h = float(self.model.predict_proba(X_curr)[0][1])
            else:
                # Heuristic calibration if model not yet saved
                p_24h = min(0.85, (eq.hours_since_last_maintenance / 250.0) * 0.25 + (eq.average_load_pct / 100.0) * 0.15)
                if eq.past_failure_count_90d >= 3:
                    p_24h += 0.15

            p_24h = round(float(np.clip(p_24h, 0.02, 0.92)), 2)
            p_48h = round(float(np.clip(p_24h * 1.55, 0.04, 0.95)), 2)
            p_72h = round(float(np.clip(p_24h * 2.10, 0.07, 0.98)), 2)

            # Top risk factors
            factors = []
            if eq.hours_since_last_maintenance > 180:
                factors.append(f"High Operating Hours since Service ({eq.hours_since_last_maintenance:.0f} hrs)")
            if eq.average_load_pct > 85:
                factors.append(f"Heavy Digging Load Duty Cycle ({eq.average_load_pct:.0f}%)")
            if eq.past_failure_count_90d >= 2:
                factors.append(f"Recurring Unplanned Stoppages ({eq.past_failure_count_90d} in 90 days)")
            if amb_temp > 35:
                factors.append(f"High Ambient Temperature ({amb_temp:.1f}°C Hydraulic Stress)")
            if not factors:
                factors.append("Nominal Mechanical Wear & Fluid Levels")

            # Recommended action
            if p_72h >= 0.40:
                rec_action = f"Immediate Pre-emptive Service for {eq.critical_component} within 24h"
            elif p_72h >= 0.20:
                rec_action = f"Schedule 250h Preventive Inspection; Check {eq.critical_component}"
            else:
                rec_action = "Routine Shift Inspection; Continue Active Production"

            # Expected lost hours over next 7 days: p_72h * mean breakdown duration (6.5 hours)
            exp_dt_7d = round(p_72h * 6.5, 1)
            total_expected_downtime_7d += exp_dt_7d

            # Dynamic Health score
            h_score = round(max(20.0, 100.0 - (p_72h * 60.0) - (eq.hours_since_last_maintenance / 250.0 * 20.0)), 1)

            # Update DB model instance
            eq.failure_risk_24h = p_24h
            eq.failure_risk_48h = p_48h
            eq.failure_risk_72h = p_72h
            eq.health_score = h_score
            db.merge(eq)

            items.append({
                "id": eq.id,
                "name": eq.name,
                "equipment_type": eq.equipment_type,
                "status": "Critical" if p_72h >= 0.45 else ("Warning" if p_72h >= 0.25 else "Operational"),
                "capacity_tph": eq.capacity_tph,
                "engine_hours": eq.engine_hours,
                "hours_since_last_maintenance": eq.hours_since_last_maintenance,
                "past_failure_count_90d": eq.past_failure_count_90d,
                "average_load_pct": eq.average_load_pct,
                "health_score": h_score,
                "failure_risk_24h": p_24h,
                "failure_risk_48h": p_48h,
                "failure_risk_72h": p_72h,
                "critical_component": eq.critical_component or "Hydraulic System",
                "top_risk_factors": factors,
                "recommended_action": rec_action,
                "expected_downtime_hours_next_7d": exp_dt_7d
            })

        db.commit()

        high_risk_count = sum(1 for it in items if it["failure_risk_72h"] >= 0.35)
        avg_health = round(sum(it["health_score"] for it in items) / len(items), 1) if items else 90.0

        return {
            "mine_id": mine_id,
            "fleet_count": len(items),
            "high_risk_count": high_risk_count,
            "fleet_health_score_avg": avg_health,
            "expected_total_downtime_hours_next_7d": round(total_expected_downtime_7d, 1),
            "evaluation_metrics": self.metrics,
            "equipment": items
        }
