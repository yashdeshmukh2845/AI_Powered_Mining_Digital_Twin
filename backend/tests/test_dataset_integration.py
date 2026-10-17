import os
import sys
import json
import pytest
import pandas as pd
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.app.main import app
from backend.app.database.db import SessionLocal
from backend.app.database.models import (
    ProductionRecord, WeatherObservation, Borehole, BoreholeInterval,
    AssaySample, DataProvenance, SatelliteImageRecord
)
from backend.app.services.ingestion_service import IngestionService
from backend.app.services.report_service import ReportService
from backend.app.ml.production_model import ProductionModel
from backend.app.ml.eurosat_classifier import EuroSATClassifier

client = TestClient(app)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# 1. Reading all available datasets
def test_1_discover_all_available_datasets():
    datasets = IngestionService.discover_datasets()
    assert len(datasets) >= 5
    keys = {d["dataset_key"] for d in datasets}
    assert "mining_production_cleaned" in keys
    assert "mining_production_raw" in keys
    assert "monthly_production_summary" in keys
    assert "weather_open_meteo" in keys
    assert "eurosat_rgb_imagery" in keys
    assert "orebit_geology_nikel" in keys

# 2. Detecting their schemas and data types
def test_2_detect_schemas_and_types():
    prod_path = os.path.join(DATA_DIR, "mining_production_cleaned.csv")
    df = pd.read_csv(prod_path, nrows=10)
    expected_cols = [
        "Date", "Mine", "Shift", "Equipment", "Manpower",
        "Downtime_Hours", "Energy_Consumption_kWh", "Target_Tonnes",
        "Production_Tonnes", "Production_Efficiency_%"
    ]
    for c in expected_cols:
        assert c in df.columns
    assert pd.api.types.is_numeric_dtype(df["Production_Tonnes"])
    assert pd.api.types.is_numeric_dtype(df["Target_Tonnes"])

# 3. Handling metadata rows in weather CSV
def test_3_weather_csv_metadata_parsing():
    weather_path = os.path.join(DATA_DIR, "open-meteo-21.20N79.10E293m.csv")
    with open(weather_path, "r", encoding="utf-8") as f:
        l0 = f.readline()
        l1 = f.readline()
        l2 = f.readline()
        l3 = f.readline()
        
    assert "latitude" in l0.lower()
    assert "21.19" in l1
    assert "79.10" in l1
    assert l2.strip() == "" # Blank row separator
    assert "temperature_2m_mean" in l3
    
    # Read with skiprows=3
    df_w = pd.read_csv(weather_path, skiprows=3)
    assert len(df_w) == 2192
    assert "precipitation_sum (mm)" in df_w.columns

# 4. Validating borehole depths, intervals, coordinates, and assay joins
def test_4_borehole_geological_integrity():
    db = SessionLocal()
    try:
        bhs = db.query(Borehole).filter(Borehole.provenance_source == "orebit-datasets").all()
        assert len(bhs) == 350
        for b in bhs[:20]:
            assert b.total_depth > 0
            assert b.latitude is not None
            assert b.longitude is not None
            assert b.commodity == "Nickel Laterite"

        # Validate intervals: from_depth < to_depth
        intervals = db.query(BoreholeInterval).filter(BoreholeInterval.id.like("%OREBIT%")).limit(50).all()
        for i in intervals:
            assert i.from_depth < i.to_depth

        # Validate assays
        assays = db.query(AssaySample).filter(AssaySample.provenance_source == "orebit-datasets").limit(50).all()
        for a in assays:
            assert a.primary_grade >= 0.0
            assert a.commodity == "Nickel Laterite"
    finally:
        db.close()

# 5. Preventing duplicate imports and double-counting
def test_5_anti_double_counting_and_idempotence():
    db = SessionLocal()
    try:
        # Check that monthly records are NOT inserted into production_records
        shift_prods = db.query(ProductionRecord).filter(ProductionRecord.provenance_source == "mining_production_cleaned.csv").count()
        assert shift_prods == 5000

        # Re-running ingestion does not double count
        IngestionService.ingest_mining_production(db)
        post_shift_prods = db.query(ProductionRecord).filter(ProductionRecord.provenance_source == "mining_production_cleaned.csv").count()
        assert post_shift_prods == 5000
    finally:
        db.close()

# 6. Computing production aggregates correctly
def test_6_production_aggregation_accuracy():
    db = SessionLocal()
    try:
        # Calculate sum of shift records
        records = db.query(ProductionRecord).filter(ProductionRecord.provenance_source == "mining_production_cleaned.csv").all()
        df = pd.DataFrame([{
            "date": pd.to_datetime(r.date),
            "prod": r.actual_production_tonnes,
            "target": r.planned_target_tonnes
        } for r in records])
        
        total_prod = df["prod"].sum()
        total_target = df["target"].sum()
        
        # Monthly file totals
        monthly_df = pd.read_csv(os.path.join(DATA_DIR, "monthly_production.csv"))
        m_prod = monthly_df["Production_Tonnes"].sum()
        m_target = monthly_df["Target_Tonnes"].sum()
        
        # Must match exactly to 2 decimal places
        assert round(total_prod, 2) == round(m_prod, 2)
        assert round(total_target, 2) == round(m_target, 2)
    finally:
        db.close()

