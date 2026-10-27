import React, { useState, useEffect } from 'react';
import {
  Wrench, AlertTriangle, ShieldCheck, Clock, Activity,
  CheckCircle2, Gauge, RefreshCw, Cpu, Flame, Layers
} from 'lucide-react';
import { api } from '../services/api';
import type { EquipmentRiskResponse, EquipmentRiskItem } from '../types';

export const EquipmentHealth: React.FC = () => {
  const [data, setData] = useState<EquipmentRiskResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedMachine, setSelectedMachine] = useState<EquipmentRiskItem | null>(null);
  const [filterType, setFilterType] = useState<string>('All');

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await api.getEquipmentRisks('MINE-001');
      setData(res);
      if (res.equipment && res.equipment.length > 0) {
        setSelectedMachine(res.equipment[0]);
      }
    } catch (err) {
      console.error('Failed to load equipment risk data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const filteredFleet = data?.equipment.filter((eq) => {
    if (filterType === 'All') return true;
    if (filterType === 'Excavators') return eq.equipment_type.toLowerCase().includes('excavator') || eq.equipment_type.toLowerCase().includes('shovel');
    if (filterType === 'Trucks') return eq.equipment_type.toLowerCase().includes('truck') || eq.equipment_type.toLowerCase().includes('dumper');
    if (filterType === 'HighRisk') return eq.failure_risk_72h >= 0.35;
    return true;
  }) || [];

  return (
    <div className="space-y-6">
      {/* Page Title & Action Bar */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-slate-900/60 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400">
              <Wrench className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight">Fleet Health & Predictive Maintenance</h1>
              <p className="text-slate-400 text-sm mt-0.5">
                Calibrated machine breakdown probability (24h, 48h, 72h) feeding directly into production forecasting.
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={loadData}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium rounded-xl border border-slate-700 transition"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh Telemetry
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-slate-900/40 border border-slate-800/80 backdrop-blur-lg">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs uppercase tracking-wider font-semibold">Active Fleet Size</span>
            <Activity className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-3xl font-extrabold text-white">
            {data?.fleet_count ?? 12}
            <span className="text-xs font-normal text-slate-400 ml-2">heavy units</span>
          </div>
          <p className="text-xs text-slate-400 mt-2 flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            Dongri Buzurg Pit & ROM operations
          </p>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/40 border border-slate-800/80 backdrop-blur-lg">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs uppercase tracking-wider font-semibold">High Breakdown Risk (&gt;35%)</span>
            <AlertTriangle className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-3xl font-extrabold text-rose-400">
            {data?.high_risk_count ?? 0}
            <span className="text-xs font-normal text-slate-400 ml-2">units flagged</span>
          </div>
          <p className="text-xs text-slate-400 mt-2">
            Requires pre-emptive inspection within 48h
          </p>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/40 border border-slate-800/80 backdrop-blur-lg">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs uppercase tracking-wider font-semibold">Average Fleet Health</span>
            <Gauge className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-3xl font-extrabold text-cyan-400">
            {data?.fleet_health_score_avg ?? 86.4}
            <span className="text-xs font-normal text-slate-400 ml-1">/ 100</span>
          </div>
          <p className="text-xs text-slate-400 mt-2">
            Wear rate index based on duty cycle & hours
          </p>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/40 border border-slate-800/80 backdrop-blur-lg">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs uppercase tracking-wider font-semibold">7-Day Expected Downtime</span>
            <Clock className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-3xl font-extrabold text-amber-400">
            {data?.expected_total_downtime_hours_next_7d ?? 10.5}
            <span className="text-xs font-normal text-slate-400 ml-2">hours lost</span>
          </div>
          <p className="text-xs text-slate-400 mt-2">
            Feeds directly into Production Forecast P10-P90
          </p>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
        {['All', 'Excavators', 'Trucks', 'HighRisk'].map((tab) => (
          <button
            key={tab}
            onClick={() => setFilterType(tab)}
            className={`px-4 py-2 rounded-xl text-xs font-semibold tracking-wide transition ${
              filterType === tab
                ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            {tab === 'HighRisk' ? 'High Risk Units' : tab}
          </button>
        ))}
      </div>

      {/* Fleet Table & Selected Machine Detail View */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Fleet Telemetry & Risk Table */}
        <div className="lg:col-span-2 rounded-2xl bg-slate-900/40 border border-slate-800 overflow-hidden">
          <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-900/60">
            <div className="flex items-center gap-2">
              <Cpu className="w-4 h-4 text-amber-400" />
              <h2 className="text-sm font-semibold text-white">Machine Telemetry & Calibrated Risk Table</h2>
            </div>
            <span className="text-xs text-slate-400">Click a machine to inspect telemetry</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/60 text-slate-400 border-b border-slate-800 uppercase tracking-wider font-semibold">
                <tr>
                  <th className="py-3 px-4">Equipment</th>
                  <th className="py-3 px-3">Type</th>
                  <th className="py-3 px-3">Engine Hrs</th>
                  <th className="py-3 px-3">Since Svc</th>
                  <th className="py-3 px-3">Load %</th>
                  <th className="py-3 px-3 text-center">24h Risk</th>
                  <th className="py-3 px-3 text-center">48h Risk</th>
                  <th className="py-3 px-3 text-center">72h Risk</th>
                  <th className="py-3 px-3 text-right">Health</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {filteredFleet.map((eq) => {
                  const isSelected = selectedMachine?.id === eq.id;
                  const isCritical = eq.failure_risk_72h >= 0.40;
                  const isWarning = eq.failure_risk_72h >= 0.20 && !isCritical;

                  return (
                    <tr
                      key={eq.id}
                      onClick={() => setSelectedMachine(eq)}
                      className={`cursor-pointer transition hover:bg-slate-800/40 ${
                        isSelected ? 'bg-amber-500/10 border-l-2 border-amber-400' : ''
                      }`}
                    >
                      <td className="py-3.5 px-4 font-semibold text-white">
                        <div className="flex items-center gap-2">
                          <span className={`w-2 h-2 rounded-full ${isCritical ? 'bg-rose-500' : isWarning ? 'bg-amber-500' : 'bg-emerald-500'}`} />
                          {eq.name}
                        </div>
                      </td>
                      <td className="py-3.5 px-3 text-slate-400">{eq.equipment_type}</td>
                      <td className="py-3.5 px-3 text-slate-300 font-mono">{eq.engine_hours.toFixed(0)}</td>
                      <td className="py-3.5 px-3 font-mono">
                        <span className={eq.hours_since_last_maintenance > 200 ? 'text-amber-400 font-bold' : 'text-slate-300'}>
                          {eq.hours_since_last_maintenance.toFixed(0)}h
                        </span>
                      </td>
                      <td className="py-3.5 px-3 font-mono text-slate-300">{eq.average_load_pct.toFixed(0)}%</td>
                      <td className="py-3.5 px-3 text-center">
                        <span className="font-mono text-slate-300">{Math.round(eq.failure_risk_24h * 100)}%</span>
                      </td>
                      <td className="py-3.5 px-3 text-center">
                        <span className="font-mono text-slate-300">{Math.round(eq.failure_risk_48h * 100)}%</span>
                      </td>
                      <td className="py-3.5 px-3 text-center">
                        <span
                          className={`inline-block px-2 py-0.5 rounded-full font-mono font-bold ${
                            isCritical
                              ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                              : isWarning
                              ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                              : 'bg-emerald-500/20 text-emerald-400'
                          }`}
                        >
                          {Math.round(eq.failure_risk_72h * 100)}%
                        </span>
                      </td>
                      <td className="py-3.5 px-3 text-right font-mono font-semibold text-cyan-400">
                        {eq.health_score.toFixed(0)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right Col: Machine Diagnostic Dossier */}
        {selectedMachine && (
          <div className="rounded-2xl bg-slate-900/60 border border-slate-800 p-6 space-y-5">
            <div className="border-b border-slate-800 pb-4">
              <div className="flex items-center justify-between">
                <span className="text-xs uppercase font-mono tracking-wider text-amber-400 font-bold">
                  Machine Diagnostic Dossier
                </span>
                <span
                  className={`text-xs px-2.5 py-1 rounded-full font-semibold ${
                    selectedMachine.failure_risk_72h >= 0.40
                      ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                      : selectedMachine.failure_risk_72h >= 0.20
                      ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                      : 'bg-emerald-500/20 text-emerald-400'
                  }`}
                >
                  {selectedMachine.status}
                </span>
              </div>
              <h3 className="text-xl font-bold text-white mt-1">{selectedMachine.name}</h3>
              <p className="text-xs text-slate-400">{selectedMachine.equipment_type} • Rated {selectedMachine.capacity_tph} TPH</p>
            </div>

            {/* Risk Probabilities Progress Bars */}
            <div className="space-y-3 bg-slate-950/40 p-4 rounded-xl border border-slate-800/80">
              <span className="text-xs font-semibold text-slate-300">Breakdown Risk Horizons:</span>
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-400">24-Hour Breakdown Risk:</span>
                  <span className="font-mono font-bold text-white">{Math.round(selectedMachine.failure_risk_24h * 100)}%</span>
                </div>
                <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                  <div
                    className="h-full bg-emerald-400 transition-all"
                    style={{ width: `${selectedMachine.failure_risk_24h * 100}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-400">48-Hour Breakdown Risk:</span>
                  <span className="font-mono font-bold text-amber-400">{Math.round(selectedMachine.failure_risk_48h * 100)}%</span>
                </div>
                <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                  <div
                    className="h-full bg-amber-400 transition-all"
                    style={{ width: `${selectedMachine.failure_risk_48h * 100}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-400">72-Hour Breakdown Risk:</span>
                  <span className="font-mono font-bold text-rose-400">{Math.round(selectedMachine.failure_risk_72h * 100)}%</span>
                </div>
                <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                  <div
                    className="h-full bg-rose-500 transition-all"
                    style={{ width: `${selectedMachine.failure_risk_72h * 100}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Critical Subsystem Under Stress */}
            <div className="p-4 rounded-xl bg-slate-950/40 border border-slate-800/80">
              <div className="flex items-center gap-2 text-rose-400 text-xs font-semibold uppercase tracking-wider mb-1">
                <Flame className="w-4 h-4" />
                Vulnerable Subsystem
              </div>
              <div className="text-sm font-bold text-white">{selectedMachine.critical_component}</div>
              <p className="text-xs text-slate-400 mt-1">
                Expected lost shift time next 7 days: <span className="text-amber-400 font-mono font-bold">+{selectedMachine.expected_downtime_hours_next_7d} hours</span>
              </p>
            </div>

            {/* Top Root Cause Factors */}
            <div>
              <span className="text-xs font-semibold text-slate-300 block mb-2">Identified Risk Factors:</span>
              <div className="space-y-1.5">
                {selectedMachine.top_risk_factors.map((factor, idx) => (
                  <div key={idx} className="flex items-start gap-2 text-xs text-slate-400 bg-slate-900/80 p-2 rounded-lg border border-slate-800">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 shrink-0" />
                    <span>{factor}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Recommended Action */}
            <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30">
              <span className="text-xs font-bold text-amber-400 uppercase tracking-wider block mb-1">
                Recommended Action:
              </span>
              <p className="text-xs text-slate-200 font-medium leading-relaxed">
                {selectedMachine.recommended_action}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Model Calibration & Scientific Disclaimer */}
      <div className="p-4 rounded-2xl bg-slate-900/30 border border-slate-800/60 text-xs text-slate-400 flex items-start gap-3">
        <ShieldCheck className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-slate-300">Model Methodology & Validation:</span>
          <p className="mt-0.5">
            Breakdown probabilities are generated using a Calibrated Random Forest Classifier evaluated on a chronological out-of-time test split.
            Outputs feed directly into the Quantile Production Forecasting Engine as forward-looking loss hours rather than contemporaneous after-the-fact surprises.
          </p>
        </div>
      </div>
    </div>
  );
};
