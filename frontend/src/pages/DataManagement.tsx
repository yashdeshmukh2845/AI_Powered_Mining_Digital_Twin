import React, { useState, useEffect } from 'react';
import { Database, Upload, Download, CheckCircle2, FileSpreadsheet } from 'lucide-react';
import type { DataImportRecord } from '../types';
import { api } from '../services/api';

export const DataManagement: React.FC = () => {
  const [selectedDatasetType, setSelectedDatasetType] = useState<string>('production_records');
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<any | null>(null);
  const [importResult, setImportResult] = useState<any | null>(null);
  const [importHistory, setImportHistory] = useState<DataImportRecord[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const datasetTypes = [
    { id: 'production_records', name: 'Production Records' },
    { id: 'boreholes', name: 'Boreholes & Collar Logs' },
    { id: 'borehole_intervals', name: 'Borehole Lithology Intervals' },
    { id: 'assay_samples', name: 'Lab Assay Results' },
    { id: 'ore_blocks', name: 'Ore Block Attributes' },
    { id: 'equipment', name: 'Mining Equipment & Fleet' },
    { id: 'environmental_observations', name: 'Satellite & Weather Observations' }
  ];

  const loadHistory = async () => {
    try {
      const hist = await api.getImportHistory();
      setImportHistory(hist);
    } catch (err) {
      console.error('Error loading import history:', err);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setPreview(null);
      setImportResult(null);
    }
  };

  const handlePreview = async () => {
    if (!file) return;
    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('dataset_type', selectedDatasetType);
      const res = await api.previewData(formData);
      setPreview(res);
    } catch (err: any) {
      alert(`Preview failed: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleImport = async () => {
    if (!file) return;
    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('dataset_type', selectedDatasetType);
      const res = await api.importData(formData);
      setImportResult(res);
      setPreview(null);
      setFile(null);
      loadHistory();
    } catch (err: any) {
      alert(`Import failed: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Database className="w-5 h-5 text-amber-500" />
            Data Ingestion & Dataset Management Pipeline
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Import CSV, Excel, or GeoJSON files, preview rows, map headers, validate required fields, and download templates.
          </p>
        </div>

        {/* Download Template & Demo Actions */}
        <div className="flex items-center gap-2">
          <a
            href={`/api/data/templates/${selectedDatasetType}`}
            download
            className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg flex items-center gap-1.5 transition-colors border border-slate-700"
          >
            <Download className="w-3.5 h-3.5 text-amber-500" />
            CSV Template
          </a>
          <a
            href={`/api/data/download-demo/${selectedDatasetType}`}
            download
            className="px-3 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 text-xs font-bold rounded-lg flex items-center gap-1.5 transition-colors shadow-sm"
          >
            <FileSpreadsheet className="w-3.5 h-3.5" />
            Demo Dataset
          </a>
        </div>
      </div>

      {/* Main Upload Box */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h3 className="font-bold text-base text-slate-900 border-b border-slate-100 pb-3 flex items-center gap-2">
            <Upload className="w-4 h-4 text-amber-500" />
            Upload New File
          </h3>

          <div className="space-y-3 text-xs">
            <div>
              <label className="font-semibold text-slate-700 block mb-1">Target Dataset Type:</label>
              <select
                value={selectedDatasetType}
                onChange={(e) => setSelectedDatasetType(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2 text-slate-800 focus:outline-none"
              >
                {datasetTypes.map(d => (
                  <option key={d.id} value={d.id}>{d.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">Select File (CSV, XLSX, GeoJSON):</label>
              <input
                type="file"
                accept=".csv, .xlsx, .xls, .geojson"
                onChange={handleFileChange}
                className="w-full text-xs text-slate-500 file:mr-3 file:py-2 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-slate-900 file:text-white hover:file:bg-slate-800 cursor-pointer"
              />
            </div>
          </div>

          <div className="flex gap-2 pt-2">
            <button
              onClick={handlePreview}
              disabled={!file || isLoading}
              className="flex-1 py-2 bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold text-xs rounded-lg transition-colors"
            >
              Preview & Validate
            </button>
            <button
              onClick={handleImport}
              disabled={!file || isLoading}
              className="flex-1 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs rounded-lg transition-colors shadow-sm"
            >
              Commit Import
            </button>
          </div>
        </div>

        {/* Preview & Validation Report */}
        <div className="lg:col-span-2 space-y-6">
          {preview && (
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
              <div className="flex justify-between items-center border-b border-slate-100 pb-3">
                <h3 className="font-bold text-base text-slate-900">Validation & Column Mapping Preview</h3>
                <span className={`px-2.5 py-1 rounded text-xs font-bold ${
                  preview.is_valid ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'
                }`}>
                  {preview.is_valid ? 'VALID HEADER SCHEMA' : 'INVALID / MISSING COLUMNS'}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="p-2.5 bg-slate-50 rounded">
                  <span className="text-slate-500">Total Rows Detected:</span>
                  <span className="font-bold text-slate-800 font-mono ml-2">{preview.total_rows}</span>
                </div>
                <div className="p-2.5 bg-slate-50 rounded">
                  <span className="text-slate-500">Dataset Format:</span>
                  <span className="font-bold text-slate-800 font-mono ml-2">{selectedDatasetType}</span>
                </div>
              </div>

              {preview.missing_required_columns && preview.missing_required_columns.length > 0 && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-xs text-red-700">
                  <strong>Missing Required Columns:</strong> {preview.missing_required_columns.join(', ')}
                </div>
              )}

              {/* Sample Table */}
              {preview.preview_rows && (
                <div className="overflow-x-auto border border-slate-200 rounded-lg">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-50 text-slate-700 border-b border-slate-200 font-semibold">
                      <tr>
                        {Object.keys(preview.preview_rows[0] || {}).slice(0, 6).map((col) => (
                          <th key={col} className="py-2 px-3">{col}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {preview.preview_rows.map((row: any, i: number) => (
                        <tr key={i}>
                          {Object.values(row).slice(0, 6).map((val: any, j: number) => (
                            <td key={j} className="py-2 px-3 font-mono text-slate-700">{String(val)}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {importResult && (
            <div className="bg-emerald-50 p-6 rounded-xl border border-emerald-200 shadow-sm space-y-2 text-xs">
              <h3 className="font-bold text-sm text-emerald-900 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                Import Result Confirmed
              </h3>
              <p className="text-emerald-800">
                Successfully imported <strong>{importResult.imported_rows}</strong> out of {importResult.total_rows} records into the database.
              </p>
              {importResult.rejected_rows > 0 && (
                <p className="text-amber-800">
                  {importResult.rejected_rows} invalid rows were logged to error history and rejected.
                </p>
              )}
            </div>
          )}

          {/* Import Audit History */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-3">
            <h3 className="font-bold text-sm text-slate-900">Recent Data Ingestion Audit Log</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-600 border-b border-slate-200 font-semibold">
                  <tr>
                    <th className="py-2.5 px-3">File Name</th>
                    <th className="py-2.5 px-3">Type</th>
                    <th className="py-2.5 px-3">Imported</th>
                    <th className="py-2.5 px-3">Rejected</th>
                    <th className="py-2.5 px-3">Status</th>
                    <th className="py-2.5 px-3">Timestamp</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-medium">
                  {importHistory.map((rec) => (
                    <tr key={rec.id}>
                      <td className="py-2.5 px-3 font-semibold text-slate-800">{rec.file_name}</td>
                      <td className="py-2.5 px-3 text-slate-600 font-mono">{rec.dataset_type}</td>
                      <td className="py-2.5 px-3 text-emerald-600 font-mono font-bold">{rec.imported_rows}</td>
                      <td className="py-2.5 px-3 text-red-600 font-mono">{rec.rejected_rows}</td>
                      <td className="py-2.5 px-3">
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800">
                          {rec.status}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 text-slate-400 font-mono">{rec.timestamp.replace('T', ' ').substring(0, 16)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
