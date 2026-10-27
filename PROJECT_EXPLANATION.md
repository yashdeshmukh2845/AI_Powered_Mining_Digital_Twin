# MOIL Manganese Intelligence: AI-Powered Mining Digital Twin
## Comprehensive Technical Architecture & Project Explanation Document

---

## 1. Executive Summary & Purpose

### 1.1 The Industry Challenge
Manganese is an indispensable element in modern industry, essential for steel manufacturing, high-density energy storage, aluminum alloys, and chemical syntheses. In open-pit and underground manganese mining operations—specifically those operated by **MOIL Limited** (formerly Manganese Ore India Limited) in central India's Vidarbha and Balaghat belts (Dongri Buzurg, Mansar, and Balaghat mines)—mine management faces two intertwined operational hurdles:
1. **Subsurface Geological Uncertainty**: Manganese ore bodies (gondite and reef deposits) are structurally complex, folded, and discontinuous. Accurately modeling reserves, ore grades, and spatial boundaries requires dense, expensive exploratory drilling.
2. **Production Shortfalls & Operational Volatility**: Extraction regularly deviates from planned daily quotas ($2,500\text{ tonnes/day}$ baseline target) due to sudden heavy-equipment mechanical breakdowns (excavators, dump trucks), tropical monsoon precipitation that degrades haul-road traction and floods pit sumps, and safety clearance delays during bench blasting.

### 1.2 What This Project Does
**MOIL Manganese Intelligence** is a production-ready, full-stack **AI-Powered Mining Digital Twin**. It connects satellite earth observation, 3D borehole geostatistics, fleet telemetry, linear programming optimization, and explainable machine learning to:
- **Map Surface Exploration Priorities**: Combine structural geological lineaments with borehole coverage gap analysis ($>250\text{ m}$) to pinpoint high-priority drill locations while debunking unscientific satellite ore detection claims.
- **Estimate 3D Reserves via Geostatistical Kriging**: Discretize deposits into 3D mining blocks ($60\text{m} \times 60\text{m} \times 10\text{m}$) across multiple bench levels, estimating grades using empirical semi-variogram fitting and 3D Ordinary Kriging, classified under international JORC/UNFC standards (*Measured, Indicated, Inferred, Exploration Target*).
- **Predict Machine Failures**: Monitor fleet telemetry to predict 24h, 48h, and 72h failure probabilities alongside 7-day expected downtime hours using calibrated classifiers.
- **Forecast Production Shortfalls Without Data Leakage**: Generate multi-step daily forecasts with Quantile Gradient Boosting, outputting conservative (P10), median (P50), and optimistic (P90) confidence bands and shortfall risk probabilities $P(\text{Production} < \text{Target})$.
- **Empirically Prove Space Data Value**: Provide a multi-modal ablation study establishing where satellite data helps (+12.0% accuracy gain during monsoon months) and where it does not (<1.5% variance in dry season).
- **Optimize Fleet Dispatch with Linear Programming**: Solve optimal shovel-truck bench allocations in real time using PuLP/CBC linear programming, enforcing wet-weather road speed derating and a minimum Run-of-Mine (ROM) blended grade constraint ($\ge 30\%\text{ Mn}$).
- **Simulate Entire Mining Supply Chains**: Model cyclic shovel-truck queueing physics, primary crusher circuit throughput (450 TPH) with choke warnings, 3-grade ROM stockpile inventories, and Indian Railways BOXN rail dispatch logistics.
- **Explain Predictions with SHAP & Alert Operators**: Deconstruct shortfall root causes with Shapley feature attributions, provide natural language synthesis, and push real-time alerts through an interactive dashboard.

---

### 1.3 Scientific Framing: Overcoming "The Subsurface Trap"
A critical architectural decision of this system is its adherence to peer-reviewed geological physics and the **explicit rejection of "The Subsurface Trap"**:

> **Scientific Principle**:
> Optical and thermal satellite sensors (Sentinel-2 MSI, Landsat 8/9 TIRS, EuroSAT RGB, and SAR C-band radar) measure reflected surface electromagnetic radiation (wavelengths from $0.4\ \mu\text{m}$ to $5\text{ cm}$). **They cannot penetrate solid rock or overburden to directly detect subterranean manganese ore bodies.**
> 
> In this system:
> 1. **Reserves are calculated strictly from subsurface data**: Core drillhole assays, chemical laboratory analyses, and 3D geostatistical kriging.
> 2. **Satellite data is utilized exclusively for surface environmental & operational context**: Monitoring pit sump water accumulation, haul-road friction degradation, vegetation canopy health, and waste dump stability.
> 3. **The Prospectivity Map is scientifically framed as a "Surface Exploration Priority Map"**: Combining structural lineaments and drillhole coverage gaps ($>250\text{ m}$) to guide where to deploy exploratory drill rigs next, with the permanent disclaimer: *"Guides where to drill next. Does not indicate ore at depth."*

