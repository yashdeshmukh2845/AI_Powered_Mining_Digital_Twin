import os
import glob
import joblib
import numpy as np
from PIL import Image
from typing import Dict, Any, List, Optional
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
MODEL_DIR = os.path.join(BASE_DIR, 'models')
EUROSAT_MODEL_PATH = os.path.join(MODEL_DIR, 'eurosat_classifier.joblib')
DATA_DIR = os.path.join(BASE_DIR, 'data')

CLASSES = [
    'AnnualCrop', 'Forest', 'HerbaceousVegetation', 'Highway', 'Industrial',
    'Pasture', 'PermanentCrop', 'Residential', 'River', 'SeaLake'
]

class EuroSATClassifier:
    def __init__(self):
        self.model = None
        self.classes = CLASSES
        self.metrics = {}
        
    @staticmethod
    def extract_features(img_path: str) -> np.ndarray:
        with Image.open(img_path) as img:
            rgb = img.convert('RGB')
            arr = np.array(rgb, dtype=np.float32) / 255.0 # (64, 64, 3)
            
        feats = []
        # Overall channel stats
        for c in range(3):
            ch = arr[:, :, c]
            feats.extend([
                float(np.mean(ch)),
                float(np.std(ch)),
                float(np.percentile(ch, 10)),
                float(np.percentile(ch, 90))
            ])
            
        # 4 Quadrants (top-left, top-right, bottom-left, bottom-right)
        h, w, _ = arr.shape
        quads = [
            arr[:h//2, :w//2, :],
            arr[:h//2, w//2:, :],
            arr[h//2:, :w//2, :],
            arr[h//2:, w//2:, :]
        ]
        for q in quads:
            for c in range(3):
                q_ch = q[:, :, c]
                feats.extend([float(np.mean(q_ch)), float(np.std(q_ch))])
                
        # Center crop (32x32 center)
        center = arr[h//4:3*h//4, w//4:3*w//4, :]
        for c in range(3):
            c_ch = center[:, :, c]
            feats.extend([float(np.mean(c_ch)), float(np.std(c_ch))])
            
        return np.array(feats, dtype=np.float32)

    def train_on_samples(self, samples_per_class: int = 60) -> Dict[str, Any]:
        eurosat_base = os.path.join(DATA_DIR, "EuroSAT_RGB", "EuroSAT_RGB")
        if not os.path.exists(eurosat_base):
            eurosat_base = os.path.join(DATA_DIR, "EuroSAT_RGB")
        if not os.path.exists(eurosat_base):
            raise FileNotFoundError("EuroSAT_RGB folder not found")

        X_list = []
        y_list = []
        
        for class_idx, c in enumerate(self.classes):
            class_folder = os.path.join(eurosat_base, c)
            if not os.path.isdir(class_folder):
                continue
            files = sorted(glob.glob(os.path.join(class_folder, "*.jpg")))[:samples_per_class]
            for f in files:
                feats = self.extract_features(f)
                X_list.append(feats)
                y_list.append(c)
                
        if len(X_list) < 20:
            raise ValueError(f"Insufficient images found to train EuroSAT model: {len(X_list)}")
            
        X = np.array(X_list)
        y = np.array(y_list)
        
        # Train / test split (80/20 stratified)
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        clf = RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42)
        clf.fit(X_train, y_train)
        
        preds = clf.predict(X_test)
        acc = float(accuracy_score(y_test, preds))
        
        self.model = clf
        self.metrics = {
            "accuracy": round(acc, 3),
            "num_classes": len(self.classes),
            "total_train_samples": len(X_train),
            "total_test_samples": len(X_test),
            "classes": self.classes,
            "scientific_disclaimer": "EuroSAT land-cover classification detects surface vegetation, urban, industrial, and aquatic features from optical Sentinel-2 RGB bands. It does not detect subsurface manganese reserves."
        }
        
        joblib.dump({
            "model": self.model,
            "classes": self.classes,
            "metrics": self.metrics
        }, EUROSAT_MODEL_PATH)
        
        return self.metrics

    def predict_image(self, img_path: str) -> Dict[str, Any]:
        if self.model is None and os.path.exists(EUROSAT_MODEL_PATH):
            saved = joblib.load(EUROSAT_MODEL_PATH)
            self.model = saved["model"]
            self.classes = saved.get("classes", CLASSES)
            self.metrics = saved.get("metrics", {})
            
        if self.model is None:
            # Fallback to trained model or sample train
            self.train_on_samples(samples_per_class=40)
            
        feats = self.extract_features(img_path).reshape(1, -1)
        pred_class = self.model.predict(feats)[0]
        probs = self.model.predict_proba(feats)[0]
        class_probs = {c: round(float(p), 3) for c, p in zip(self.model.classes_, probs)}
        max_prob = max(probs)
        
        return {
            "predicted_class": pred_class,
            "confidence": round(float(max_prob), 3),
            "probabilities": class_probs,
            "disclaimer": "Surface optical land-cover identification only. Does not detect underground manganese mineralization."
        }
