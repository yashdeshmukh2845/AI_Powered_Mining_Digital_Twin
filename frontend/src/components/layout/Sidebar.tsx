import React from 'react';
import {
  LayoutDashboard, MapPin, Layers, TrendingUp, AlertTriangle,
  Zap, Cpu, Database, BarChart3, FileText, Pickaxe
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const navItems = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard },
  { id: 'map', label: 'Mine Map', icon: MapPin },
  { id: 'reserves', label: 'Reserve Intelligence', icon: Layers },
  { id: 'forecast', label: 'Production Forecast', icon: TrendingUp },
  { id: 'risk', label: 'Risk Center', icon: AlertTriangle },
  { id: 'actions', label: 'AI Action Center', icon: Zap },
  { id: 'simulator', label: 'Digital Twin Simulator', icon: Cpu },
  { id: 'data', label: 'Data Management', icon: Database },
  { id: 'models', label: 'Model Performance', icon: BarChart3 },
  { id: 'reports', label: 'Reports & Settings', icon: FileText },
];

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
  return (
    <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col border-r border-slate-800 shrink-0 h-screen sticky top-0">
      {/* Brand Header */}
      <div className="p-4 flex items-center gap-3 border-b border-slate-800 bg-slate-950">
        <div className="p-2 bg-gradient-to-br from-amber-500 to-orange-600 rounded-lg text-slate-950 font-bold shadow-md">
          <Pickaxe className="w-6 h-6" />
        </div>
        <div>
          <h1 className="font-bold text-white text-base tracking-tight leading-tight">MOIL Intelligence</h1>
          <p className="text-xs text-amber-500 font-medium tracking-wide">Manganese Digital Twin</p>
        </div>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        <div className="px-3 py-2 text-[10px] font-semibold text-slate-500 uppercase tracking-wider">
          Analytical Workspaces
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-amber-500 text-slate-950 shadow-md font-semibold'
                  : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-slate-950' : 'text-slate-400'}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Footer Info */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-950/60 text-xs text-slate-500 flex flex-col gap-1">
        <div className="flex justify-between items-center text-slate-400">
          <span>Version</span>
          <span className="font-mono text-slate-300">v1.0.0</span>
        </div>
        <div className="flex justify-between items-center text-slate-400">
          <span>ML Core</span>
          <span className="text-emerald-400 font-medium">Scikit / XGB</span>
        </div>
      </div>
    </aside>
  );
};
