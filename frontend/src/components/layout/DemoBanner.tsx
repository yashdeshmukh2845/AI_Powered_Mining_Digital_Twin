import React from 'react';
import { Database, AlertTriangle, CheckCircle2 } from 'lucide-react';

interface DemoBannerProps {
  isDemoMode?: boolean;
  onToggleDemoMode?: (val: boolean) => void;
  provenanceSummary?: string;
}

export const DemoBanner: React.FC<DemoBannerProps> = ({
  isDemoMode = false,
  onToggleDemoMode,
  provenanceSummary
}) => {
  return (
    <div className={`border-b px-4 py-2 text-xs flex items-center justify-between shadow-sm transition-colors ${
      isDemoMode 
        ? 'bg-amber-950/90 border-amber-800 text-amber-200' 
        : 'bg-slate-900 border-slate-800 text-slate-200'
    }`}>
      <div className="flex items-center gap-2 max-w-6xl mx-auto text-left font-medium w-full justify-between">
        <div className="flex items-center gap-2">
          {isDemoMode ? (
            <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
          ) : (
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          )}
          <span>
            {isDemoMode ? (
              <>
                <strong className="text-amber-400">DEMO MODE:</strong> Demo data - replace via the Data Ingestion pipeline with MOIL data.
              </>
            ) : (
              <>
                <strong className="text-emerald-400 font-bold">DATA-DRIVEN MODE:</strong>{' '}
                {provenanceSummary || 'Active integration: 5,000 shift records + 2,192 weather days (Open-Meteo) + Orebit drillholes + Sentinel-2 surface monitoring.'}
              </>
            )}

          </span>
        </div>

        {onToggleDemoMode && (
          <button
            onClick={() => onToggleDemoMode(!isDemoMode)}
            className={`px-3 py-1 rounded text-[11px] font-bold border transition-all flex items-center gap-1.5 ${
              isDemoMode
                ? 'bg-emerald-600 hover:bg-emerald-500 text-white border-emerald-500'
                : 'bg-slate-800 hover:bg-slate-700 text-amber-300 border-slate-700'
            }`}
          >
            <Database className="w-3.5 h-3.5" />
            {isDemoMode ? 'Switch to Data-Driven Mode' : 'Switch to Demo Mode'}
          </button>
        )}
      </div>
    </div>
  );
};
