export interface Mine {
  id: string;
  name: string;
  code: string;
  location?: string;
  latitude: number;
  longitude: number;
  elevation: number;
  operational_status: string;
}

export interface BoreholeInterval {
  from_depth: number;
  to_depth: number;
  lithology: string;
  mn_grade: number;
  primary_grade?: number;
  primary_commodity?: string;
  secondary_grade?: number;
  secondary_commodity?: string;
}

export interface Borehole {
  id: string;
  borehole_id: string;
  latitude: number;
  longitude: number;
  elevation: number;
  total_depth: number;
  x_coord?: number;
  y_coord?: number;
  crs?: string;
  commodity?: string;
  is_synthetic?: boolean;
  provenance_source?: string;
  intervals?: BoreholeInterval[];
}

export interface OreBlock {
  id: string;
  mine_id: string;
  block_code: string;
  min_x: number;
  max_x: number;
  min_y: number;
  max_y: number;
  volume_m3: number;
  bulk_density: number;
  tonnage: number;
  est_mn_grade: number;
  contained_mn_tonnes: number;
  category: string;
}

export interface DashboardSummary {
  selected_mine: Mine;
  est_resources_tonnes: number;
  est_contained_mn_tonnes: number;
  avg_mn_grade_pct: number;
  latest_actual_production: number;
  latest_target_production: number;
  forecast_production: number;
  forecast_shortfall_tonnes: number;
  forecast_shortfall_pct: number;
  shortfall_risk_category: string;
  equipment_availability_pct: number;
  num_high_prospectivity_blocks: number;
  production_attainment_pct?: number;
  total_production_records?: number;
  weather_coverage_days?: number;
  total_boreholes?: number;
  total_intervals?: number;
  total_assays?: number;
  geology_commodity?: string;
  weather_station_info?: string;
  provenance_warnings?: string[];
  demo_mode: boolean;
  last_updated: string;
}

export interface ProductionRecord {
  id: string;
  date: string;
  actual_production_tonnes: number;
  planned_target_tonnes: number;
  operating_hours: number;
  downtime_hours: number;
  equipment_availability_pct: number;
  rainfall_mm: number;
  blasting_delay_hours: number;
}

export interface ForecastItem {
  date: string;
  planned_target_tonnes: number;
  actual_production_tonnes?: number;
  forecast_tonnes: number;
  shortfall_tonnes: number;
  shortfall_pct: number;
  risk_category: string;
  horizon_day?: number;
  target_tonnes?: number;
  forecast_p10_tonnes?: number;
  forecast_p50_tonnes?: number;
  forecast_p90_tonnes?: number;
  expected_shortfall_tonnes?: number;
  expected_shortfall_pct?: number;
  shortfall_probability_pct?: number;
  primary_driver?: string;
  forecast_rainfall_mm?: number;
  predicted_downtime_hours?: number;
  planned_blasting_delay_hours?: number;
  is_model_prediction?: boolean;
}

export interface FeatureContribution {
  feature: string;
  displayName: string;
  importance: number;
  impact: string;
  unit: string;
}

export interface ExplanationResponse {
  mine_id: string;
  feature_contributions: FeatureContribution[];
  method: string;
  manager_confirmation_status: string;
}

export interface Recommendation {
  id: string;
  priority: 'High' | 'Medium' | 'Low';
  title: string;
  description: string;
  rationale: string;
  affected_block_or_mine: string;
  est_production_impact_tonnes: number;
  constraints_assumptions: string;
  responsible_team: string;
  status: 'Pending Review' | 'Approved' | 'Rejected' | 'Implemented';
}

export interface SimulationRequestParams {
  available_excavators: number;
  available_trucks: number;
  equipment_downtime_hours: number;
  blasting_delay_hours: number;
  rainfall_scenario_mm: number;
  planned_operating_hours: number;
  production_target_tonnes: number;
}

export interface SimulationResult {
  baseline_forecast_tonnes: number;
  scenario_forecast_tonnes: number;
  difference_tonnes: number;
  production_target_tonnes: number;
  revised_shortfall_tonnes: number;
  revised_shortfall_pct: number;
  revised_risk_category: string;
  fleet_throughput_tph: number;
  net_operating_hours: number;
  excavator_utilization_pct: number;
  truck_utilization_pct: number;
  constraints_violated: string[];
}

