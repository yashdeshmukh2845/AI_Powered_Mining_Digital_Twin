import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.app.main import app
from backend.app.ml.production_model import ProductionModel
from backend.app.services.simulator_service import SimulatorService

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["demo_mode"] is True

def test_dashboard_summary():
    response = client.get("/api/dashboard/summary?mine_id=MINE-001")
    assert response.status_code == 200
    data = response.json()
    assert "selected_mine" in data
    assert data["est_resources_tonnes"] > 0
    assert data["est_contained_mn_tonnes"] > 0
    assert data["avg_mn_grade_pct"] > 0

def test_reserve_estimation_calculations():
    response = client.post("/api/reserves/estimate", json={
        "mine_id": "MINE-001",
        "bulk_density": 3.4,
        "cutoff_grade": 15.0
    })
    assert response.status_code == 200
    data = response.json()
    assert data["bulk_density_t_per_m3"] == 3.4
    assert data["total_ore_tonnage"] == data["total_volume_m3"] * 3.4
    assert "categories" in data
    assert "Measured" in data["categories"]

def test_shortfall_risk_threshold_boundaries():
    # 1. Low risk: < 5% shortfall
    low_res = ProductionModel.calculate_shortfall_risk(2500.0, 2420.0, low_thresh=5.0, med_thresh=10.0)
    assert low_res["shortfall_pct"] < 5.0
    assert low_res["risk_category"] == "Low"

    # 2. Medium risk: 5% to 10% shortfall
    med_res = ProductionModel.calculate_shortfall_risk(2500.0, 2300.0, low_thresh=5.0, med_thresh=10.0)
    assert 5.0 <= med_res["shortfall_pct"] < 10.0
    assert med_res["risk_category"] == "Medium"

    # 3. High risk: >= 10% shortfall
    high_res = ProductionModel.calculate_shortfall_risk(2500.0, 2100.0, low_thresh=5.0, med_thresh=10.0)
    assert high_res["shortfall_pct"] >= 10.0
    assert high_res["risk_category"] == "High"

def test_prospectivity_model_training_api():
    response = client.post("/api/models/prospectivity/train", json={
        "mine_id": "MINE-001",
        "algorithm": "RandomForest"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "f1_score" in data["metrics"]
    assert data["metrics"]["f1_score"] > 0.5

def test_production_model_training_api():
    response = client.post("/api/models/production/train", json={
        "mine_id": "MINE-001",
        "algorithm": "RandomForest"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "mae" in data["metrics"]
    assert data["metrics"]["wape_pct"] < 15.0

def test_simulator_capacity_physics():
    sim_res = SimulatorService.run_simulation(
        available_excavators=2,
        available_trucks=3,
        equipment_downtime_hours=2.0,
        blasting_delay_hours=1.0,
        rainfall_scenario_mm=0.0,
        planned_operating_hours=16.0,
        production_target_tonnes=2500.0
    )
    assert sim_res["net_operating_hours"] == 13.0
    assert sim_res["fleet_throughput_tph"] == 540.0 # Min(2*350=700, 3*180=540) = 540
    assert sim_res["scenario_forecast_tonnes"] == 13.0 * 540.0
    assert sim_res["revised_shortfall_tonnes"] == max(0.0, 2500.0 - (13.0 * 540.0))

def test_scenario_save_and_delete():
    # Save
    save_res = client.post("/api/simulator/scenarios", json={
        "name": "Test Rainy Season Plan",
        "description": "Simulation under 25mm rainfall",
        "parameters": {"available_excavators": 2, "available_trucks": 4},
        "results": {"scenario_forecast_tonnes": 2100.0}
    })
    assert save_res.status_code == 200
    sc_id = save_res.json()["scenario_id"]

    # List
    list_res = client.get("/api/simulator/scenarios")
    assert list_res.status_code == 200
    scenarios = list_res.json()
    assert any(s["id"] == sc_id for s in scenarios)

    # Delete
    del_res = client.delete(f"/api/simulator/scenarios/{sc_id}")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "deleted"

def test_reports_summary_csv_and_pdf():
    # CSV
    csv_res = client.get("/api/reports/summary?format=csv")
    assert csv_res.status_code == 200
    assert "MOIL MANGANESE INTELLIGENCE" in csv_res.text

    # PDF
    pdf_res = client.get("/api/reports/summary?format=pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
