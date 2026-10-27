import React, { useState, useEffect } from 'react';
import {
  RefreshCw, Database, CheckCircle2, User, Clock, HardHat,
  Bell, AlertTriangle, ShieldAlert, X, ChevronDown, Globe2
} from 'lucide-react';
import type { Mine } from '../../types';
import { api } from '../../services/api';

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
  const [alerts, setAlerts] = useState<any[]>([]);
  const [showAlerts, setShowAlerts] = useState<boolean>(false);
  const [language, setLanguage] = useState<string>('en');

  const loadAlerts = async () => {
    try {
      const res = await api.getAlerts(selectedMine?.id || 'MINE-001');
      setAlerts(res);
    } catch (err) {
      console.error('Failed to load operational alerts:', err);
    }
  };

  useEffect(() => {
    loadAlerts();
    const interval = setInterval(loadAlerts, 30000);
    return () => clearInterval(interval);
  }, [selectedMine]);

  const criticalCount = alerts.filter(a => a.severity === 'critical').length;

  return (
    <header className="h-16 bg-slate-900 border-b border-slate-800 px-6 flex items-center justify-between text-slate-200 sticky top-0 z-30 shadow-sm">
      {/* Mine Selector & Period */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 bg-slate-800/80 px-3 py-1.5 rounded-xl border border-slate-700/60 shadow-sm">
          <HardHat className="w-4 h-4 text-amber-500" />
          <span className="text-xs text-slate-400 font-medium">Mine:</span>
          <select
            value={selectedMine?.id || 'MINE-001'}
            onChange={(e) => onMineChange(e.target.value)}
            className="bg-transparent text-sm font-semibold text-white focus:outline-none cursor-pointer"
          >
            <option value="MINE-001" className="bg-slate-900 text-white">Dongri Buzurg Manganese Mine (Bhandara, MH)</option>
            <option value="MINE-002" className="bg-slate-900 text-white">Mansar Manganese Mine (Nagpur, MH)</option>
            <option value="MINE-003" className="bg-slate-900 text-white">Balaghat Manganese Mine (Balaghat, MP)</option>
          </select>
        </div>

        <div className="hidden xl:flex items-center gap-2 text-xs text-slate-400 bg-slate-800/40 px-3 py-1.5 rounded-lg">
          <span>Reporting Period:</span>
          <span className="font-semibold text-slate-200">FY 2025 – 2026 Active Shift</span>
        </div>
      </div>

      {/* System Status Indicators & Action Controls */}
      <div className="flex items-center gap-3 text-xs">
        {/* Language Switcher */}
        <div className="hidden sm:flex items-center gap-1.5 bg-slate-800/60 px-2.5 py-1.5 rounded-lg border border-slate-700/60 text-slate-300">
          <Globe2 className="w-3.5 h-3.5 text-slate-400" />
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="bg-transparent text-xs font-medium text-slate-200 focus:outline-none cursor-pointer"
          >
            <option value="en" className="bg-slate-900">EN (English)</option>
            <option value="hi" className="bg-slate-900">HI (हिन्दी)</option>
            <option value="mr" className="bg-slate-900">MR (मराठी)</option>
          </select>
        </div>

        {/* Live Operational Alerts Bell */}
        <div className="relative">
          <button
            onClick={() => setShowAlerts(!showAlerts)}
            className={`relative p-2 rounded-xl transition ${
              criticalCount > 0
                ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                : 'hover:bg-slate-800 text-slate-300'
            }`}
            title="Operational Alerts"
          >
            <Bell className="w-4 h-4" />
            {alerts.length > 0 && (
              <span className={`absolute -top-1 -right-1 w-4 h-4 rounded-full text-[10px] font-bold flex items-center justify-center text-white ${
                criticalCount > 0 ? 'bg-rose-500' : 'bg-amber-500'
              }`}>
                {alerts.length}
              </span>
            )}
          </button>

          {/* Alerts Dropdown Modal */}
          {showAlerts && (
            <div className="absolute right-0 mt-2 w-80 sm:w-96 bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-4 space-y-3 z-50">
              <div className="flex justify-between items-center border-b border-slate-800 pb-2">
                <div className="flex items-center gap-2">
                  <ShieldAlert className="w-4 h-4 text-amber-400" />
                  <span className="font-bold text-white text-xs uppercase tracking-wider">Active Operations Alerts ({alerts.length})</span>
                </div>
                <button onClick={() => setShowAlerts(false)} className="text-slate-400 hover:text-white">
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="space-y-2 max-h-72 overflow-y-auto">
                {alerts.length === 0 ? (
                  <p className="text-xs text-slate-400 text-center py-4">No active operational alerts.</p>
                ) : (
                  alerts.map((alt) => (
                    <div
                      key={alt.id}
                      className={`p-3 rounded-xl border text-xs space-y-1 ${
                        alt.severity === 'critical'
                          ? 'bg-rose-950/20 border-rose-800/40 text-rose-200'
                          : 'bg-amber-950/20 border-amber-800/40 text-amber-200'
                      }`}
                    >
                      <div className="flex justify-between items-center">
                        <span className="font-bold flex items-center gap-1.5">
                          <AlertTriangle className={`w-3.5 h-3.5 ${alt.severity === 'critical' ? 'text-rose-400' : 'text-amber-400'}`} />
                          {alt.title}
                        </span>
                        <span className="text-[10px] text-slate-400">{alt.timestamp}</span>
                      </div>
                      <p className="text-[11px] text-slate-300 leading-relaxed">{alt.message}</p>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* Updated Timestamp */}
        <div className="hidden sm:flex items-center gap-1.5 text-slate-400 bg-slate-800/40 px-2.5 py-1.5 rounded-lg">
          <Clock className="w-3.5 h-3.5 text-slate-500" />
          <span className="font-mono text-slate-300">{lastUpdated || 'Active'}</span>
        </div>

        {/* Refresh Button */}
        <button
          onClick={onRefresh}
          disabled={isLoading}
          className="p-2 hover:bg-slate-800 rounded-lg text-slate-400 hover:text-white transition"
          title="Refresh Dashboard Data"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin text-amber-500' : ''}`} />
        </button>

        <div className="h-6 w-px bg-slate-800" />

        {/* User Profile */}
        <div className="flex items-center gap-2 text-slate-300">
          <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-amber-500 font-bold">
            <User className="w-4 h-4" />
          </div>
          <div className="hidden lg:block text-left">
            <p className="text-xs font-semibold text-slate-200 leading-none">Senior Mine Engineer</p>
            <p className="text-[10px] text-slate-400 leading-none mt-1">MOIL Analytics Division</p>
          </div>
        </div>
      </div>
    </header>
  );
};
