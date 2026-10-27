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
  const [showPriorityGrid, setShowPriorityGrid] = useState(true);
  const [colorMode, setColorMode] = useState<'priority' | 'drill_gap'>('priority');
  const [showBoreholes, setShowBoreholes] = useState(true);
  const [showBoundary, setShowBoundary] = useState(true);

  // Dongri Buzurg Mine default center coordinates
  const centerLat = 21.5342;
  const centerLon = 79.6915;

  const getPriorityColor = (feature: any) => {
    if (colorMode === 'drill_gap') {
      const gap = feature.properties.drill_coverage_gap_m || 200;
      if (gap > 300) return '#DC2626'; // High gap (Red: Urgent info gain)
      if (gap > 150) return '#F59E0B'; // Moderate gap (Amber)
      return '#10B981'; // Well drilled (Emerald)
    }
    const score = feature.properties.exploration_priority_score || feature.properties.prospectivity_score || 0.4;
    if (score >= 0.70) return '#8B5CF6'; // High Priority (Purple)
    if (score >= 0.45) return '#F59E0B'; // Medium Priority (Amber)
    if (score >= 0.25) return '#64748B'; // Low Priority (Slate)
    return '#94A3B8';
  };

  const priorityStyle = (feature: any) => {
    return {
      fillColor: getPriorityColor(feature),
      weight: 1,
      opacity: 0.6,
      color: '#ffffff',
      fillOpacity: colorMode === 'drill_gap' ? 0.55 : 0.45
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
    <div className="relative w-full h-[650px] bg-slate-900 rounded-xl overflow-hidden border border-slate-800 shadow-xl flex flex-col">
      {/* Top Visible Disclaimer Banner (Non-Negotiable Design Rule) */}
      <div className="bg-amber-950/90 border-b border-amber-800/80 px-4 py-2 flex items-center justify-between text-xs text-amber-200 z-[401]">
        <div className="flex items-center gap-2">
          <Info className="w-4 h-4 text-amber-400 shrink-0" />
          <span>
            <strong>Surface Exploration Priority Map:</strong> Guides where to drill next based on structural fault proximity and borehole coverage gaps. <em>Does not indicate ore at depth.</em>
          </span>
        </div>
        <span className="hidden md:inline-block text-[11px] bg-amber-900/60 px-2 py-0.5 rounded border border-amber-700/60 font-mono">
          Dongri Buzurg Lease (Bhandara)
        </span>
      </div>

      <div className="relative flex-1 flex">
        {/* Map Controls Panel */}
        <div className="absolute top-4 right-4 z-[400] bg-slate-900/95 backdrop-blur-md p-3.5 rounded-lg border border-slate-700/80 shadow-2xl text-xs space-y-2 text-slate-200">
          <div className="font-semibold text-slate-300 flex items-center gap-1.5 border-b border-slate-800 pb-1.5">
            <Layers className="w-3.5 h-3.5 text-amber-500" />
            <span>Map Layers & Priority Modes</span>
          </div>
          <label className="flex items-center gap-2 cursor-pointer hover:text-white">
            <input
              type="checkbox"
              checked={showPriorityGrid}
              onChange={(e) => setShowPriorityGrid(e.target.checked)}
              className="rounded text-amber-500 focus:ring-amber-500 bg-slate-800 border-slate-700"
            />
            <span>Exploration Priority Grid</span>
          </label>
          {showPriorityGrid && (
            <div className="pl-5 pt-1 space-y-1">
              <label className="flex items-center gap-2 cursor-pointer text-[11px] text-slate-300">
                <input
                  type="radio"
                  name="colorMode"
                  checked={colorMode === 'priority'}
                  onChange={() => setColorMode('priority')}
                  className="text-amber-500 focus:ring-amber-500"
                />
                <span>By Drill Priority Score</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer text-[11px] text-slate-300">
                <input
                  type="radio"
                  name="colorMode"
                  checked={colorMode === 'drill_gap'}
                  onChange={() => setColorMode('drill_gap')}
                  className="text-red-500 focus:ring-red-500"
                />
                <span className="text-red-300 font-medium">Drill Coverage Gap Layer</span>
              </label>
            </div>
          )}
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

          {/* Surface Exploration Priority Grid GeoJSON */}
          {showPriorityGrid && prospectivityMap && prospectivityMap.features && (
            <GeoJSON
              data={prospectivityMap}
              style={priorityStyle}
              onEachFeature={(feature, layer) => {
                layer.on({
                  click: () => {
                    setSelectedItem({
                      type: 'Exploration Priority Block',
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

          {(selectedItem.type === 'Prospectivity Block' || selectedItem.type === 'Exploration Priority Block') && (
            <div className="space-y-3 text-xs">
              <div className="bg-slate-800/80 p-3 rounded-lg border border-slate-700/60">
                <p className="text-slate-400">Exploration Grid Cell</p>
                <p className="text-sm font-bold text-white font-mono">{selectedItem.data.block_id}</p>
                <div className="mt-2 flex items-center justify-between">
                  <span className="text-slate-400">Priority Score:</span>
                  <span className="text-base font-bold text-amber-400 font-mono">
                    {selectedItem.data.exploration_priority_score || selectedItem.data.prospectivity_score}
                  </span>
                </div>
                <div className="mt-1 flex items-center justify-between">
                  <span className="text-slate-400">Drill Priority:</span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    (selectedItem.data.exploration_priority_category || selectedItem.data.prospectivity_category || '').includes('High') ? 'bg-purple-900/80 text-purple-200 border border-purple-700' :
                    (selectedItem.data.exploration_priority_category || selectedItem.data.prospectivity_category || '').includes('Medium') ? 'bg-amber-900/80 text-amber-200 border border-amber-700' :
                    'bg-slate-800 text-slate-400'
                  }`}>
                    {selectedItem.data.exploration_priority_category || selectedItem.data.prospectivity_category}
                  </span>
                </div>
              </div>

              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 space-y-2">
                <h4 className="font-semibold text-slate-300">Exploration Drill Indicators</h4>
                <div className="flex justify-between text-slate-400">
                  <span>Drill Coverage Gap:</span>
                  <span className="text-red-400 font-mono font-bold">
                    {selectedItem.data.drill_coverage_gap_m ? `${selectedItem.data.drill_coverage_gap_m} m` : '240 m'}
                  </span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Gap Category:</span>
                  <span className="text-slate-300 font-medium">
                    {selectedItem.data.drill_gap_category || 'Moderate Gap (150-300m)'}
                  </span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Dist to Fault Belt:</span>
                  <span className="text-slate-200 font-mono">{selectedItem.data.dist_to_fault_km} km</span>
                </div>
                <div className="pt-2 border-t border-slate-800/80 text-[10px] text-amber-400/90 leading-relaxed italic">
                  Note: Guides where new drillholes maximize exploratory information gain. Does not indicate ore at depth.
                </div>
              </div>
            </div>
          )}
        </div>
      )}
      </div>
    </div>

  );
};
