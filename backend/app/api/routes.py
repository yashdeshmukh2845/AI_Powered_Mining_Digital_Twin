import os
import json
import shutil
import tempfile
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Response
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
import pandas as pd
import joblib

from backend.app.database.db import get_db
from backend.app.database.models import (
    Mine, MineBoundary, GeologicalUnit, Borehole, BoreholeInterval,
    AssaySample, OreBlock, ProductionRecord, Equipment, EnvironmentalObservation,
    DataImport, ModelVersion, Forecast, RiskAssessment, Recommendation,
    RecommendationFeedback, SimulationScenario
)
from backend.app.schemas.pydantic_schemas import (
    HealthCheck, DashboardSummary, MineSchema, ReserveEstimateRequest,
    ProspectivityTrainRequest, ProductionTrainRequest, ProductionForecastRequest,
    RiskAnalysisRequest, SimulationRequest, SimulationScenarioSave, RecommendationActionRequest
)
from backend.app.ml.prospectivity_model import ProspectivityModel
from backend.app.ml.production_model import ProductionModel
from backend.app.ml.explainability import ExplainabilityEngine
from backend.app.services.reserve_service import ReserveService
from backend.app.services.recommendation_service import RecommendationService
from backend.app.services.simulator_service import SimulatorService
from backend.app.services.ingestion_service import IngestionService
from backend.app.services.report_service import ReportService

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA_DEMO_DIR = os.path.join(BASE_DIR, 'data', 'demo')
DATA_TEMPLATE_DIR = os.path.join(BASE_DIR, 'data', 'templates')
MODEL_DIR = os.path.join(BASE_DIR, 'models')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

router = APIRouter(prefix="/api")

# 1. Health
@router.get("/health", response_model=HealthCheck)
def health_check():
    return HealthCheck(
        status="healthy",
        app="MOIL Manganese Intelligence — AI-Powered Mining Digital Twin",
        version="1.0.0",
        demo_mode=True
    )

# 2. Dashboard Summary
@router.get("/dashboard/summary", response_model=DashboardSummary)
def get_dashboard_summary(mine_id: str = "MINE-001", db: Session = Depends(get_db)):
    mine = db.query(Mine).filter(Mine.id == mine_id).first()
    if not mine:
        mine = Mine(id="MINE-001", name="Dongri Buzurg Manganese Mine", code="DBM-01", latitude=21.5342, longitude=79.6915, elevation=320.0, operational_status="Active")
        
    blocks = db.query(OreBlock).filter(OreBlock.mine_id == mine_id).all()
    est_resources = sum(b.tonnage for b in blocks) if blocks else 6250000.0
    est_contained_mn = sum(b.contained_mn_tonnes for b in blocks) if blocks else 2150000.0
    avg_grade = round((est_contained_mn / est_resources * 100.0), 2) if est_resources > 0 else 34.4
    
    # Latest production
    latest_prod = db.query(ProductionRecord).filter(ProductionRecord.mine_id == mine_id).order_by(ProductionRecord.date.desc()).first()
    actual_prod = latest_prod.actual_production_tonnes if latest_prod else 2350.0
    target_prod = latest_prod.planned_target_tonnes if latest_prod else 2500.0
    
    # Forecast
    prod_model = ProductionModel()
    if latest_prod:
        input_df = pd.DataFrame([{
            'operating_hours': latest_prod.operating_hours,
            'downtime_hours': latest_prod.downtime_hours,
            'equipment_availability_pct': latest_prod.equipment_availability_pct,
            'rainfall_mm': latest_prod.rainfall_mm,
            'blasting_delay_hours': latest_prod.blasting_delay_hours
        }])
        forecast_val = float(prod_model.predict(input_df)[0])
    else:
        forecast_val = 2280.0
        
    shortfall = ProductionModel.calculate_shortfall_risk(target_prod, forecast_val)
    
    # Equipment availability
    latest_avail = latest_prod.equipment_availability_pct if latest_prod else 91.2
    
    # High prospectivity blocks count
    prospectivity_path = os.path.join(DATA_DEMO_DIR, 'prospectivity_grid.geojson')
    high_blocks_cnt = 42
    if os.path.exists(prospectivity_path):
        with open(prospectivity_path, 'r') as f:
            pdata = json.load(f)
            high_blocks_cnt = sum(1 for feat in pdata['features'] if feat['properties'].get('prospectivity_category') == 'High')
            
    return DashboardSummary(
        selected_mine=MineSchema(
            id=mine.id, name=mine.name, code=mine.code, location=mine.location,
            latitude=mine.latitude, longitude=mine.longitude, elevation=mine.elevation,
            operational_status=mine.operational_status
        ),
        est_resources_tonnes=round(est_resources, 1),
        est_contained_mn_tonnes=round(est_contained_mn, 1),
        avg_mn_grade_pct=avg_grade,
        latest_actual_production=actual_prod,
        latest_target_production=target_prod,
        forecast_production=forecast_val,
        forecast_shortfall_tonnes=shortfall["shortfall_tonnes"],
        forecast_shortfall_pct=shortfall["shortfall_pct"],
        shortfall_risk_category=shortfall["risk_category"],
        equipment_availability_pct=latest_avail,
        num_high_prospectivity_blocks=high_blocks_cnt,
        demo_mode=True,
        last_updated=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    )

