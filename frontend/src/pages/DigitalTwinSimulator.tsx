import React, { useState, useEffect } from 'react';
import {
  Cpu, Save, Trash2, Sliders, Layers, Train,
  Flame, CheckCircle2, AlertTriangle, ArrowRight, Activity
} from 'lucide-react';
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip,
  Legend, CartesianGrid
} from 'recharts';
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

  const [simulationResult, setSimulationResult] = useState<any | null>(null);
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
      name: 'Daily Output',
      Baseline: simulationResult.baseline_forecast_tonnes,
      Scenario: simulationResult.scenario_forecast_tonnes,
      Target: simulationResult.production_target_tonnes
    }
  ] : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-900/60 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400">
              <Cpu className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight">
                Mining Digital Twin &amp; Supply Chain Simulator
              </h1>
              <p className="text-slate-400 text-sm mt-0.5">
                Simulate fleet dispatch, cyclic queueing, primary crusher throughput, ROM stockpiles, and BOXN rail rakes.
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Simulator Input Sliders Panel */}
        <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800 space-y-4">
          <h2 className="font-bold text-sm text-white border-b border-slate-800 pb-3 flex items-center gap-2">
            <Sliders className="w-4 h-4 text-amber-400" />
            Operational Scenario Sliders
          </h2>

          <div className="space-y-3.5 text-xs">
            <div>
              <div className="flex justify-between mb-1">
                <span className="font-medium text-slate-300">Available Excavators (350 TPH):</span>
                <span className="font-mono font-bold text-amber-400">{params.available_excavators} Shovels</span>
              </div>
              <input
                type="range" min="1" max="5" value={params.available_excavators}
                onChange={(e) => setParams({ ...params, available_excavators: Number(e.target.value) })}
                className="w-full accent-amber-500 cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between mb-1">
                <span className="font-medium text-slate-300">Available Haul Dumpers (180 TPH):</span>
                <span className="font-mono font-bold text-cyan-400">{params.available_trucks} Trucks</span>
              </div>
              <input
                type="range" min="1" max="10" value={params.available_trucks}
                onChange={(e) => setParams({ ...params, available_trucks: Number(e.target.value) })}
                className="w-full accent-cyan-500 cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between mb-1">
                <span className="font-medium text-slate-300">Equipment Downtime:</span>
                <span className="font-mono font-bold text-rose-400">{params.equipment_downtime_hours} Hours</span>
              </div>
              <input
                type="range" min="0" max="8" step="0.5" value={params.equipment_downtime_hours}
                onChange={(e) => setParams({ ...params, equipment_downtime_hours: Number(e.target.value) })}
                className="w-full accent-rose-500 cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between mb-1">
                <span className="font-medium text-slate-300">Blasting Clearance Delay:</span>
                <span className="font-mono font-bold text-purple-400">{params.blasting_delay_hours} Hours</span>
              </div>
              <input
                type="range" min="0" max="4" step="0.5" value={params.blasting_delay_hours}
                onChange={(e) => setParams({ ...params, blasting_delay_hours: Number(e.target.value) })}
                className="w-full accent-purple-500 cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between mb-1">
                <span className="font-medium text-slate-300">Rainfall Road Scenario:</span>
                <span className="font-mono font-bold text-blue-400">{params.rainfall_scenario_mm} mm</span>
              </div>
              <input
                type="range" min="0" max="50" step="5" value={params.rainfall_scenario_mm}
                onChange={(e) => setParams({ ...params, rainfall_scenario_mm: Number(e.target.value) })}
                className="w-full accent-blue-500 cursor-pointer"
              />
              <span className="text-[10px] text-slate-500">
                {params.rainfall_scenario_mm > 10 ? 'Rain road friction derating active' : 'Optimal dry roads'}
              </span>
            </div>
          </div>

          <button
            onClick={runSim}
            className="w-full py-3 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs rounded-xl transition shadow-lg shadow-amber-500/10 mt-2"
          >
            Run Physics Simulation
          </button>
        </div>

        {/* Results & Comparison Section */}
        <div className="lg:col-span-2 space-y-6">
          {simulationResult && (
            <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800 space-y-5">
              <div className="flex justify-between items-center border-b border-slate-800 pb-3">
                <h2 className="font-bold text-base text-white">Scenario Simulation Outcome</h2>
                <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${
                  simulationResult.revised_risk_category === 'High'
                    ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                    : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                }`}>
                  Shortfall Risk: {simulationResult.revised_risk_category}
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="p-3.5 bg-slate-950/60 rounded-xl border border-slate-800 text-center">
                  <span className="text-[10px] text-slate-400 uppercase font-semibold block">Baseline Output</span>
                  <p className="text-xl font-bold text-slate-300 font-mono mt-0.5">{simulationResult.baseline_forecast_tonnes} t</p>
                </div>
                <div className="p-3.5 bg-amber-500/10 rounded-xl border border-amber-500/30 text-center">
                  <span className="text-[10px] text-amber-400 uppercase font-semibold block">Scenario Output</span>
                  <p className="text-xl font-bold text-amber-300 font-mono mt-0.5">{simulationResult.scenario_forecast_tonnes} t</p>
                </div>
                <div className="p-3.5 bg-slate-950/60 rounded-xl border border-slate-800 text-center">
                  <span className="text-[10px] text-slate-400 uppercase font-semibold block">Tonnage Difference</span>
                  <p className={`text-xl font-bold font-mono mt-0.5 ${simulationResult.difference_tonnes >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {simulationResult.difference_tonnes > 0 ? '+' : ''}{simulationResult.difference_tonnes} t
                  </p>
                </div>
                <div className="p-3.5 bg-slate-950/60 rounded-xl border border-slate-800 text-center">
                  <span className="text-[10px] text-slate-400 uppercase font-semibold block">Forecast Shortfall</span>
                  <p className="text-xl font-bold text-rose-400 font-mono mt-0.5">{simulationResult.revised_shortfall_tonnes} t</p>
                </div>
              </div>

              {/* Chart */}
              <div className="h-56 w-full pt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="name" stroke="#64748b" fontSize={11} />
                    <YAxis stroke="#64748b" fontSize={11} domain={[0, 3200]} />
                    <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', fontSize: '12px' }} />
                    <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                    <Bar dataKey="Baseline" fill="#64748b" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="Scenario" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="Target" fill="#38bdf8" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Cyclic Queueing & Crusher Circuit */}
              {simulationResult.queueing_physics && (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 border-t border-slate-800">
                  <div className="p-4 rounded-xl bg-slate-950/40 border border-slate-800 space-y-2">
                    <span className="text-xs font-bold text-amber-400 uppercase tracking-wider block">
                      Cyclic Haul Queueing Physics
                    </span>
                    <div className="text-xs text-slate-300 font-medium">
                      Status: <span className="text-white font-bold">{simulationResult.queueing_physics.queue_bottleneck}</span>
                    </div>
                    <div className="flex justify-between text-xs text-slate-400">
                      <span>Shovel Wait: {simulationResult.queueing_physics.shovel_idle_wait_min_per_hr} min/hr</span>
                      <span>Dumper Wait: {simulationResult.queueing_physics.truck_queue_wait_min_per_cycle} min/cyc</span>
                    </div>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-950/40 border border-slate-800 space-y-2">
                    <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider block">
                      Primary Crusher Circuit
                    </span>
                    <div className="text-xs text-slate-300">
                      Rated: 450 TPH • Intake: <span className="font-mono font-bold text-white">{simulationResult.crushing_circuit?.crushed_ore_tonnes ?? 2200} t</span>
                    </div>
                    <div className="text-xs text-slate-400">
                      Circuit Utilization: <span className="font-mono font-bold text-cyan-400">{simulationResult.crushing_circuit?.crusher_utilization_pct ?? 85}%</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Stockpile Inventory & Rail Logistics */}
              {simulationResult.stockpiles && (
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
                  {Object.entries(simulationResult.stockpiles).map(([k, s]: [string, any]) => (
                    <div key={k} className="p-3.5 rounded-xl bg-slate-950/50 border border-slate-800/80 space-y-1">
                      <span className="text-[10px] uppercase font-bold text-slate-400 block">{s.grade_spec}</span>
                      <div className="text-base font-black text-white font-mono">
                        {Math.round(s.current_level_tonnes).toLocaleString()} t
                      </div>
                      <div className="text-[10px] text-slate-500">
                        {s.utilization_pct}% capacity ({s.capacity_tonnes.toLocaleString()} t max)
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Rail Dispatch Status */}
              {simulationResult.rail_dispatch && (
                <div className="p-4 rounded-xl bg-gradient-to-r from-blue-950/30 to-slate-950 border border-blue-900/40 flex items-center justify-between text-xs">
                  <div className="flex items-center gap-3">
                    <Train className="w-5 h-5 text-blue-400 shrink-0" />
                    <div>
                      <span className="font-bold text-white block">Rail Dispatch to Domestic Smelters</span>
                      <span className="text-slate-400 text-[11px]">{simulationResult.rail_dispatch.destination_corridors}</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="font-mono font-bold text-cyan-400 block">{simulationResult.rail_dispatch.total_dispatched_tonnes} t / day</span>
                    <span className="text-[10px] text-slate-400">{simulationResult.rail_dispatch.wagon_type}</span>
                  </div>
                </div>
              )}

              {/* Save Scenario Bar */}
              <div className="flex gap-2 pt-2 border-t border-slate-800">
                <input
                  type="text"
                  placeholder="Scenario name (e.g. Monsoon 25mm Contingency + 1 Shovel)"
                  value={scenarioName}
                  onChange={(e) => setScenarioName(e.target.value)}
                  className="flex-1 bg-slate-950 border border-slate-800 px-3 py-2 rounded-xl text-xs text-white"
                />
                <button
                  onClick={handleSaveScenario}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs rounded-xl transition flex items-center gap-1.5"
                >
                  <Save className="w-4 h-4" />
                  Save Scenario
                </button>
              </div>
            </div>
          )}

          {/* Saved Scenarios Table */}
          {savedScenarios.length > 0 && (
            <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800 space-y-3">
              <h3 className="font-bold text-sm text-white">Saved Scenario History</h3>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {savedScenarios.map((sc) => (
                  <div key={sc.id} className="p-3 bg-slate-950/60 rounded-xl border border-slate-800/80 flex justify-between items-center text-xs">
                    <div>
                      <p className="font-bold text-white">{sc.name}</p>
                      <p className="text-[10px] text-slate-400">{sc.created_at} | Output: {sc.results.scenario_forecast_tonnes} tonnes</p>
                    </div>
                    <button
                      onClick={() => handleDeleteScenario(sc.id)}
                      className="text-rose-400 hover:text-rose-300 p-1.5"
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
