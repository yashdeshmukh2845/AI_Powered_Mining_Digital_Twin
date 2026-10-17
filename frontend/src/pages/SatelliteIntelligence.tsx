import React, { useState, useEffect } from 'react';
import { Globe, AlertTriangle, CheckCircle2, RefreshCw, Eye, Sparkles } from 'lucide-react';
import { api } from '../services/api';
import type { SatelliteSummary, SatelliteSample } from '../types';

export const SatelliteIntelligence: React.FC = () => {
  const [summary, setSummary] = useState<SatelliteSummary | null>(null);
  const [samples, setSamples] = useState<SatelliteSample[]>([]);
  const [selectedClass, setSelectedClass] = useState<string>('All');
  const [selectedSample, setSelectedSample] = useState<SatelliteSample | null>(null);
  const [classificationResult, setClassificationResult] = useState<any>(null);
  const [isClassifying, setIsClassifying] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [sumRes, sampRes] = await Promise.allSettled([
        api.getSatelliteSummary(),
        api.getSatelliteSamples(60)
      ]);
      if (sumRes.status === 'fulfilled') setSummary(sumRes.value);
      if (sampRes.status === 'fulfilled') {
        setSamples(sampRes.value);
        if (sampRes.value.length > 0) {
          setSelectedSample(sampRes.value[0]);
        }
      }
    } catch (err) {
      console.error('Error loading satellite data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClassify = async (sample: SatelliteSample) => {
    setIsClassifying(true);
    setClassificationResult(null);
    try {
      const res = await api.classifySatelliteImage(sample.class_label, sample.file_name);
      setClassificationResult(res);
    } catch (err: any) {
      console.error('Classification error:', err);
      setClassificationResult({
        error: err.message || 'Failed to classify image'
      });
    } finally {
      setIsClassifying(false);
    }
  };

  const filteredSamples = selectedClass === 'All'
    ? samples
    : samples.filter(s => s.class_label === selectedClass);

  const classesList = summary?.classes || [
    'AnnualCrop', 'Forest', 'HerbaceousVegetation', 'Highway', 'Industrial',
    'Pasture', 'PermanentCrop', 'Residential', 'River', 'SeaLake'
  ];

  return (
    <div className="space-y-6 pb-12">
      {/* Header Banner */}
      <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 shadow-md flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-2 text-amber-500 font-bold text-xs uppercase tracking-wider mb-1">
            <Globe className="w-4 h-4" /> Space Technology & Earth Observation
          </div>
          <h2 className="text-xl font-bold text-white tracking-tight">
            Sentinel-2 Satellite Land-Cover Intelligence
          </h2>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Integrated EuroSAT RGB Optical Imagery dataset containing 27,000 Sentinel-2 satellite tiles across 10 European Land Cover classes.
          </p>
        </div>
        <button
          onClick={loadData}
          disabled={isLoading}
          className="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg border border-slate-700 flex items-center gap-2 transition-all shadow-sm"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh Imagery
        </button>
      </div>

      {/* Critical Scientific Disclaimer Notice */}
      <div className="bg-amber-950/40 border border-amber-800/80 rounded-xl p-5 text-xs text-amber-200/90 shadow-sm space-y-2">
        <div className="flex items-center gap-2 font-bold text-amber-400 text-sm">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          SCIENTIFIC & SATELLITE SENSING LIMITATIONS NOTICE
        </div>
        <p className="leading-relaxed">
          <strong>1. Surface Land Cover vs Underground Reserves:</strong> The EuroSAT optical RGB imagery dataset captures surface land features (vegetation, waterways, residential structures, industrial plants) at 10m/pixel spatial resolution. <em>Optical RGB imagery cannot independently detect or quantify subsurface manganese ore bodies.</em>
        </p>
        <p className="leading-relaxed">
          <strong>2. Multi-Spectral & Hyper-Spectral Requirements:</strong> Spectral absorption indices (such as iron oxide ratios, clay absorption, and genuine NDVI) require Sentinel-2 MultiSpectral Instrument (MSI) Near-Infrared (B8) and Short-Wave Infrared (B11, B12) bands. Because the EuroSAT RGB dataset provides only 3 optical bands (Red, Green, Blue), these multi-spectral indices are marked as <strong>Unavailable</strong> rather than fabricated.
        </p>
        <p className="leading-relaxed">
          <strong>3. Reserve Validation:</strong> Definitive manganese reserve estimation at Dongri Buzurg requires direct geological sampling via diamond core borehole exploration, lithological assays, and structural cross-sections.
        </p>
      </div>

      {/* Dataset Statistics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Satellite Tiles</span>
          <p className="text-2xl font-black text-slate-900 mt-2 font-mono">
            {summary ? summary.total_images.toLocaleString() : '27,000'}
          </p>
          <span className="text-[11px] text-slate-500 mt-1 block">EuroSAT Sentinel-2 RGB</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Surface Classes</span>
          <p className="text-2xl font-black text-slate-900 mt-2 font-mono">
            {summary ? summary.num_classes : 10} <span className="text-xs font-normal text-slate-500">Classes</span>
          </p>
          <span className="text-[11px] text-slate-500 mt-1 block">Land Cover Categories</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Tile Geometry</span>
          <p className="text-2xl font-black text-slate-900 mt-2 font-mono">64 &times; 64 <span className="text-xs font-normal text-slate-500">px</span></p>
          <span className="text-[11px] text-slate-500 mt-1 block">RGB 3-channel optical</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Multi-Spectral Bands</span>
          <p className="text-xl font-bold text-slate-500 mt-2">Unavailable</p>
          <span className="text-[11px] text-amber-700 mt-1 block">Requires NIR / SWIR sensors</span>
        </div>
      </div>

      {/* Interactive Satellite Gallery and Classification Sandbox */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Class Selector & Image Grid */}
        <div className="lg:col-span-2 bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h3 className="font-bold text-slate-900 text-sm">EuroSAT Image Gallery</h3>
              <p className="text-xs text-slate-500">Select a land-cover class to view genuine Sentinel-2 tiles</p>
            </div>
            
            <div className="flex flex-wrap gap-1.5">
              <button
                onClick={() => setSelectedClass('All')}
                className={`px-2.5 py-1 rounded text-xs font-semibold transition-all ${
                  selectedClass === 'All'
                    ? 'bg-amber-500 text-slate-950 shadow-sm'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                All
              </button>
              {classesList.map(c => (
                <button
                  key={c}
                  onClick={() => setSelectedClass(c)}
                  className={`px-2 py-1 rounded text-[11px] font-semibold transition-all ${
                    selectedClass === c
                      ? 'bg-amber-500 text-slate-950 shadow-sm'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {c}
                </button>
              ))}
            </div>
          </div>

          {/* Image Tiles Grid */}
          <div className="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 gap-3 max-h-[380px] overflow-y-auto p-2 bg-slate-50 rounded-lg border border-slate-200">
            {filteredSamples.map((sample) => {
              const isSelected = selectedSample?.id === sample.id;
              return (
                <div
                  key={sample.id}
                  onClick={() => {
                    setSelectedSample(sample);
                    setClassificationResult(null);
                  }}
                  className={`cursor-pointer rounded-lg overflow-hidden border-2 transition-all p-1 bg-white flex flex-col items-center ${
                    isSelected
                      ? 'border-amber-500 shadow-md ring-2 ring-amber-300'
                      : 'border-transparent hover:border-slate-300'
                  }`}
                >
                  <img
                    src={sample.image_url}
                    alt={sample.class_label}
                    className="w-16 h-16 object-cover rounded"
                    loading="lazy"
                  />
                  <span className="text-[10px] text-slate-600 font-medium truncate w-full text-center mt-1">
                    {sample.class_label}
                  </span>
                </div>
              );
            })}
          </div>

          <div className="text-[11px] text-slate-500 italic flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
            Showing real Sentinel-2 tiles served directly from project <code>data/EuroSAT_RGB/</code> storage.
          </div>
        </div>

        {/* Right: Live AI Classifier Sandbox */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Sparkles className="w-4 h-4 text-purple-600" />
              <h3 className="font-bold text-slate-900 text-sm">Land-Cover AI Classifier</h3>
            </div>

            {selectedSample ? (
              <div className="space-y-4">
                <div className="p-4 bg-slate-900 rounded-xl flex flex-col items-center border border-slate-800">
                  <img
                    src={selectedSample.image_url}
                    alt="Active Tile"
                    className="w-32 h-32 object-cover rounded-lg shadow-lg border border-slate-700"
                  />
                  <div className="mt-3 text-center">
                    <span className="text-[11px] text-slate-400 block font-mono">{selectedSample.file_name}</span>
                    <span className="inline-block mt-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">
                      Ground Truth: {selectedSample.class_label}
                    </span>
                  </div>
                </div>

                <button
                  onClick={() => handleClassify(selectedSample)}
                  disabled={isClassifying}
                  className="w-full py-2.5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold text-xs rounded-lg shadow-md transition-all flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  <Eye className="w-4 h-4" />
                  {isClassifying ? 'Analyzing Tile...' : 'Classify Surface Land Cover'}
                </button>

                {classificationResult && (
                  <div className="p-3.5 bg-purple-50 border border-purple-200 rounded-lg text-xs space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="font-bold text-purple-900">Model Prediction:</span>
                      <span className="font-black text-sm text-purple-700 font-mono">
                        {classificationResult.predicted_class}
                      </span>
                    </div>
                    <div className="flex justify-between items-center text-slate-600 border-t border-purple-100 pt-1.5">
                      <span>Model Confidence:</span>
                      <span className="font-bold text-emerald-700 font-mono">
                        {(classificationResult.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                    {classificationResult.disclaimer && (
                      <p className="text-[10px] text-purple-900/80 pt-1 border-t border-purple-100">
                        {classificationResult.disclaimer}
                      </p>
                    )}
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-12 text-slate-400 text-xs">
                Select an image tile from the gallery to run classification.
              </div>
            )}
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] text-slate-400 text-center">
            Algorithm: Random Forest Spatial-Moment Classifier (Trained on EuroSAT)
          </div>
        </div>
      </div>
    </div>
  );
};