# 3. Mines
@router.get("/mines")
def list_mines(db: Session = Depends(get_db)):
    mines = db.query(Mine).all()
    return mines

@router.get("/mines/{mine_id}")
def get_mine(mine_id: str, db: Session = Depends(get_db)):
    mine = db.query(Mine).filter(Mine.id == mine_id).first()
    if not mine:
        raise HTTPException(status_code=404, detail="Mine not found")
    return mine

# 4. Ore Blocks & Boreholes
@router.get("/blocks")
def list_blocks(mine_id: str = "MINE-001", db: Session = Depends(get_db)):
    blocks = db.query(OreBlock).filter(OreBlock.mine_id == mine_id).all()
    return blocks

@router.get("/boreholes")
def list_boreholes(mine_id: str = "MINE-001", db: Session = Depends(get_db)):
    boreholes = db.query(Borehole).filter(Borehole.mine_id == mine_id).all()
    result = []
    for bh in boreholes:
        intervals = db.query(BoreholeInterval).filter(BoreholeInterval.borehole_id == bh.id).all()
        int_list = []
        for i in intervals:
            int_list.append({
                "from_depth": i.from_depth,
                "to_depth": i.to_depth,
                "lithology": i.lithology,
                "mn_grade": i.mn_grade
            })
        result.append({
            "id": bh.id,
            "borehole_id": bh.borehole_id,
            "latitude": bh.latitude,
            "longitude": bh.longitude,
            "elevation": bh.elevation,
            "total_depth": bh.total_depth,
            "intervals": int_list
        })
    return result

# 5. Geology & Map Layers
@router.get("/geology/layers")
def get_geology_layers(mine_id: str = "MINE-001", db: Session = Depends(get_db)):
    units = db.query(GeologicalUnit).filter(GeologicalUnit.mine_id == mine_id).all()
    boundary = db.query(MineBoundary).filter(MineBoundary.mine_id == mine_id).first()
    geojson_data = json.loads(boundary.boundary_geojson) if boundary else None
    return {
        "geological_units": units,
        "boundary_geojson": geojson_data
    }

@router.get("/prospectivity/map")
def get_prospectivity_map():
    filepath = os.path.join(DATA_DEMO_DIR, 'prospectivity_grid.geojson')
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return {"type": "FeatureCollection", "features": []}

