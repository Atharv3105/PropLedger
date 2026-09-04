import React, { useEffect, useState } from 'react';
import { Card } from '../components/common/Card';
import { MonthlyRentChart } from '../components/charts/MonthlyRentChart';
import { DelinquencyAgingChart } from '../components/charts/DelinquencyAgingChart';
import { OccupancyDonut } from '../components/charts/OccupancyDonut';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { propertiesApi, reportsApi, collectionsApi, maintenanceApi, financeApi } from '../services/api';
import { Property, PropertyOccupancy, RentPivot, DelinquencyItem, MaintenanceRequest, FinancialSummary } from '../types';
import { Building2, Home, Percent, AlertCircle, Wrench, IndianRupee, TrendingUp, ShieldCheck } from 'lucide-react';

export const DashboardPage: React.FC<{ onNavigate: (tab: string) => void }> = ({ onNavigate }) => {
  const [loading, setLoading] = useState(true);
  const [properties, setProperties] = useState<Property[]>([]);
  const [occupancy, setOccupancy] = useState<PropertyOccupancy[]>([]);
  const [rentPivot, setRentPivot] = useState<RentPivot[]>([]);
  const [delinquencies, setDelinquencies] = useState<DelinquencyItem[]>([]);
  const [maintenance, setMaintenance] = useState<MaintenanceRequest[]>([]);
  const [financials, setFinancials] = useState<FinancialSummary[]>([]);

  useEffect(() => {
    Promise.all([
      propertiesApi.list(100),
      reportsApi.getOccupancy(),
      reportsApi.getRentPivot(50),
      collectionsApi.listDelinquent(),
      maintenanceApi.list(100),
      financeApi.getSummaries(),
    ])
      .then(([props, occ, pvt, del, maint, fin]) => {
        setProperties(props);
        setOccupancy(occ);
        setRentPivot(pvt);
        setDelinquencies(del);
        setMaintenance(maint);
        setFinancials(fin);
      })
      .catch((err) => console.error('Dashboard fetch failed', err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner message="Calculating authoritative portfolio analytics..." />;

  // Authoritative calculations from database datasets
  const totalProperties = properties.length;
  const totalUnits = properties.reduce((sum, p) => sum + (p.total_units || 0), 0);
  const totalOccupied = occupancy.reduce((sum, o) => sum + Number(o.occupied_units || 0), 0);
  const totalVacant = occupancy.reduce((sum, o) => sum + Number(o.vacant_units || 0), 0);
  const avgOccupancyRate = totalUnits > 0 ? (totalOccupied / totalUnits) * 100 : 0;
  
  const totalDelinquentBalance = delinquencies.reduce((sum, d) => sum + Number(d.total_delinquent_balance || 0), 0);
  const openMaintenanceCount = maintenance.filter((m) => m.status !== 'CLOSED').length;
  
  const totalRevenueCollected = financials.reduce((sum, f) => sum + Number(f.total_collected_rent || 0), 0);
  const totalNOI = financials.reduce((sum, f) => sum + Number(f.net_operating_income || 0), 0);

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 rounded-2xl p-6 text-white shadow-lg border border-slate-700">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-emerald-400 text-xs font-bold uppercase tracking-wider mb-1">
              <ShieldCheck className="w-4 h-4" /> Live Portfolio Intelligence
            </div>
            <h1 className="text-2xl font-black tracking-tight">Executive Property Operations & Analytics</h1>
            <p className="text-slate-300 text-xs mt-1 max-w-2xl">
              Strictly synchronized with PostgreSQL 16 stored procedures, analytical CTEs, and FIFO transactional ledgers.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => onNavigate('payments')}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold transition shadow-sm"
            >
              + Record Payment
            </button>
            <button
              onClick={() => onNavigate('leases')}
              className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-xs font-bold transition border border-slate-600"
            >
              Manage Leases
            </button>
          </div>
        </div>
      </div>

      {/* KPI Grid (8 Cards) */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="hover:shadow-md transition border-l-4 border-l-emerald-500">
          <div className="flex items-center justify-between text-slate-500 text-xs font-semibold">
            <span>Total Properties</span>
            <Building2 className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="mt-2 text-2xl font-black text-slate-900">{totalProperties.toLocaleString()}</div>
          <div className="text-[11px] text-slate-400 mt-1">Across residential & commercial</div>
        </Card>

        <Card className="hover:shadow-md transition border-l-4 border-l-sky-500">
          <div className="flex items-center justify-between text-slate-500 text-xs font-semibold">
            <span>Total Units Inventory</span>
            <Home className="w-4 h-4 text-sky-600" />
          </div>
          <div className="mt-2 text-2xl font-black text-slate-900">{totalUnits.toLocaleString()}</div>
          <div className="text-[11px] text-slate-400 mt-1">{totalOccupied.toLocaleString()} active tenants</div>
        </Card>

        <Card className="hover:shadow-md transition border-l-4 border-l-indigo-500">
          <div className="flex items-center justify-between text-slate-500 text-xs font-semibold">
            <span>Portfolio Occupancy</span>
            <Percent className="w-4 h-4 text-indigo-600" />
          </div>
          <div className="mt-2 text-2xl font-black text-slate-900">{avgOccupancyRate.toFixed(1)}%</div>
          <div className="text-[11px] text-slate-400 mt-1">Target threshold: 92.0%</div>
        </Card>

        <Card className="hover:shadow-md transition border-l-4 border-l-rose-500">
          <div className="flex items-center justify-between text-slate-500 text-xs font-semibold">
            <span>Delinquent Balance</span>
            <AlertCircle className="w-4 h-4 text-rose-600" />
          </div>
          <div className="mt-2 text-2xl font-black text-rose-700">
            ₹{(totalDelinquentBalance / 100000).toFixed(2)} Lakhs
          </div>
          <div className="text-[11px] text-rose-500 font-semibold mt-1">
            {delinquencies.length} accounts overdue
          </div>
        </Card>

        <Card className="hover:shadow-md transition border-l-4 border-l-emerald-600">
          <div className="flex items-center justify-between text-slate-500 text-xs font-semibold">
            <span>YTD Revenue Collected</span>
            <IndianRupee className="w-4 h-4 text-emerald-700" />
          </div>
          <div className="mt-2 text-2xl font-black text-emerald-800">
            ₹{(totalRevenueCollected / 100000).toFixed(2)} Lakhs
          </div>
          <div className="text-[11px] text-slate-400 mt-1">From vw_PropertyFinancialSummary</div>
        </Card>

        <Card className="hover:shadow-md transition border-l-4 border-l-teal-500">
          <div className="flex items-center justify-between text-slate-500 text-xs font-semibold">
            <span>Net Operating Income (NOI)</span>
            <TrendingUp className="w-4 h-4 text-teal-600" />
          </div>
          <div className="mt-2 text-2xl font-black text-teal-800">
            ₹{(totalNOI / 100000).toFixed(2)} Lakhs
          </div>
          <div className="text-[11px] text-slate-400 mt-1">Revenue minus operating expenses</div>
        </Card>

        <Card className="hover:shadow-md transition border-l-4 border-l-amber-500">
          <div className="flex items-center justify-between text-slate-500 text-xs font-semibold">
            <span>Open Maintenance</span>
            <Wrench className="w-4 h-4 text-amber-600" />
          </div>
          <div className="mt-2 text-2xl font-black text-slate-900">{openMaintenanceCount}</div>
          <div className="text-[11px] text-slate-400 mt-1">Active tickets requiring dispatch</div>
        </Card>

        <Card className="hover:shadow-md transition border-l-4 border-l-purple-500">
          <div className="flex items-center justify-between text-slate-500 text-xs font-semibold">
            <span>Data Source</span>
            <ShieldCheck className="w-4 h-4 text-purple-600" />
          </div>
          <div className="mt-2 text-xl font-bold text-slate-900">PostgreSQL 16</div>
          <div className="text-[11px] text-purple-700 font-semibold mt-1">Pure SQL Stored Procedures</div>
        </Card>
      </div>

      {/* Analytics Visualizers Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 12-Month Rent Collection Trend */}
        <Card
          title="12-Month Rent Collection Trend"
          subtitle="Cross-tabulated monthly collections from vw_MonthlyRentCollectionPivot"
          className="lg:col-span-2"
        >
          <MonthlyRentChart data={rentPivot} />
        </Card>

        {/* Occupancy Donut */}
        <Card title="Occupancy Distribution" subtitle="Aggregated from vw_PropertyOccupancy">
          <OccupancyDonut
            rate={avgOccupancyRate}
            total={totalUnits}
            occupied={totalOccupied}
            vacant={totalVacant}
          />
        </Card>
      </div>

      {/* Delinquency & Quick Workflows Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Delinquency Aging Matrix */}
        <Card
          title="Delinquency Aging Buckets (Rule BR-06)"
          subtitle="Real-time aging breakdown from usp_GetDelinquencyReport"
          action={
            <button
              onClick={() => onNavigate('collections')}
              className="text-xs font-bold text-emerald-600 hover:text-emerald-700"
            >
              View Full Aging →
            </button>
          }
        >
          <DelinquencyAgingChart data={delinquencies} />
        </Card>

        {/* Quick Domain Navigation Hub */}
        <Card title="Operational Workflow Center" subtitle="Direct access to verified core business engines">
          <div className="grid grid-cols-2 gap-3 pt-2">
            <button
              onClick={() => onNavigate('leases')}
              className="p-3 bg-slate-50 hover:bg-emerald-50/60 border border-slate-200 hover:border-emerald-300 rounded-xl text-left transition group"
            >
              <div className="font-bold text-xs text-slate-900 group-hover:text-emerald-700">Lease Renewals</div>
              <div className="text-[11px] text-slate-500 mt-0.5">Executes usp_RenewLease with deposit rollover</div>
            </button>

            <button
              onClick={() => onNavigate('payments')}
              className="p-3 bg-slate-50 hover:bg-emerald-50/60 border border-slate-200 hover:border-emerald-300 rounded-xl text-left transition group"
            >
              <div className="font-bold text-xs text-slate-900 group-hover:text-emerald-700">FIFO Payment Ledger</div>
              <div className="text-[11px] text-slate-500 mt-0.5">Executes usp_RecordPayment with balance updates</div>
            </button>

            <button
              onClick={() => onNavigate('maintenance')}
              className="p-3 bg-slate-50 hover:bg-emerald-50/60 border border-slate-200 hover:border-emerald-300 rounded-xl text-left transition group"
            >
              <div className="font-bold text-xs text-slate-900 group-hover:text-emerald-700">Maintenance & BR-08</div>
              <div className="text-[11px] text-slate-500 mt-0.5">Audit reopen workflow for closed work tickets</div>
            </button>

            <button
              onClick={() => onNavigate('reports')}
              className="p-3 bg-slate-50 hover:bg-emerald-50/60 border border-slate-200 hover:border-emerald-300 rounded-xl text-left transition group"
            >
              <div className="font-bold text-xs text-slate-900 group-hover:text-emerald-700">Recursive CTE Reports</div>
              <div className="text-[11px] text-slate-500 mt-0.5">Explores vw_AssetHierarchyCTE multi-level rollups</div>
            </button>
          </div>
        </Card>
      </div>
    </div>
  );
};
