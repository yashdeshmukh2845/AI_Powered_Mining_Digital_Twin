import React from 'react';
import { FileText, Download, Settings } from 'lucide-react';
import { api } from '../services/api';

export const ReportsSettings: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <FileText className="w-5 h-5 text-amber-500" />
            Executive Reports & Application Settings
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Export executive summaries as CSV or PDF documents, configure risk threshold parameters, and review system audit events.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Export Executive Reports Card */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h3 className="font-bold text-base text-slate-900 border-b border-slate-100 pb-3 flex items-center gap-2">
            <Download className="w-4 h-4 text-amber-500" />
            Download Executive Reports
          </h3>
          <p className="text-xs text-slate-600 leading-relaxed">
            Generate printable operational reports containing resource estimates, daily target attainment, forecast shortfalls, equipment availability, and demo mode disclaimers.
          </p>

          <div className="flex flex-col sm:flex-row gap-3 pt-2">
            <a
              href={api.getReportSummary('csv')}
              download="MOIL_Executive_Summary_Report.csv"
              className="flex-1 py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs rounded-lg transition-colors flex items-center justify-center gap-2 shadow-sm"
            >
              <Download className="w-4 h-4 text-amber-500" />
              Download CSV Summary
            </a>

            <a
              href={api.getReportSummary('pdf')}
              download="MOIL_Executive_Report.pdf"
              className="flex-1 py-2.5 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs rounded-lg transition-colors flex items-center justify-center gap-2 shadow-sm"
            >
              <FileText className="w-4 h-4" />
              Download PDF Report
            </a>
          </div>
        </div>

        {/* System Settings & Threshold Defaults */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h3 className="font-bold text-base text-slate-900 border-b border-slate-100 pb-3 flex items-center gap-2">
            <Settings className="w-4 h-4 text-amber-500" />
            System Default Settings
          </h3>

          <div className="space-y-3 text-xs">
            <div className="flex justify-between items-center p-2.5 bg-slate-50 rounded-lg">
              <span className="font-semibold text-slate-700">Prototype Shortfall Risk Thresholds:</span>
              <span className="font-mono text-slate-900 font-bold">Low &lt;5% | Med 5-10% | High &ge;10%</span>
            </div>

            <div className="flex justify-between items-center p-2.5 bg-slate-50 rounded-lg">
              <span className="font-semibold text-slate-700">Ore Bulk Density Baseline:</span>
              <span className="font-mono text-purple-700 font-bold">3.4 tonnes/m³</span>
            </div>

            <div className="flex justify-between items-center p-2.5 bg-slate-50 rounded-lg">
              <span className="font-semibold text-slate-700">Demonstration Mode Status:</span>
              <span className="font-bold text-amber-600">ACTIVE (Synthetic Data)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