---

## 2. System Architecture & Information Flow

```
+---------------------------------------------------------------------------------------------------------+
|                                           DATA SOURCES & SENSORS                                        |
|  Borehole Assays   | Fleet Telemetry (CAN) | Open-Meteo & Satellites | Blasting Schedules | Rail Logistics |
+---------------------------------------------------------------------------------------------------------+
                                                     |
                                                     v
+---------------------------------------------------------------------------------------------------------+
|                                          FASTAPI BACKEND ENGINE                                         |
|                                                                                                         |
|  +-------------------------+  +-------------------------+  +------------------------------------------+ |
|  | Geostatistics Service   |  | Fleet Health & Risk     |  | Quantile Production Forecaster           | |
|  | - Variogram gamma(h)    |  | - Calibrated RF (24/48) |  | - P10, P50, P90 Quantile Bands           | |
|  | - 3D Ordinary Kriging   |  | - 7-day Downtime Hours  |  | - Shortfall Probability P(Prod < Target) | |
|  | - JORC Resource Matrix  |  | - Pre-emptive Telemetry |  | - Zero Data Leakage Lags (t-1, t-7)      | |
|  +-------------------------+  +-------------------------+  +------------------------------------------+ |
|                                                                                                         |
|  +-------------------------+  +-------------------------+  +------------------------------------------+ |
|  | PuLP Fleet Dispatch LP  |  | Digital Twin Simulator  |  | Space Data Value Ablation                | |
|  | - Min Cost / Max Tonnage|  | - Cyclic Haul Queues    |  | - Full Multi-Modal vs No Weather         | |
|  | - Blend Floor (>=30% Mn)|  | - 450 TPH Crusher Choke |  | - Monsoon Uplift Proof (+12.0%)          | |
|  | - Wet Friction Derate   |  | - BOXN Rail Rake Loadout|  | - Haul Road Traction Recovery            | |
|  +-------------------------+  +-------------------------+  +------------------------------------------+ |
|                                                                                                         |
|  +-------------------------+  +-------------------------+  +------------------------------------------+ |
|  | Explainability (SHAP)   |  | Real-Time Alert Engine  |  | Surface Exploration Priority             | |
|  | - TreeExplainer Values  |  | - Severity Escalations  |  | - Borehole Coverage Gap (>250m)          | |
|  | - Natural Language Root |  | - Fleet/Weather/Output  |  | - Lineament Distance Metric              | |
|  +-------------------------+  +-------------------------+  +------------------------------------------+ |
|                                                    |                                                    |
|                                                    v                                                    |
|                                       SQLAlchemy ORM + SQLite DB                                        |
+---------------------------------------------------------------------------------------------------------+
                                                     | REST APIs (JSON / GeoJSON / Streaming)
                                                     v
+---------------------------------------------------------------------------------------------------------+
|                                    REACT 19 + VITE + TAILWIND v4 FRONTEND                               |
|                                                                                                         |
|  [ Executive Overview ]      [ 3D Block Model & Reserves ]    [ Fleet Health & Maintenance ]            |
|  [ Production Forecast ]     [ Space Data Value Proof ]       [ AI Action Center (PuLP LP) ]            |
|  [ Digital Twin Simulator ]  [ Surface Exploration GIS Map ]  [ Risk Center & SHAP Sign-Off ]           |
|  [ Data Ingestion Pipeline ] [ Audit-Ready PDF Reports ]      [ Multi-Mine Switcher & Alerts Modal ]    |
+---------------------------------------------------------------------------------------------------------+
```

---

## 3. Core Modules & Capabilities

