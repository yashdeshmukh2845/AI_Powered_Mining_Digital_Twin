from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime

class HealthCheck(BaseModel):
    status: str
    app: str
    version: str
    demo_mode: bool = True

class MineSchema(BaseModel):
    id: str
    name: str
    code: str
    location: Optional[str] = None
    latitude: float
    longitude: float
    elevation: float
    operational_status: str

class BoreholeSchema(BaseModel):
    id: str
    mine_id: str
    borehole_id: str
    latitude: float
    longitude: float
    elevation: float
    total_depth: float
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class OreBlockSchema(BaseModel):
    id: str
    mine_id: str
    block_code: str
    min_x: float
    max_x: float
    min_y: float
    max_y: float
    min_z: float
    max_z: float
    volume_m3: float
    bulk_density: float
    tonnage: float
    est_mn_grade: float
    contained_mn_tonnes: float
    category: str

class DashboardSummary(BaseModel):
    selected_mine: MineSchema
    est_resources_tonnes: float
    est_contained_mn_tonnes: float
    avg_mn_grade_pct: float
    latest_actual_production: float
    latest_target_production: float
    forecast_production: float
    forecast_shortfall_tonnes: float
    forecast_shortfall_pct: float
    shortfall_risk_category: str
    equipment_availability_pct: float
    num_high_prospectivity_blocks: int
    demo_mode: bool = True
    last_updated: str

class ReserveEstimateRequest(BaseModel):
    mine_id: str = "MINE-001"
    bulk_density: float = 3.4
    cutoff_grade: float = 15.0

class ProspectivityTrainRequest(BaseModel):
    mine_id: str = "MINE-001"
    algorithm: str = "RandomForest"

class ProductionTrainRequest(BaseModel):
    mine_id: str = "MINE-001"
    algorithm: str = "RandomForest"

class ProductionForecastRequest(BaseModel):
    mine_id: str = "MINE-001"
    forecast_horizon_days: int = 7

class RiskAnalysisRequest(BaseModel):
    target_tonnes: float
    forecast_tonnes: float
    low_threshold_pct: float = 5.0
    medium_threshold_pct: float = 10.0

class SimulationRequest(BaseModel):
    available_excavators: int = 2
    available_trucks: int = 3
    equipment_downtime_hours: float = 2.0
    blasting_delay_hours: float = 1.0
    rainfall_scenario_mm: float = 0.0
    planned_operating_hours: float = 16.0
    production_target_tonnes: float = 2500.0

class SimulationScenarioSave(BaseModel):
    name: str
    description: Optional[str] = None
    parameters: Dict[str, Any]
    results: Dict[str, Any]

class RecommendationActionRequest(BaseModel):
    action: str  # 'Approve', 'Reject', 'Implement'
    comments: Optional[str] = None
