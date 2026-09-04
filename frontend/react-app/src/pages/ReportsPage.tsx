import React, { useEffect, useState } from 'react';
import { reportsApi } from '../services/api';
import { HierarchyNode, RentPivot, PropertyOccupancy } from '../types';
import { Card } from '../components/common/Card';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { GitBranch, Table, PieChart } from 'lucide-react';

export const ReportsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'hierarchy' | 'pivot' | 'occupancy'>('hierarchy');
  const [hierarchy, setHierarchy] = useState<HierarchyNode[]>([]);
  const [rentPivot, setRentPivot] = useState<RentPivot[]>([]);
  const [occupancy, setOccupancy] = useState<PropertyOccupancy[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      reportsApi.getHierarchy(4),
      reportsApi.getRentPivot(50),
      reportsApi.getOccupancy(),
    ])
      .then(([hier, pvt, occ]) => {
        setHierarchy(hier);
        setRentPivot(pvt);
        setOccupancy(occ);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Advanced SQL Analytical Reports</h2>
          <p className="text-xs text-slate-500">
            Recursive CTEs, Monthly PIVOT matrices, and multi-tier occupancy rollups
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-lg border border-slate-200">
          <button
            onClick={() => setActiveTab('hierarchy')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-bold transition ${
              activeTab === 'hierarchy' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            <GitBranch className="w-3.5 h-3.5 text-emerald-600" />
            Asset Hierarchy (CTE)
          </button>
          <button
            onClick={() => setActiveTab('pivot')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-bold transition ${
              activeTab === 'pivot' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            <Table className="w-3.5 h-3.5 text-sky-600" />
            Monthly Rent Pivot
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
        <LoadingSpinner message="Querying advanced SQL reporting views..." />
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
