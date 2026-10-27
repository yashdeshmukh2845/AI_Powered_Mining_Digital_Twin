import React, { useState, useEffect } from 'react';
import { Globe, AlertTriangle, CheckCircle2, RefreshCw, Droplets, Mountain, ShieldCheck, Info } from 'lucide-react';
import { api } from '../services/api';

export const SatelliteIntelligence: React.FC = () => {
  const [surfaceData, setSurfaceData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    loadSurfaceData();
  }, []);

  const loadSurfaceData = async () => {
    setIsLoading(true);
    try {
      // Fetch surface change monitoring data
      const res = await fetch('/api/satellite/surface-change?mine_id=MINE-001');
      if (res.ok) {
        const data = await res.json();
        setSurfaceData(data);
      }
    } catch (err) {
      console.error('Error loading surface monitoring data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Non-Negotiable Design Rule: Subsurface Trap Banner */}
      <div className="bg-amber-950/90 border border-amber-800 rounded-xl p-4 text-amber-200 shadow-md">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <h4 className="font-bold text-amber-300 text-sm">
              Scientific Non-Negotiable Rule: Surface Operational Context Only
            </h4>
            <p className="text-xs text-amber-200/90 leading-relaxed">
              Satellite and remote-sensing data (rainfall, soil moisture, Sentinel-2 NDVI, LST, Sentinel-1 SAR coherence) provide <strong>surface environmental context</strong>:
              monitoring pit sump water-logging, haul-road mud friction, and waste dump growth.
              <strong> Satellite sensors CANNOT and DO NOT detect subterranean manganese ore bodies.</strong> Subsurface reserve estimation is derived solely from borehole drilling, assays, and geostatistics.
            </p>
          </div>
        </div>
      </div>

      {/* Header & Status */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center gap-2">
            <Globe className="w-5 h-5 text-amber-600" />
            <h2 className="text-lg font-bold text-slate-900">Surface Environmental & Change Monitor</h2>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Dongri Buzurg Mine Perimeter (21.5342°N, 79.6915°E) • Sentinel-2 L2A Optical & Sentinel-1 InSAR Coherence
          </p>
        </div>

        <button
          onClick={loadSurfaceData}
          disabled={isLoading}
          className="flex items-center gap-2 px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg transition-colors border border-slate-300"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-amber-600' : ''}`} />
          <span>Refresh Satellite Feeds</span>
        </button>
      </div>

      {/* Primary KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-start gap-3">
          <div className="p-2.5 bg-blue-50 text-blue-600 rounded-lg shrink-0">
            <Droplets className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs text-slate-500 font-medium">Pit Sump Water Risk</p>
            <p className="text-lg font-bold text-slate-900 mt-0.5">Moderate</p>
            <p className="text-[11px] text-blue-600 mt-1">High-head pump #2 on standby</p>
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-start gap-3">
          <div className="p-2.5 bg-amber-50 text-amber-600 rounded-lg shrink-0">
            <Mountain className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs text-slate-500 font-medium">Haul Road Mud Index</p>
            <p className="text-lg font-bold text-slate-900 mt-0.5">85 / 100</p>
            <p className="text-[11px] text-amber-600 mt-1">Traction optimal; speed 25 km/h</p>
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-start gap-3">
          <div className="p-2.5 bg-purple-50 text-purple-600 rounded-lg shrink-0">
            <Globe className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs text-slate-500 font-medium">Waste Dump Area</p>
            <p className="text-lg font-bold text-slate-900 mt-0.5">44.8 ha</p>
            <p className="text-[11px] text-purple-600 mt-1">+3.2% seasonal terrace extension</p>
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-start gap-3">
          <div className="p-2.5 bg-emerald-50 text-emerald-600 rounded-lg shrink-0">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs text-slate-500 font-medium">Buffer Zone Compliance</p>
            <p className="text-lg font-bold text-slate-900 mt-0.5">0.52 NDVI</p>
            <p className="text-[11px] text-emerald-600 mt-1">Full environmental perimeter compliance</p>
          </div>
        </div>
      </div>

      {/* Multi-Temporal Surface Trends Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-200 bg-slate-50/70 flex justify-between items-center">
          <div>
            <h3 className="font-bold text-sm text-slate-900">Multi-Temporal Seasonal Surface Monitoring</h3>
            <p className="text-xs text-slate-500">Tracking pit dewatering, haulage road friction, and green belt buffers over annual cycles</p>
          </div>
          <span className="text-xs bg-slate-200/80 text-slate-700 px-2.5 py-1 rounded font-mono">
            Optical & SAR Indices
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="bg-slate-100 text-slate-600 font-semibold border-b border-slate-200 uppercase tracking-wider text-[10px]">
              <tr>
                <th className="p-3">Period</th>
                <th className="p-3">Pit Water Area (%)</th>
                <th className="p-3">Flooding Risk</th>
                <th className="p-3">Dump Area (Ha)</th>
                <th className="p-3">Green Belt NDVI</th>
                <th className="p-3">Haul Road Traction</th>
                <th className="p-3">Operational Action Required</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {surfaceData?.quarterly_trends?.map((q: any, i: number) => (
                <tr key={i} className="hover:bg-slate-50/80">
                  <td className="p-3 font-semibold text-slate-900">{q.period}</td>
                  <td className="p-3 font-mono">{q.pit_water_index_pct}%</td>
                  <td className="p-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      q.pit_flooding_risk.includes('High') ? 'bg-red-100 text-red-700 border border-red-200' :
                      q.pit_flooding_risk.includes('Moderate') ? 'bg-amber-100 text-amber-700 border border-amber-200' :
                      'bg-emerald-100 text-emerald-700 border border-emerald-200'
                    }`}>
                      {q.pit_flooding_risk}
                    </span>
                  </td>
                  <td className="p-3 font-mono">{q.waste_dump_area_hectares} ha</td>
                  <td className="p-3 font-mono">{q.green_belt_ndvi_avg}</td>
                  <td className="p-3 font-mono font-bold text-slate-700">{q.haul_road_traction_score} / 100</td>
                  <td className="p-3 text-slate-600">{q.surface_status}</td>
                </tr>
              )) || (
                <tr>
                  <td colSpan={7} className="p-4 text-center text-slate-400 italic">
                    Loading surface monitoring observations...
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Surface Environmental Zones Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {surfaceData?.active_surface_zones?.map((zone: any, idx: number) => (
          <div key={idx} className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-2">
            <div className="flex justify-between items-start">
              <h4 className="font-bold text-sm text-slate-900">{zone.zone_name}</h4>
              <span className="text-[10px] bg-slate-100 text-slate-700 px-2 py-0.5 rounded border border-slate-200 font-mono">
                {zone.indicator}
              </span>
            </div>
            <div className="text-xs space-y-1 text-slate-600 pt-1">
              <p><span className="text-slate-400">Current Observation:</span> <strong>{zone.current_val}</strong></p>
              <p><span className="text-slate-400">Alert Status:</span> <span className="text-amber-600 font-medium">{zone.alert_level}</span></p>
              <p><span className="text-slate-400">Mine Operational Impact:</span> {zone.operational_implication}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
