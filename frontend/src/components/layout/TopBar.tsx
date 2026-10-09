import React from 'react';
import { RefreshCw, Database, CheckCircle2, User, Clock, HardHat } from 'lucide-react';
import type { Mine } from '../../types';

interface TopBarProps {
  selectedMine: Mine | null;
  onMineChange: (mineId: string) => void;
  lastUpdated: string;
  onRefresh: () => void;
  isLoading: boolean;
}

export const TopBar: React.FC<TopBarProps> = ({
  selectedMine,
  onMineChange,
  lastUpdated,
  onRefresh,
  isLoading
}) => {
  return (
    <header className="h-16 bg-slate-900 border-b border-slate-800 px-6 flex items-center justify-between text-slate-200 sticky top-0 z-30 shadow-sm">
      {/* Mine Selector & Period */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 bg-slate-800/80 px-3 py-1.5 rounded-md border border-slate-700/60">
          <HardHat className="w-4 h-4 text-amber-500" />
          <span className="text-xs text-slate-400 font-medium">Mine:</span>
          <select
            value={selectedMine?.id || 'MINE-001'}
            onChange={(e) => onMineChange(e.target.value)}
            className="bg-transparent text-sm font-semibold text-white focus:outline-none cursor-pointer"
          >
            <option value="MINE-001" className="bg-slate-900">Dongri Buzurg Manganese Mine</option>
            <option value="MINE-002" className="bg-slate-900">Mansar Manganese Mine</option>
            <option value="MINE-003" className="bg-slate-900">Balaghat Manganese Mine</option>
          </select>
        </div>

        <div className="hidden md:flex items-center gap-2 text-xs text-slate-400 bg-slate-800/40 px-3 py-1.5 rounded-md">
          <span>Reporting Period:</span>
          <span className="font-semibold text-slate-200">October 2025 – September 2026</span>
        </div>
      </div>

      {/* System Status Indicators */}
      <div className="flex items-center gap-4 text-xs">
        <div className="hidden lg:flex items-center gap-2 text-slate-400">
          <Database className="w-3.5 h-3.5 text-emerald-400" />
          <span>Dataset:</span>
          <span className="text-emerald-400 font-medium">Connected</span>
        </div>

        <div className="hidden lg:flex items-center gap-2 text-slate-400">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
          <span>Models:</span>
          <span className="text-emerald-400 font-medium">Active (RF/XGB)</span>
        </div>

        <div className="flex items-center gap-1.5 text-slate-400 bg-slate-800/40 px-2.5 py-1 rounded">
          <Clock className="w-3.5 h-3.5 text-slate-500" />
          <span>Updated:</span>
          <span className="font-mono text-slate-300">{lastUpdated || 'Just Now'}</span>
        </div>

        <button
          onClick={onRefresh}
          disabled={isLoading}
          className="p-2 hover:bg-slate-800 rounded-md text-slate-400 hover:text-white transition-colors"
          title="Refresh Dashboard Data"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin text-amber-500' : ''}`} />
        </button>

        <div className="h-6 w-px bg-slate-800" />

        {/* User Profile */}
        <div className="flex items-center gap-2 text-slate-300">
          <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-amber-500">
            <User className="w-4 h-4" />
          </div>
          <div className="hidden sm:block text-left">
            <p className="text-xs font-semibold text-slate-200 leading-none">Senior Mine Engineer</p>
            <p className="text-[10px] text-slate-400 leading-none mt-1">MOIL Analytics Division</p>
          </div>
        </div>
      </div>
    </header>
  );
};
