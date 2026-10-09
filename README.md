# MOIL Manganese Intelligence — AI-Powered Mining Digital Twin

> **Problem Statement**: Using AI/ML and Space Technology to Identify Manganese Reserves and Overcome Production Shortfalls.

**MOIL Manganese Intelligence** is a complete, full-stack, enterprise-grade AI Mining Digital Twin application. It combines geological exploration data, drilling and assay records, historical mine production, equipment availability, blasting delays, weather, and satellite-derived indicators to estimate mineral prospectivity, forecast production shortfalls, explain root causes using SHAP, recommend prioritized corrective actions, and simulate alternative mining scenarios.

---

> [!IMPORTANT]  
> **DEMO MODE Disclaimer**: All operational figures, geological reserves, borehole assays, and map overlays generated in default demonstration mode are synthetic and reproducibly created using seed 42. They do not represent official MOIL operational data.

---

## 1. Key Features & Modules

1. **Overview Dashboard**: High-level KPIs (Estimated Ore Resources, Contained Manganese, Target Attainment, Shortfall Risk, Equipment Availability), historical vs forecast trend chart, and priority AI recommendations.
2. **Geological Mine Map Explorer**: Interactive OpenStreetMap Leaflet viewer displaying Dongri Buzurg lease perimeter, 30+ borehole markers, lithological assay intervals, and ML prospectivity grid zones.
3. **Reserve & Grade Estimation**: Cutoff grade slider and bulk density controls for volume, tonnage ($T = V \times \rho$), grade, and contained manganese ($Mn_{tonnes} = T \times Grade / 100$) breakdown by Measured, Indicated, Inferred, and Exploration Target categories.
4. **AI Production Shortfall Forecasting**: Time-aware regression model (RandomForest & XGBoost) forecasting daily tonnes, calculating shortfall ($max(0, Target - Forecast)$), and categorizing shortfall risk (Low <5%, Medium 5-10%, High $\ge$10%).
5. **Explainable Root Cause Analysis**: SHAP and Permutation feature contributions explaining forecast drivers (downtime, rain, blasting delays) with an interactive manager confirmation audit workflow.
6. **AI Action & Optimization Engine**: Prioritized corrective action protocols with estimated production gain (+tonnes), constraints, and human approval buttons (Approve / Reject / Implement).
7. **Mining Digital Twin What-If Simulator**: Fleet capacity physics simulation (excavators, trucks, downtime, blasting, rain penalty) comparing baseline vs scenario output, constraint violation checks, and scenario persistence.
8. **Data Management & Ingestion**: File import for CSV, Excel, and GeoJSON with dataset preview, header schema validation, missing column reporting, downloadable templates, demo dataset export, and audit history.
9. **ML Model Performance**: Evaluation metrics display (Prospectivity: Precision, Recall, F1, ROC-AUC; Production: MAE, RMSE, WAPE) and one-click model retraining controls.
10. **Executive Reports & Settings**: Executive summary report generator supporting one-click CSV and printable PDF downloads.

---

## 2. Technology Stack

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons, Recharts, React Leaflet (OpenStreetMap tile layer + GeoJSON).
- **Backend**: Python 3.10+, FastAPI, Pydantic v2, SQLAlchemy ORM (SQLite fallback / PostgreSQL with PostGIS).
- **Machine Learning**: pandas, NumPy, scikit-learn (RandomForestClassifier, RandomForestRegressor), XGBoost, SHAP, SciPy, Joblib.
- **Reporting & Storage**: ReportLab PDF generator, OpenPyXL, SQLite/PostgreSQL.

---

## 3. Quick Start & Execution Commands (Windows / Linux)

### Step 1: Install Python Dependencies & Generate Demo Data

```bash
# 1. Install required Python packages
pip install pandas numpy scikit-learn xgboost shap scipy fastapi uvicorn sqlalchemy reportlab openpyxl joblib pydantic pytest

# 2. Generate reproducible synthetic demonstration datasets
python scripts/generate_demo_data.py

# 3. Initialize & seed SQLite database (moil_manganese.db)
python scripts/seed_db.py

# 4. Train & persist initial ML model artifacts (models/*.joblib)
python scripts/train_models.py
```

### Step 2: Start Backend Server

```bash
# Run FastAPI server on http://127.0.0.1:8000
python backend/app/main.py
```
- **API Documentation (Swagger UI)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **API Health Check**: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

### Step 3: Start Frontend Application

In a separate terminal window:

```bash
cd frontend

# Install Node dependencies (if not already installed)
npm install

# Start Vite dev server on http://localhost:5173
npm run dev
```
- **Application URL**: [http://localhost:5173](http://localhost:5173)

---

## 4. Run Automated Test Suite

```bash
# Run pytest automated backend test suite (9 tests)
pytest backend/tests/test_api.py
```

---

## 5. Required CSV Dataset Templates

The data ingestion pipeline supports CSV/Excel uploads matching these header schemas:

| Dataset Type | Required Columns |
| :--- | :--- |
| `production_records` | `id`, `mine_id`, `date`, `actual_production_tonnes`, `planned_target_tonnes` |
| `boreholes` | `id`, `mine_id`, `borehole_id`, `latitude`, `longitude`, `elevation`, `total_depth` |
| `borehole_intervals` | `id`, `borehole_id`, `from_depth`, `to_depth`, `lithology` |
| `assay_samples` | `id`, `interval_id`, `sample_id`, `mn_grade` |
| `ore_blocks` | `id`, `mine_id`, `block_code`, `min_x`, `max_x`, `min_y`, `max_y`, `volume_m3`, `tonnage`, `est_mn_grade` |
| `equipment` | `id`, `mine_id`, `name`, `equipment_type` |
| `environmental_observations` | `id`, `mine_id`, `date`, `rainfall_mm` |

---

## 6. Docker Deployment (Optional)

```bash
# Launch PostgreSQL/PostGIS container and backend
docker-compose up --build -d
```
