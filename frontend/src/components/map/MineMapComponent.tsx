import React, { useState } from 'react';
import { MapContainer, TileLayer, GeoJSON, CircleMarker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import type { Borehole } from '../../types';
import { Layers, Info } from 'lucide-react';

interface MineMapComponentProps {
  boreholes: Borehole[];
  geologyData: any;
  prospectivityMap: any;
}

export const MineMapComponent: React.FC<MineMapComponentProps> = ({
  boreholes,
  geologyData,
  prospectivityMap
}) => {
  const [selectedItem, setSelectedItem] = useState<any>(null);
  const [showProspectivity, setShowProspectivity] = useState(true);
  const [showBoreholes, setShowBoreholes] = useState(true);
  const [showBoundary, setShowBoundary] = useState(true);

  // Dongri Buzurg Mine default center coordinates
  const centerLat = 21.5342;
  const centerLon = 79.6915;

  const getProspectivityColor = (category: string) => {
    switch (category) {
      case 'High': return '#8B5CF6'; // Vibrant Manganese Purple
      case 'Medium': return '#F59E0B'; // Muted Amber/Copper
      case 'Low': return '#64748B'; // Slate Grey
      default: return '#94A3B8';
    }
  };

  const prospectivityStyle = (feature: any) => {
    const category = feature.properties.prospectivity_category;
    return {
      fillColor: getProspectivityColor(category),
      weight: 1,
      opacity: 0.6,
      color: '#ffffff',
      fillOpacity: 0.45
    };
  };

  const boundaryStyle = {
    color: '#EF4444',
    weight: 3,
    dashArray: '6, 6',
    fillColor: '#EF4444',
    fillOpacity: 0.05
  };

  return (
    <div className="relative w-full h-[650px] bg-slate-900 rounded-xl overflow-hidden border border-slate-800 shadow-xl flex">
      {/* Map Controls Panel */}
      <div className="absolute top-4 right-4 z-[400] bg-slate-900/95 backdrop-blur-md p-3.5 rounded-lg border border-slate-700/80 shadow-2xl text-xs space-y-2 text-slate-200">
        <div className="font-semibold text-slate-300 flex items-center gap-1.5 border-b border-slate-800 pb-1.5">
          <Layers className="w-3.5 h-3.5 text-amber-500" />
          <span>Map Layers & Toggles</span>
        </div>
        <label className="flex items-center gap-2 cursor-pointer hover:text-white">
          <input
            type="checkbox"
            checked={showProspectivity}
            onChange={(e) => setShowProspectivity(e.target.checked)}
            className="rounded text-amber-500 focus:ring-amber-500 bg-slate-800 border-slate-700"
          />
          <span>Prospectivity Zones</span>
        </label>
        <label className="flex items-center gap-2 cursor-pointer hover:text-white">
          <input
            type="checkbox"
            checked={showBoreholes}
            onChange={(e) => setShowBoreholes(e.target.checked)}
            className="rounded text-amber-500 focus:ring-amber-500 bg-slate-800 border-slate-700"
          />
          <span>Borehole Drilling Logs</span>
        </label>
        <label className="flex items-center gap-2 cursor-pointer hover:text-white">
          <input
            type="checkbox"
            checked={showBoundary}
            onChange={(e) => setShowBoundary(e.target.checked)}
            className="rounded text-amber-500 focus:ring-amber-500 bg-slate-800 border-slate-700"
          />
          <span>Mine Lease Perimeter</span>
        </label>
      </div>

      {/* Main Map */}
      <div className="flex-1 h-full relative">
        <MapContainer
          center={[centerLat, centerLon]}
          zoom={13}
          scrollWheelZoom={true}
          style={{ width: '100%', height: '100%' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {/* Mine Boundary Layer */}
          {showBoundary && geologyData?.boundary_geojson && (
            <GeoJSON data={geologyData.boundary_geojson} style={boundaryStyle} />
          )}

          {/* Prospectivity Grid GeoJSON */}
          {showProspectivity && prospectivityMap && prospectivityMap.features && (
            <GeoJSON
              data={prospectivityMap}
              style={prospectivityStyle}
              onEachFeature={(feature, layer) => {
                layer.on({
                  click: () => {
                    setSelectedItem({
                      type: 'Prospectivity Block',
                      data: feature.properties
                    });
                  }
                });
              }}
            />
          )}

          {/* Borehole Markers */}
          {showBoreholes && boreholes.map((bh) => (
            <CircleMarker
              key={bh.id}
              center={[bh.latitude, bh.longitude]}
              radius={6}
              pathOptions={{
                fillColor: '#3B82F6',
                fillOpacity: 0.9,
                color: '#ffffff',
                weight: 2
              }}
              eventHandlers={{
                click: () => setSelectedItem({ type: 'Borehole', data: bh })
              }}
            >
              <Popup>
                <div className="text-xs space-y-1">
                  <p className="font-bold text-amber-400 border-b border-slate-700 pb-1">{bh.borehole_id}</p>
                  <p><span className="text-slate-400">Total Depth:</span> {bh.total_depth}m</p>
                  <p><span className="text-slate-400">Elevation:</span> {bh.elevation}m</p>
                  {bh.intervals && bh.intervals.length > 0 && (
                    <div className="mt-1 pt-1 border-t border-slate-700">
                      <p className="font-semibold text-slate-300">Top Assay Grade:</p>
                      <p className="text-emerald-400 font-mono font-bold">
                        {Math.max(...bh.intervals.map(i => i.mn_grade))}% Mn
                      </p>
                    </div>
                  )}
                </div>
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>

      {/* Side Inspector Panel */}
      {selectedItem && (
        <div className="w-80 bg-slate-900 border-l border-slate-800 p-5 overflow-y-auto z-20 text-slate-200">
          <div className="flex justify-between items-center border-b border-slate-800 pb-3 mb-4">
            <h3 className="font-bold text-sm text-white flex items-center gap-2">
              <Info className="w-4 h-4 text-amber-500" />
              {selectedItem.type} Inspector
            </h3>
            <button
              onClick={() => setSelectedItem(null)}
              className="text-slate-400 hover:text-white text-xs px-2 py-1 rounded bg-slate-800"
            >
              Close
            </button>
          </div>

          {selectedItem.type === 'Borehole' && (
            <div className="space-y-3 text-xs">
              <div className="bg-slate-800/80 p-3 rounded-lg border border-slate-700/60">
                <p className="text-slate-400">Borehole ID</p>
                <p className="text-sm font-bold text-amber-400 font-mono">{selectedItem.data.borehole_id}</p>
                <div className="mt-2 grid grid-cols-2 gap-2 text-[11px]">
                  <div><span className="text-slate-500">Lat:</span> {selectedItem.data.latitude}</div>
                  <div><span className="text-slate-500">Lon:</span> {selectedItem.data.longitude}</div>
                  <div><span className="text-slate-500">Collar Elev:</span> {selectedItem.data.elevation}m</div>
                  <div><span className="text-slate-500">Depth:</span> {selectedItem.data.total_depth}m</div>
                </div>
              </div>

              <h4 className="font-semibold text-slate-300 pt-1">Borehole Lithology & Assay Intervals</h4>
              {selectedItem.data.intervals && selectedItem.data.intervals.length > 0 ? (
                <div className="space-y-1.5 max-h-60 overflow-y-auto pr-1">
                  {selectedItem.data.intervals.map((int: any, idx: number) => (
                    <div key={idx} className="p-2 bg-slate-800/50 rounded border border-slate-700/40 flex justify-between items-center">
                      <div>
                        <p className="font-medium text-slate-200">{int.lithology}</p>
                        <p className="text-[10px] text-slate-400">{int.from_depth}m - {int.to_depth}m</p>
                      </div>
                      <span className={`font-mono font-bold px-2 py-0.5 rounded text-[11px] ${
                        int.mn_grade > 25 ? 'bg-purple-950 text-purple-300 border border-purple-800' : 'bg-slate-700 text-slate-300'
                      }`}>
                        {int.mn_grade}% Mn
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-slate-500 italic">No detailed interval assay records.</p>
              )}
            </div>
          )}

          {selectedItem.type === 'Prospectivity Block' && (
            <div className="space-y-3 text-xs">
              <div className="bg-slate-800/80 p-3 rounded-lg border border-slate-700/60">
                <p className="text-slate-400">Block Identifier</p>
                <p className="text-sm font-bold text-white font-mono">{selectedItem.data.block_id}</p>
                <div className="mt-2 flex items-center justify-between">
                  <span className="text-slate-400">Prospectivity Score:</span>
                  <span className="text-base font-bold text-amber-400 font-mono">
                    {selectedItem.data.prospectivity_score}
                  </span>
                </div>
                <div className="mt-1 flex items-center justify-between">
                  <span className="text-slate-400">Prospectivity Category:</span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    selectedItem.data.prospectivity_category === 'High' ? 'bg-purple-900/80 text-purple-200 border border-purple-700' :
                    selectedItem.data.prospectivity_category === 'Medium' ? 'bg-amber-900/80 text-amber-200 border border-amber-700' :
                    'bg-slate-800 text-slate-400'
                  }`}>
                    {selectedItem.data.prospectivity_category}
                  </span>
                </div>
              </div>

              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 space-y-2">
                <h4 className="font-semibold text-slate-300">Contributing Geospatial Features</h4>
                <div className="flex justify-between text-slate-400">
                  <span>Dist to Fault Belt:</span>
                  <span className="text-slate-200 font-mono">{selectedItem.data.dist_to_fault_km} km</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Vegetation (NDVI):</span>
                  <span className="text-slate-200 font-mono">{selectedItem.data.ndvi}</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Surface Temp (LST):</span>
                  <span className="text-slate-200 font-mono">{selectedItem.data.lst_c} °C</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>SAR Coherence:</span>
                  <span className="text-slate-200 font-mono">{selectedItem.data.sar_coherence}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
