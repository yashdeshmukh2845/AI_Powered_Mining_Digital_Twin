import React, { useState, useEffect } from 'react';
import { Cpu, Save, Trash2, Sliders } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from 'recharts';
import type { SimulationRequestParams, SimulationResult, SavedScenario } from '../types';
import { api } from '../services/api';

export const DigitalTwinSimulator: React.FC = () => {
  const [params, setParams] = useState<SimulationRequestParams>({
    available_excavators: 2,
    available_trucks: 3,
    equipment_downtime_hours: 1.5,
    blasting_delay_hours: 0.5,
    rainfall_scenario_mm: 0.0,
    planned_operating_hours: 16.0,
    production_target_tonnes: 2500.0
  });

  const [simulationResult, setSimulationResult] = useState<SimulationResult | null>(null);
  const [savedScenarios, setSavedScenarios] = useState<SavedScenario[]>([]);
  const [scenarioName, setScenarioName] = useState<string>('');

  const runSim = async () => {
    try {
      const res = await api.runSimulation(params);
      setSimulationResult(res);
    } catch (err) {
      console.error('Error running simulation:', err);
    }
  };

  const loadScenarios = async () => {
    try {
      const list = await api.getSavedScenarios();
      setSavedScenarios(list);
    } catch (err) {
      console.error('Error loading saved scenarios:', err);
    }
  };

  useEffect(() => {
    runSim();
    loadScenarios();
  }, []);

  const handleSaveScenario = async () => {
    if (!scenarioName || !simulationResult) return;
    try {
      await api.saveScenario(scenarioName, 'Custom Digital Twin Scenario', params, simulationResult);
      setScenarioName('');
      loadScenarios();
    } catch (err) {
      console.error('Error saving scenario:', err);
    }
  };

  const handleDeleteScenario = async (id: string) => {
    try {
      await api.deleteScenario(id);
      loadScenarios();
    } catch (err) {
      console.error('Error deleting scenario:', err);
    }
  };

  const chartData = simulationResult ? [
    {
      name: 'Daily Production (Tonnes)',
      Baseline: simulationResult.baseline_forecast_tonnes,
      Scenario: simulationResult.scenario_forecast_tonnes,
      Target: simulationResult.production_target_tonnes
    }
  ] : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Cpu className="w-5 h-5 text-amber-500" />
            Mining Digital Twin & What-If Scenario Simulator
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Simulate equipment fleet changes, downtime, rainfall, and blasting delays under physical capacity constraints.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Simulator Input Sliders Panel */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h3 className="font-bold text-base text-slate-900 border-b border-slate-100 pb-3 flex items-center gap-2">
            <Sliders className="w-4 h-4 text-amber-500" />
            Scenario Parameter Controls
          </h3>

          <div className="space-y-3 text-xs">
            <div>
              <div className="flex justify-between mb-1">
                <span className="font-semibold text-slate-700">Available Excavators:</span>
                <span className="font-mono font-bold text-amber-600">{params.available_excavators} Units</span>
              </div>
              <input
                type="range" min="1" max="5" value={params.available_excavators}
                onChange={(e) => setParams({ ...params, available_excavators: Number(e.target.value) })}
                className="w-full accent-amber-500 cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between mb-1">
                <span className="font-semibold text-slate-700">Available Haul Trucks:</span>
                <span className="font-mono font-bold text-amber-600">{params.available_trucks} Units</span>
              </div>
              <input
                type="range" min="1" max="8" value={params.available_trucks}
                onChange={(e) => setParams({ ...params, available_trucks: Number(e.target.value) })}
                className="w-full accent-amber-500 cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between mb-1">
                <span className="font-semibold text-slate-700">Equipment Downtime:</span>
                <span className="font-mono font-bold text-red-600">{params.equipment_downtime_hours} Hours</span>
              </div>
              <input
                type="range" min="0" max="8" step="0.5" value={params.equipment_downtime_hours}
                onChange={(e) => setParams({ ...params, equipment_downtime_hours: Number(e.target.value) })}
                className="w-full accent-red-500 cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between mb-1">
                <span className="font-semibold text-slate-700">Blasting Delay:</span>
                <span className="font-mono font-bold text-amber-600">{params.blasting_delay_hours} Hours</span>
              </div>
              <input
                type="range" min="0" max="4" step="0.5" value={params.blasting_delay_hours}
                onChange={(e) => setParams({ ...params, blasting_delay_hours: Number(e.target.value) })}
                className="w-full accent-amber-500 cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between mb-1">
                <span className="font-semibold text-slate-700">Rainfall Scenario:</span>
                <span className="font-mono font-bold text-blue-600">{params.rainfall_scenario_mm} mm</span>
              </div>
              <input
                type="range" min="0" max="50" step="5" value={params.rainfall_scenario_mm}
                onChange={(e) => setParams({ ...params, rainfall_scenario_mm: Number(e.target.value) })}
                className="w-full accent-blue-500 cursor-pointer"
              />
            </div>
          </div>

          <button
            onClick={runSim}
            className="w-full py-2.5 bg-slate-900 text-white font-bold text-xs rounded-lg hover:bg-slate-800 transition-colors shadow-md"
          >
            Run Scenario Physics Recalculation
          </button>
        </div>

        {/* Results & Comparison Section */}
        <div className="lg:col-span-2 space-y-6">
          {simulationResult && (
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
              <div className="flex justify-between items-center border-b border-slate-100 pb-3">
                <h3 className="font-bold text-base text-slate-900">Baseline vs Scenario Simulation Outcome</h3>
                <span className={`px-2.5 py-1 rounded text-xs font-bold ${
                  simulationResult.revised_risk_category === 'High' ? 'bg-red-100 text-red-700' : 'bg-emerald-100 text-emerald-800'
                }`}>
                  Revised Risk: {simulationResult.revised_risk_category}
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="p-3 bg-slate-50 rounded-lg text-center">
                  <span className="text-[10px] text-slate-500 uppercase font-semibold">Baseline Output</span>
                  <p className="text-lg font-bold text-slate-700 font-mono mt-0.5">{simulationResult.baseline_forecast_tonnes} t</p>
                </div>
                <div className="p-3 bg-amber-50 rounded-lg text-center">
                  <span className="text-[10px] text-amber-700 uppercase font-semibold">Scenario Output</span>
                  <p className="text-lg font-bold text-amber-900 font-mono mt-0.5">{simulationResult.scenario_forecast_tonnes} t</p>
                </div>
                <div className="p-3 bg-purple-50 rounded-lg text-center">
                  <span className="text-[10px] text-purple-700 uppercase font-semibold">Difference</span>
                  <p className={`text-lg font-bold font-mono mt-0.5 ${simulationResult.difference_tonnes >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                    {simulationResult.difference_tonnes > 0 ? '+' : ''}{simulationResult.difference_tonnes} t
                  </p>
                </div>
                <div className="p-3 bg-red-50 rounded-lg text-center">
                  <span className="text-[10px] text-red-700 uppercase font-semibold">Revised Shortfall</span>
                  <p className="text-lg font-bold text-red-900 font-mono mt-0.5">{simulationResult.revised_shortfall_tonnes} t</p>
                </div>
              </div>

              {/* Chart */}
              <div className="h-56 w-full pt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                    <YAxis tick={{ fontSize: 10 }} domain={[0, 3000]} />
                    <Tooltip contentStyle={{ backgroundColor: '#0f172a', color: '#f8fafc', borderRadius: '0.5rem' }} />
                    <Legend />
                    <Bar dataKey="Baseline" fill="#94A3B8" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="Scenario" fill="#F59E0B" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="Target" fill="#0F172A" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Save Scenario Bar */}
              <div className="flex gap-2 pt-2">
                <input
                  type="text"
                  placeholder="Enter scenario name to save (e.g. Rain Contingency Plan #2)"
                  value={scenarioName}
                  onChange={(e) => setScenarioName(e.target.value)}
                  className="flex-1 bg-slate-50 border border-slate-300 px-3 py-1.5 rounded-lg text-xs"
                />
                <button
                  onClick={handleSaveScenario}
                  className="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs rounded-lg transition-colors flex items-center gap-1.5"
                >
                  <Save className="w-3.5 h-3.5" />
                  Save Scenario
                </button>
              </div>
            </div>
          )}

          {/* Saved Scenarios Table */}
          {savedScenarios.length > 0 && (
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-3">
              <h3 className="font-bold text-sm text-slate-900">Saved Scenario History</h3>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {savedScenarios.map((sc) => (
                  <div key={sc.id} className="p-3 bg-slate-50 rounded-lg border border-slate-200 flex justify-between items-center text-xs">
                    <div>
                      <p className="font-bold text-slate-800">{sc.name}</p>
                      <p className="text-[10px] text-slate-500">{sc.created_at} | Output: {sc.results.scenario_forecast_tonnes} tonnes</p>
                    </div>
                    <button
                      onClick={() => handleDeleteScenario(sc.id)}
                      className="text-red-500 hover:text-red-700 p-1"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
