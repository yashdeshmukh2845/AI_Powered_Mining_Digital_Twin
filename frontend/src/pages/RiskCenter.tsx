import React, { useState, useEffect } from 'react';
import { AlertTriangle, CheckCircle2, XCircle } from 'lucide-react';
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-500" />
            Production Shortfall Risk & Root Cause Analysis
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Configurable shortfall risk category thresholds and explainable feature contributions (SHAP & Permutation Importance).
          </p>
        </div>

        {/* Risk Threshold Sliders */}
        <div className="flex items-center gap-4 bg-slate-950 p-3 rounded-lg border border-slate-800 text-xs">
          <div className="flex items-center gap-2">
            <span className="text-slate-400">Low Risk &lt;</span>
            <input
              type="number"
              min="1"
              max="9"
              value={lowThresh}
              onChange={(e) => setLowThresh(Number(e.target.value))}
              className="w-12 bg-slate-900 border border-slate-700 px-2 py-0.5 rounded text-amber-400 font-mono text-center font-bold"
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
              className="w-12 bg-slate-900 border border-slate-700 px-2 py-0.5 rounded text-red-400 font-mono text-center font-bold"
            />
            <span className="text-slate-400">%</span>
          </div>
        </div>
      </div>

      {/* SHAP & Feature Attribution Card */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex justify-between items-center border-b border-slate-100 pb-3">
            <div>
              <h3 className="font-bold text-base text-slate-900">Explainable Feature Attribution (SHAP Analysis)</h3>
              <p className="text-xs text-slate-500">Factors influencing predicted production output and shortfall</p>
            </div>
            <span className="text-xs font-semibold px-2.5 py-1 bg-purple-100 text-purple-800 rounded">
              SHAP / Permutation
            </span>
          </div>

          <div className="space-y-3">
            {explanations?.feature_contributions.map((fc, idx) => (
              <div key={idx} className="space-y-1">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="text-slate-800">{fc.displayName}</span>
                  <span className={`font-mono ${fc.impact === 'Negative' ? 'text-red-600' : 'text-emerald-600'}`}>
                    {(fc.importance * 100).toFixed(1)}% ({fc.impact})
                  </span>
                </div>
                <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${fc.impact === 'Negative' ? 'bg-red-500' : 'bg-emerald-500'}`}
                    style={{ width: `${Math.max(5, fc.importance * 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Manager Verification Feedback Box */}
        <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 shadow-sm text-slate-200 flex flex-col justify-between">
          <div>
            <h3 className="font-bold text-base text-white border-b border-slate-800 pb-3 mb-3">
              Operational Causation Feedback
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              ML feature importance highlights predictive correlations, but human operational confirmation is required to verify actual pit root causes.
            </p>

            <div className="mt-4 p-3 bg-slate-950 rounded-lg border border-slate-800 text-xs space-y-2">
              <span className="text-slate-400 font-semibold">Current Audit Status:</span>
              <p className="text-amber-400 font-bold font-mono">
                {managerConfirmation ? managerConfirmation : 'Pending Operational Manager Review'}
              </p>
            </div>
          </div>

          <div className="mt-6 space-y-2">
            <button
              onClick={() => setManagerConfirmation('Confirmed: Equipment Downtime & Rain Delay Verified')}
              className="w-full py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              <CheckCircle2 className="w-4 h-4" />
              Confirm Primary Root Cause
            </button>
            <button
              onClick={() => setManagerConfirmation('Rejected: Cause Attributed to Off-site Haulage Delay')}
              className="w-full py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-xs rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              <XCircle className="w-4 h-4" />
              Reject & Log Alternative Cause
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