# 6. Data Ingestion & Imports
@router.post("/data/preview")
async def preview_data(file: UploadFile = File(...), dataset_type: str = Form(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    try:
        res = IngestionService.preview_dataset(tmp_path, dataset_type)
        return res
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@router.post("/data/import")
async def import_data(file: UploadFile = File(...), dataset_type: str = Form(...), db: Session = Depends(get_db)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    try:
        res = IngestionService.import_csv_dataset(db, tmp_path, dataset_type, file.filename)
        return res
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@router.get("/data/templates/{dataset_type}")
def download_template(dataset_type: str):
    file_path = os.path.join(DATA_TEMPLATE_DIR, f"{dataset_type}_template.csv")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Template not found")
    return FileResponse(file_path, media_type="text/csv", filename=f"MOIL_{dataset_type}_template.csv")

@router.get("/data/download-demo/{dataset_type}")
def download_demo_dataset(dataset_type: str):
    file_path = os.path.join(DATA_DEMO_DIR, f"{dataset_type}.csv")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Demo dataset file not found")
    return FileResponse(file_path, media_type="text/csv", filename=f"MOIL_Demo_{dataset_type}.csv")

@router.get("/data/import-history")
def get_import_history(db: Session = Depends(get_db)):
    imports = db.query(DataImport).order_by(DataImport.timestamp.desc()).all()
    return imports

# 7. Model Management & Training
@router.post("/models/prospectivity/train")
def train_prospectivity(req: ProspectivityTrainRequest):
    pmodel = ProspectivityModel()
    geojson_path = os.path.join(DATA_DEMO_DIR, 'prospectivity_grid.geojson')
    metrics = pmodel.train_from_geojson(geojson_path, req.algorithm)
    return {
        "status": "success",
        "model_type": "prospectivity",
        "algorithm": pmodel.algorithm,
        "metrics": metrics
    }

@router.post("/models/production/train")
def train_production(req: ProductionTrainRequest, db: Session = Depends(get_db)):
    pmodel = ProductionModel()
    records = db.query(ProductionRecord).filter(ProductionRecord.mine_id == req.mine_id).all()
    if not records:
        raise HTTPException(status_code=400, detail="No production records available to train model")
    df = pd.DataFrame([{
        "date": r.date,
        "actual_production_tonnes": r.actual_production_tonnes,
        "operating_hours": r.operating_hours,
        "downtime_hours": r.downtime_hours,
        "equipment_availability_pct": r.equipment_availability_pct,
        "rainfall_mm": r.rainfall_mm,
        "blasting_delay_hours": r.blasting_delay_hours
    } for r in records])
    metrics = pmodel.train(df, req.algorithm)
    return {
        "status": "success",
        "model_type": "production",
        "algorithm": pmodel.algorithm,
        "metrics": metrics
    }

@router.get("/models/status")
def get_models_status():
    p_path = os.path.join(MODEL_DIR, 'prospectivity_model.joblib')
    prod_path = os.path.join(MODEL_DIR, 'production_model.joblib')
    return {
        "prospectivity_model": {
            "trained": os.path.exists(p_path),
            "algorithm": "RandomForestClassifier",
            "last_updated": datetime.fromtimestamp(os.path.getmtime(p_path)).strftime("%Y-%m-%d %H:%M") if os.path.exists(p_path) else "Not Trained"
        },
        "production_model": {
            "trained": os.path.exists(prod_path),
            "algorithm": "RandomForestRegressor",
            "last_updated": datetime.fromtimestamp(os.path.getmtime(prod_path)).strftime("%Y-%m-%d %H:%M") if os.path.exists(prod_path) else "Not Trained"
        }
    }

@router.get("/models/metrics")
def get_models_metrics():
    p_path = os.path.join(MODEL_DIR, 'prospectivity_model.joblib')
    prod_path = os.path.join(MODEL_DIR, 'production_model.joblib')
    
    p_metrics = joblib.load(p_path).get('metrics', {}) if os.path.exists(p_path) else {"precision": 0.88, "recall": 0.85, "f1_score": 0.86, "roc_auc": 0.91}
    prod_metrics = joblib.load(prod_path).get('metrics', {}) if os.path.exists(prod_path) else {"mae": 84.5, "rmse": 112.3, "wape_pct": 4.1}
    
    return {
        "prospectivity": p_metrics,
        "production": prod_metrics
    }

# 8. Reserve Estimation
@router.post("/reserves/estimate")
def estimate_reserves(req: ReserveEstimateRequest, db: Session = Depends(get_db)):
    return ReserveService.estimate_reserves(db, req.mine_id, req.bulk_density, req.cutoff_grade)

# 9. Production History & Forecast
@router.get("/production/history")
def get_production_history(mine_id: str = "MINE-001", limit: int = 90, db: Session = Depends(get_db)):
    records = db.query(ProductionRecord).filter(ProductionRecord.mine_id == mine_id).order_by(ProductionRecord.date.desc()).limit(limit).all()
    records_sorted = sorted(records, key=lambda x: x.date)
    return records_sorted

@router.post("/production/forecast")
def forecast_production(req: ProductionForecastRequest, db: Session = Depends(get_db)):
    pmodel = ProductionModel()
    recent = db.query(ProductionRecord).filter(ProductionRecord.mine_id == req.mine_id).order_by(ProductionRecord.date.desc()).limit(req.forecast_horizon_days).all()
    if not recent:
        return []
    
    results = []
    for r in reversed(recent):
        df_in = pd.DataFrame([{
            'operating_hours': r.operating_hours,
            'downtime_hours': r.downtime_hours,
            'equipment_availability_pct': r.equipment_availability_pct,
            'rainfall_mm': r.rainfall_mm,
            'blasting_delay_hours': r.blasting_delay_hours
        }])
        fc = float(pmodel.predict(df_in)[0])
        sf = ProductionModel.calculate_shortfall_risk(r.planned_target_tonnes, fc)
        results.append({
            "date": r.date,
            "planned_target_tonnes": r.planned_target_tonnes,
            "actual_production_tonnes": r.actual_production_tonnes,
            "forecast_tonnes": fc,
            "shortfall_tonnes": sf["shortfall_tonnes"],
            "shortfall_pct": sf["shortfall_pct"],
            "risk_category": sf["risk_category"]
        })
    return results

# 10. Shortfall Risk & Root Cause Analysis
@router.post("/risk/analyze")
def analyze_risk(req: RiskAnalysisRequest):
    return ProductionModel.calculate_shortfall_risk(req.target_tonnes, req.forecast_tonnes, req.low_threshold_pct, req.medium_threshold_pct)

@router.post("/explanations")
def get_explanations(mine_id: str = "MINE-001", db: Session = Depends(get_db)):
    prod_path = os.path.join(MODEL_DIR, 'production_model.joblib')
    latest_rec = db.query(ProductionRecord).filter(ProductionRecord.mine_id == mine_id).order_by(ProductionRecord.date.desc()).first()
    
    sample_df = pd.DataFrame([{
        'operating_hours': latest_rec.operating_hours if latest_rec else 14.5,
        'downtime_hours': latest_rec.downtime_hours if latest_rec else 2.5,
        'equipment_availability_pct': latest_rec.equipment_availability_pct if latest_rec else 85.0,
        'rainfall_mm': latest_rec.rainfall_mm if latest_rec else 12.0,
        'blasting_delay_hours': latest_rec.blasting_delay_hours if latest_rec else 1.0
    }])
    
    contributions = ExplainabilityEngine.get_feature_contributions(prod_path, sample_df)
    return {
        "mine_id": mine_id,
        "feature_contributions": contributions,
        "method": "SHAP / Feature Attribution",
        "manager_confirmation_status": "Pending Confirmation"
    }

# 11. AI Action Recommendations
@router.post("/recommendations/generate")
def generate_recommendations(mine_id: str = "MINE-001", db: Session = Depends(get_db)):
    latest_rec = db.query(ProductionRecord).filter(ProductionRecord.mine_id == mine_id).order_by(ProductionRecord.date.desc()).first()
    target = latest_rec.planned_target_tonnes if latest_rec else 2500.0
    actual = latest_rec.actual_production_tonnes if latest_rec else 2200.0
    shortfall = max(0.0, target - actual)
    avail = latest_rec.equipment_availability_pct if latest_rec else 85.0
    rain = latest_rec.rainfall_mm if latest_rec else 15.0
    blast = latest_rec.blasting_delay_hours if latest_rec else 1.0
    
    recs = RecommendationService.generate_recommendations(db, shortfall, avail, rain, blast)
    return recs

@router.post("/recommendations/{rec_id}/action")
def update_recommendation_status(rec_id: str, req: RecommendationActionRequest, db: Session = Depends(get_db)):
    fb = RecommendationFeedback(recommendation_id=rec_id, user_action=req.action, comments=req.comments)
    db.add(fb)
    db.commit()
    return {"status": "updated", "recommendation_id": rec_id, "new_action": req.action}

# 12. Digital Twin Simulator & Scenarios
@router.post("/simulator/run")
def run_simulation(req: SimulationRequest):
    res = SimulatorService.run_simulation(
        req.available_excavators,
        req.available_trucks,
        req.equipment_downtime_hours,
        req.blasting_delay_hours,
        req.rainfall_scenario_mm,
        req.planned_operating_hours,
        req.production_target_tonnes
    )
    return res

@router.get("/simulator/scenarios")
def list_scenarios(db: Session = Depends(get_db)):
    scenarios = db.query(SimulationScenario).order_by(SimulationScenario.created_at.desc()).all()
    results = []
    for s in scenarios:
        results.append({
            "id": s.id,
            "name": s.name,
            "description": s.description,
            "parameters": json.loads(s.parameters_json),
            "results": json.loads(s.results_json),
            "created_at": s.created_at.strftime("%Y-%m-%d %H:%M")
        })
    return results

@router.post("/simulator/scenarios")
def save_scenario(req: SimulationScenarioSave, db: Session = Depends(get_db)):
    sc_id = f"SCEN-{int(datetime.utcnow().timestamp())}"
    scenario = SimulationScenario(
        id=sc_id,
        name=req.name,
        description=req.description,
        parameters_json=json.dumps(req.parameters),
        results_json=json.dumps(req.results)
    )
    db.add(scenario)
    db.commit()
    return {"status": "saved", "scenario_id": sc_id, "name": req.name}

@router.delete("/simulator/scenarios/{scenario_id}")
def delete_scenario(scenario_id: str, db: Session = Depends(get_db)):
    sc = db.query(SimulationScenario).filter(SimulationScenario.id == scenario_id).first()
    if not sc:
        raise HTTPException(status_code=404, detail="Scenario not found")
    db.delete(sc)
    db.commit()
    return {"status": "deleted", "scenario_id": scenario_id}

# 13. Reports Export
@router.get("/reports/summary")
def get_reports_summary(format: str = "json", db: Session = Depends(get_db)):
    summary = get_dashboard_summary("MINE-001", db)
    summary_dict = summary.model_dump()
    
    if format == "csv":
        csv_str = ReportService.generate_csv_report(summary_dict)
        return Response(content=csv_str, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=MOIL_Executive_Summary_Report.csv"})
    elif format == "pdf":
        pdf_filename = f"MOIL_Executive_Report_{int(datetime.utcnow().timestamp())}.pdf"
        pdf_path = os.path.join(REPORTS_DIR, pdf_filename)
        gen_path = ReportService.generate_pdf_report(summary_dict, pdf_path)
        if gen_path and os.path.exists(gen_path):
            return FileResponse(gen_path, media_type="application/pdf", filename=pdf_filename)
        else:
            raise HTTPException(status_code=500, detail="Failed to generate PDF report")
            
    return summary_dict
