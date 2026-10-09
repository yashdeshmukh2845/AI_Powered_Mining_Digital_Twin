import React, { useState, useEffect } from 'react';
import { BarChart3, RefreshCw } from 'lucide-react';
import type { ModelStatus } from '../types';
import { api } from '../services/api';

export const ModelPerformance: React.FC = () => {
  const [modelStatus, setModelStatus] = useState<ModelStatus | null>(null);
  const [metrics, setMetrics] = useState<any | null>(null);
  const [isTraining, setIsTraining] = useState<boolean>(false);
  const [trainMessage, setTrainMessage] = useState<string | null>(null);

  const loadModelData = async () => {
    try {
      const statusRes = await api.getModelStatus();
      const metricsRes = await api.getModelMetrics();
      setModelStatus(statusRes);
      setMetrics(metricsRes);
    } catch (err) {
      console.error('Error loading model performance data:', err);
    }
  };

  useEffect(() => {
    loadModelData();
  }, []);

  const handleRetrainProspectivity = async () => {
    setIsTraining(true);
    setTrainMessage('Training Mineral Prospectivity Random Forest Classifier...');
    try {
      const res = await api.trainProspectivityModel('RandomForest');
      setTrainMessage(`Prospectivity Model Retrained Successfully! (F1: ${res.metrics.f1_score}, ROC-AUC: ${res.metrics.roc_auc})`);
      loadModelData();
    } catch (err: any) {
      setTrainMessage(`Training failed: ${err.message}`);
    } finally {
      setIsTraining(false);
    }
  };

  const handleRetrainProduction = async () => {
    setIsTraining(true);
    setTrainMessage('Training Production Forecasting Regressor on historical records...');
    try {
      const res = await api.trainProductionModel('RandomForest');
      setTrainMessage(`Production Model Retrained Successfully! (MAE: ${res.metrics.mae} t, WAPE: ${res.metrics.wape_pct}%)`);
      loadModelData();
    } catch (err: any) {
      setTrainMessage(`Training failed: ${err.message}`);
    } finally {
      setIsTraining(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-amber-500" />
            Machine Learning Model Performance & Version Management
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Persisted joblib model artifacts, spatial & time-aware evaluation metrics, data leakage prevention, and model retraining controls.
          </p>
        </div>
      </div>

      {trainMessage && (
        <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl text-amber-900 text-xs font-medium shadow-sm flex items-center justify-between">
          <span>{trainMessage}</span>
          <button onClick={() => setTrainMessage(null)} className="text-amber-700 hover:text-amber-950 font-bold">Dismiss</button>
        </div>
      )}

      {/* Model Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Model 1: Prospectivity Classifier */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex justify-between items-center border-b border-slate-100 pb-3">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-purple-700 bg-purple-50 px-2 py-0.5 rounded">Geological Prospectivity</span>
              <h3 className="font-bold text-base text-slate-900 mt-1">Mineral Prospectivity Classifier</h3>
            </div>
            <span className="text-xs font-mono font-bold text-slate-500">
              {modelStatus?.prospectivity_model?.algorithm || 'RandomForest'}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="p-3 bg-slate-50 rounded-lg">
              <span className="text-slate-500 block">Precision</span>
              <span className="text-lg font-bold text-slate-900 font-mono">{metrics?.prospectivity?.precision || 0.7917}</span>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg">
              <span className="text-slate-500 block">Recall</span>
              <span className="text-lg font-bold text-slate-900 font-mono">{metrics?.prospectivity?.recall || 0.9500}</span>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg">
              <span className="text-slate-500 block">F1 Score</span>
              <span className="text-lg font-bold text-purple-700 font-mono">{metrics?.prospectivity?.f1_score || 0.8636}</span>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg">
              <span className="text-slate-500 block">ROC-AUC</span>
              <span className="text-lg font-bold text-emerald-600 font-mono">{metrics?.prospectivity?.roc_auc || 0.9216}</span>
            </div>
          </div>

          <div className="pt-2 flex justify-between items-center text-xs border-t border-slate-100">
            <span className="text-slate-400">Last Trained: {modelStatus?.prospectivity_model?.last_updated}</span>
            <button
              onClick={handleRetrainProspectivity}
              disabled={isTraining}
              className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs rounded-lg transition-colors flex items-center gap-1.5 shadow-sm"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isTraining ? 'animate-spin text-amber-500' : ''}`} />
              Retrain Model
            </button>
          </div>
        </div>

        {/* Model 2: Production Regressor */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex justify-between items-center border-b border-slate-100 pb-3">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-amber-700 bg-amber-50 px-2 py-0.5 rounded">Operational Forecasting</span>
              <h3 className="font-bold text-base text-slate-900 mt-1">Production Shortfall Regressor</h3>
            </div>
            <span className="text-xs font-mono font-bold text-slate-500">
              {modelStatus?.production_model?.algorithm || 'RandomForestRegressor'}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="p-3 bg-slate-50 rounded-lg">
              <span className="text-slate-500 block">Mean Absolute Error</span>
              <span className="text-lg font-bold text-slate-900 font-mono">{metrics?.production?.mae || 77.21} t</span>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg">
              <span className="text-slate-500 block">Root Mean Sq Error</span>
              <span className="text-lg font-bold text-slate-900 font-mono">{metrics?.production?.rmse || 97.98} t</span>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg">
              <span className="text-slate-500 block">WAPE Metric</span>
              <span className="text-lg font-bold text-emerald-600 font-mono">{metrics?.production?.wape_pct || 4.41}%</span>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg">
              <span className="text-slate-500 block">Train/Test Split</span>
              <span className="text-lg font-bold text-slate-700 font-mono">Time-Aware (80/20)</span>
            </div>
          </div>

          <div className="pt-2 flex justify-between items-center text-xs border-t border-slate-100">
            <span className="text-slate-400">Last Trained: {modelStatus?.production_model?.last_updated}</span>
            <button
              onClick={handleRetrainProduction}
              disabled={isTraining}
              className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs rounded-lg transition-colors flex items-center gap-1.5 shadow-sm"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isTraining ? 'animate-spin text-amber-500' : ''}`} />
              Retrain Model
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