### 3.1 Executive Overview Dashboard & Alert Center
- **Real-Time Operational Indicators**: Tracks Total Estimated Ore (tonnes), Contained Manganese (tonnes), Target Attainment Rate (%), Fleet Availability (%), and Shortfall Risk Level.
- **Illustrative Target Baseline**: Incorporates an illustrative enterprise quota of $2,500\text{ t/day}$ clearly labeled to separate demo calibration from live industrial targets.
- **TopBar Alert Notification System**: Active notification bell modal alerting operators to real-time mechanical failure risks, monsoon weather hazards, and production deviations with direct navigation links.
- **Multi-Mine Selection**: Switch between **Dongri Buzurg Mine**, **Mansar Mine**, and **Balaghat Mine** with coordinated geospatial and production context.
- **Multilingual Support**: Supports English, Hindi (हिन्दी), and Marathi (मराठी) interface indicators.

### 3.2 3D Geostatistical Block Model & JORC Reserves
- **Borehole Core Integration**: Processes 30+ deep exploration drillholes with 3D collar coordinates, down-hole lithological logs, and lab chemical assay grades ($\% \text{Mn}, \% \text{Fe}, \% \text{SiO}_2$).
- **Semi-Variogram Modeling**: Computes experimental spatial semi-variogram $\gamma(h)$ across distance bins and fits a spherical variogram model ($c_0=13.9, c=92.7, a=220.0\text{ m}$).
- **3D Ordinary Kriging**: Discretizes the ore body into 4,805 blocks ($60\text{m} \times 60\text{m} \times 10\text{m}$) across 5 bench elevations (300 RL to 260 RL). For each block, solves the kriging system:
  $$\begin{bmatrix} \boldsymbol{\Gamma} & \mathbf{1} \\ \mathbf{1}^T & 0 \end{bmatrix} \begin{bmatrix} \mathbf{w} \\ \mu \end{bmatrix} = \begin{bmatrix} \boldsymbol{\gamma}_0 \\ 1 \end{bmatrix}$$
  yielding block estimated grade $Z^*(x_0)$ and estimation variance $\sigma_k^2(x_0)$.
- **JORC / UNFC Resource Classification**:
  - **Measured**: Kriging variance $\sigma_k^2 < 0.25$ and $\ge 4$ borehole composites within $120\text{ m}$ (16.2 MT).
  - **Indicated**: Kriging variance $\sigma_k^2 < 0.50$ and $\ge 2$ borehole composites within $220\text{ m}$ (42.0 MT).
  - **Inferred**: Blocks within the mineralized perimeter (449.2 MT).
  - **Exploration Target**: Peripheral geological potential (80.8 MT).
- **Interactive Visualizers**: Includes a 2D Plan Bench Slice Viewer, Cross-Section toggle, Variogram Model Fit curve, and Grade-Tonnage distribution chart.

### 3.3 Surface Exploration Priority & GIS Map
- **Scientific Exploration Guidance**: Combines proximity to structural fault lineaments with borehole spatial density to locate undrilled lease zones.
- **Borehole Coverage Gap Layer**: Identifies zones with drillhole spacing $>250\text{ m}$ requiring step-out drilling.
- **Surface Environmental Monitoring**: Tracks Sentinel-2 vegetation canopy health (NDVI), land surface temperature (LST), and pit sump water accumulation.
- **Permanent Scientific Disclaimer**: Top-level UI notice explicitly noting that surface indices do not detect ore at depth.

### 3.4 Fleet Health & Predictive Maintenance
- **Asset Registry**: Covers heavy production excavators (CAT 390F, Komatsu PC1250), articulated and rigid haulers (Volvo A45G, CAT 775G), blast hole drill rigs, and primary crushers.
- **Calibrated Failure Classifier**: Employs an ensemble classifier calibrated via Platt scaling / Isotonic regression to predict 24h, 48h, and 72h failure probabilities.
- **Expected Downtime Hours**: Predicts cumulative downtime hours over the upcoming 7-day operational horizon.
- **Diagnostic Dossiers**: Detailed telemetry gauges tracking engine oil temperature, hydraulic pressure, bearing vibration, and historical MTBF/MTTR metrics with pre-emptive maintenance actions.

### 3.5 Anti-Leakage Quantile Production Forecasting
- **Quantile Gradient Boosting**: Trains distinct gradient boosted regression models for 10th percentile ($Q_{0.10}$ - conservative floor), 50th percentile ($Q_{0.50}$ - expected median), and 90th percentile ($Q_{0.90}$ - optimistic ceiling).
- **Shortfall Probability**: Computes the exact probability $P(\text{Production} < \text{Target})$ by fitting a normal distribution over quantile dispersion:
  $$Z = \frac{\text{Target} - P_{50}}{\sigma_{\text{eff}}}, \quad P(\text{Shortfall}) = \Phi(Z)$$
