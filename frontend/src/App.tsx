import { useState, useEffect } from 'react';
import { Sidebar } from './components/layout/Sidebar';
import { TopBar } from './components/layout/TopBar';
import { DemoBanner } from './components/layout/DemoBanner';
import { Overview } from './pages/Overview';
import { MineMapPage } from './pages/MineMapPage';
import { ReserveIntelligence } from './pages/ReserveIntelligence';
import { ProductionForecast } from './pages/ProductionForecast';
import { RiskCenter } from './pages/RiskCenter';
import { AiActionCenter } from './pages/AiActionCenter';
import { DigitalTwinSimulator } from './pages/DigitalTwinSimulator';
import { DataManagement } from './pages/DataManagement';
import { ModelPerformance } from './pages/ModelPerformance';
import { ReportsSettings } from './pages/ReportsSettings';
import type { DashboardSummary, Borehole, OreBlock, ForecastItem, Recommendation } from './types';
import { api } from './services/api';

export function App() {
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [selectedMineId, setSelectedMineId] = useState<string>('MINE-001');
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [boreholes, setBoreholes] = useState<Borehole[]>([]);
  const [blocks, setBlocks] = useState<OreBlock[]>([]);
  const [geologyData, setGeologyData] = useState<any>(null);
  const [prospectivityMap, setProspectivityMap] = useState<any>(null);
  const [forecastHistory, setForecastHistory] = useState<ForecastItem[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [modelMetrics, setModelMetrics] = useState<any>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadData = async (mineId: string) => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const sumRes = await api.getDashboardSummary(mineId);
      setSummary(sumRes);

      // Load remaining data in parallel
      const [bhRes, blkRes, geoRes, pmapRes, fcRes, recRes, metRes] = await Promise.allSettled([
        api.getBoreholes(mineId),
        api.getBlocks(mineId),
        api.getGeologyLayers(mineId),
        api.getProspectivityMap(),
        api.getProductionForecast(mineId, 30),
        api.generateRecommendations(mineId),
        api.getModelMetrics()
      ]);

      if (bhRes.status === 'fulfilled') setBoreholes(bhRes.value);
      if (blkRes.status === 'fulfilled') setBlocks(blkRes.value);
      if (geoRes.status === 'fulfilled') setGeologyData(geoRes.value);
      if (pmapRes.status === 'fulfilled') setProspectivityMap(pmapRes.value);
      if (fcRes.status === 'fulfilled') setForecastHistory(fcRes.value);
      if (recRes.status === 'fulfilled') setRecommendations(recRes.value);
      if (metRes.status === 'fulfilled') setModelMetrics(metRes.value);
    } catch (err: any) {
      console.error('Error loading dashboard summary:', err);
      setErrorMessage(err.message || 'Failed to connect to backend server');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData(selectedMineId);
  }, [selectedMineId]);

  const handleRefreshForecast = async (days: number) => {
    try {
      const res = await api.getProductionForecast(selectedMineId, days);
      setForecastHistory(res);
    } catch (err) {
      console.error('Error refreshing forecast:', err);
    }
  };

  const handleRefreshRecommendations = async () => {
    try {
      const res = await api.generateRecommendations(selectedMineId);
      setRecommendations(res);
    } catch (err) {
      console.error('Error refreshing recommendations:', err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col font-sans">
      <DemoBanner />
      <div className="flex flex-1">
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

        <div className="flex-1 flex flex-col min-w-0">
          <TopBar
            selectedMine={summary?.selected_mine || null}
            onMineChange={(id) => setSelectedMineId(id)}
            lastUpdated={summary?.last_updated || ''}
            onRefresh={() => loadData(selectedMineId)}
            isLoading={isLoading}
          />

          {errorMessage && (
            <div className="mx-6 mt-4 p-4 bg-red-900/90 text-white rounded-lg text-xs flex justify-between items-center shadow">
              <span><strong>Backend Connection Warning:</strong> {errorMessage}. Make sure backend server is running on port 8080.</span>
              <button onClick={() => loadData(selectedMineId)} className="underline font-bold hover:text-amber-300">Retry</button>
            </div>
          )}

          <main className="flex-1 p-6 overflow-y-auto max-w-[1600px] w-full mx-auto">
            {activeTab === 'overview' && (
              <Overview
                summary={summary}
                forecastHistory={forecastHistory}
                recommendations={recommendations}
                onNavigate={(tab) => setActiveTab(tab)}
              />
            )}

            {activeTab === 'map' && (
              <MineMapPage
                boreholes={boreholes}
                geologyData={geologyData}
                prospectivityMap={prospectivityMap}
              />
            )}

            {activeTab === 'reserves' && (
              <ReserveIntelligence blocks={blocks} />
            )}

            {activeTab === 'forecast' && (
              <ProductionForecast
                forecastItems={forecastHistory}
                modelMetrics={modelMetrics}
                onRefreshForecast={handleRefreshForecast}
              />
            )}

            {activeTab === 'risk' && (
              <RiskCenter />
            )}

            {activeTab === 'actions' && (
              <AiActionCenter
                recommendations={recommendations}
                onRefreshRecommendations={handleRefreshRecommendations}
              />
            )}

            {activeTab === 'simulator' && (
              <DigitalTwinSimulator />
            )}

            {activeTab === 'data' && (
              <DataManagement />
            )}

            {activeTab === 'models' && (
              <ModelPerformance />
            )}

            {activeTab === 'reports' && (
              <ReportsSettings />
            )}
          </main>
        </div>
      </div>
    </div>
  );
}

export default App;
