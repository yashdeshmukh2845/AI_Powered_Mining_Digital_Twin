import React, { useState } from 'react';
import { TrendingUp, BarChart, CheckCircle2 } from 'lucide-react';
import { ResponsiveContainer, ComposedChart, Line, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from 'recharts';
import type { ForecastItem } from '../types';

interface ForecastProps {
  forecastItems: ForecastItem[];
  modelMetrics: any;
  onRefreshForecast: (days: number) => void;
}

export const ProductionForecast: React.FC<ForecastProps> = ({
  forecastItems,
  modelMetrics,
  onRefreshForecast
}) => {
  const [horizonDays, setHorizonDays] = useState<number>(14);

  const handleHorizonChange = (days: number) => {
    setHorizonDays(days);
    onRefreshForecast(days);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-amber-500" />
            AI Production Forecasting Engine
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Time-aware machine learning regression forecasting next-day, next-week, and monthly manganese output.
          </p>
        </div>

        {/* Horizon Selector */}
        <div className="flex items-center gap-2 bg-slate-950 p-2 rounded-lg border border-slate-800 text-xs">
          <span className="text-slate-400 font-semibold px-2">Forecast Horizon:</span>
          {[7, 14, 30].map((d) => (
            <button
              key={d}
              onClick={() => handleHorizonChange(d)}
              className={`px-3 py-1.5 rounded-md font-bold transition-all ${
                horizonDays === d ? 'bg-amber-500 text-slate-950 shadow-sm' : 'text-slate-400 hover:text-white bg-slate-900'
              }`}
            >
              {d} Days
            </button>
          ))}
        </div>
      </div>

      {/* Model Performance Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-blue-50 text-blue-600 rounded-lg">
            <BarChart className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs text-slate-500 font-semibold uppercase">Mean Absolute Error (MAE)</p>
            <p className="text-xl font-black text-slate-900 mt-0.5">{modelMetrics?.production?.mae || 77.2} <span className="text-xs text-slate-500 font-normal">tonnes</span></p>
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-purple-50 text-purple-600 rounded-lg">
            <BarChart className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs text-slate-500 font-semibold uppercase">Root Mean Sq Error (RMSE)</p>
            <p className="text-xl font-black text-slate-900 mt-0.5">{modelMetrics?.production?.rmse || 97.9} <span className="text-xs text-slate-500 font-normal">tonnes</span></p>
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-emerald-50 text-emerald-600 rounded-lg">
            <CheckCircle2 className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs text-slate-500 font-semibold uppercase">WAPE Percentage Metric</p>
            <p className="text-xl font-black text-emerald-600 mt-0.5">{modelMetrics?.production?.wape_pct || 4.41}%</p>
          </div>
        </div>
      </div>

      {/* Main Forecast Chart */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-bold text-base text-slate-900">Forecasted Daily Tonnes vs Planned Target</h3>
          <span className="text-xs text-slate-400 font-mono">Showing {forecastItems.length} Days</span>
        </div>

        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={forecastItems}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="date" tick={{ fontSize: 10 }} stroke="#94a3b8" />
              <YAxis tick={{ fontSize: 10 }} stroke="#94a3b8" domain={[1500, 3000]} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc', borderRadius: '0.5rem', fontSize: '12px' }}
              />
              <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
              <Bar dataKey="forecast_tonnes" name="Forecast Production (t)" fill="#F59E0B" barSize={16} radius={[4, 4, 0, 0]} />
              <Bar dataKey="shortfall_tonnes" name="Forecast Shortfall (t)" fill="#EF4444" barSize={16} radius={[4, 4, 0, 0]} />
              <Line type="monotone" dataKey="planned_target_tonnes" name="Target (t)" stroke="#0F172A" strokeWidth={2} dot={false} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