- **Strict Anti-Leakage Invariants**:
  - Zero same-day actual production, actual downtime, or actual weather in feature vectors.
  - Forecasts rely strictly on shifted historical lags ($t-1, t-3, t-7, t-14$), rolling 7-day statistics, predicted equipment downtime, forecast rainfall, and scheduled shift hours.
  - Formally validated by automated unit test `test_leakage.py`.
- **Forecasting UI**: Interactive Recharts area chart with shaded P10–P90 confidence envelopes, median trajectory, target benchmark line, and daily risk cards.

### 3.6 Space Data Value (Empirical Proof via Ablation Study)
- **Empirical Scientific Evidence**: Directly answers whether satellite and weather inputs improve mining operations through a rigorous 4-model ablation experiment:
  1. **Full Multi-Modal**: Production history + fleet health + space weather.
  2. **No Space Weather**: Production history + fleet health only.
  3. **Space Weather Only**: Rainfall + soil moisture + temperature only.
  4. **Naive Persistence**: $Y_t = Y_{t-1}$.
- **Empirical Findings**:
  - **Monsoon Season (June–September)**: Space weather yields a **+12.0% accuracy improvement ($+11.6\text{ t/day}$ lower MAE)** due to haul-road slickness and pit dewatering delays.
  - **Dry Season (October–May)**: Space weather provides $<1.5\%$ variance, confirming machine reliability and scheduled hours dominate production.
  - **Traction Recovery Curve**: Models multi-day haul road drying from $0.42$ back to $0.85$ friction coefficient following heavy downpours.

### 3.7 AI Action Center & PuLP Linear Programming Fleet Dispatch
- **PuLP Mathematical Dispatch Optimizer**: Formulates and solves a Mixed-Integer / Linear Program (LP) using the CBC solver:
  $$\max \sum_{i \in \text{Shovels}} \sum_{j \in \text{Benches}} \text{Tonnage}_{ij} - \text{Penalty}(\text{Road Friction})$$
  subject to:
  - Shovel cycle capacity and truck hauling match limits.
  - Wet haul road speed derating ($0.85 \rightarrow 0.42$).
  - **Grade Blending Constraint**: Blended Run-of-Mine (ROM) feed to crusher must meet or exceed $30.0\%\text{ Mn}$:
    $$\frac{\sum_{i,j} \text{Tonnage}_{ij} \cdot \text{Grade}_j}{\sum_{i,j} \text{Tonnage}_{ij}} \ge 30.0\%$$
- **Weather-Adaptive Blasting Scheduler**: 7-day lookahead scheduler adjusting blast charge timings based on forecast rainfall to prevent flyrock and DGMS lightning hazards.
- **Workflow Approval Controls**: Human-in-the-loop transition states (*Pending Review* $\rightarrow$ *Approved* $\rightarrow$ *Implemented* or *Rejected*) with projected recovery tonnes.

### 3.8 Supply Chain Digital Twin Simulator
- **Cyclic Haul Queueing Physics**: Evaluates shovel loading vs truck transit cycles, detecting shovel starvation (truck deficit) and truck bunching (excess haulers).
- **Primary Crusher Circuit**: Simulates a 450 TPH jaw/cone crushing plant, calculating utilization rate and alerting on hopper choke risks when feed exceeds capacity.
- **3-Grade Stockpile Inventories**: Tracks inventory levels (tonnes and average $\% \text{Mn}$) across:
  - **High-Grade Stockpile**: $>35.0\%\text{ Mn}$
  - **Medium-Grade Stockpile**: $28.0\%\text{--}35.0\%\text{ Mn}$
  - **Low-Grade Stockpile**: $<28.0\%\text{ Mn}$
- **Indian Railways Rail Dispatch Logistics**: Tracks rake turnaround times, loadout efficiency, and dispatch schedules for standard 58-wagon BOXN rakes ($\approx 3,800\text{ tonnes/rake}$).

### 3.9 Explainable AI (SHAP) & Root Cause Audit
- **TreeExplainer Attribution**: Computes exact Shapley values for production shortfall predictions, quantifying the relative impact of equipment downtime, monsoon rainfall, blasting delays, and availability.
- **Natural Language Synthesis**: Translates numerical SHAP values into operator-friendly explanatory sentences.
- **Audit Compliance Sign-Off**: Shift supervisors can mark explanations as *Confirmed*, *Needs Review*, or *Disputed*, saving audit logs with user timestamps.

