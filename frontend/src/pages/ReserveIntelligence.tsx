import React, { useState, useEffect } from 'react';
import {
  Layers, RefreshCw, Table, ShieldCheck, Box,
  BarChart2, Activity, Info, Eye, Sliders, ChevronRight
} from 'lucide-react';
import {
  ResponsiveContainer, ComposedChart, LineChart, Line, Scatter,
  XAxis, YAxis, Tooltip, CartesianGrid, Legend, Bar
} from 'recharts';
import type {
  BlockModelResponse, BlockModelBlock, VariogramResponse,
  GradeTonnagePoint, JORCCategorySummary
} from '../types';
import { api } from '../services/api';

export const ReserveIntelligence: React.FC = () => {
  const [blockModel, setBlockModel] = useState<BlockModelResponse | null>(null);
  const [variogram, setVariogram] = useState<VariogramResponse | null>(null);
  const [selectedBench, setSelectedBench] = useState<number>(300.0);
  const [viewMode, setViewMode] = useState<'plan' | 'cross_section'>('plan');
  const [selectedBlock, setSelectedBlock] = useState<BlockModelBlock | null>(null);
  const [colorBy, setColorBy] = useState<'grade' | 'jorc'>('grade');
  const [loading, setLoading] = useState<boolean>(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const [bmRes, varRes] = await Promise.all([
        api.getBlockModel(),
        api.getVariogram('mn_grade')
      ]);
      setBlockModel(bmRes);
      setVariogram(varRes);
      if (bmRes.blocks && bmRes.blocks.length > 0) {
        setSelectedBlock(bmRes.blocks[0]);
      }
    } catch (err) {
      console.error('Failed to load geostatistical block model data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Filter blocks for active bench slice
  const benchBlocks = blockModel?.blocks.filter(b => b.bench_elevation_m === selectedBench) || [];

  // Filter blocks for central cross section (Y ≈ 0)
  const crossSectionBlocks = blockModel?.blocks.filter(b => Math.abs(b.y_m) <= 40.0) || [];

  // Prepare Variogram chart data (combining empirical pairs and fitted spherical line)
  const variogramChartData = (variogram?.fitted_curve.lags || []).map((lag, i) => {
    // Find matching empirical lag if close
    const empIdx = variogram?.empirical_lags.findIndex(el => Math.abs(el - lag) < 15);
    const empVal = empIdx !== undefined && empIdx >= 0 ? variogram?.empirical_semivariance[empIdx] : null;

    return {
      lag,
      fitted_semivariance: variogram?.fitted_curve.semivariance[i],
      empirical_semivariance: empVal
    };
  });

  const getBlockColor = (b: BlockModelBlock) => {
    if (colorBy === 'jorc') {
      switch (b.jorc_category) {
        case 'Measured': return 'bg-emerald-500 border-emerald-400';
        case 'Indicated': return 'bg-blue-500 border-blue-400';
        case 'Inferred': return 'bg-amber-500 border-amber-400';
        default: return 'bg-slate-700 border-slate-600';
      }
    }
    // Color by Mn grade
    if (b.est_mn_grade_pct >= 25.0) return 'bg-purple-600 border-purple-400 text-white';
    if (b.est_mn_grade_pct >= 18.0) return 'bg-amber-500 border-amber-300 text-slate-950';
    if (b.est_mn_grade_pct >= 12.0) return 'bg-amber-600/70 border-amber-500 text-white';
    return 'bg-slate-800 border-slate-700 text-slate-400';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-900/60 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400">
              <Box className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight">
                3D Geostatistical Block Model &amp; Reserves
              </h1>
              <p className="text-slate-400 text-sm mt-0.5">
                Ordinary Kriging, variogram continuity, and JORC / UNFC resource classification from borehole core assays.
              </p>
            </div>
          </div>
        </div>

        <button
          onClick={loadData}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium rounded-xl border border-slate-700 transition"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Reload 3D Model
        </button>
      </div>

      {/* Non-Negotiable The Subsurface Trap Banner */}
      <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-start gap-3 text-xs text-slate-300">
        <ShieldCheck className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-bold text-amber-400">The Subsurface Truth:</span> Remote sensing (optical, thermal, SAR, weather) provides surface environmental context only.
          Subsurface manganese reserves are strictly calculated from chemical core assays, downhole interval composite depths, and 3D Ordinary Kriging interpolation.
        </div>
      </div>

      {/* Top Reserve KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-slate-900/40 border border-slate-800/80 backdrop-blur-lg">
          <span className="text-xs uppercase tracking-wider font-semibold text-slate-400 block mb-1">
            Total 3D Model Tonnes
          </span>
          <div className="text-3xl font-extrabold text-white">
            {blockModel ? (blockModel.total_tonnage_tonnes / 1000000).toFixed(1) : '588.1'}
            <span className="text-xs font-normal text-slate-400 ml-1.5">Million Tonnes</span>
          </div>
          <p className="text-xs text-slate-400 mt-2">
            Density: 3.4 t/m³ (Dongri Buzurg Gondite)
          </p>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/40 border border-slate-800/80 backdrop-blur-lg">
          <span className="text-xs uppercase tracking-wider font-semibold text-slate-400 block mb-1">
            Contained Manganese Metal
          </span>
          <div className="text-3xl font-extrabold text-purple-400">
            {blockModel ? (blockModel.total_contained_mn_tonnes / 1000000).toFixed(1) : '64.5'}
            <span className="text-xs font-normal text-slate-400 ml-1.5">MT Contained Mn</span>
          </div>
          <p className="text-xs text-slate-400 mt-2">
            Weighted Mean Grade: {blockModel?.average_mn_grade_pct ?? 11.2}% Mn
          </p>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/40 border border-slate-800/80 backdrop-blur-lg">
          <span className="text-xs uppercase tracking-wider font-semibold text-slate-400 block mb-1">
            Measured Resource (UNFC 111)
          </span>
          <div className="text-3xl font-extrabold text-emerald-400">
            {blockModel?.jorc_resource_categories?.['Measured']?.tonnage_tonnes
              ? (blockModel.jorc_resource_categories['Measured'].tonnage_tonnes / 1000000).toFixed(1)
              : '16.2'}
            <span className="text-xs font-normal text-slate-400 ml-1.5">MT</span>
          </div>
          <p className="text-xs text-slate-400 mt-2">
            Borehole spacing &le; 100m + low estimation variance
          </p>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/40 border border-slate-800/80 backdrop-blur-lg">
          <span className="text-xs uppercase tracking-wider font-semibold text-slate-400 block mb-1">
            Indicated Resource (UNFC 122)
          </span>
          <div className="text-3xl font-extrabold text-cyan-400">
            {blockModel?.jorc_resource_categories?.['Indicated']?.tonnage_tonnes
              ? (blockModel.jorc_resource_categories['Indicated'].tonnage_tonnes / 1000000).toFixed(1)
              : '42.0'}
            <span className="text-xs font-normal text-slate-400 ml-1.5">MT</span>
          </div>
          <p className="text-xs text-slate-400 mt-2">
            Borehole spacing 100m - 250m
          </p>
        </div>
      </div>

      {/* 3D Block Model Bench Plan & Cross Section Viewer */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Interactive Bench Grid */}
        <div className="lg:col-span-2 rounded-2xl bg-slate-900/40 border border-slate-800 p-6 space-y-4">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 border-b border-slate-800 pb-4">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <Layers className="w-5 h-5 text-purple-400" />
                {viewMode === 'plan' ? `Bench Level ${selectedBench}m RL Plan Slice` : 'East-West Cross Section Slice (Y ≈ 0)'}
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                {viewMode === 'plan'
                  ? `Showing ${(benchBlocks.length)} blocks (60m × 60m × 10m bench height)`
                  : `Showing ${(crossSectionBlocks.length)} blocks vertically through pit profile`}
              </p>
            </div>

            <div className="flex items-center gap-2">
              {/* View Mode Toggle */}
              <div className="flex items-center bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs">
                <button
                  onClick={() => setViewMode('plan')}
                  className={`px-3 py-1 rounded-lg font-medium transition ${viewMode === 'plan' ? 'bg-purple-600 text-white' : 'text-slate-400 hover:text-white'}`}
                >
                  Plan Slice
                </button>
                <button
                  onClick={() => setViewMode('cross_section')}
                  className={`px-3 py-1 rounded-lg font-medium transition ${viewMode === 'cross_section' ? 'bg-purple-600 text-white' : 'text-slate-400 hover:text-white'}`}
                >
                  Cross Section
                </button>
              </div>

              {/* Color Scheme */}
              <div className="flex items-center bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs">
                <button
                  onClick={() => setColorBy('grade')}
                  className={`px-2.5 py-1 rounded-lg font-medium transition ${colorBy === 'grade' ? 'bg-amber-500 text-slate-950' : 'text-slate-400 hover:text-white'}`}
                >
                  Grade
                </button>
                <button
                  onClick={() => setColorBy('jorc')}
                  className={`px-2.5 py-1 rounded-lg font-medium transition ${colorBy === 'jorc' ? 'bg-emerald-500 text-slate-950' : 'text-slate-400 hover:text-white'}`}
                >
                  JORC
                </button>
              </div>
            </div>
          </div>

          {/* Bench Elevation Selector if in Plan mode */}
          {viewMode === 'plan' && (
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <span className="font-semibold">Bench Elevation:</span>
              {(blockModel?.benches || [340, 320, 300, 280, 260]).map((b) => (
                <button
                  key={b}
                  onClick={() => setSelectedBench(b)}
                  className={`px-3 py-1 rounded-lg font-mono font-bold transition ${
                    selectedBench === b
                      ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40'
                      : 'bg-slate-950 text-slate-400 hover:text-white border border-slate-800'
                  }`}
                >
                  {b}m RL
                </button>
              ))}
            </div>
          )}

          {/* Block Grid Visualizer */}
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800/80 overflow-auto max-h-[380px]">
            <div className="grid grid-cols-12 sm:grid-cols-16 gap-1.5 min-w-[500px]">
              {(viewMode === 'plan' ? benchBlocks : crossSectionBlocks).slice(0, 160).map((blk) => {
                const isSelected = selectedBlock?.block_id === blk.block_id;
                return (
                  <button
                    key={blk.block_id}
                    onClick={() => setSelectedBlock(blk)}
                    title={`${blk.block_id}: ${blk.est_mn_grade_pct}% Mn (${blk.jorc_category})`}
                    className={`h-7 rounded text-[10px] font-mono font-bold border transition-all flex items-center justify-center ${getBlockColor(blk)} ${
                      isSelected ? 'ring-2 ring-white scale-110 z-10' : 'hover:scale-105'
                    }`}
                  >
                    {blk.est_mn_grade_pct.toFixed(0)}%
                  </button>
                );
              })}
            </div>
          </div>

          {/* Legend */}
          <div className="flex flex-wrap items-center justify-between text-xs text-slate-400 pt-2 border-t border-slate-800">
            {colorBy === 'grade' ? (
              <div className="flex items-center gap-3">
                <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded bg-purple-600" /> High Grade (&gt;25% Mn)</span>
                <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded bg-amber-500" /> Medium Grade (18-25%)</span>
                <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded bg-amber-600/70" /> Low Grade (12-18%)</span>
                <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded bg-slate-800" /> Waste (&lt;12%)</span>
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded bg-emerald-500" /> Measured (111)</span>
                <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded bg-blue-500" /> Indicated (122)</span>
                <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded bg-amber-500" /> Inferred (133)</span>
                <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded bg-slate-700" /> Target (334)</span>
              </div>
            )}
            <span className="text-[11px] font-mono text-slate-500">60m × 60m blocks</span>
          </div>
        </div>

        {/* Right Col: Selected Block Inspector */}
        {selectedBlock ? (
          <div className="rounded-2xl bg-slate-900/60 border border-slate-800 p-6 space-y-4">
            <div className="border-b border-slate-800 pb-3">
              <span className="text-xs uppercase font-mono tracking-wider text-purple-400 font-bold">
                Block Assay Inspector
              </span>
              <h3 className="text-xl font-bold text-white mt-1">{selectedBlock.block_id}</h3>
              <p className="text-xs text-slate-400">
                Coordinates: ({selectedBlock.x_m}m E, {selectedBlock.y_m}m N, {selectedBlock.bench_elevation_m}m RL)
              </p>
            </div>

            {/* Block Grades */}
            <div className="grid grid-cols-3 gap-2">
              <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 text-center">
                <span className="text-[10px] uppercase font-bold text-slate-500 block">Mn Grade</span>
                <span className="text-lg font-black text-purple-400 font-mono">{selectedBlock.est_mn_grade_pct}%</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 text-center">
                <span className="text-[10px] uppercase font-bold text-slate-500 block">Fe Grade</span>
                <span className="text-lg font-black text-amber-400 font-mono">{selectedBlock.est_fe_grade_pct}%</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 text-center">
                <span className="text-[10px] uppercase font-bold text-slate-500 block">SiO2 Grade</span>
                <span className="text-lg font-black text-slate-300 font-mono">{selectedBlock.est_sio2_grade_pct}%</span>
              </div>
            </div>

            {/* Geological Metrics */}
            <div className="space-y-2.5 text-xs bg-slate-950/40 p-4 rounded-xl border border-slate-800/80">
              <div className="flex justify-between">
                <span className="text-slate-400">Ore Tonnage:</span>
                <span className="text-white font-mono font-bold">{selectedBlock.tonnage_tonnes.toLocaleString()} t</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Contained Mn Metal:</span>
                <span className="text-purple-300 font-mono font-bold">{selectedBlock.contained_mn_tonnes.toLocaleString()} t</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Dist to Nearest Drillhole:</span>
                <span className="text-cyan-400 font-mono font-bold">{selectedBlock.distance_to_nearest_drillhole_m} m</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Kriging Estimation Variance:</span>
                <span className="text-amber-400 font-mono font-bold">{selectedBlock.kriging_variance}</span>
              </div>
              <div className="flex justify-between pt-1 border-t border-slate-800">
                <span className="text-slate-400">JORC / UNFC Class:</span>
                <span className="font-bold text-white bg-slate-800 px-2 py-0.5 rounded">
                  {selectedBlock.jorc_category} (UNFC {selectedBlock.unfc_code})
                </span>
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-purple-500/10 border border-purple-500/20 text-xs text-purple-200">
              <span className="font-bold block mb-1">Geostatistical Certainty:</span>
              Ordinary Kriging estimation error &sigma;²_k is proportional to distance from drillhole collars.
            </div>
          </div>
        ) : null}
      </div>

      {/* Variogram & Grade-Tonnage Curves */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 1: Semi-Variogram */}
        <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800 space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-base font-bold text-white">Spatial Continuity (Semi-Variogram &gamma;(h))</h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Nugget c₀={variogram?.nugget_c0} • Sill c={variogram?.sill_c} • Range a={variogram?.range_a_meters}m
              </p>
            </div>
            <Activity className="w-5 h-5 text-purple-400" />
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={variogramChartData} margin={{ top: 10, right: 10, left: -20, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="lag" stroke="#64748b" fontSize={11} unit="m" />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', fontSize: '12px' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                <Line
                  type="monotone"
                  dataKey="fitted_semivariance"
                  name="Fitted Spherical Variogram Model"
                  stroke="#a855f7"
                  strokeWidth={2.5}
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="empirical_semivariance"
                  name="Empirical Assay Pairs &gamma;(h)"
                  stroke="#f59e0b"
                  strokeWidth={0}
                  dot={{ r: 4, fill: '#f59e0b' }}
                  connectNulls={true}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: Grade-Tonnage Curve */}
        <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800 space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-base font-bold text-white">Grade-Tonnage Sensitivity Curve</h3>
              <p className="text-xs text-slate-400 mt-0.5">Ore Tonnage (MT) and Average Grade vs Cutoff Grade %</p>
            </div>
            <BarChart2 className="w-5 h-5 text-amber-400" />
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={blockModel?.grade_tonnage_curve || []} margin={{ top: 10, right: 10, left: -20, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="cutoff_grade_pct" stroke="#64748b" fontSize={11} unit="%" />
                <YAxis yAxisId="tonnage" stroke="#64748b" fontSize={11} tickFormatter={(v) => `${(v/1000000).toFixed(0)}M`} />
                <YAxis yAxisId="grade" orientation="right" stroke="#a855f7" fontSize={11} unit="%" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', fontSize: '12px' }}
                  formatter={(val: any, name: any) => [
                    name.includes('Tonnage') ? `${(val / 1000000).toFixed(2)} MT` : `${val}%`,
                    name
                  ]}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                <Bar yAxisId="tonnage" dataKey="ore_tonnage_tonnes" name="Ore Tonnage (t)" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                <Line yAxisId="grade" type="monotone" dataKey="avg_mn_grade_pct" name="Average Grade (% Mn)" stroke="#a855f7" strokeWidth={2.5} dot={{ r: 3 }} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* JORC / UNFC Resource Classification Table */}
      <div className="rounded-2xl bg-slate-900/40 border border-slate-800 overflow-hidden">
        <div className="p-4 border-b border-slate-800 bg-slate-900/60 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Table className="w-4 h-4 text-purple-400" />
            <h3 className="text-sm font-semibold text-white">JORC (2012) &amp; UNFC Resource Statement</h3>
          </div>
          <span className="text-xs text-slate-400 font-mono">Dongri Buzurg Manganese Deposit</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/60 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4">UNFC Code</th>
                <th className="py-3 px-4">Drill Spacing Criteria</th>
                <th className="py-3 px-4 text-right">Blocks</th>
                <th className="py-3 px-4 text-right">Tonnage (MT)</th>
                <th className="py-3 px-4 text-right">Avg Mn %</th>
                <th className="py-3 px-4 text-right">Contained Mn (MT)</th>
                <th className="py-3 px-4 text-right">Share</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-medium">
              {blockModel && Object.entries(blockModel.jorc_resource_categories).map(([cat, info]) => {
                const unfsCode = cat === 'Measured' ? '111' : cat === 'Indicated' ? '122' : cat === 'Inferred' ? '133' : '334';
                const spacing = cat === 'Measured' ? '≤ 100m' : cat === 'Indicated' ? '100m - 250m' : cat === 'Inferred' ? '250m - 550m' : '> 550m';

                return (
                  <tr key={cat} className="hover:bg-slate-800/30 transition">
                    <td className="py-3 px-4 font-bold text-white flex items-center gap-2">
                      <span className={`w-2 h-2 rounded-full ${cat === 'Measured' ? 'bg-emerald-400' : cat === 'Indicated' ? 'bg-blue-400' : cat === 'Inferred' ? 'bg-amber-400' : 'bg-slate-500'}`} />
                      {cat}
                    </td>
                    <td className="py-3 px-4 font-mono text-cyan-400">{unfsCode}</td>
                    <td className="py-3 px-4 text-slate-400 font-mono">{spacing}</td>
                    <td className="py-3 px-4 text-right font-mono text-slate-300">{info.block_count}</td>
                    <td className="py-3 px-4 text-right font-mono font-bold text-white">{(info.tonnage_tonnes / 1000000).toFixed(2)}</td>
                    <td className="py-3 px-4 text-right font-mono font-bold text-purple-400">{info.avg_mn_grade_pct}%</td>
                    <td className="py-3 px-4 text-right font-mono font-bold text-emerald-400">{(info.contained_mn_tonnes / 1000000).toFixed(2)}</td>
                    <td className="py-3 px-4 text-right font-mono text-slate-400">{info.pct_of_total}%</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
