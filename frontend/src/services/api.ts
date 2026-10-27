import type {
  DashboardSummary, Mine, Borehole, OreBlock, ForecastItem,
  ExplanationResponse, Recommendation, SimulationRequestParams,
  SimulationResult, SavedScenario, ReserveEstimate, ModelStatus, DataImportRecord,
  EquipmentRiskResponse, AblationStudyResult, BlockModelResponse, BlockModelBlock,
  VariogramResponse, DispatchOptimizationResult, BlastingScheduleResult
} from '../types';

const API_BASE = '/api';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, options);
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`API Error (${res.status}): ${errorText}`);
  }
  return res.json();
}

export const api = {
  // Dashboard & Mines
  getHealth: () => fetchJson<{ status: string; app: string; demo_mode: boolean }>('/health'),
  getDashboardSummary: (mineId = 'MINE-001') => fetchJson<DashboardSummary>(`/dashboard/summary?mine_id=${mineId}`),
  getAlerts: (mineId = 'MINE-001') => fetchJson<any[]>(`/alerts?mine_id=${mineId}`),
  getMines: () => fetchJson<Mine[]>('/mines'),
  getBlocks: (mineId = 'MINE-001') => fetchJson<OreBlock[]>(`/blocks?mine_id=${mineId}`),
  getBoreholes: (mineId = 'MINE-001') => fetchJson<Borehole[]>(`/boreholes?mine_id=${mineId}`),
  getGeologyLayers: (mineId = 'MINE-001') => fetchJson<any>(`/geology/layers?mine_id=${mineId}`),
  getProspectivityMap: () => fetchJson<any>('/prospectivity/map'),

  // Equipment Fleet Health & Failure Risk Engine (Phase 2)
  getEquipment: (mineId = 'MINE-001') => fetchJson<any[]>(`/equipment?mine_id=${mineId}`),
  getEquipmentRisks: (mineId = 'MINE-001') => fetchJson<EquipmentRiskResponse>(`/equipment/risk?mine_id=${mineId}`),

  // Space & Weather Empirical Ablation Study (Phase 4)
  getAblationStudy: () => fetchJson<AblationStudyResult>('/models/ablation'),

  // 3D Geostatistical Block Model & JORC/UNFC Resource Estimation (Phase 5)
  getBlockModel: () => fetchJson<BlockModelResponse>('/reserves/block-model'),
  getBlockModelSlice: (elevation = 300.0) => fetchJson<BlockModelBlock[]>(`/reserves/block-model/slice?elevation=${elevation}`),
  getBlockModelCrossSection: (yCoord = 0.0, tolerance = 35.0) => fetchJson<BlockModelBlock[]>(`/reserves/block-model/cross-section?y_coord=${yCoord}&tolerance=${tolerance}`),
  getVariogram: (variable = 'mn_grade') => fetchJson<VariogramResponse>(`/reserves/variogram?variable=${variable}`),

  // Reserves & Forecasting
  estimateReserves: (mineId = 'MINE-001', bulkDensity = 3.4, cutoffGrade = 15.0) =>
    fetchJson<ReserveEstimate>('/reserves/estimate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mine_id: mineId, bulk_density: bulkDensity, cutoff_grade: cutoffGrade })
    }),
  getProductionHistory: (mineId = 'MINE-001', limit = 90) => fetchJson<any[]>(`/production/history?mine_id=${mineId}&limit=${limit}`),
  getProductionForecast: (mineId = 'MINE-001', horizonDays = 14) =>
    fetchJson<ForecastItem[]>('/production/forecast', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mine_id: mineId, forecast_horizon_days: horizonDays })
    }),

  // Operations Research & Optimization Engine (Phase 6)
  optimizeDispatch: (params: { target_tonnes?: number; forecast_rain_mm?: number; blend_target_mn_pct?: number; mine_id?: string } = {}) =>
    fetchJson<DispatchOptimizationResult>('/optimizer/dispatch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        target_tonnes: params.target_tonnes ?? 2500.0,
        forecast_rain_mm: params.forecast_rain_mm ?? 0.0,
        blend_target_mn_pct: params.blend_target_mn_pct ?? 30.0,
        mine_id: params.mine_id ?? 'MINE-001'
      })
    }),
  getBlastingWindow: (mineId = 'MINE-001') => fetchJson<BlastingScheduleResult>(`/optimizer/blasting?mine_id=${mineId}`),

  // Risk & Explainability & AI Actions
  analyzeRisk: (target: number, forecast: number) =>
    fetchJson<any>('/risk/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target_tonnes: target, forecast_tonnes: forecast })
    }),
  getExplanations: (mineId = 'MINE-001') =>
    fetchJson<ExplanationResponse>('/explanations', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mine_id: mineId })
    }),
  generateRecommendations: (mineId = 'MINE-001') =>
    fetchJson<Recommendation[]>('/recommendations/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mine_id: mineId })
    }),
  updateRecommendationStatus: (recId: string, action: string, comments?: string) =>
    fetchJson<any>(`/recommendations/${recId}/action`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action, comments })
    }),

  // Digital Twin Simulator
  runSimulation: (params: SimulationRequestParams) =>
    fetchJson<SimulationResult>('/simulator/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    }),
  getSavedScenarios: () => fetchJson<SavedScenario[]>('/simulator/scenarios'),
  saveScenario: (name: string, description: string, parameters: SimulationRequestParams, results: SimulationResult) =>
    fetchJson<any>('/simulator/scenarios', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, description, parameters, results })
    }),
  deleteScenario: (scenarioId: string) =>
    fetchJson<any>(`/simulator/scenarios/${scenarioId}`, { method: 'DELETE' }),

  // Data Ingestion & Models
  previewData: (formData: FormData) =>
    fetchJson<any>('/data/preview', { method: 'POST', body: formData }),
  importData: (formData: FormData) =>
    fetchJson<any>('/data/import', { method: 'POST', body: formData }),
  getImportHistory: () => fetchJson<DataImportRecord[]>('/data/import-history'),
  getDataProvenance: () => fetchJson<any[]>('/data/provenance'),
  getDatasetInventory: () => fetchJson<any[]>('/data/inventory'),
  refreshDatasets: () => fetchJson<any>('/data/refresh', { method: 'POST' }),

  // Weather & Geological Datasets
  getMonthlyProduction: () => fetchJson<any[]>('/production/monthly'),
  getWeatherHistory: (limit = 180) => fetchJson<any[]>(`/weather/history?limit=${limit}`),
  getWeatherStation: () => fetchJson<any>('/weather/station'),
  getGeologySummary: () => fetchJson<any>('/geology/summary'),
  getSatelliteSummary: () => fetchJson<any>('/satellite/summary'),
  getSatelliteSamples: (limit = 40) => fetchJson<any[]>(`/satellite/samples?limit=${limit}`),
  classifySatelliteImage: (className: string, imageName: string) =>
    fetchJson<any>(`/satellite/classify?class_name=${className}&image_name=${imageName}`, { method: 'POST' }),

  trainProspectivityModel: (algorithm = 'RandomForest') =>
    fetchJson<any>('/models/prospectivity/train', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mine_id: 'MINE-001', algorithm })
    }),
  trainProductionModel: (algorithm = 'RandomForest') =>
    fetchJson<any>('/models/production/train', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mine_id: 'MINE-001', algorithm })
    }),
  getModelStatus: () => fetchJson<ModelStatus>('/models/status'),
  getModelMetrics: () => fetchJson<any>('/models/metrics'),
  getReportSummary: (format = 'json') => `${API_BASE}/reports/summary?format=${format}`
};
