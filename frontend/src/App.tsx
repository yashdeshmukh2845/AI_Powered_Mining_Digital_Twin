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

  const loadData = async (mineId: string) => {
    setIsLoading(true);
    try {
      const [sumRes, bhRes, blkRes, geoRes, pmapRes, fcRes, recRes, metRes] = await Promise.all([
        api.getDashboardSummary(mineId),
        api.getBoreholes(mineId),
        api.getBlocks(mineId),
        api.getGeologyLayers(mineId),
        api.getProspectivityMap(),
        api.getProductionForecast(mineId, 30),
        api.generateRecommendations(mineId),
        api.getModelMetrics()
      ]);

      setSummary(sumRes);
      setBoreholes(bhRes);
      setBlocks(blkRes);
      setGeologyData(geoRes);
      setProspectivityMap(pmapRes);
      setForecastHistory(fcRes);
      setRecommendations(recRes);
      setModelMetrics(metRes);
    } catch (err) {
      console.error('Error loading dashboard data:', err);
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
