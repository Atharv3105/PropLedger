import React, { useEffect, useState } from 'react';
import { reportsApi } from '../services/api';
import { HierarchyNode, RentPivot, PropertyOccupancy } from '../types';
import { Card } from '../components/common/Card';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { GitBranch, Table, PieChart, FileText, Download, Eye, CheckCircle } from 'lucide-react';

export const ReportsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'catalog' | 'hierarchy' | 'pivot' | 'occupancy'>('catalog');
  const [hierarchy, setHierarchy] = useState<HierarchyNode[]>([]);
  const [rentPivot, setRentPivot] = useState<RentPivot[]>([]);
  const [occupancy, setOccupancy] = useState<PropertyOccupancy[]>([]);
  const [catalog, setCatalog] = useState<any[]>([]);
  const [selectedReport, setSelectedReport] = useState<any | null>(null);
  const [reportData, setReportData] = useState<any | null>(null);
  const [loadingData, setLoadingData] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      reportsApi.getCatalog().catch(() => []),
      reportsApi.getHierarchy(4).catch(() => []),
      reportsApi.getRentPivot(50).catch(() => []),
      reportsApi.getOccupancy().catch(() => []),
    ])
      .then(([cat, hier, pvt, occ]) => {
        setCatalog(cat);
        setHierarchy(hier);
        setRentPivot(pvt);
        setOccupancy(occ);
      })
      .finally(() => setLoading(false));
  }, []);

  const handlePreviewReport = (report: any) => {
    setSelectedReport(report);
    setLoadingData(true);
    reportsApi.getReportData(report.report_code, 25)
      .then((data) => setReportData(data))
      .catch((err) => console.error(err))
      .finally(() => setLoadingData(false));
  };

  const handleExport = (reportCode: string, format: 'excel' | 'pdf') => {
    const url = `/api/v1/reports/${reportCode}/export/${format}`;
    window.open(url, '_blank');
  };

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Enterprise Reports & Analytics</h2>
          <p className="text-xs text-slate-500">
            SSRS-equivalent institutional reporting engine (Excel & PDF) and SQL analytical rollups
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-lg border border-slate-200">
          <button
            onClick={() => setActiveTab('catalog')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-bold transition ${
              activeTab === 'catalog' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            <FileText className="w-3.5 h-3.5 text-blue-600" />
            Report Catalog ({catalog.length || 14})
          </button>
          <button
            onClick={() => setActiveTab('hierarchy')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-bold transition ${
              activeTab === 'hierarchy' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            <GitBranch className="w-3.5 h-3.5 text-emerald-600" />
            Asset Hierarchy
          </button>
          <button
            onClick={() => setActiveTab('pivot')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-bold transition ${
              activeTab === 'pivot' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            <Table className="w-3.5 h-3.5 text-sky-600" />
            Rent Pivot
          </button>
          <button
            onClick={() => setActiveTab('occupancy')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-bold transition ${
              activeTab === 'occupancy' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            <PieChart className="w-3.5 h-3.5 text-indigo-600" />
            Occupancy Rollups
          </button>
        </div>
      </div>

      {loading ? (
        <LoadingSpinner message="Querying enterprise reporting engine..." />
      ) : activeTab === 'catalog' ? (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {catalog.map((rep) => (
              <div
                key={rep.report_code}
                className="bg-white p-4 rounded-xl border border-slate-200 hover:border-blue-300 hover:shadow-sm transition flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
                      {rep.report_code}
                    </span>
                    <span className="text-[11px] font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full">
                      {rep.category}
                    </span>
                  </div>
                  <h3 className="text-sm font-bold text-slate-900 mb-1">{rep.title}</h3>
                  <p className="text-xs text-slate-600 line-clamp-3 mb-3">{rep.description}</p>
                </div>

                <div className="pt-3 border-t border-slate-100 flex items-center justify-between gap-1.5">
                  <button
                    onClick={() => handlePreviewReport(rep)}
                    className="flex items-center gap-1 text-[11px] font-semibold text-slate-700 hover:text-blue-600 px-2 py-1 rounded hover:bg-slate-50"
                  >
                    <Eye className="w-3.5 h-3.5" />
                    Preview
                  </button>
                  <div className="flex items-center gap-1.5">
                    <button
                      onClick={() => handleExport(rep.report_code, 'excel')}
                      className="flex items-center gap-1 text-[11px] font-bold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 px-2.5 py-1 rounded border border-emerald-200 transition"
                    >
                      <Download className="w-3 h-3" />
                      Excel
                    </button>
                    <button
                      onClick={() => handleExport(rep.report_code, 'pdf')}
                      className="flex items-center gap-1 text-[11px] font-bold text-rose-700 bg-rose-50 hover:bg-rose-100 px-2.5 py-1 rounded border border-rose-200 transition"
                    >
                      <Download className="w-3 h-3" />
                      PDF
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Live Data Preview Modal / Drawer */}
          {selectedReport && (
            <Card
              title={`Live Preview: ${selectedReport.report_code} — ${selectedReport.title}`}
              subtitle={`Showing top 25 records generated from PostgreSQL view / tables`}
            >
              <div className="mb-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-xs text-slate-500">Category: <b>{selectedReport.category}</b></span>
                  <span className="text-xs text-slate-500">Columns: <b>{selectedReport.columns?.length || 0}</b></span>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleExport(selectedReport.report_code, 'excel')}
                    className="flex items-center gap-1 text-xs font-bold text-emerald-700 bg-emerald-50 px-3 py-1.5 rounded border border-emerald-200"
                  >
                    <Download className="w-3.5 h-3.5" /> Download Full Excel (.xlsx)
                  </button>
                  <button
                    onClick={() => handleExport(selectedReport.report_code, 'pdf')}
                    className="flex items-center gap-1 text-xs font-bold text-rose-700 bg-rose-50 px-3 py-1.5 rounded border border-rose-200"
                  >
                    <Download className="w-3.5 h-3.5" /> Download Full PDF (.pdf)
                  </button>
                  <button
                    onClick={() => setSelectedReport(null)}
                    className="text-xs font-semibold text-slate-500 hover:text-slate-800 px-2 py-1"
                  >
                    Close
                  </button>
                </div>
              </div>

              {loadingData ? (
                <LoadingSpinner message="Fetching report data..." />
              ) : reportData ? (
                <div className="space-y-4">
                  {/* Summary KPI Cards */}
                  {reportData.kpis && reportData.kpis.length > 0 && (
                    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-3">
                      {reportData.kpis.map((kpi: any, idx: number) => (
                        <div key={idx} className="bg-blue-50/60 p-2.5 rounded-lg border border-blue-100 text-center">
                          <div className="text-[10px] font-bold text-slate-500 uppercase">{kpi.label}</div>
                          <div className="text-base font-extrabold text-blue-900 mt-0.5">{kpi.value}</div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Data Table */}
                  <div className="overflow-x-auto max-h-[400px]">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-slate-100 text-slate-700 font-bold sticky top-0">
                        <tr>
                          {selectedReport.columns.map((col: any) => (
                            <th key={col.key} className={`p-2.5 ${col.align === 'right' ? 'text-right' : col.align === 'center' ? 'text-center' : 'text-left'}`}>
                              {col.label}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {reportData.data.map((row: any, rIdx: number) => (
                          <tr key={rIdx} className="hover:bg-slate-50">
                            {selectedReport.columns.map((col: any) => (
                              <td key={col.key} className={`p-2.5 ${col.align === 'right' ? 'text-right font-mono' : col.align === 'center' ? 'text-center font-mono' : 'text-left'}`}>
                                {col.type === 'currency' && row[col.key] != null
                                  ? `₹${Number(row[col.key]).toLocaleString('en-IN')}`
                                  : col.type === 'percent' && row[col.key] != null
                                  ? `${Number(row[col.key]).toFixed(1)}%`
                                  : String(row[col.key] ?? '-')}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ) : null}
            </Card>
          )}
        </div>
      ) : activeTab === 'hierarchy' ? (
        <Card title="Recursive Asset Hierarchy (vw_AssetHierarchyCTE)" subtitle="Self-referencing CTE navigating Property → Building → Unit">
          <div className="divide-y divide-slate-100 max-h-[600px] overflow-y-auto">
            {hierarchy.map((node) => (
              <div
                key={node.node_id}
                style={{ paddingLeft: `${node.depth_level * 24}px` }}
                className="py-2 flex items-center gap-2 text-xs hover:bg-slate-50 rounded"
              >
                <span className="font-mono text-slate-400 text-[10px]">L{node.depth_level}</span>
                <span
                  className={`font-mono text-[10px] font-bold px-1.5 py-0.5 rounded ${
                    node.node_type === 'PROPERTY'
                      ? 'bg-emerald-100 text-emerald-800'
                      : node.node_type === 'BUILDING'
                      ? 'bg-sky-100 text-sky-800'
                      : 'bg-purple-100 text-purple-800'
                  }`}
                >
                  {node.node_type}
                </span>
                <span className="font-bold text-slate-900">{node.node_name}</span>
                <span className="text-slate-400 font-mono text-[11px] truncate">{node.hierarchy_path}</span>
              </div>
            ))}
          </div>
        </Card>
      ) : activeTab === 'pivot' ? (
        <Card title="12-Month Cross-Tabulated Collections (vw_MonthlyRentCollectionPivot)" subtitle="PIVOT matrix aggregating monthly revenue per property">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-slate-100 text-slate-700 font-bold font-sans">
                <tr>
                  <th className="p-2.5">Code</th>
                  <th className="p-2.5">Property</th>
                  <th className="p-2 text-right">Jan</th>
                  <th className="p-2 text-right">Feb</th>
                  <th className="p-2 text-right">Mar</th>
                  <th className="p-2 text-right">Apr</th>
                  <th className="p-2 text-right">May</th>
                  <th className="p-2 text-right">Jun</th>
                  <th className="p-2 text-right">Jul</th>
                  <th className="p-2 text-right">Aug</th>
                  <th className="p-2 text-right">Sep</th>
                  <th className="p-2 text-right">Oct</th>
                  <th className="p-2 text-right">Nov</th>
                  <th className="p-2 text-right">Dec</th>
                  <th className="p-2.5 text-right font-sans">Total Annual</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {rentPivot.map((p, i) => (
                  <tr key={i} className="hover:bg-slate-50">
                    <td className="p-2.5 font-sans font-bold text-slate-900">{p.property_code}</td>
                    <td className="p-2.5 font-sans font-medium text-slate-900 truncate max-w-xs">{p.property_name}</td>
                    <td className="p-2 text-right">₹{Number(p.jan_collected).toLocaleString('en-IN')}</td>
                    <td className="p-2 text-right">₹{Number(p.feb_collected).toLocaleString('en-IN')}</td>
                    <td className="p-2 text-right">₹{Number(p.mar_collected).toLocaleString('en-IN')}</td>
                    <td className="p-2 text-right">₹{Number(p.apr_collected).toLocaleString('en-IN')}</td>
                    <td className="p-2 text-right">₹{Number(p.may_collected).toLocaleString('en-IN')}</td>
                    <td className="p-2 text-right">₹{Number(p.jun_collected).toLocaleString('en-IN')}</td>
                    <td className="p-2 text-right">₹{Number(p.jul_collected).toLocaleString('en-IN')}</td>
                    <td className="p-2 text-right">₹{Number(p.aug_collected).toLocaleString('en-IN')}</td>
                    <td className="p-2 text-right">₹{Number(p.sep_collected).toLocaleString('en-IN')}</td>
                    <td className="p-2 text-right">₹{Number(p.oct_collected).toLocaleString('en-IN')}</td>
                    <td className="p-2 text-right">₹{Number(p.nov_collected).toLocaleString('en-IN')}</td>
                    <td className="p-2 text-right">₹{Number(p.dec_collected).toLocaleString('en-IN')}</td>
                    <td className="p-2.5 text-right font-bold text-emerald-800">
                      ₹{Number(p.annual_total_collected).toLocaleString('en-IN')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      ) : (
        <Card title="Multi-Tier Occupancy Rollups (vw_PropertyOccupancy)" subtitle="Real-time occupancy percentages calculated across units">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-100 text-slate-700 font-bold">
                <tr>
                  <th className="p-3">Property</th>
                  <th className="p-3 text-right">Total Units</th>
                  <th className="p-3 text-right">Occupied Units</th>
                  <th className="p-3 text-right">Vacant Units</th>
                  <th className="p-3 text-right">Under Maintenance</th>
                  <th className="p-3 text-right">Occupancy Rate</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {occupancy.map((o, idx) => (
                  <tr key={idx} className="hover:bg-slate-50">
                    <td className="p-3 font-bold text-slate-900">{o.property_name}</td>
                    <td className="p-3 text-right font-mono">{o.total_units}</td>
                    <td className="p-3 text-right font-mono font-bold text-emerald-700">{o.occupied_units}</td>
                    <td className="p-3 text-right font-mono text-slate-500">{o.vacant_units}</td>
                    <td className="p-3 text-right font-mono text-amber-700">{o.under_maintenance_units}</td>
                    <td className="p-3 text-right font-bold text-slate-900">
                      {Number(o.occupancy_rate_pct).toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
};