# 7. Preventing future-data leakage in forecasting
def test_7_no_future_data_leakage():
    prod_model = ProductionModel()
    db = SessionLocal()
    try:
        records = db.query(ProductionRecord).order_by(ProductionRecord.date.asc()).all()
        df = pd.DataFrame([{
            "date": r.date,
            "actual_production_tonnes": r.actual_production_tonnes,
            "operating_hours": r.operating_hours,
            "downtime_hours": r.downtime_hours,
            "equipment_availability_pct": r.equipment_availability_pct,
            "rainfall_mm": r.rainfall_mm,
            "blasting_delay_hours": r.blasting_delay_hours,
            "manpower": r.manpower if r.manpower else 25,
            "energy_consumption_kwh": r.energy_consumption_kwh if r.energy_consumption_kwh else 2500.0,
            "is_synthetic": r.is_synthetic
        } for r in records])
        
        metrics = prod_model.train(df)
        assert "evaluation_method" in metrics
        assert "Chronological" in metrics["evaluation_method"]
        # Train period must precede test period
        train_end = metrics["train_period"].split(" to ")[1]
        test_start = metrics["test_period"].split(" to ")[0]
        assert train_end <= test_start
        assert "improvement_over_baseline_pct" in metrics
    finally:
        db.close()

# 8. Handling missing target columns and unavailable model features
def test_8_graceful_missing_features_handling():
    prod_model = ProductionModel()
    # Missing manpower and energy columns
    incomplete_df = pd.DataFrame([{
        "operating_hours": 7.0,
        "downtime_hours": 1.0,
        "equipment_availability_pct": 87.5
    }])
    pred = prod_model.predict(incomplete_df)
    assert len(pred) == 1
    assert pred[0] > 0

    # Shortfall with 0 target
    sf_zero = ProductionModel.calculate_shortfall_risk(0.0, 1500.0)
    assert sf_zero["shortfall_tonnes"] == 0.0
    assert sf_zero["shortfall_pct"] == 0.0

# 9. Distinguishing imported, synthetic, derived, and predicted data
def test_9_provenance_and_data_origin_distinction():
    db = SessionLocal()
    try:
        provs = db.query(DataProvenance).all()
        origins = {p.data_origin for p in provs}
        assert "imported_operational_data" in origins
        assert "observed_grid_data" in origins
        assert "derived_monthly_aggregation" in origins
        assert "benchmark_exploration_dataset" in origins
        
        # Verify orebit disclaimer
        orebit_prov = db.query(DataProvenance).filter(DataProvenance.dataset_key == "orebit_geology_nikel").first()
        assert orebit_prov.commodity == "Nickel Laterite (Ni/Co/Fe)"
        assert "NOT official MOIL" in orebit_prov.validation_warnings
    finally:
        db.close()

# 10. API endpoints and frontend integration
def test_10_api_endpoints_integration():
    # Provenance
    res_p = client.get("/api/data/provenance")
    assert res_p.status_code == 200
    assert len(res_p.json()) >= 5

    # Monthly production
    res_m = client.get("/api/production/monthly")
    assert res_m.status_code == 200
    assert len(res_m.json()) == 24

    # Weather station
    res_w = client.get("/api/weather/station")
    assert res_w.status_code == 200
    assert "21.19" in str(res_w.json()["latitude"])

    # Geology summary
    res_g = client.get("/api/geology/summary")
    assert res_g.status_code == 200
    assert res_g.json()["commodity"] == "Nickel Laterite"

    # Satellite summary
    res_s = client.get("/api/satellite/summary")
    assert res_s.status_code == 200
    assert res_s.json()["num_classes"] == 10

    # Satellite samples
    res_samp = client.get("/api/satellite/samples")
    assert res_samp.status_code == 200
    assert len(res_samp.json()) > 0

# 11. Generating reports with provenance and disclaimers
def test_11_reports_generation_with_audit_disclaimers():
    res_csv = client.get("/api/reports/summary?format=csv")
    assert res_csv.status_code == 200
    csv_text = res_csv.text
    assert "DATA PROVENANCE & SOURCE AUDIT" in csv_text
    assert "SCIENTIFIC LIMITATIONS & DISCLAIMERS" in csv_text
    assert "mining_production_cleaned" in csv_text

    res_pdf = client.get("/api/reports/summary?format=pdf")
    assert res_pdf.status_code == 200
    assert res_pdf.headers["content-type"] == "application/pdf"
    assert len(res_pdf.content) > 1000
