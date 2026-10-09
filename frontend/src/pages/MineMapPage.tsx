import React from 'react';
import { MineMapComponent } from '../components/map/MineMapComponent';
import type { Borehole } from '../types';
import { MapPin } from 'lucide-react';

interface MineMapPageProps {
  boreholes: Borehole[];
  geologyData: any;
  prospectivityMap: any;
}

export const MineMapPage: React.FC<MineMapPageProps> = ({
  boreholes,
  geologyData,
  prospectivityMap
}) => {
  return (
    <div className="space-y-4">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900 p-5 rounded-xl border border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <MapPin className="w-5 h-5 text-amber-500" />
            Geological & Spatial Mine Map Explorer
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Interactive OpenStreetMap viewer displaying Dongri Buzurg lease perimeter, 30+ borehole locations, and ML mineral prospectivity zones.
          </p>
        </div>

        {/* Prospectivity Legend */}
        <div className="flex items-center gap-4 bg-slate-950 p-2.5 rounded-lg border border-slate-800 text-xs">
          <span className="text-slate-400 font-semibold text-[11px]">Prospectivity Legend:</span>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-purple-600 inline-block"></span>
            <span className="text-slate-200">High (&gt;0.7)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-amber-500 inline-block"></span>
            <span className="text-slate-200">Medium (0.4-0.7)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-slate-500 inline-block"></span>
            <span className="text-slate-200">Low (&lt;0.4)</span>
          </div>
        </div>
      </div>

      <MineMapComponent
        boreholes={boreholes}
        geologyData={geologyData}
        prospectivityMap={prospectivityMap}
      />
    </div>
  );
};
