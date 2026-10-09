import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, Date, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from backend.app.database.db import Base

class Mine(Base):
    __tablename__ = "mines"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, index=True)
    location = Column(String)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    elevation = Column(Float, default=300.0)
    operational_status = Column(String, default="Active")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class MineBoundary(Base):
    __tablename__ = "mine_boundaries"
    id = Column(Integer, primary_key=True, autoincrement=True)
    mine_id = Column(String, ForeignKey("mines.id"), index=True)
    boundary_geojson = Column(Text, nullable=False)
    crs = Column(String, default="EPSG:4326")

class GeologicalUnit(Base):
    __tablename__ = "geological_units"
    id = Column(String, primary_key=True, index=True)
    mine_id = Column(String, ForeignKey("mines.id"), index=True)
    name = Column(String, nullable=False)
    code = Column(String, index=True)
    description = Column(Text)
    rock_type = Column(String)
    color = Column(String, default="#8B5CF6")

class Borehole(Base):
    __tablename__ = "boreholes"
    id = Column(String, primary_key=True, index=True)
    mine_id = Column(String, ForeignKey("mines.id"), index=True)
    borehole_id = Column(String, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    elevation = Column(Float, nullable=False)
    total_depth = Column(Float, nullable=False)
    start_date = Column(String)
    end_date = Column(String)

class BoreholeInterval(Base):
    __tablename__ = "borehole_intervals"
    id = Column(String, primary_key=True, index=True)
    borehole_id = Column(String, ForeignKey("boreholes.id"), index=True)
    from_depth = Column(Float, nullable=False)
    to_depth = Column(Float, nullable=False)
    lithology = Column(String)
    mn_grade = Column(Float, default=0.0)

class AssaySample(Base):
    __tablename__ = "assay_samples"
    id = Column(String, primary_key=True, index=True)
    interval_id = Column(String, ForeignKey("borehole_intervals.id"), index=True)
    sample_id = Column(String, index=True)
    mn_grade = Column(Float, nullable=False)
    fe_grade = Column(Float, default=0.0)
    sio2_grade = Column(Float, default=0.0)
    sample_date = Column(String)
    assay_source = Column(String)

class OreBlock(Base):
    __tablename__ = "ore_blocks"
    id = Column(String, primary_key=True, index=True)
    mine_id = Column(String, ForeignKey("mines.id"), index=True)
    block_code = Column(String, index=True)
    min_x = Column(Float, nullable=False)
    max_x = Column(Float, nullable=False)
    min_y = Column(Float, nullable=False)
    max_y = Column(Float, nullable=False)
    min_z = Column(Float, default=0.0)
    max_z = Column(Float, default=100.0)
    volume_m3 = Column(Float, nullable=False)
    bulk_density = Column(Float, default=3.4)
    tonnage = Column(Float, nullable=False)
    est_mn_grade = Column(Float, nullable=False)
    contained_mn_tonnes = Column(Float, nullable=False)
    category = Column(String, default="Indicated")

class ProductionRecord(Base):
    __tablename__ = "production_records"
    id = Column(String, primary_key=True, index=True)
    mine_id = Column(String, ForeignKey("mines.id"), index=True)
    date = Column(String, index=True)
    actual_production_tonnes = Column(Float, nullable=False)
    planned_target_tonnes = Column(Float, nullable=False)
    operating_hours = Column(Float, default=16.0)
    downtime_hours = Column(Float, default=0.0)
    equipment_availability_pct = Column(Float, default=90.0)
    rainfall_mm = Column(Float, default=0.0)
    blasting_delay_hours = Column(Float, default=0.0)

class ProductionTarget(Base):
    __tablename__ = "production_targets"
    id = Column(String, primary_key=True, index=True)
    mine_id = Column(String, ForeignKey("mines.id"), index=True)
    period_start = Column(String)
    period_end = Column(String)
    target_tonnes = Column(Float, nullable=False)

class Equipment(Base):
    __tablename__ = "equipment"
    id = Column(String, primary_key=True, index=True)
    mine_id = Column(String, ForeignKey("mines.id"), index=True)
    name = Column(String, nullable=False)
    equipment_type = Column(String, nullable=False)
    status = Column(String, default="Operational")
    capacity_tph = Column(Float, default=150.0)

class EquipmentDowntime(Base):
    __tablename__ = "equipment_downtime"
    id = Column(String, primary_key=True, index=True)
    equipment_id = Column(String, ForeignKey("equipment.id"), index=True)
    start_time = Column(String)
    end_time = Column(String)
    downtime_hours = Column(Float, nullable=False)
    reason = Column(String)
    category = Column(String)

class BlastingEvent(Base):
    __tablename__ = "blasting_events"
    id = Column(String, primary_key=True, index=True)
    mine_id = Column(String, ForeignKey("mines.id"), index=True)
    date = Column(String, index=True)
    blast_id = Column(String, index=True)
    location = Column(String)
    powder_factor = Column(Float, default=0.5)
    delay_hours = Column(Float, default=0.0)
    status = Column(String, default="Completed")

class EnvironmentalObservation(Base):
    __tablename__ = "environmental_observations"
    id = Column(String, primary_key=True, index=True)
    mine_id = Column(String, ForeignKey("mines.id"), index=True)
    date = Column(String, index=True)
    rainfall_mm = Column(Float, default=0.0)
    soil_moisture = Column(Float, default=0.3)
    ndvi = Column(Float, default=0.5)
    land_surface_temp_c = Column(Float, default=32.0)
    sar_coherence = Column(Float, default=0.7)

class DataImport(Base):
    __tablename__ = "data_imports"
    id = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(String, nullable=False)
    dataset_type = Column(String, nullable=False)
    status = Column(String, default="Success")
    total_rows = Column(Integer, default=0)
    imported_rows = Column(Integer, default=0)
    rejected_rows = Column(Integer, default=0)
    error_log = Column(Text, default="[]")
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class ModelVersion(Base):
    __tablename__ = "model_versions"
    id = Column(String, primary_key=True, index=True)
    model_type = Column(String, nullable=False) # 'prospectivity' or 'production'
    version = Column(String, nullable=False)
    algorithm = Column(String, nullable=False)
    metrics_json = Column(Text, default="{}")
    feature_names_json = Column(Text, default="[]")
    file_path = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class ModelMetric(Base):
    __tablename__ = "model_metrics"
    id = Column(Integer, primary_key=True, autoincrement=True)
    model_version_id = Column(String, ForeignKey("model_versions.id"), index=True)
    metric_name = Column(String, nullable=False)
    metric_value = Column(Float, nullable=False)
    dataset_split = Column(String, default="test")

class Forecast(Base):
    __tablename__ = "forecasts"
    id = Column(String, primary_key=True, index=True)
    mine_id = Column(String, ForeignKey("mines.id"), index=True)
    date = Column(String, index=True)
    forecast_tonnes = Column(Float, nullable=False)
    target_tonnes = Column(Float, nullable=False)
    shortfall_tonnes = Column(Float, nullable=False)
    shortfall_pct = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)
    model_version_id = Column(String, ForeignKey("model_versions.id"))