export interface SavedScenario {
  id: string;
  name: string;
  description?: string;
  parameters: SimulationRequestParams;
  results: SimulationResult;
  created_at: string;
}

export interface ReserveEstimate {
  mine_id: string;
  cutoff_grade_pct: number;
  bulk_density_t_per_m3: number;
  total_volume_m3: number;
  total_ore_tonnage: number;
  total_contained_mn_tonnes: number;
  average_mn_grade_pct: number;
  categories: Record<string, {
    tonnage: number;
    contained_mn: number;
    avg_grade: number;
    count: number;
  }>;
  blocks_count: number;
}

export interface ModelStatus {
  prospectivity_model: {
    trained: boolean;
    algorithm: string;
    last_updated: string;
  };
  production_model: {
    trained: boolean;
    algorithm: string;
    last_updated: string;
  };
}

export interface DataImportRecord {
  id: number;
  file_name: string;
  dataset_type: string;
  status: string;
  total_rows: number;
  imported_rows: number;
  rejected_rows: number;
  timestamp: string;
}

export interface DataProvenanceRecord {
  id: number;
  dataset_key: string;
  file_name: string;
  file_path: string;
  dataset_type: string;
  commodity: string;
  units: string;
  data_origin: string;
  total_rows: number;
  accepted_rows: number;
  rejected_rows: number;
  validation_warnings: string[];
  date_range?: string;
  spatial_info?: string;
  is_synthetic: boolean;
  status: string;
  imported_at?: string;
}

export interface DiscoveredDataset {
  dataset_key: string;
  file_name: string;
  relative_path: string;
  file_size_kb: number;
  dataset_type: string;
  commodity: string;
  units: string;
  data_origin: string;
  is_primary: boolean;
  is_synthetic: boolean;
  columns?: string[];
  expected_rows?: number;
  date_coverage?: string;
  description: string;
}

export interface WeatherStation {
  station_name: string;
  latitude: number;
  longitude: number;
  elevation_m: number;
  timezone: string;
  observation_period: string;
  total_observations: number;
  disclaimer: string;
}

export interface SatelliteSummary {
  dataset_name: string;
  total_images: number;
  tile_resolution: string;
  classes: string[];
  num_classes: number;
  preview_samples_stored: number;
  sensor: string;
  scientific_disclaimer: string;
}

export interface SatelliteSample {
  id: string;
  file_name: string;
  relative_path: string;
  class_label: string;
  predicted_label?: string;
  confidence?: number;
  source_dataset: string;
  image_url: string;
}

export interface MonthlyProductionRecord {
  Date: string;
  Production_Tonnes: number;
  Target_Tonnes: number;
  Average_Efficiency: number;
  'Attainment_%': number;
}

export interface GeologySummary {
  borehole_count: number;
  interval_count: number;
  assay_count: number;
  commodity: string;
  primary_element: string;
  units: string;
  average_grade: number;
  coordinate_reference_system: string;
  source: string;
  scientific_disclaimer: string;
}

export interface EquipmentRiskItem {
  id: string;
  name: string;
  equipment_type: string;
  status: string;
  capacity_tph: number;
  engine_hours: number;
  hours_since_last_maintenance: number;
  past_failure_count_90d: number;
  average_load_pct: number;
  health_score: number;
  failure_risk_24h: number;
  failure_risk_48h: number;
  failure_risk_72h: number;
  critical_component: string;
  top_risk_factors: string[];
  recommended_action: string;
  expected_downtime_hours_next_7d: number;
}

export interface EquipmentRiskResponse {
  mine_id: string;
  fleet_count: number;
  high_risk_count: number;
  fleet_health_score_avg: number;
  expected_total_downtime_hours_next_7d: number;
  evaluation_metrics: Record<string, any>;
  equipment: EquipmentRiskItem[];
}

export interface AblationModelResult {
  model_name: string;
  features_used: string;
  overall_mae: number;
  overall_rmse: number;
  overall_wape_pct: number;
  monsoon_mae: number;
  monsoon_wape_pct: number;
  dry_season_mae: number;
  dry_season_wape_pct: number;
  r2_score: number;
  status: string;
}

export interface AblationFeatureImportance {
  feature: string;
  label: string;
  importance_pct: number;
  category: string;
}