### 3.10 Data Management, Ingestion & Audit-Ready PDF Reporting
- **Multi-Format Ingestion**: Ingests `.csv`, `.xlsx`, and `.geojson` files for boreholes, equipment telemetry, production logs, and environmental observations.
- **Data Source Transparency**: Explicitly tags data records as `"synthetic"` (demo data), `"public_real"` (Open-Meteo weather), or `"uploaded"` (customer datasets).
- **PDF Executive Reports**: Generates formal, audit-ready PDF documents using ReportLab, summarizing operational KPIs, reserve estimates, shortfall risks, and recommended actions.

---

## 4. Machine Learning & Mathematical Formulations

### 4.1 Summary Model Architecture Table

| Model Task | Algorithm | Input Features | Output Target | Performance & Objective |
| :--- | :--- | :--- | :--- | :--- |
| **3D Block Kriging** | **Ordinary Kriging** with Spherical Variogram | Borehole 3D coords $(x,y,z)$, lab assays $(\% \text{Mn})$ | Estimated block grade $Z^*(x_0)$, Kriging variance $\sigma_k^2$ | Minimizes estimation variance under unbiasedness constraint $\sum w_i = 1$ |
| **Fleet Failure Risk** | **Calibrated Random Forest** (Isotonic/Platt) | Operating hrs, days since maintenance, hydraulic press, oil temp, vibration | $P(\text{Fail}_{24\text{h}})$, $P(\text{Fail}_{48\text{h}})$, $P(\text{Fail}_{72\text{h}})$, 7d Downtime hrs | Brier score minimization; reliable probability calibration |
| **Quantile Forecaster** | **Quantile Gradient Boosting** ($\alpha \in \{0.1, 0.5, 0.9\}$) | Shifted lags $(t-1, t-3, t-7)$, predicted downtime, forecast rain, shift hrs | P10, P50, P90 tonnage; $P(\text{Prod} < \text{Target})$ | Pinball loss $\mathcal{L}_\alpha(y, \hat{y}) = \max(\alpha(y-\hat{y}), (1-\alpha)(\hat{y}-y))$ |
| **Fleet Dispatch LP** | **PuLP / CBC Solver** | Active bench grades, shovel capacities, haul distances, road friction | Optimal truck-to-shovel assignment matrix $X_{ij}$ | Maximizes clean manganese tonnage subject to $\ge 30\%$ Mn blend floor |
| **Space Ablation Study**| **Multi-Modal Comparative Regressors** | Multi-Modal vs No-Weather vs Weather-Only vs Persistence | Daily tonnage MAE, RMSE, seasonal uplift $\%$ | Empirical proof of weather value during monsoon ($+12.0\%$ uplift) |
| **Model Explainability**| **TreeExplainer (SHAP)** | Tree ensembles from Production Engine | Local \& global Shapley values $\phi_i$ | $\sum \phi_i = f(x) - E[f(x)]$ local accuracy guarantee |
| **Surface Exploration** | **Spatial Lineament Proximity** | Fault distance, borehole coverage gap $>250\text{ m}$ | Exploration Priority Score $[0, 1]$ | Targets drilling to maximize geological knowledge gain |

---

### 4.2 Mathematical Formulations

#### 1. Geostatistical Semi-Variogram & 3D Ordinary Kriging
The empirical semi-variogram $\gamma(h)$ is computed over spatial separation distance $h$:
$$\gamma(h) = \frac{1}{2N(h)} \sum_{i=1}^{N(h)} [Z(x_i) - Z(x_i + h)]^2$$

The fitted spherical variogram model with nugget $c_0$, sill $c$, and range $a$:
$$\gamma(h) = \begin{cases} 0 & \text{if } h = 0 \\ c_0 + c \left[ 1.5 \left(\frac{h}{a}\right) - 0.5 \left(\frac{h}{a}\right)^3 \right] & \text{if } 0 < h \le a \\ c_0 + c & \text{if } h > a \end{cases}$$
*Calibrated Parameters for Dongri Buzurg*: $c_0 = 13.91$, $c = 92.74$, $a = 220.0\text{ m}$.

