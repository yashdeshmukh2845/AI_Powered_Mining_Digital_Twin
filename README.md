# MOIL Manganese Intelligence — AI-Powered Mining Digital Twin

[![CI Pipeline](https://github.com/moil-analytics/mining-digital-twin/actions/workflows/ci.yml/badge.svg)](https://github.com/moil-analytics/mining-digital-twin/actions/workflows/ci.yml)
[![Tests Passing](https://img.shields.io/badge/pytest-30%20passed-brightgreen.svg)](backend/tests/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![React 19](https://img.shields.io/badge/React-19.0-61DAFB.svg?logo=react)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6.svg?logo=typescript)](https://www.typescriptlang.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Problem Statement (MOIL Limited)**:  
> *"Using AI/ML and Space Technology to Identify Manganese Reserves and Overcome Production Shortfalls. Use geological data, historical production, equipment performance, and satellite inputs (rainfall, soil moisture, vegetation index, land temperature) to (1) identify and map manganese reserves using surface and sub-surface indicators, (2) predict production shortfalls from equipment downtime, weather and blasting delays, (3) suggest corrective actions such as adjusting mine schedules, optimizing blasting or re-deploying equipment. Expected output: a user-friendly dashboard showing predicted reserves, production trends, shortfall risks, and recommended actions."*

---

## 1. Scientific Foundation: Avoiding "The Subsurface Trap"

> [!IMPORTANT]  
> **The Subsurface Trap — Scientific Truth & Limitations**:  
> Space-borne optical and thermal sensors (such as Sentinel-2 MSI, Landsat-8/9, MODIS, and EuroSAT RGB) observe strictly the top 1 to 2 millimeters of Earth's surface land cover. **Satellite sensors CANNOT directly detect underground manganese ore bodies beneath 20 to 150 meters of basalt, soil, and overburden.**  
> In this platform:
> - **Space & Meteorological Technology** is applied strictly for **Surface Environmental Context**: monitoring pit sump flooding water accumulation, haul-road mud slickness, waste dump slope geometry, and precipitation disruption.
> - **Subsurface Reserve Estimation** is 100% geostatistically computed from **borehole core drilling, chemical laboratory assays, downhole interval logging, and 3D Ordinary Kriging interpolation** compliant with JORC (2012) and UNFC standards.
> - **Surface Exploration Priority Maps** rank where to drill next based on structural fault lineaments and borehole coverage gaps ($d > 250\text{ m}$), accompanied by the mandatory disclaimer: *"Guides where to drill next. Does not indicate ore at depth."*

### Empirical Proof: Space & Weather Ablation Study
On 365 operational days at Dongri Buzurg evaluated on a strict chronological out-of-time test set:
- **Monsoon Accuracy Gain**: $+12.0\%$ ($+11.6\text{ tonnes/day}$ error reduction) during rainy months (June – September).
- **Dry Season Sensitivity**: $<1.5\%$ variance during dry months (October – May), confirming that weather is an episodic operational covariate rather than a year-round baseline driver.
- **Haul Road Lag Recovery**: Documented that rain causes $-32.5\%$ traction loss and $+5.4\text{ min/cycle}$ dumper slowdown on Day 0, stabilizing across 72 hours.

---

## 2. Key Modules & Analytical Workspaces

| Module | Purpose & Core Capabilities | Scientific / Mathematical Engine |
| :--- | :--- | :--- |
| **1. Overview Dashboard** | Executive KPIs: Estimated Resources, Contained Mn, Attainment %, Shortfall Risk, Equipment Availability, and Live Alert Feed. | Aggregated SQLite/PostgreSQL warehouse with provenance labeling |
| **2. Mine Map Explorer** | Interactive Leaflet GIS viewer displaying Dongri Buzurg lease perimeter, 31 boreholes, drill coverage gap layers, and lineaments. | GeoJSON coordinate transformation relative to Dongri Buzurg pit center |
| **3. Satellite Environmental Monitor** | Replaces EuroSAT ore claims; tracks pit sump water index, haul-road mud friction, and waste dump stability. | Multi-temporal optical RGB & SAR surface change indexing |
| **4. Space Data Value (Proof)** | Interactive empirical ablation study comparing Full Multi-Modal, Telemetry Only, Weather Only, and Naive Persistence models. | Chronological out-of-time validation split (80% train / 20% test) |
| **5. 3D Block Model & Reserves** | Interactive 3D block model viewer with plan bench slices, cross-sections, variogram curves, and JORC/UNFC statements. | Empirical semi-variogram $\gamma(h)$ + 3D Ordinary Kriging ($60\text{m} \times 60\text{m} \times 10\text{m}$) |
| **6. Production Forecasting** | P10, P50, and P90 uncertainty bands, daily $P(\text{Shortfall} < \text{Target})$ cards, and primary operational driver tags. | Quantile Gradient Boosting with strict anti-leakage shifted lags |
| **7. Fleet Health & Maintenance** | Fleet failure risk heatmaps (24h, 48h, 72h), machine diagnostic dossiers, critical subsystem tagging, and expected lost hours. | Calibrated Random Forest Classifier evaluated with PR-AUC & Brier score |
| **8. Shortfall Risk Center** | Configurable risk category thresholds, TreeExplainer SHAP attributions, and natural language root-cause summary sentences. | Shapley TreeExplainer feature attributions with human sign-off audit |
| **9. AI Action Center (LP)** | Operations research fleet dispatch optimizer (PuLP LP), 7-day blasting window scheduler, and simulator-validated actions. | PuLP Linear Programming (CBC solver) + Simulator validation |
| **10. Digital Twin Simulator** | What-if scenario simulator with cyclic truck queueing, 450 TPH primary crusher circuit, 3-grade stockpiles, and BOXN rail rakes. | Cyclic haul queueing physics, crusher choke limits, rail logistics balance |
| **11. Data Management** | CSV/Excel data ingestion engine with schema validation, missing column checks, downloadable templates, and import audit trail. | IngestionService with automated SQLite cache synchronization |
| **12. Model Performance** | Live model registry tracking training status, algorithms, hyperparameters, and chronological validation metrics. | Model Versioning & audit metadata storage |
| **13. Executive Reports** | One-click export of executive audit summaries in CSV and print-ready PDF formats with full scientific disclaimers. | ReportLab automated PDF reporting engine |

---

## 3. Technology Stack

- **Backend**: Python 3.10+, FastAPI, Pydantic v2, SQLAlchemy ORM (SQLite / PostgreSQL with PostGIS).
- **Operations Research & Geostatistics**: PuLP (Linear Programming CBC solver), PyKrige (Ordinary Kriging), SciPy.
- **Machine Learning**: Scikit-Learn (Quantile Gradient Boosting, Calibrated Random Forest), SHAP, NumPy, Pandas, Joblib.
- **Frontend**: React 19, TypeScript, Vite 8.3, TailwindCSS v4, Recharts, React Leaflet (OpenStreetMap + GeoJSON), Lucide Icons.
- **External Data Ingestion**: Open-Meteo Weather API (historical archive & 14-day forecast), NASA POWER, Sentinel-2 Optical Land Cover.
- **Containerization & DevOps**: Docker, Docker Compose, GitHub Actions CI.

---

## 4. Quick Start & Execution Commands

### Prerequisites
- Python 3.10 or higher
- Node.js 18+ and npm
- Git

### Step 1: Clone Repository & Install Python Dependencies
```bash
git clone https://github.com/moil-analytics/mining-digital-twin.git
cd mining-digital-twin

# Install Python packages
pip install -r requirements.txt
```

### Step 2: Seed Database & Train AI Models
```bash
# 1. Ingest datasets and seed SQLite database (moil_manganese.db)
python -c "from backend.app.database.db import SessionLocal; from backend.app.services.ingestion_service import IngestionService; db=SessionLocal(); IngestionService.ingest_all(db); db.close()"

# 2. Train and persist machine learning models (models/*.joblib)
python scripts/train_models.py

# 3. Run Space & Weather Ablation Study (models/ablation_results.json)
python scripts/ablation_study.py

# 4. Compute 3D Geostatistical Block Model (models/geostat_block_model.json)
python -c "from backend.app.services.geostatistics_service import GeostatisticsService; GeostatisticsService.generate_or_get_block_model()"
```

### Step 3: Run Backend Server
```bash
# Start FastAPI backend server on port 8080
python backend/app/main.py
```
- **Backend API URL**: [http://127.0.0.1:8080](http://127.0.0.1:8080)
- **Interactive Swagger Documentation**: [http://127.0.0.1:8080/docs](http://127.0.0.1:8080/docs)
- **API Health Check**: [http://127.0.0.1:8080/api/health](http://127.0.0.1:8080/api/health)

### Step 4: Run Frontend Application
In a separate terminal window:
```bash
cd frontend

# Install Node dependencies
npm install

# Start Vite development server
npm run dev
```
- **Frontend Dashboard URL**: [http://localhost:5173](http://localhost:5173)

---

## 5. Docker Deployment

Run the entire full-stack application (FastAPI backend + Vite React frontend) with a single command:

```bash
docker-compose up --build
```

- **Web Dashboard**: `http://localhost:5173`
- **Backend API**: `http://localhost:8080`

---

## 6. Automated Testing & Quality Assurance

The codebase includes an automated test suite with **30 unit and integration tests** verifying zero data leakage, geostatistical calculations, linear programming constraint satisfaction, and API contracts.

```bash
# Run complete test suite with verbose output
pytest backend/tests/ -v
```

### Test Suite Structure:
- `backend/tests/test_leakage.py`: Tests that the production forecasting engine has zero same-day actual leakage and strict lag shifting.
- `backend/tests/test_geostatistics_and_optimization.py`: Tests semi-variogram calculation, 3D block model generation, JORC resource classification, PuLP dispatch optimizer, and equipment failure bounds.
- `backend/tests/test_api.py`: Tests FastAPI REST endpoints, dashboard summaries, simulator physics, and report generation.
- `backend/tests/test_dataset_integration.py`: Tests data provenance, schema detection, and multi-dataset integration.

---

## 7. Multi-Mine Registry Configuration

Configured in `backend/app/core/config.py`:
1. **MINE-001**: Dongri Buzurg Manganese Mine (21.5342°N, 79.6915°E, Bhandara District, Maharashtra)
2. **MINE-002**: Mansar Manganese Mine (21.3986°N, 79.2814°E, Nagpur District, Maharashtra)
3. **MINE-003**: Balaghat Manganese Mine (21.8124°N, 80.1832°E, Balaghat District, Madhya Pradesh)

---

## 8. License

This project is licensed under the MIT License. Developed for MOIL Limited mining operations research.