export interface AblationLagEffect {
  day_lag: string;
  haul_road_friction_reduction_pct: number;
  average_truck_cycle_slowdown_min: number;
  blasting_lockout_risk: string;
  pit_sump_inflow_m3_per_mm: number;
  production_impact: string;
}

export interface AblationStudyResult {
  title: string;
  evaluated_mine: string;
  study_period: string;
  summary_conclusion: string;
  scientific_limitations: string;
  model_comparison: AblationModelResult[];
  monsoon_accuracy_gain: {
    mae_gain_tonnes: number;
    mae_gain_pct: number;
    wape_improvement_pct_pts: number;
  };
  overall_accuracy_gain: {
    mae_gain_tonnes: number;
    mae_gain_pct: number;
    wape_improvement_pct_pts: number;
  };
  feature_importances: AblationFeatureImportance[];
  lag_effects: AblationLagEffect[];
  generated_at: string;
}

export interface BlockModelBlock {
  block_id: string;
  x_m: number;
  y_m: number;
  bench_elevation_m: number;
  dx: number;
  dy: number;
  dz: number;
  volume_m3: number;
  tonnage_tonnes: number;
  est_mn_grade_pct: number;
  est_fe_grade_pct: number;
  est_sio2_grade_pct: number;
  contained_mn_tonnes: number;
  distance_to_nearest_drillhole_m: number;
  kriging_variance: number;
  jorc_category: 'Measured' | 'Indicated' | 'Inferred' | 'Exploration Target';
  unfc_code: string;
}

export interface JORCCategorySummary {
  block_count: number;
  tonnage_tonnes: number;
  contained_mn_tonnes: number;
  avg_mn_grade_pct: number;
  pct_of_total: number;
}

export interface GradeTonnagePoint {
  cutoff_grade_pct: number;
  ore_tonnage_tonnes: number;
  contained_mn_tonnes: number;
  avg_mn_grade_pct: number;
  block_count: number;
}

export interface BlockModelResponse {
  mine_id: string;
  mine_name: string;
  block_dimensions_m: { dx: number; dy: number; dz: number };
  benches: number[];
  total_blocks: number;
  total_tonnage_tonnes: number;
  total_contained_mn_tonnes: number;
  average_mn_grade_pct: number;
  bulk_density_t_per_m3: number;
  jorc_resource_categories: Record<string, JORCCategorySummary>;
  grade_tonnage_curve: GradeTonnagePoint[];
  variogram_parameters: Record<string, any>;
  blocks: BlockModelBlock[];
  disclaimer: string;
}

export interface VariogramResponse {
  variable: string;
  units: string;
  model_type: string;
  nugget_c0: number;
  sill_c: number;
  range_a_meters: number;
  empirical_lags: number[];
  empirical_semivariance: number[];
  pair_counts: number[];
  fitted_curve: {
    lags: number[];
    semivariance: number[];
  };
  disclaimer: string;
}

export interface BenchAllocation {
  bench_id: string;
  bench_name: string;
  allocated_trucks: number;
  optimized_production_tonnes: number;
  in_situ_mn_grade_pct: number;
  haul_distance_km: number;
  cycle_time_min: number;
}

export interface DispatchOptimizationResult {
  solver_status: string;
  target_tonnes: number;
  optimized_total_tonnes: number;
  expected_shortfall_tonnes: number;
  forecast_rain_mm: number;
  rain_speed_derating_pct: number;
  blended_grades: {
    mn_grade_pct: number;
    fe_grade_pct: number;
    sio2_grade_pct: number;
    blend_target_mn_pct: number;
  };
  bench_allocations: BenchAllocation[];
  fleet_deployed: {
    total_excavators: number;
    total_trucks: number;
    trucks_idle_or_standby: number;
  };
}

export interface BlastingWindowCandidate {
  date: string;
  day_index: number;
  score: number;
  forecast_rainfall_mm: number;
  max_temp_c: number;
  suitability: string;
  rain_risk_assessment: string;
  thermal_risk_assessment: string;
  recommended_blast_time: string;
  evacuation_radius_m: number;
}

export interface BlastingScheduleResult {
  optimal_blast_day: string;
  optimal_window_score: number;
  recommended_time: string;
  evacuation_radius_meters: number;
  primary_rationale: string;
  weekly_lookahead: BlastingWindowCandidate[];
}

