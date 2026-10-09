import type {
  DashboardSummary, Mine, Borehole, OreBlock, ForecastItem,
  ExplanationResponse, Recommendation, SimulationRequestParams,
  SimulationResult, SavedScenario, ReserveEstimate, ModelStatus, DataImportRecord
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
  getMines: () => fetchJson<Mine[]>('/mines'),
  getBlocks: (mineId = 'MINE-001') => fetchJson<OreBlock[]>(`/blocks?mine_id=${mineId}`),
  getBoreholes: (mineId = 'MINE-001') => fetchJson<Borehole[]>(`/boreholes?mine_id=${mineId}`),
  getGeologyLayers: (mineId = 'MINE-001') => fetchJson<any>(`/geology/layers?mine_id=${mineId}`),
  getProspectivityMap: () => fetchJson<any>('/prospectivity/map'),

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