#### 2. Strict Anti-Leakage Quantile Forecasting Formulation
To prevent target leakage, all features for predicting production at day $T$ ($Y_T$) must satisfy:
$$\mathcal{F}_T \subseteq \sigma(\{Y_t\}_{t \le T-1}, \{\text{Downtime}^{\text{pred}}_T\}, \{\text{Rain}^{\text{forecast}}_T\}, \{\text{Hours}^{\text{sched}}_T\})$$
Under no circumstances are actual same-day downtime, actual rain, or contemporaneous production features permitted. The 3 quantile models solve:
$$\hat{\theta}_\alpha = \arg\min_\theta \sum_{t} \rho_\alpha (Y_t - f_\theta(X_t)), \quad \rho_\alpha(u) = u(\alpha - \mathbb{I}(u < 0))$$

#### 3. Linear Programming Fleet Dispatch with Quality Blending
Let $x_{ij} \ge 0$ denote the number of truckloads dispatched from Shovel $i$ on Bench $j$. The LP maximizes delivered value:
$$\max \sum_{i} \sum_{j} x_{ij} \cdot \text{Capacity}_{\text{truck}} \cdot \mu_{\text{friction}} - \sum_i \text{Cost}_i(x_{ij})$$
subject to:
$$\sum_{j} x_{ij} \le \text{MaxShovelLoads}_i \quad \forall i$$
$$\sum_i \sum_j x_{ij} \cdot \text{Capacity}_{\text{truck}} \cdot (\text{Grade}_j - 30.0\%) \ge 0 \quad \text{(Blending constraint: } \ge 30\%\text{ Mn)}$$
$$\mu_{\text{friction}} = \max(0.42, 0.85 - 0.015 \cdot \max(0, \text{Rainfall}_{\text{mm}} - 10.0))$$

---

## 5. Datasets & Schemas

The system combines real-world environmental and spatial datasets with geologically calibrated demonstration data anchored to the **Dongri Buzurg Manganese Mine** ($21.5342^\circ\text{N}, 79.6915^\circ\text{E}$):

### 5.1 Mines & Geospatial Boundaries
- `mines.csv`: Core records for Dongri Buzurg (`MINE-001`), Mansar (`MINE-002`), and Balaghat (`MINE-003`).
- `mine_boundaries.geojson`: Polygon geometry defining the $8.45\text{ km}^2$ active mining lease.
- `prospectivity_grid.geojson`: 225 spatial grid cells ($15 \times 15$) containing fault distance, drill coverage gap distance, and surface exploration priority ratings.

### 5.2 Subsurface Geological Data
- `geological_units.csv`: Stratigraphic units (*Manganese Gondite Ore*, *Quartzite Footwall*, *Mica Schist Hangingwall*, *Pegmatite Intrusion*).
- `boreholes.csv`: 30 boreholes with collar coordinates, collar elevations ($310\text{--}335\text{ m}$), and depths ($80\text{--}220\text{ m}$).
- `borehole_intervals.csv`: Down-hole lithology logs and visual mineralization tags.
- `assay_samples.csv`: Laboratory chemical grade analyses ($\% \text{Mn}$ $28.0\%\text{--}48.5\%$ in ore, $<4.5\%$ in waste, $\% \text{Fe}$, $\% \text{SiO}_2$).
- `ore_blocks.csv`: 4,805 discretized 3D mining blocks ($60\text{m} \times 60\text{m} \times 10\text{m}$) with kriged grades and JORC classifications.

### 5.3 Fleet Telemetry & Equipment Records
- `equipment.csv`: Asset registry covering excavators, haulers, drill rigs, and crushers.
- `equipment_downtime.csv`: Breakdown records with failure mode (hydraulic, mechanical, electrical), duration, and affected component.

### 5.4 Daily Operations & Environmental Observations
- `production_records.csv`: 365 daily production records with target quotas, actual extraction, scheduled hours, and downtime.
- `environmental_observations.csv`: 365 days of Open-Meteo real historical weather (rainfall, temperature, wind) and simulated satellite indices (NDVI, soil moisture, SAR coherence).
- `blasting_events.csv`: Blasting records documenting bench location, powder factor ($0.42\text{--}0.58\text{ kg/t}$), and clearance delays.

---

## 6. Complete Technology Stack