class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    id = Column(String, primary_key=True, index=True)
    forecast_id = Column(String, ForeignKey("forecasts.id"), index=True)
    risk_level = Column(String, nullable=False)
    risk_score = Column(Float, nullable=False)
    primary_factors_json = Column(Text, default="[]")

class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(String, primary_key=True, index=True)
    forecast_id = Column(String, ForeignKey("forecasts.id"), index=True)
    priority = Column(String, nullable=False) # 'High', 'Medium', 'Low'
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    rationale = Column(Text)
    affected_block_or_mine = Column(String)
    est_production_impact_tonnes = Column(Float, default=0.0)
    status = Column(String, default="Pending Review") # 'Pending Review', 'Approved', 'Rejected', 'Implemented'
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class RecommendationFeedback(Base):
    __tablename__ = "recommendation_feedback"
    id = Column(Integer, primary_key=True, autoincrement=True)
    recommendation_id = Column(String, ForeignKey("recommendations.id"), index=True)
    user_action = Column(String, nullable=False)
    comments = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class SimulationScenario(Base):
    __tablename__ = "simulation_scenarios"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    parameters_json = Column(Text, nullable=False)
    results_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class AuditEvent(Base):
    __tablename__ = "audit_events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    action_type = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(String)
    payload_json = Column(Text, default="{}")
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
