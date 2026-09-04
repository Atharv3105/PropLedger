import React, { useEffect, useState } from 'react';
import { Card } from '../components/common/Card';
import { MonthlyRentChart } from '../components/charts/MonthlyRentChart';
import { DelinquencyAgingChart } from '../components/charts/DelinquencyAgingChart';
import { OccupancyDonut } from '../components/charts/OccupancyDonut';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { propertiesApi, reportsApi, collectionsApi, maintenanceApi, financeApi } from '../services/api';
import { Property, PropertyOccupancy, RentPivot, DelinquencyItem, MaintenanceRequest, FinancialSummary } from '../types';
import {
  Building2, Home, Percent, AlertCircle, Wrench, IndianRupee,
  TrendingUp, ShieldCheck, Users, FileText, CreditCard
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const DashboardPage: React.FC<{ onNavigate: (tab: string) => void }> = ({ onNavigate }) => {
  const { currentRole, user, token, hasRole } = useAuth();
  const [loading, setLoading] = useState(true);
  const [properties, setProperties] = useState<Property[]>([]);
  const [occupancy, setOccupancy] = useState<PropertyOccupancy[]>([]);
  const [rentPivot, setRentPivot] = useState<RentPivot[]>([]);
  const [delinquencies, setDelinquencies] = useState<DelinquencyItem[]>([]);
  const [maintenance, setMaintenance] = useState<MaintenanceRequest[]>([]);
  const [financials, setFinancials] = useState<FinancialSummary[]>([]);

  const isManagement = hasRole(['ADMIN', 'PROPERTY_MANAGER', 'ACCOUNTANT', 'OWNER']);

  useEffect(() => {
    if (!token) return;

    if (!isManagement) {
      setLoading(false);
      return;
    }

    setLoading(true);
    Promise.allSettled([
      propertiesApi.list(100),
      reportsApi.getOccupancy(),
      reportsApi.getRentPivot(50),
      collectionsApi.listDelinquent(),
      maintenanceApi.list(100),
      financeApi.getSummaries(),
    ])
      .then(([propsRes, occRes, pvtRes, delRes, maintRes, finRes]) => {
        if (propsRes.status === 'fulfilled') setProperties(propsRes.value);
        if (occRes.status === 'fulfilled') setOccupancy(occRes.value);
        if (pvtRes.status === 'fulfilled') setRentPivot(pvtRes.value);
        if (delRes.status === 'fulfilled') setDelinquencies(delRes.value);
        if (maintRes.status === 'fulfilled') setMaintenance(maintRes.value);
        if (finRes.status === 'fulfilled') setFinancials(finRes.value);
      })
      .catch((err) => console.error('Dashboard fetch failed', err))
      .finally(() => setLoading(false));
  }, [currentRole, token]);

  if (loading) return <LoadingSpinner message="Calculating authoritative portfolio analytics..." />;

  // Non-executive role views: Tenant, Maintenance Tech, Leasing Staff
  if (!isManagement) {
    if (currentRole === 'TENANT') {
      return (
        <div className="space-y-6">
          <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 rounded-2xl p-6 text-white shadow-lg border border-slate-700">
            <div className="flex items-center gap-2 text-emerald-400 text-xs font-bold uppercase tracking-wider mb-1">
              <ShieldCheck className="w-4 h-4" /> Resident Portal
            </div>
            <h1 className="text-2xl font-black tracking-tight">
              Welcome, {user?.full_name || 'Resident'}
            </h1>
            <p className="text-slate-300 text-xs mt-1 max-w-2xl">
              Manage your lease details, submit maintenance requests, and pay rent online with FIFO transaction allocation.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card
              title="Online Rent & Payments"
              subtitle="FIFO Transaction Allocation"
              className="hover:shadow-md transition border-t-4 border-t-emerald-500"
            >
              <p className="text-xs text-slate-600 mb-4">
                Execute automated payment allocations with instant credit clearing and receipt generation.
              </p>
              <button
                onClick={() => onNavigate('payments')}
                className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold transition flex items-center justify-center gap-2 cursor-pointer"
              >
                <CreditCard className="w-4 h-4" /> Pay Rent / View Ledger
              </button>
            </Card>

            <Card
              title="Active Lease Agreement"
              subtitle="Terms & Lineage Tracking"
              className="hover:shadow-md transition border-t-4 border-t-sky-500"
            >
              <p className="text-xs text-slate-600 mb-4">
                Review your unit details, lease expiry date, security deposit balance, and renewal options.
              </p>
              <button
                onClick={() => onNavigate('leases')}
                className="w-full py-2.5 bg-sky-600 hover:bg-sky-500 text-white rounded-lg text-xs font-bold transition flex items-center justify-center gap-2 cursor-pointer"
              >
                <FileText className="w-4 h-4" /> View My Lease
              </button>
            </Card>

            <Card
              title="Maintenance & Repairs"
              subtitle="Real-Time Technician Dispatch"
              className="hover:shadow-md transition border-t-4 border-t-amber-500"
            >
              <p className="text-xs text-slate-600 mb-4">
                Report property maintenance issues and track service technician resolution status in real-time.
              </p>
              <button
                onClick={() => onNavigate('maintenance')}
                className="w-full py-2.5 bg-amber-600 hover:bg-amber-500 text-white rounded-lg text-xs font-bold transition flex items-center justify-center gap-2 cursor-pointer"
              >
                <Wrench className="w-4 h-4" /> Maintenance Tickets
              </button>
            </Card>
          </div>
        </div>
      );
    }

    if (currentRole === 'MAINTENANCE_STAFF') {
      return (
        <div className="space-y-6">
          <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 rounded-2xl p-6 text-white shadow-lg border border-slate-700">
            <div className="flex items-center gap-2 text-amber-400 text-xs font-bold uppercase tracking-wider mb-1">
              <Wrench className="w-4 h-4" /> Operations Dispatch
            </div>
            <h1 className="text-2xl font-black tracking-tight">
              Maintenance Field Operations Hub
            </h1>
            <p className="text-slate-300 text-xs mt-1 max-w-2xl">
              Welcome, {user?.full_name || 'Field Technician'}. Review active maintenance tickets, update work orders, and ensure Rule BR-08 reopen audit compliance.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card
              title="Work Order Dispatch"
              subtitle="Active Property Tickets"
              className="hover:shadow-md transition border-t-4 border-t-amber-500"
            >
              <p className="text-xs text-slate-600 mb-4">
                Inspect assigned tenant requests, schedule vendor dispatches, and log resolution notes.
              </p>
              <button
                onClick={() => onNavigate('maintenance')}
                className="w-full py-2.5 bg-amber-600 hover:bg-amber-500 text-white rounded-lg text-xs font-bold transition flex items-center justify-center gap-2 cursor-pointer"
              >
                <Wrench className="w-4 h-4" /> View Open Work Orders
              </button>
            </Card>

            <Card
              title="Rule BR-08 Compliance"
              subtitle="Closed Ticket Reopen Audit"
              className="hover:shadow-md transition border-t-4 border-t-purple-500"
            >
              <p className="text-xs text-slate-600 mb-4">
                Enforces strict database trigger security: closed work tickets cannot be silently altered without mandatory audit logging.
              </p>
              <button
                onClick={() => onNavigate('maintenance')}
                className="w-full py-2.5 bg-purple-600 hover:bg-purple-500 text-white rounded-lg text-xs font-bold transition flex items-center justify-center gap-2 cursor-pointer"
              >
                <ShieldCheck className="w-4 h-4" /> Maintenance Module
              </button>
            </Card>
          </div>
        </div>
      );
    }

    if (currentRole === 'LEASING_STAFF') {
      return (
        <div className="space-y-6">
          <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 rounded-2xl p-6 text-white shadow-lg border border-slate-700">
            <div className="flex items-center gap-2 text-sky-400 text-xs font-bold uppercase tracking-wider mb-1">
              <Home className="w-4 h-4" /> Leasing Operations
            </div>
            <h1 className="text-2xl font-black tracking-tight">
              Leasing & Occupancy Portal
            </h1>
            <p className="text-slate-300 text-xs mt-1 max-w-2xl">
              Welcome, {user?.full_name || 'Leasing Agent'}. Track vacant unit inventory, review active leases, and manage tenant onboarding.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card
              title="Properties & Units"
              subtitle="Available Inventory"
              className="hover:shadow-md transition border-t-4 border-t-sky-500"
            >
              <p className="text-xs text-slate-600 mb-4">
                Explore building portfolios, unit specs, and ready-to-lease vacant inventory.
              </p>
              <button
                onClick={() => onNavigate('properties')}
                className="w-full py-2.5 bg-sky-600 hover:bg-sky-500 text-white rounded-lg text-xs font-bold transition flex items-center justify-center gap-2 cursor-pointer"
              >
                <Home className="w-4 h-4" /> Explore Properties
              </button>
            </Card>

            <Card
              title="Leases & Renewals"
              subtitle="Lease Lineage Tracking"
              className="hover:shadow-md transition border-t-4 border-t-emerald-500"
            >
              <p className="text-xs text-slate-600 mb-4">
                Draft agreements, manage expiration dates, and execute lease renewals.
              </p>
              <button
                onClick={() => onNavigate('leases')}
                className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold transition flex items-center justify-center gap-2 cursor-pointer"
              >
                <FileText className="w-4 h-4" /> Manage Leases
              </button>
            </Card>

            <Card
              title="Tenant Directory"
              subtitle="Resident Records"
              className="hover:shadow-md transition border-t-4 border-t-indigo-500"
            >
              <p className="text-xs text-slate-600 mb-4">
                Search verified tenant profiles, contact numbers, and lease associations.
              </p>
              <button
                onClick={() => onNavigate('tenants')}
                className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-bold transition flex items-center justify-center gap-2 cursor-pointer"
              >
                <Users className="w-4 h-4" /> Tenant Directory
              </button>
            </Card>
          </div>
        </div>
      );
    }
  }

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
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold transition shadow-sm cursor-pointer"
            >
              + Record Payment
            </button>
            <button
              onClick={() => onNavigate('leases')}
              className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-xs font-bold transition border border-slate-600 cursor-pointer"
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
              className="text-xs font-bold text-emerald-600 hover:text-emerald-700 cursor-pointer"
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
              className="p-3 bg-slate-50 hover:bg-emerald-50/60 border border-slate-200 hover:border-emerald-300 rounded-xl text-left transition group cursor-pointer"
            >
              <div className="font-bold text-xs text-slate-900 group-hover:text-emerald-700">Lease Renewals</div>
              <div className="text-[11px] text-slate-500 mt-0.5">Executes usp_RenewLease with deposit rollover</div>
            </button>

            <button
              onClick={() => onNavigate('payments')}
              className="p-3 bg-slate-50 hover:bg-emerald-50/60 border border-slate-200 hover:border-emerald-300 rounded-xl text-left transition group cursor-pointer"
            >
              <div className="font-bold text-xs text-slate-900 group-hover:text-emerald-700">FIFO Payment Ledger</div>
              <div className="text-[11px] text-slate-500 mt-0.5">Executes usp_RecordPayment with balance updates</div>
            </button>

            <button
              onClick={() => onNavigate('maintenance')}
              className="p-3 bg-slate-50 hover:bg-emerald-50/60 border border-slate-200 hover:border-emerald-300 rounded-xl text-left transition group cursor-pointer"
            >
              <div className="font-bold text-xs text-slate-900 group-hover:text-emerald-700">Maintenance & BR-08</div>
              <div className="text-[11px] text-slate-500 mt-0.5">Audit reopen workflow for closed work tickets</div>
            </button>

            <button
              onClick={() => onNavigate('reports')}
              className="p-3 bg-slate-50 hover:bg-emerald-50/60 border border-slate-200 hover:border-emerald-300 rounded-xl text-left transition group cursor-pointer"
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
