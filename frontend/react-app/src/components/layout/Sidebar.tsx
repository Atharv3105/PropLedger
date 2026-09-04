import React from 'react';
import {
  Building2, Users, FileText, CreditCard, AlertCircle,
  Wrench, DollarSign, BarChart3, Activity, LayoutDashboard
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { UserRole } from '../../types';

interface NavItem {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  roles: UserRole[];
}

const NAV_ITEMS: NavItem[] = [
  { id: 'dashboard', label: 'Executive Dashboard', icon: LayoutDashboard, roles: ['ADMIN', 'PROPERTY_MANAGER', 'ACCOUNTANT', 'OWNER', 'LEASING_STAFF', 'MAINTENANCE_STAFF', 'TENANT'] },
  { id: 'properties', label: 'Properties & Units', icon: Building2, roles: ['ADMIN', 'PROPERTY_MANAGER', 'ACCOUNTANT', 'OWNER', 'LEASING_STAFF'] },
  { id: 'tenants', label: 'Tenants & Balances', icon: Users, roles: ['ADMIN', 'PROPERTY_MANAGER', 'ACCOUNTANT', 'LEASING_STAFF'] },
  { id: 'leases', label: 'Leases & Renewals', icon: FileText, roles: ['ADMIN', 'PROPERTY_MANAGER', 'LEASING_STAFF'] },
  { id: 'payments', label: 'Payments & FIFO', icon: CreditCard, roles: ['ADMIN', 'ACCOUNTANT', 'TENANT'] },
  { id: 'collections', label: 'Delinquency & Cases', icon: AlertCircle, roles: ['ADMIN', 'PROPERTY_MANAGER', 'ACCOUNTANT'] },
  { id: 'maintenance', label: 'Maintenance Tickets', icon: Wrench, roles: ['ADMIN', 'PROPERTY_MANAGER', 'MAINTENANCE_STAFF', 'TENANT'] },
  { id: 'finance', label: 'P&L & Expenses', icon: DollarSign, roles: ['ADMIN', 'ACCOUNTANT', 'PROPERTY_MANAGER'] },
  { id: 'reports', label: 'Analytical Reports', icon: BarChart3, roles: ['ADMIN', 'PROPERTY_MANAGER', 'ACCOUNTANT', 'OWNER'] },
  { id: 'diagnostics', label: 'System Diagnostics', icon: Activity, roles: ['ADMIN', 'PROPERTY_MANAGER'] },
];

interface SidebarProps {
  activeTab: string;
  onSelectTab: (id: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onSelectTab }) => {
  const { hasRole, currentRole } = useAuth();

  const visibleItems = NAV_ITEMS.filter((item) => hasRole(item.roles));

  return (
    <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col border-r border-slate-800 select-none">
      {/* Brand Header */}
      <div className="h-16 flex items-center gap-3 px-6 border-b border-slate-800/80 bg-slate-950/40">
        <div className="w-9 h-9 rounded-lg bg-emerald-500 flex items-center justify-center font-black text-slate-950 text-xl shadow-md shadow-emerald-500/20">
          PL
        </div>
        <div>
          <h1 className="font-extrabold text-white text-base tracking-tight">PropLedger</h1>
          <p className="text-[10px] text-slate-400 font-mono tracking-wider">ENTERPRISE v1.0</p>
        </div>
      </div>

      {/* Nav Menu */}
      <div className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        <div className="px-3 pb-2 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
          Main Navigation
        </div>
        {visibleItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-semibold transition duration-150 ${
                isActive
                  ? 'bg-emerald-600 text-white shadow-sm'
                  : 'hover:bg-slate-800/70 text-slate-400 hover:text-slate-200'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>

      {/* User Footer */}
      <div className="p-3 border-t border-slate-800 bg-slate-950/30">
        <div className="bg-slate-800/60 rounded-lg p-3">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold text-slate-400 uppercase">Active Role</span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/30">
              {currentRole}
            </span>
          </div>
          <p className="text-xs font-medium text-slate-300 mt-1 truncate">
            {currentRole === 'ADMIN' ? 'admin@propledger.com' : `${currentRole.toLowerCase()}@propledger.com`}
          </p>
        </div>
      </div>
    </aside>
  );
};
