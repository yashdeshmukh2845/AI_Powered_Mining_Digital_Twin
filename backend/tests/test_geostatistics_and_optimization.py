import pytest
import numpy as np
from sqlalchemy.orm import Session
from backend.app.database.db import SessionLocal
from backend.app.services.geostatistics_service import GeostatisticsService
from backend.app.services.optimization_service import OptimizationService
from backend.app.ml.equipment_failure_model import EquipmentFailureModel
from backend.app.ml.ablation_study import AblationStudyService
from backend.app.services.simulator_service import SimulatorService

def test_geostatistics_variogram_calculation():
    var_res = GeostatisticsService.compute_variogram('mn_grade')
    assert "fitted_curve" in var_res
    assert var_res["nugget_c0"] >= 0.0
    assert var_res["sill_c"] > var_res["nugget_c0"]
    assert var_res["range_a_meters"] > 50.0
    assert len(var_res["fitted_curve"]["lags"]) > 0
    assert len(var_res["fitted_curve"]["semivariance"]) == len(var_res["fitted_curve"]["lags"])

def test_block_model_generation_and_jorc():
    bm = GeostatisticsService.generate_or_get_block_model()
    assert bm["total_blocks"] > 1000
    assert bm["total_tonnage_tonnes"] > 0
    assert "jorc_resource_categories" in bm
    assert "Measured" in bm["jorc_resource_categories"]
    assert "Indicated" in bm["jorc_resource_categories"]
    assert "Inferred" in bm["jorc_resource_categories"]
    
    # Grade-Tonnage curve verification
    assert len(bm["grade_tonnage_curve"]) >= 5
    first_pt = bm["grade_tonnage_curve"][0]
    last_pt = bm["grade_tonnage_curve"][-1]
    # Higher cutoff grade must have less or equal tonnage than lower cutoff
    assert first_pt["ore_tonnage_tonnes"] >= last_pt["ore_tonnage_tonnes"]

def test_fleet_dispatch_lp_solver():
    db = SessionLocal()
    try:
        opt_res = OptimizationService.optimize_fleet_dispatch(
            db=db,
            target_tonnes=2500.0,
            forecast_rain_mm=12.0,
            blend_target_mn_pct=29.0
        )
        assert opt_res["solver_status"] in ["Optimal", "Feasible"]
        assert opt_res["optimized_total_tonnes"] > 0
        assert opt_res["blended_grades"]["mn_grade_pct"] >= 28.5
        assert len(opt_res["bench_allocations"]) == 3
        # Rain friction must derate truck cycle time
        assert opt_res["rain_speed_derating_pct"] > 0.0
    finally:
        db.close()

def test_blasting_window_optimizer():
    db = SessionLocal()
    try:
        blast_res = OptimizationService.schedule_blasting_window(db, "MINE-001")
        assert "optimal_blast_day" in blast_res
        assert blast_res["optimal_window_score"] >= 0.0
        assert len(blast_res["weekly_lookahead"]) == 7
        assert blast_res["evacuation_radius_meters"] >= 500.0
    finally:
        db.close()

def test_equipment_failure_risk_bounds():
    db = SessionLocal()
    try:
        model = EquipmentFailureModel()
        risk_res = model.predict_equipment_risks(db, "MINE-001")
        assert risk_res["fleet_count"] > 0
        assert 0.0 <= risk_res["fleet_health_score_avg"] <= 100.0
        assert risk_res["expected_total_downtime_hours_next_7d"] >= 0.0
        
        for eq in risk_res["equipment"]:
            assert 0.0 <= eq["failure_risk_24h"] <= 1.0
            assert 0.0 <= eq["failure_risk_48h"] <= 1.0
            assert 0.0 <= eq["failure_risk_72h"] <= 1.0
            assert eq["failure_risk_24h"] <= eq["failure_risk_48h"] <= eq["failure_risk_72h"]
            assert 0.0 <= eq["health_score"] <= 100.0
    finally:
        db.close()

def test_ablation_study_integrity():
    res = AblationStudyService.get_ablation_results()
    assert "model_comparison" in res
    assert len(res["model_comparison"]) == 4
    assert res["monsoon_accuracy_gain"]["mae_gain_pct"] > 0.0
    assert len(res["feature_importances"]) > 0
    assert len(res["lag_effects"]) == 4

def test_simulator_supply_chain_extensions():
    sim = SimulatorService.run_simulation(
        available_excavators=3,
        available_trucks=6,
        equipment_downtime_hours=1.0,
        blasting_delay_hours=0.5,
        rainfall_scenario_mm=15.0,
        planned_operating_hours=16.0,
        production_target_tonnes=2500.0,
        crusher_capacity_tph=450.0,
        rail_rakes_available=1
    )
    assert "queueing_physics" in sim
    assert "crushing_circuit" in sim
    assert "stockpiles" in sim
    assert "rail_dispatch" in sim
    assert sim["rail_dispatch"]["total_dispatched_tonnes"] == 3800.0
    assert sim["crushing_circuit"]["crushed_ore_tonnes"] > 0