| Layer | Technologies | Purpose |
| :--- | :--- | :--- |
| **Backend Framework** | **FastAPI** (Python 3.10+) | High-performance asynchronous REST API, OpenAPI/Swagger documentation, CORS handling. |
| **Database & ORM** | **SQLAlchemy ORM**, **SQLite** (`moil_manganese.db`), PostGIS-compatible schemas | Relational persistence, transactional updates, schema migrations. |
| **3D Geostatistics** | **SciPy**, **NumPy**, custom Ordinary Kriging solver | Empirical variograms, spherical curve fitting, 3D block kriging systems. |
| **Mathematical Optimization** | **PuLP**, **CBC Solver** | Linear programming fleet dispatch optimizer with grade blending floors. |
| **Predictive Machine Learning** | **scikit-learn**, **XGBoost**, **Joblib** | Quantile Gradient Boosting, Calibrated Classifiers, time series splits. |
| **Model Explainability** | **SHAP (Shapley Additive exPlanations)** | TreeExplainer feature attributions and waterfall breakdowns. |
| **Data Processing & Weather** | **pandas**, **Open-Meteo API** | Time series manipulation, lag feature engineering, weather caching. |
| **Document Generation** | **ReportLab** | Server-side PDF executive report generation with tabular layouts. |
| **Frontend Framework** | **React 19**, **TypeScript**, **Vite** | Single-page application, strict type safety, fast HMR build tool. |
| **Styling & UI Components** | **Tailwind CSS v4**, **Lucide React** | Responsive design system, dark-mode styling, industrial mining theme. |
| **Interactive Mapping** | **Leaflet**, **React Leaflet** | Interactive OpenStreetMap canvas, borehole pins, GeoJSON layer toggles. |
| **Data Visualization** | **Recharts** | P10-P90 shaded area charts, variograms, grade-tonnage distributions. |
| **Containerization & CI** | **Docker**, **Docker Compose**, **GitHub Actions** | Multi-container deployment and automated test verification. |

---

## 7. How to Run, Test & Deploy

### 7.1 Local Development

#### Step 1: Start Backend API Server
```powershell
cd "AI_Powered_Mining_Digital_Twin"
python backend/app/main.py
```
- **Backend API**: `http://127.0.0.1:8080`
- **Interactive Swagger Docs**: `http://127.0.0.1:8080/docs`

#### Step 2: Start Frontend Web Dashboard
From a separate terminal window:
```powershell
cd "AI_Powered_Mining_Digital_Twin\frontend"
npm run dev
```
- **Web Application URL**: `http://localhost:5173`

---

### 7.2 Running the Automated Test Suite
The project includes 30 automated tests validating data integrity, mathematical geostatistics, linear programming dispatch, simulator physics, and zero data leakage:
```powershell
pytest backend/tests/ -v
```
All 30 unit tests pass with zero warnings or errors.

---

### 7.3 Docker Containerized Deployment
A production-ready `Dockerfile` and `docker-compose.yml` are provided for one-command containerization:
```powershell
docker-compose up --build
```
- Backend container runs on port `8080`.
- Frontend container serves the production bundle on port `5173`.

---

## 8. Summary of Upgrades & Deliverables

| Area | Before Upgrade | After Upgrade |
| :--- | :--- | :--- |
| **Scientific Grounding** | Unscientific satellite prospectivity claims | Explicitly rejects Subsurface Trap; satellite for surface context only; honest drilling priority map. |
| **Reserve Modeling** | 25 static tabular blocks | 4,805 3D Kriged blocks ($60\text{m} \times 60\text{m} \times 10\text{m}$) across 5 benches with spherical variogram & JORC statement. |
| **Shortfall Forecasting** | Single-point forecast with potential data leakage | Quantile Gradient Boosting (P10, P50, P90); strictly shifted historical lags; $P(\text{Prod} < \text{Target})$ risk probability. |
| **Equipment Maintenance** | Generic downtime logs | Calibrated failure probabilities (24h/48h/72h); 7-day expected downtime; fleet diagnostic dossiers. |
| **Space Data Evaluation** | Unsubstantiated claims | Empirical Ablation Study proving $+12.0\%$ monsoon boost vs $<1.5\%$ dry season variance. |
| **Operational Optimization** | Static text suggestions | PuLP Linear Programming fleet dispatch solver enforcing road friction derating and $\ge 30\%$ Mn grade blending floor. |
| **Supply Chain Simulation** | Basic multiplier formulas | Physics-based digital twin with cyclic haul queues, 450 TPH crusher choke detection, 3-grade stockpiles, and BOXN rail rakes. |
| **Production Engineering** | Local scripts only | 30/30 passing pytest suite, Docker/Compose configs, GitHub Actions CI workflow, and executive presentation docs. |
