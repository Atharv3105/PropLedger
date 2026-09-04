import React, { useEffect, useState } from 'react';
import { tenantsApi } from '../services/api';
import { Tenant, TenantBalance } from '../types';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { Modal } from '../components/common/Modal';
import { Users, Search, Phone, Mail, Award, CreditCard } from 'lucide-react';

export const TenantsPage: React.FC = () => {
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  // Balance Inspection Drawer
  const [selectedTenant, setSelectedTenant] = useState<Tenant | null>(null);
  const [balance, setBalance] = useState<TenantBalance | null>(null);
  const [loadingBalance, setLoadingBalance] = useState(false);

  useEffect(() => {
    setLoading(true);
    tenantsApi
      .list(100, 0, search)
      .then(setTenants)
      .finally(() => setLoading(false));
  }, [search]);

  const handleInspectBalance = async (t: Tenant) => {
    setSelectedTenant(t);
    setLoadingBalance(true);
    try {
      const b = await tenantsApi.getBalance(t.tenant_id);
      setBalance(b);
    } catch {
      setBalance(null);
    } finally {
      setLoadingBalance(false);
    }
  };

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Tenant Directory & Ledgers</h2>
          <p className="text-xs text-slate-500">Contact information, credit evaluations, and live running balance view</p>
        </div>
        <div className="relative w-72">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
          <input
            type="text"
            placeholder="Search tenant name or email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-white border border-slate-200 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500"
          />
        </div>
      </div>

      {loading ? (
        <LoadingSpinner message="Loading tenant directory..." />
      ) : (
        <Card className="p-0 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-100 text-slate-700 font-bold border-b border-slate-200">
                <tr>
                  <th className="p-3">Tenant ID</th>
                  <th className="p-3">Full Name</th>
                  <th className="p-3">Email</th>
                  <th className="p-3">Phone</th>
                  <th className="p-3">Credit Score</th>
                  <th className="p-3">Status</th>
                  <th className="p-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {tenants.map((t) => (
                  <tr key={t.tenant_id} className="hover:bg-slate-50/70">
                    <td className="p-3 font-mono text-slate-500">#{t.tenant_id}</td>
                    <td className="p-3 font-bold text-slate-900">{t.full_name}</td>
                    <td className="p-3 text-slate-600 flex items-center gap-1.5">
                      <Mail className="w-3 h-3 text-slate-400" /> {t.email}
                    </td>
                    <td className="p-3 text-slate-600 font-mono">
                      <Phone className="w-3 h-3 text-slate-400 inline mr-1" />{t.phone}
                    </td>
                    <td className="p-3">
                      <span className="inline-flex items-center gap-1 font-bold text-slate-800">
                        <Award className="w-3 h-3 text-amber-500" />
                        {t.credit_score || '720'}
                      </span>
                    </td>
                    <td className="p-3">
                      <Badge variant={t.is_active ? 'success' : 'neutral'}>
                        {t.is_active ? 'ACTIVE' : 'INACTIVE'}
                      </Badge>
                    </td>
                    <td className="p-3 text-right">
                      <button
                        onClick={() => handleInspectBalance(t)}
                        className="px-2.5 py-1 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 rounded font-semibold text-xs transition border border-emerald-200"
                      >
                        Ledger Balance →
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Tenant Ledger Modal */}
      <Modal
        isOpen={!!selectedTenant}
        onClose={() => setSelectedTenant(null)}
        title={`${selectedTenant?.full_name} — Ledger Balance`}
        subtitle="Live ledger balance calculated from vw_TenantOutstandingBalance"
      >
        {loadingBalance ? (
          <LoadingSpinner message="Calculating running ledger balance..." />
        ) : balance ? (
          <div className="space-y-4 text-xs">
            <div className="grid grid-cols-2 gap-3 bg-slate-50 p-4 rounded-xl border border-slate-200">
              <div>
                <span className="text-slate-500">Property:</span>
                <p className="font-bold text-slate-900 text-sm mt-0.5">{balance.property_name}</p>
              </div>
              <div>
                <span className="text-slate-500">Unit:</span>
                <p className="font-bold text-slate-900 text-sm mt-0.5">{balance.unit_number}</p>
              </div>
              <div>
                <span className="text-slate-500">Active Lease ID:</span>
                <p className="font-bold font-mono text-slate-900 mt-0.5">#{balance.lease_id}</p>
              </div>
              <div>
                <span className="text-slate-500">Lease Status:</span>
                <p className="font-bold text-emerald-700 mt-0.5">{balance.lease_status}</p>
              </div>
            </div>

            <div className="space-y-2 pt-2">
              <div className="flex justify-between py-2 border-b border-slate-100">
                <span className="text-slate-600">Total Billed Rent:</span>
                <span className="font-bold text-slate-900">₹{Number(balance.total_billed).toLocaleString('en-IN')}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-slate-100">
                <span className="text-slate-600">Total Payments Recorded:</span>
                <span className="font-bold text-emerald-700">-₹{Number(balance.total_paid).toLocaleString('en-IN')}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-slate-100">
                <span className="text-slate-600">Late Fees Assessed:</span>
                <span className="font-bold text-amber-700">+₹{Number(balance.total_late_fees).toLocaleString('en-IN')}</span>
              </div>
              <div className="flex justify-between py-3 bg-slate-100 px-3 rounded-lg text-sm font-black">
                <span>Current Outstanding Balance:</span>
                <span className={Number(balance.outstanding_balance) > 0 ? 'text-rose-600' : 'text-emerald-700'}>
                  ₹{Number(balance.outstanding_balance).toLocaleString('en-IN')}
                </span>
              </div>
            </div>
          </div>
        ) : (
          <div className="py-6 text-center text-slate-400">
            No active billing history found for this tenant.
          </div>
        )}
      </Modal>
    </div>
  );
};
