import React, { useState, useEffect } from 'react';
import { Layers, RefreshCw, Table } from 'lucide-react';
import type { ReserveEstimate, OreBlock } from '../types';
import { api } from '../services/api';

interface ReserveProps {
  blocks: OreBlock[];
}

export const ReserveIntelligence: React.FC<ReserveProps> = () => {
  const [cutoffGrade, setCutoffGrade] = useState<number>(15.0);
  const [bulkDensity, setBulkDensity] = useState<number>(3.4);
  const [estimate, setEstimate] = useState<ReserveEstimate | null>(null);
  const [isCalculating, setIsCalculating] = useState<boolean>(false);

  const fetchEstimate = async () => {
    setIsCalculating(true);
    try {
      const res = await api.estimateReserves('MINE-001', bulkDensity, cutoffGrade);
      setEstimate(res);
    } catch (err) {
      console.error('Error calculating reserves:', err);
    } finally {
      setIsCalculating(false);
    }
  };

  useEffect(() => {
    fetchEstimate();
  }, [cutoffGrade, bulkDensity]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Layers className="w-5 h-5 text-amber-500" />
            Manganese Reserve & Grade Estimation Engine
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Calculates ore block volume, tonnage (Tonnage = Volume × Density), average Mn grade, and contained manganese (Contained Mn = Tonnage × Grade / 100).
          </p>
        </div>

        {/* Dynamic Controls */}
        <div className="flex flex-wrap items-center gap-4 bg-slate-950 p-3 rounded-lg border border-slate-800 text-xs">
          <div className="flex items-center gap-2">
            <span className="text-slate-400 font-medium">Cutoff Grade:</span>
            <input
              type="range"
              min="5"
              max="30"
              step="1"
              value={cutoffGrade}
              onChange={(e) => setCutoffGrade(Number(e.target.value))}
              className="w-24 accent-amber-500 cursor-pointer"
            />
            <span className="font-mono font-bold text-amber-400 w-8">{cutoffGrade}%</span>
          </div>

          <div className="h-4 w-px bg-slate-800" />

          <div className="flex items-center gap-2">
            <span className="text-slate-400 font-medium">Bulk Density:</span>
            <input
              type="number"
              step="0.1"
              min="2.5"
              max="4.5"
              value={bulkDensity}
              onChange={(e) => setBulkDensity(Number(e.target.value))}
              className="w-16 bg-slate-900 border border-slate-700 px-2 py-1 rounded text-amber-400 font-mono text-xs"
            />
            <span className="text-slate-400 text-[10px]">t/m³</span>
          </div>

          <button
            onClick={fetchEstimate}
            className="p-1.5 bg-slate-800 hover:bg-slate-700 rounded text-slate-300"
            title="Recalculate"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isCalculating ? 'animate-spin text-amber-500' : ''}`} />
          </button>
        </div>
      </div>

      {/* Summary KPI Cards */}
      {estimate && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
            <span className="text-xs text-slate-500 font-semibold uppercase tracking-wider">Total Volume</span>
            <p className="text-2xl font-black text-slate-900 mt-2">
              {(estimate.total_volume_m3 / 1000000).toFixed(2)}M <span className="text-xs font-normal text-slate-500">m³</span>
            </p>
            <p className="text-[11px] text-slate-400 mt-1">Sum of 25 model ore blocks</p>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
            <span className="text-xs text-slate-500 font-semibold uppercase tracking-wider">Total Ore Tonnage</span>
            <p className="text-2xl font-black text-slate-900 mt-2">
              {(estimate.total_ore_tonnage / 1000000).toFixed(2)}M <span className="text-xs font-normal text-slate-500">tonnes</span>
            </p>
            <p className="text-[11px] text-slate-400 mt-1">Density = {estimate.bulk_density_t_per_m3} t/m³</p>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
            <span className="text-xs text-slate-500 font-semibold uppercase tracking-wider">Contained Manganese</span>
            <p className="text-2xl font-black text-purple-700 mt-2">
              {(estimate.total_contained_mn_tonnes / 1000000).toFixed(2)}M <span className="text-xs font-normal text-slate-500">tonnes</span>
            </p>
            <p className="text-[11px] text-slate-400 mt-1">At cutoff grade &ge; {estimate.cutoff_grade_pct}% Mn</p>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
            <span className="text-xs text-slate-500 font-semibold uppercase tracking-wider">Average Mn Grade</span>
            <p className="text-2xl font-black text-amber-600 mt-2">
              {estimate.average_mn_grade_pct}%
            </p>
            <p className="text-[11px] text-slate-400 mt-1">Weighted average manganese purity</p>
          </div>
        </div>
      )}

      {/* Reserves Breakdown Table by Geological Category */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
        <h3 className="font-bold text-base text-slate-900 mb-4 flex items-center gap-2">
          <Table className="w-4 h-4 text-amber-500" />
          Resource Categorization (Measured, Indicated, Inferred & Targets)
        </h3>

        {estimate && estimate.categories && (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-600 border-b border-slate-200 font-semibold">
                <tr>
                  <th className="py-3 px-4">Resource Category</th>
                  <th className="py-3 px-4">Block Count</th>
                  <th className="py-3 px-4">Ore Tonnage (tonnes)</th>
                  <th className="py-3 px-4">Avg Mn Grade (%)</th>
                  <th className="py-3 px-4">Contained Mn (tonnes)</th>
                  <th className="py-3 px-4">Share of Total</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {Object.entries(estimate.categories).map(([catName, data]) => {
                  const share = estimate.total_ore_tonnage > 0 ? (data.tonnage / estimate.total_ore_tonnage * 100).toFixed(1) : '0';
                  return (
                    <tr key={catName} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3 px-4 font-bold text-slate-800">{catName}</td>
                      <td className="py-3 px-4 text-slate-600 font-mono">{data.count}</td>
                      <td className="py-3 px-4 text-slate-900 font-mono">{data.tonnage.toLocaleString()} t</td>
                      <td className="py-3 px-4 text-amber-600 font-mono font-bold">{data.avg_grade}%</td>
                      <td className="py-3 px-4 text-purple-700 font-mono font-bold">{data.contained_mn.toLocaleString()} t</td>
                      <td className="py-3 px-4 text-slate-500 font-mono">{share}%</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
