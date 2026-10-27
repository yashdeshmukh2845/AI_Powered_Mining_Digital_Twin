import React, { useState, useEffect } from 'react';
import {
  AlertTriangle, CheckCircle2, XCircle, ShieldCheck, Sparkles,
  TrendingDown, Wrench, CloudRain, Flame, Activity, ArrowRight
} from 'lucide-react';
import type { ExplanationResponse } from '../types';
import { api } from '../services/api';

export const RiskCenter: React.FC = () => {
  const [lowThresh, setLowThresh] = useState<number>(5.0);
  const [medThresh, setMedThresh] = useState<number>(10.0);
  const [explanations, setExplanations] = useState<ExplanationResponse | null>(null);
  const [managerConfirmation, setManagerConfirmation] = useState<string | null>(null);

  useEffect(() => {
    api.getExplanations('MINE-001').then(res => setExplanations(res)).catch(console.error);
  }, []);

  // Generate natural language SHAP executive summary sentence
  const topNegative = explanations?.feature_contributions
    .filter(f => f.impact === 'Negative')
    .sort((a, b) => b.importance - a.importance) || [];

  const topPositive = explanations?.feature_contributions
    .filter(f => f.impact === 'Positive')
    .sort((a, b) => b.importance - a.importance) || [];

  const naturalLanguageSummary = topNegative.length > 0
    ? `Primary operational drag on today's extraction is ${topNegative[0]?.displayName || 'Unplanned Equipment Downtime'} (contributing ${Math.round(topNegative[0]?.importance * 100)}% of variance), ${
        topNegative[1] ? `compounded by ${topNegative[1]?.displayName} (${Math.round(topNegative[1]?.importance * 100)}% impact)` : ''
      }. ${topPositive[0] ? `Partially offset by steady ${topPositive[0]?.displayName}.` : ''}`
    : 'All telemetry variables are operating within nominal baseline parameters with no critical shortfall drag detected.';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-900/60 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400">
              <AlertTriangle className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight">
                Production Shortfall Risk &amp; Root Cause Analysis
              </h1>
              <p className="text-slate-400 text-sm mt-0.5">
                Explainable TreeExplainer SHAP attributions and human manager causality sign-off.
              </p>
            </div>
          </div>
        </div>

        {/* Risk Threshold Sliders */}
        <div className="flex items-center gap-4 bg-slate-950/60 p-2.5 rounded-xl border border-slate-800 text-xs">
          <div className="flex items-center gap-2">
            <span className="text-slate-400">Low Risk &lt;</span>
            <input
              type="number"
              min="1"
              max="9"
              value={lowThresh}
              onChange={(e) => setLowThresh(Number(e.target.value))}
              className="w-12 bg-slate-900 border border-slate-700 px-2 py-1 rounded text-amber-400 font-mono text-center font-bold"
            />
            <span className="text-slate-400">%</span>
          </div>

          <div className="h-4 w-px bg-slate-800" />

          <div className="flex items-center gap-2">
            <span className="text-slate-400">High Risk &ge;</span>
            <input
              type="number"
              min="10"
              max="25"
              value={medThresh}
              onChange={(e) => setMedThresh(Number(e.target.value))}
              className="w-12 bg-slate-900 border border-slate-700 px-2 py-1 rounded text-rose-400 font-mono text-center font-bold"
            />
            <span className="text-slate-400">%</span>
          </div>
        </div>
      </div>

      {/* Natural Language SHAP Attribution Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-rose-950/30 via-slate-900/40 to-slate-950/40 border border-rose-800/40 space-y-2">
        <div className="flex items-center gap-2 text-rose-400 text-xs font-bold uppercase tracking-wider">
          <Sparkles className="w-4 h-4" />
          Natural Language Root Cause Synthesis (SHAP Attribution)
        </div>
        <p className="text-base text-slate-200 font-medium leading-relaxed">
          "{naturalLanguageSummary}"
        </p>
        <div className="text-[11px] text-slate-400 pt-1 flex items-center gap-1.5 font-mono">
          <Activity className="w-3.5 h-3.5 text-rose-400" />
          Attribution model: Shapley TreeExplainer on Random Forest daily shift regressor
        </div>
      </div>

      {/* SHAP & Feature Attribution Card */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 p-6 rounded-2xl bg-slate-900/40 border border-slate-800 space-y-4">
          <div className="flex justify-between items-center border-b border-slate-800 pb-3">
            <div>
              <h3 className="font-bold text-base text-white">Explainable Feature Attribution (SHAP Analysis)</h3>
              <p className="text-xs text-slate-400 mt-0.5">Factors driving today's variance between actual extraction and the 2,500 t/day target</p>
            </div>
            <span className="text-xs font-semibold px-2.5 py-1 bg-purple-500/10 text-purple-300 border border-purple-500/30 rounded-lg">
              SHAP / Shapley Values
            </span>
          </div>

          <div className="space-y-4">
            {explanations?.feature_contributions.map((fc, idx) => (
              <div key={idx} className="space-y-1.5">
                <div className="flex justify-between text-xs font-medium">
                  <span className="text-slate-200">{fc.displayName}</span>
                  <span className={`font-mono font-bold ${fc.impact === 'Negative' ? 'text-rose-400' : 'text-emerald-400'}`}>
                    {(fc.importance * 100).toFixed(1)}% ({fc.impact === 'Negative' ? 'Drag Penalty' : 'Positive Driver'})
                  </span>
                </div>
                <div className="w-full h-2.5 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
                  <div
                    className={`h-full rounded-full transition-all ${fc.impact === 'Negative' ? 'bg-rose-500' : 'bg-emerald-500'}`}
                    style={{ width: `${Math.max(6, fc.importance * 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Manager Verification Feedback Box */}
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between space-y-4">
          <div>
            <h3 className="font-bold text-base text-white border-b border-slate-800 pb-3 mb-3">
              Operational Causation Sign-off
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              ML feature importance highlights predictive correlations. Shift Supervisor confirmation is required to formally verify pit root causes into the audit log.
            </p>

            <div className="mt-4 p-4 bg-slate-950 rounded-xl border border-slate-800 text-xs space-y-2">
              <span className="text-slate-400 font-semibold block">Audit Review Status:</span>
              <p className="text-amber-400 font-bold font-mono text-sm">
                {managerConfirmation ? managerConfirmation : 'Pending Shift Supervisor Sign-off'}
              </p>
            </div>
          </div>

          <div className="space-y-2 pt-2">
            <button
              onClick={() => setManagerConfirmation('Verified: Equipment Downtime & Road Friction Confirmed')}
              className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs rounded-xl transition flex items-center justify-center gap-2 shadow-sm"
            >
              <CheckCircle2 className="w-4 h-4" />
              Confirm Primary Causation
            </button>
            <button
              onClick={() => setManagerConfirmation('Rejected: Variance Logged as Rail Rake Indent Delay')}
              className="w-full py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-xs rounded-xl transition flex items-center justify-center gap-2"
            >
              <XCircle className="w-4 h-4" />
              Log Alternative Cause
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
