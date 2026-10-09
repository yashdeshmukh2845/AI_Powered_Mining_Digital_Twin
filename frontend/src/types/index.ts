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
}

export interface Borehole {
  id: string;
  borehole_id: string;
  latitude: number;
  longitude: number;
  elevation: number;
  total_depth: number;
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
  actual_production_tonnes: number;
  forecast_tonnes: number;
  shortfall_tonnes: number;
  shortfall_pct: number;
  risk_category: string;
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
