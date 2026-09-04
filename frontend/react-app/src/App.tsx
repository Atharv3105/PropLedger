import React, { useState } from 'react';
import { AppLayout } from './components/layout/AppLayout';
import { DashboardPage } from './pages/DashboardPage';
import { PropertiesPage } from './pages/PropertiesPage';
import { TenantsPage } from './pages/TenantsPage';
import { LeasesPage } from './pages/LeasesPage';
import { PaymentsPage } from './pages/PaymentsPage';
import { CollectionsPage } from './pages/CollectionsPage';
import { MaintenancePage } from './pages/MaintenancePage';
import { FinancePage } from './pages/FinancePage';
import { ReportsPage } from './pages/ReportsPage';
import { DiagnosticsPage } from './pages/DiagnosticsPage';
import { useAuth } from './context/AuthContext';
import { LoadingSpinner } from './components/common/LoadingSpinner';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const { isLoading, token } = useAuth();

  const titles: Record<string, string> = {
    dashboard: 'Executive Dashboard & Live Analytics',
    properties: 'Properties & Unit Asset Management',
    tenants: 'Tenant Records & Balances',
    leases: 'Lease Lineage & Renewals',
    payments: 'FIFO Payment Allocations & Rent Billing',
    collections: 'Delinquency Aging & Collections',
    maintenance: 'Maintenance Requests & Work Orders',
    finance: 'Property Income, Expenses & P&L',
    reports: 'Analytical Reports & CTE Hierarchy',
    diagnostics: 'System Health & Engine Diagnostics',
  };

  if (isLoading || !token) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center text-slate-200">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-500 flex items-center justify-center font-black text-slate-950 text-2xl shadow-lg shadow-emerald-500/30 animate-pulse">
            PL
          </div>
          <LoadingSpinner message="Authenticating session and establishing database security context..." />
        </div>
      </div>
    );
  }

  const renderPage = () => {
    switch (activeTab) {
      case 'dashboard':
        return <DashboardPage onNavigate={setActiveTab} />;
      case 'properties':
        return <PropertiesPage />;
      case 'tenants':
        return <TenantsPage />;
      case 'leases':
        return <LeasesPage />;
      case 'payments':
        return <PaymentsPage />;
      case 'collections':
        return <CollectionsPage />;
      case 'maintenance':
        return <MaintenancePage />;
      case 'finance':
        return <FinancePage />;
      case 'reports':
        return <ReportsPage />;
      case 'diagnostics':
        return <DiagnosticsPage />;
      default:
        return <DashboardPage onNavigate={setActiveTab} />;
    }
  };

  return (
    <AppLayout
      title={titles[activeTab] || 'PropLedger Platform'}
      activeTab={activeTab}
      onSelectTab={setActiveTab}
    >
      {renderPage()}
    </AppLayout>
  );
};

export default App;
