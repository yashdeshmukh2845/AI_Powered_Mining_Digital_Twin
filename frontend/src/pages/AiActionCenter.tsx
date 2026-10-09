import React, { useState } from 'react';
import { Zap, CheckCircle2, XCircle } from 'lucide-react';
import type { Recommendation } from '../types';
import { api } from '../services/api';

interface AiActionCenterProps {
  recommendations: Recommendation[];
  onRefreshRecommendations: () => void;
}

export const AiActionCenter: React.FC<AiActionCenterProps> = ({
  recommendations,
  onRefreshRecommendations
}) => {
  const [loadingId, setLoadingId] = useState<string | null>(null);

  const handleAction = async (recId: string, action: string) => {
    setLoadingId(recId);
    try {
      await api.updateRecommendationStatus(recId, action);
      onRefreshRecommendations();
    } catch (err) {
      console.error('Error updating recommendation action:', err);
    } finally {
      setLoadingId(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Zap className="w-5 h-5 text-amber-500" />
            AI Action & Optimization Recommendation Engine
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Prioritized corrective action protocols requiring explicit human manager review before operational execution.
          </p>
        </div>
      </div>

      {/* Recommendations List */}
      <div className="space-y-4">
        {recommendations.map((rec) => (
          <div key={rec.id} className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-all space-y-4">
            <div className="flex flex-col md:flex-row justify-between md:items-center gap-2 border-b border-slate-100 pb-3">
              <div className="flex items-center gap-3">
                <span className={`px-2.5 py-1 rounded text-xs font-bold ${
                  rec.priority === 'High' ? 'bg-red-100 text-red-700 border border-red-200' : 'bg-amber-100 text-amber-800 border border-amber-200'
                }`}>
                  {rec.priority} Priority
                </span>
                <h3 className="font-bold text-slate-900 text-base">{rec.title}</h3>
              </div>

              <div className="flex items-center gap-2 text-xs">
                <span className="text-slate-400">Target Area:</span>
                <span className="font-semibold text-slate-700 font-mono bg-slate-100 px-2 py-0.5 rounded">{rec.affected_block_or_mine}</span>
              </div>
            </div>

            <p className="text-xs text-slate-600 leading-relaxed">{rec.description}</p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 bg-slate-50 p-3 rounded-lg border border-slate-200 text-xs">
              <div>
                <span className="text-slate-500 font-semibold block">Rationale & Physics:</span>
                <span className="text-slate-800">{rec.rationale}</span>
              </div>
              <div>
                <span className="text-slate-500 font-semibold block">Constraints & Assumptions:</span>
                <span className="text-slate-800">{rec.constraints_assumptions}</span>
              </div>
              <div>
                <span className="text-slate-500 font-semibold block">Estimated Production Gain:</span>
                <span className="text-emerald-700 font-mono font-bold text-sm">+{rec.est_production_impact_tonnes} tonnes/day</span>
              </div>
            </div>

            {/* Approval Controls */}
            <div className="flex flex-col sm:flex-row justify-between items-center gap-3 pt-2">
              <div className="flex items-center gap-2 text-xs text-slate-500">
                <span>Responsible Team:</span>
                <span className="font-semibold text-slate-800">{rec.responsible_team}</span>
              </div>

              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-400 font-medium mr-2">Approval Status:</span>
                <button
                  onClick={() => handleAction(rec.id, 'Approve')}
                  disabled={loadingId === rec.id}
                  className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs rounded-lg transition-colors flex items-center gap-1.5 shadow-sm"
                >
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  Approve Protocol
                </button>
                <button
                  onClick={() => handleAction(rec.id, 'Reject')}
                  disabled={loadingId === rec.id}
                  className="px-3 py-1.5 bg-slate-200 hover:bg-slate-300 text-slate-700 font-semibold text-xs rounded-lg transition-colors flex items-center gap-1.5"
                >
                  <XCircle className="w-3.5 h-3.5" />
                  Reject
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
