import React, { useState, useEffect } from 'react';
import {
  Zap, CheckCircle2, XCircle, Play, Sliders, Calendar,
  ShieldCheck, Wrench, RefreshCw, Cpu, Layers, Flame, ArrowRight
} from 'lucide-react';
import type {
  Recommendation, DispatchOptimizationResult, BlastingScheduleResult
} from '../types';
import { api } from '../services/api';

interface AiActionCenterProps {
  recommendations: Recommendation[];
  onRefreshRecommendations: () => void;
}

export const AiActionCenter: React.FC<AiActionCenterProps> = ({
  recommendations,
  onRefreshRecommendations
}) => {
  const [activeTab, setActiveTab] = useState<'recommendations' | 'dispatch_optimizer' | 'blasting_scheduler'>('recommendations');
  const [loadingId, setLoadingId] = useState<string | null>(null);

  // Optimizer Inputs
  const [targetTonnes, setTargetTonnes] = useState<number>(2500);
  const [forecastRain, setForecastRain] = useState<number>(0);
  const [blendTargetMn, setBlendTargetMn] = useState<number>(30.0);
  const [dispatchResult, setDispatchResult] = useState<DispatchOptimizationResult | null>(null);
  const [solvingDispatch, setSolvingDispatch] = useState<boolean>(false);

  // Blasting Scheduler
  const [blastSchedule, setBlastSchedule] = useState<BlastingScheduleResult | null>(null);
  const [loadingBlast, setLoadingBlast] = useState<boolean>(false);

  // Load initial optimizer & blast schedule
  useEffect(() => {
    runDispatchOptimizer();
    loadBlastScheduler();
  }, []);

  const runDispatchOptimizer = async () => {
    setSolvingDispatch(true);
    try {
      const res = await api.optimizeDispatch({
        target_tonnes: targetTonnes,
        forecast_rain_mm: forecastRain,
        blend_target_mn_pct: blendTargetMn
      });
      setDispatchResult(res);
    } catch (err) {
      console.error('Failed to solve dispatch LP:', err);
    } finally {
      setSolvingDispatch(false);
    }
  };

  const loadBlastScheduler = async () => {
    setLoadingBlast(true);
    try {
      const res = await api.getBlastingWindow('MINE-001');
      setBlastSchedule(res);
    } catch (err) {
      console.error('Failed to load blasting window scheduler:', err);
    } finally {
      setLoadingBlast(false);
    }
  };

  const handleAction = async (recId: string, action: string) => {
    setLoadingId(recId);
    try {
      await api.updateRecommendationStatus(recId, action);
      onRefreshRecommendations();
    } catch (err) {
      console.error('Error updating recommendation action:', err);
    } finally {
      setLoadingId(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-900/60 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400">
            <Zap className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight">
              AI Action Center &amp; Operations Optimizer
            </h1>
            <p className="text-slate-400 text-sm mt-0.5">
              PuLP Linear Programming dispatch optimizer, weather-adaptive blasting scheduler, and simulator-validated corrective actions.
            </p>
          </div>
        </div>

        {/* Tab Controls */}
        <div className="flex items-center bg-slate-950 p-1.5 rounded-xl border border-slate-800 text-xs">
          <button
            onClick={() => setActiveTab('recommendations')}
            className={`px-3 py-1.5 rounded-lg font-bold transition ${
              activeTab === 'recommendations'
                ? 'bg-amber-500 text-slate-950 shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Validated Actions ({recommendations.length})
          </button>
          <button
            onClick={() => setActiveTab('dispatch_optimizer')}
            className={`px-3 py-1.5 rounded-lg font-bold transition ${
              activeTab === 'dispatch_optimizer'
                ? 'bg-amber-500 text-slate-950 shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Fleet Dispatch Optimizer (LP)
          </button>
          <button
            onClick={() => setActiveTab('blasting_scheduler')}
            className={`px-3 py-1.5 rounded-lg font-bold transition ${
              activeTab === 'blasting_scheduler'
                ? 'bg-amber-500 text-slate-950 shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Blasting Scheduler
          </button>
        </div>
      </div>

      {/* TAB 1: VALIDATED ACTION RECOMMENDATIONS */}
      {activeTab === 'recommendations' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center text-xs text-slate-400 px-1">
            <span>Prioritized corrective protocols evaluated against the Digital Twin Simulator</span>
            <button onClick={onRefreshRecommendations} className="hover:text-amber-400 flex items-center gap-1">
              <RefreshCw className="w-3.5 h-3.5" /> Refresh List
            </button>
          </div>

          {recommendations.map((rec) => (
            <div
              key={rec.id}
              className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800 backdrop-blur-lg hover:border-slate-700 transition space-y-4"
            >
              <div className="flex flex-col md:flex-row justify-between md:items-center gap-2 border-b border-slate-800/80 pb-3">
                <div className="flex items-center gap-3">
                  <span
                    className={`px-2.5 py-1 rounded-full text-xs font-bold ${
                      rec.priority === 'High'
                        ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                        : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                    }`}
                  >
                    {rec.priority} Priority
                  </span>
                  <h3 className="font-bold text-white text-base">{rec.title}</h3>
                </div>

                <div className="flex items-center gap-2 text-xs">
                  <span className="text-slate-400">Target Asset / Face:</span>
                  <span className="font-semibold text-slate-200 font-mono bg-slate-800/80 px-2.5 py-1 rounded-lg">
                    {rec.affected_block_or_mine}
                  </span>
                </div>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed">{rec.description}</p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 bg-slate-950/60 p-4 rounded-xl border border-slate-800/80 text-xs">
                <div>
                  <span className="text-slate-400 font-semibold block mb-0.5">Rationale &amp; Physics:</span>
                  <span className="text-slate-200">{rec.rationale}</span>
                </div>
                <div>
                  <span className="text-slate-400 font-semibold block mb-0.5">Constraints &amp; Logistics:</span>
                  <span className="text-slate-200">{rec.constraints_assumptions}</span>
                </div>
                <div>
                  <span className="text-slate-400 font-semibold block mb-0.5">Simulated Output Gain:</span>
                  <span className="text-emerald-400 font-mono font-bold text-base block mt-0.5">
                    +{rec.est_production_impact_tonnes} tonnes/day
                  </span>
                  <span className="text-[10px] text-slate-500">Validated via Digital Twin Simulator</span>
                </div>
              </div>

              {/* Approval Controls */}
              <div className="flex flex-col sm:flex-row justify-between items-center gap-3 pt-1">
                <div className="flex items-center gap-2 text-xs text-slate-400">
                  <span>Responsible Department:</span>
                  <span className="font-semibold text-white">{rec.responsible_team}</span>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleAction(rec.id, 'Approve')}
                    disabled={loadingId === rec.id}
                    className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs rounded-xl transition flex items-center gap-1.5 shadow-sm"
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    Approve Protocol
                  </button>
                  <button
                    onClick={() => handleAction(rec.id, 'Reject')}
                    disabled={loadingId === rec.id}
                    className="px-4 py-2 bg-slate-800 hover:bg-rose-900/60 text-slate-300 hover:text-rose-200 font-bold text-xs rounded-xl transition flex items-center gap-1.5"
                  >
                    <XCircle className="w-4 h-4" />
                    Dismiss
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* TAB 2: DISPATCH OPTIMIZER (PuLP LINEAR PROGRAMMING) */}
      {activeTab === 'dispatch_optimizer' && (
        <div className="space-y-6">
          {/* Controls Panel */}
          <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800 space-y-4">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Sliders className="w-5 h-5 text-amber-400" />
              Linear Programming Model Parameters (PuLP CBC Solver)
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-400">Daily Production Quota:</span>
                  <span className="font-mono font-bold text-white">{targetTonnes} t/day</span>
                </div>
                <input
                  type="range"
                  min="1800"
                  max="3500"
                  step="50"
                  value={targetTonnes}
                  onChange={(e) => setTargetTonnes(Number(e.target.value))}
                  className="w-full accent-amber-500 cursor-pointer"
                />
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-400">Rainfall Road Scenario:</span>
                  <span className="font-mono font-bold text-cyan-400">{forecastRain} mm</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="40"
                  step="2"
                  value={forecastRain}
                  onChange={(e) => setForecastRain(Number(e.target.value))}
                  className="w-full accent-cyan-500 cursor-pointer"
                />
                <span className="text-[10px] text-slate-500">
                  {forecastRain > 15 ? '30% speed reduction' : forecastRain > 5 ? '15% speed reduction' : 'Dry haul roads'}
                </span>
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-400">Target Blend Grade:</span>
                  <span className="font-mono font-bold text-purple-400">{blendTargetMn}% Mn</span>
                </div>
                <input
                  type="range"
                  min="24"
                  max="35"
                  step="0.5"
                  value={blendTargetMn}
                  onChange={(e) => setBlendTargetMn(Number(e.target.value))}
                  className="w-full accent-purple-500 cursor-pointer"
                />
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={runDispatchOptimizer}
                disabled={solvingDispatch}
                className="flex items-center gap-2 px-5 py-2.5 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs rounded-xl shadow-lg shadow-amber-500/10 transition"
              >
                <Play className={`w-4 h-4 ${solvingDispatch ? 'animate-spin' : ''}`} />
                Solve Optimal Fleet Allocation
              </button>
            </div>
          </div>

          {/* Solver Summary KPIs */}
          {dispatchResult && (
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
              <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800">
                <span className="text-[11px] uppercase font-bold text-slate-400 block">Solver Status</span>
                <span className="text-xl font-black text-emerald-400 font-mono">{dispatchResult.solver_status}</span>
                <p className="text-[11px] text-slate-500 mt-1">PuLP CBC Simplex Engine</p>
              </div>

              <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800">
                <span className="text-[11px] uppercase font-bold text-slate-400 block">Optimized Daily Output</span>
                <span className="text-xl font-black text-white font-mono">{dispatchResult.optimized_total_tonnes} t</span>
                <p className="text-[11px] text-slate-500 mt-1">Shortfall: {dispatchResult.expected_shortfall_tonnes} t</p>
              </div>

              <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800">
                <span className="text-[11px] uppercase font-bold text-slate-400 block">Optimized Blended Grade</span>
                <span className="text-xl font-black text-purple-400 font-mono">{dispatchResult.blended_grades.mn_grade_pct}% Mn</span>
                <p className="text-[11px] text-slate-500 mt-1">SiO2: {dispatchResult.blended_grades.sio2_grade_pct}% • Fe: {dispatchResult.blended_grades.fe_grade_pct}%</p>
              </div>

              <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800">
                <span className="text-[11px] uppercase font-bold text-slate-400 block">Truck Fleet Deployed</span>
                <span className="text-xl font-black text-cyan-400 font-mono">
                  {dispatchResult.fleet_deployed.total_trucks} Dumpers
                </span>
                <p className="text-[11px] text-slate-500 mt-1">Standby buffer: {dispatchResult.fleet_deployed.trucks_idle_or_standby} units</p>
              </div>
            </div>
          )}

          {/* Allocation Matrix Table */}
          {dispatchResult && (
            <div className="rounded-2xl bg-slate-900/40 border border-slate-800 overflow-hidden">
              <div className="p-4 border-b border-slate-800 bg-slate-900/60 flex justify-between items-center">
                <h3 className="text-sm font-bold text-white">Optimal Bench-to-Shovel Allocation Matrix</h3>
                <span className="text-xs text-slate-400 font-mono">Matched to grade blending &amp; rain friction</span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950/60 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                    <tr>
                      <th className="py-3 px-4">Bench Face</th>
                      <th className="py-3 px-4">Allocated Dumpers</th>
                      <th className="py-3 px-4 text-right">Daily Output (t)</th>
                      <th className="py-3 px-4 text-right">In-Situ Mn Grade</th>
                      <th className="py-3 px-4 text-right">Haul Distance</th>
                      <th className="py-3 px-4 text-right">Cycle Time</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-medium">
                    {dispatchResult.bench_allocations.map((alloc) => (
                      <tr key={alloc.bench_id} className="hover:bg-slate-800/30 transition">
                        <td className="py-3.5 px-4 font-bold text-white">{alloc.bench_name}</td>
                        <td className="py-3.5 px-4">
                          <span className="bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 px-2.5 py-1 rounded-lg font-mono font-bold">
                            {alloc.allocated_trucks} Trucks
                          </span>
                        </td>
                        <td className="py-3.5 px-4 text-right font-mono font-bold text-white">
                          {alloc.optimized_production_tonnes} t
                        </td>
                        <td className="py-3.5 px-4 text-right font-mono text-purple-400 font-bold">
                          {alloc.in_situ_mn_grade_pct}%
                        </td>
                        <td className="py-3.5 px-4 text-right font-mono text-slate-300">
                          {alloc.haul_distance_km} km
                        </td>
                        <td className="py-3.5 px-4 text-right font-mono text-amber-400 font-bold">
                          {alloc.cycle_time_min} min
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 3: BLASTING SCHEDULER */}
      {activeTab === 'blasting_scheduler' && blastSchedule && (
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-gradient-to-r from-purple-950/40 via-slate-900/40 to-slate-950/40 border border-purple-800/40 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div>
              <span className="text-xs font-mono uppercase font-bold text-purple-400">Optimal Blast Clearance Window</span>
              <h2 className="text-2xl font-black text-white mt-1">
                {blastSchedule.optimal_blast_day} • {blastSchedule.recommended_time}
              </h2>
              <p className="text-xs text-slate-300 mt-1 max-w-2xl leading-relaxed">
                {blastSchedule.primary_rationale}
              </p>
            </div>
            <div className="p-4 rounded-xl bg-purple-500/20 border border-purple-500/30 text-center">
              <span className="text-[10px] uppercase font-bold text-purple-300 block">Safety Clearance Radius</span>
              <span className="text-2xl font-black text-white font-mono">{blastSchedule.evacuation_radius_meters} m</span>
            </div>
          </div>

          <div className="rounded-2xl bg-slate-900/40 border border-slate-800 p-6 space-y-4">
            <h3 className="text-sm font-bold text-white">7-Day Lookahead Weather &amp; Blast Window Suitability</h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {blastSchedule.weekly_lookahead.map((cand) => {
                const isOptimal = cand.suitability === 'Recommended';
                const isLockout = cand.suitability.includes('Not Recommended');

                return (
                  <div
                    key={cand.date}
                    className={`p-4 rounded-xl border space-y-3 transition ${
                      isOptimal
                        ? 'bg-purple-950/30 border-purple-500/50 shadow-md shadow-purple-950/50'
                        : isLockout
                        ? 'bg-rose-950/20 border-rose-900/40 opacity-75'
                        : 'bg-slate-950/40 border-slate-800'
                    }`}
                  >
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-bold text-white">{cand.date}</span>
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                          isOptimal
                            ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40'
                            : isLockout
                            ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                            : 'bg-slate-800 text-slate-300'
                        }`}
                      >
                        Score: {cand.score}/100
                      </span>
                    </div>

                    <div className="space-y-1 text-xs">
                      <div className="flex justify-between">
                        <span className="text-slate-400">Forecast Rain:</span>
                        <span className="font-mono text-cyan-400 font-bold">{cand.forecast_rainfall_mm} mm</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Peak Temp:</span>
                        <span className="font-mono text-amber-400">{cand.max_temp_c}°C</span>
                      </div>
                    </div>

                    <div className="pt-2 border-t border-slate-800/60 text-xs">
                      <span className="text-slate-400 block text-[10px]">Assessment:</span>
                      <span className="text-slate-200 font-medium text-[11px]">{cand.rain_risk_assessment}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
