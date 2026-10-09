import React from 'react';
import { Layers, TrendingUp, AlertTriangle, ShieldCheck, Zap, Pickaxe, Cpu } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from 'recharts';
import type { DashboardSummary, ForecastItem, Recommendation } from '../types';

interface OverviewProps {
  summary: DashboardSummary | null;
  forecastHistory: ForecastItem[];
  recommendations: Recommendation[];
  onNavigate: (tab: string) => void;
}

export const Overview: React.FC<OverviewProps> = ({
  summary,
  forecastHistory,
  recommendations,
  onNavigate
}) => {
  if (!summary) {
    return <div className="p-8 text-center text-slate-500">Loading Overview Dashboard...</div>;
  }

  const getRiskBadge = (category: string) => {
    switch (category) {
      case 'High':
        return <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-red-950/80 text-red-400 border border-red-800/80">HIGH RISK (&ge;10%)</span>;
      case 'Medium':
        return <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-amber-950/80 text-amber-400 border border-amber-800/80">MEDIUM (5-10%)</span>;
      default:
        return <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-950/80 text-emerald-400 border border-emerald-800/80">LOW (&lt;5%)</span>;
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900 p-6 rounded-xl border border-slate-800 shadow-md">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <Pickaxe className="w-5 h-5 text-amber-500" />
            {summary.selected_mine.name} — Operational Overview
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Real-time digital twin monitoring, reserve estimates, equipment availability & AI production shortfall analysis.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => onNavigate('simulator')}
            className="px-4 py-2 bg-gradient-to-r from-amber-500 to-orange-600 text-slate-950 font-bold text-xs rounded-lg hover:from-amber-400 hover:to-orange-500 transition-all shadow-md flex items-center gap-2"
          >
            <Cpu className="w-4 h-4" />
            Launch What-If Simulator
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Estimated Ore Resources */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <div className="flex justify-between items-start">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Ore Resources</span>
            <div className="p-2 bg-purple-50 text-purple-600 rounded-lg">
              <Layers className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <p className="text-2xl font-black text-slate-900 tracking-tight">
              {(summary.est_resources_tonnes / 1000000).toFixed(2)}M <span className="text-xs font-normal text-slate-500">tonnes</span>
            </p>
            <div className="mt-2 flex items-center justify-between text-xs text-slate-600 border-t border-slate-100 pt-2">
              <span>Contained Mn:</span>
              <span className="font-semibold text-purple-700 font-mono">{(summary.est_contained_mn_tonnes / 1000000).toFixed(2)}M t ({summary.avg_mn_grade_pct}% grade)</span>
            </div>
          </div>
        </div>

        {/* Card 2: Latest Production vs Target */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <div className="flex justify-between items-start">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Daily Production Target</span>
            <div className="p-2 bg-blue-50 text-blue-600 rounded-lg">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="flex items-baseline gap-2">
              <p className="text-2xl font-black text-slate-900 tracking-tight">{summary.latest_actual_production} <span className="text-xs font-normal text-slate-500">t/day</span></p>
              <span className="text-xs text-slate-400">vs {summary.latest_target_production} t target</span>
            </div>
            <div className="mt-2 flex items-center justify-between text-xs border-t border-slate-100 pt-2">
              <span className="text-slate-500">Target Attainment:</span>
              <span className={`font-semibold font-mono ${summary.latest_actual_production >= summary.latest_target_production ? 'text-emerald-600' : 'text-amber-600'}`}>
                {((summary.latest_actual_production / summary.latest_target_production) * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        </div>

        {/* Card 3: Forecast Shortfall Risk */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <div className="flex justify-between items-start">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Forecast Shortfall</span>
            <div className="p-2 bg-amber-50 text-amber-600 rounded-lg">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="flex items-baseline gap-2">
              <p className="text-2xl font-black text-amber-700 tracking-tight">{summary.forecast_shortfall_tonnes} <span className="text-xs font-normal text-slate-500">t</span></p>
              <span className="text-xs font-semibold text-amber-600">({summary.forecast_shortfall_pct}%)</span>
            </div>
            <div className="mt-2 flex items-center justify-between border-t border-slate-100 pt-2">
              <span className="text-xs text-slate-500">Risk Category:</span>
              {getRiskBadge(summary.shortfall_risk_category)}
            </div>
          </div>
        </div>

        {/* Card 4: Equipment Availability */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <div className="flex justify-between items-start">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Equipment Availability</span>
            <div className="p-2 bg-emerald-50 text-emerald-600 rounded-lg">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <p className="text-2xl font-black text-slate-900 tracking-tight">{summary.equipment_availability_pct}%</p>
            <div className="mt-2 flex items-center justify-between text-xs border-t border-slate-100 pt-2">
              <span className="text-slate-500">High-Prospect Blocks:</span>
              <span className="font-bold text-purple-700 font-mono">{summary.num_high_prospectivity_blocks} Blocks</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Actual vs Target & Forecast Production Chart */}
        <div className="lg:col-span-2 bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h3 className="font-bold text-base text-slate-900">Historical vs Forecast Production Trends</h3>
              <p className="text-xs text-slate-500">Daily actual production against planned targets and AI forecast</p>
            </div>
            <span className="text-xs font-medium px-2.5 py-1 bg-slate-100 rounded text-slate-600">Last 30 Days</span>
          </div>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={forecastHistory.slice(-30)}>
                <defs>
                  <linearGradient id="colorActual" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.0}/>
                  </linearGradient>
                  <linearGradient id="colorForecast" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#F59E0B" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#F59E0B" stopOpacity={0.0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="date" tick={{ fontSize: 10 }} stroke="#94a3b8" />
                <YAxis tick={{ fontSize: 10 }} stroke="#94a3b8" domain={[1500, 3000]} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc', borderRadius: '0.5rem', fontSize: '12px' }}
                />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                <Area type="monotone" dataKey="actual_production_tonnes" name="Actual Production (t)" stroke="#3B82F6" fillOpacity={1} fill="url(#colorActual)" strokeWidth={2} />
                <Area type="monotone" dataKey="forecast_tonnes" name="AI Forecast (t)" stroke="#F59E0B" fillOpacity={1} fill="url(#colorForecast)" strokeWidth={2} />
                <Area type="monotone" dataKey="planned_target_tonnes" name="Planned Target (t)" stroke="#94A3B8" strokeDasharray="5 5" fill="none" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Priority AI Recommendations Summary Panel */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-bold text-base text-slate-900 flex items-center gap-2">
                <Zap className="w-4 h-4 text-amber-500" />
                Priority AI Recommendations
              </h3>
              <button
                onClick={() => onNavigate('actions')}
                className="text-xs text-amber-600 hover:text-amber-700 font-semibold"
              >
                View All &rarr;
              </button>
            </div>

            <div className="space-y-3">
              {recommendations.slice(0, 3).map((rec) => (
                <div key={rec.id} className="p-3 bg-slate-50 rounded-lg border border-slate-200 hover:border-slate-300 transition-all text-xs space-y-1.5">
                  <div className="flex justify-between items-center">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      rec.priority === 'High' ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-800'
                    }`}>
                      {rec.priority} Priority
                    </span>
                    <span className="text-[10px] text-slate-400 font-mono">{rec.affected_block_or_mine}</span>
                  </div>
                  <h4 className="font-bold text-slate-800 leading-snug">{rec.title}</h4>
                  <p className="text-slate-600 line-clamp-2">{rec.description}</p>
                  <div className="pt-1 flex justify-between items-center text-[11px] font-medium text-emerald-700">
                    <span>Impact: +{rec.est_production_impact_tonnes} tonnes</span>
                    <span className="text-slate-400 text-[10px]">{rec.status}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 text-center">
            <button
              onClick={() => onNavigate('actions')}
              className="w-full py-2 bg-slate-900 text-slate-100 font-semibold text-xs rounded-lg hover:bg-slate-800 transition-colors"
            >
              Review Action Center Protocols
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
