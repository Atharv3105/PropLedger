import React, { useEffect, useState } from 'react';
import { leasesApi } from '../services/api';
import { ActiveLease } from '../types';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Modal } from '../components/common/Modal';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { FileText, Calendar, RefreshCw, CheckCircle2, ArrowRight } from 'lucide-react';

export const LeasesPage: React.FC = () => {
  const [leases, setLeases] = useState<ActiveLease[]>([]);
  const [loading, setLoading] = useState(true);

  // Renewal Modal
  const [renewLease, setRenewLease] = useState<ActiveLease | null>(null);
  const [newStartDate, setNewStartDate] = useState('');
  const [newEndDate, setNewEndDate] = useState('');
  const [newRent, setNewRent] = useState<number>(0);
  const [submitting, setSubmitting] = useState(false);
  const [renewalSuccess, setRenewalSuccess] = useState<string | null>(null);

  const fetchLeases = () => {
    setLoading(true);
    leasesApi
      .listActive(100)
      .then(setLeases)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchLeases();
  }, []);

  const handleOpenRenew = (l: ActiveLease) => {
    setRenewLease(l);
    setNewStartDate(l.end_date);
    // 1 year forward
    const nextYear = new Date(l.end_date);
    nextYear.setFullYear(nextYear.getFullYear() + 1);
    setNewEndDate(nextYear.toISOString().split('T')[0]);
    // 5% increase
    setNewRent(Math.round(Number(l.monthly_rent) * 1.05));
    setRenewalSuccess(null);
  };

  const handleExecuteRenewal = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!renewLease) return;
    setSubmitting(true);
    try {
      const res = await leasesApi.renew(renewLease.lease_id, {
        new_start_date: newStartDate,
        new_end_date: newEndDate,
        new_monthly_rent: newRent,
      });
      setRenewalSuccess(res.message);
      fetchLeases();
    } catch (err: any) {
      alert(`Renewal failed: ${err?.response?.data?.detail || err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Leases & Predecessor Lineage</h2>
          <p className="text-xs text-slate-500">
            Active leases with self-joined predecessor history from vw_ActiveLeases
          </p>
        </div>
      </div>

      {loading ? (
        <LoadingSpinner message="Querying active leases..." />
      ) : (
        <Card className="p-0 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-100 text-slate-700 font-bold border-b border-slate-200">
                <tr>
                  <th className="p-3">Lease #</th>
                  <th className="p-3">Property & Unit</th>
                  <th className="p-3">Primary Tenant</th>
                  <th className="p-3">Term Period</th>
                  <th className="p-3 text-right">Monthly Rent</th>
                  <th className="p-3 text-right">Deposit</th>
                  <th className="p-3">Renewal Status</th>
                  <th className="p-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {leases.map((l) => (
                  <tr key={l.lease_id} className="hover:bg-slate-50/70">
                    <td className="p-3 font-mono font-bold text-slate-900">{l.lease_number}</td>
                    <td className="p-3">
                      <div className="font-bold text-slate-900">{l.property_name}</div>
                      <div className="text-[11px] text-slate-500">{l.building_name} • Unit {l.unit_number}</div>
                    </td>
                    <td className="p-3">
                      <div className="font-bold text-slate-900">{l.primary_tenant_name}</div>
                      <div className="text-[11px] text-slate-500">{l.primary_tenant_email}</div>
                    </td>
                    <td className="p-3 text-slate-600 font-mono">
                      {l.start_date} <ArrowRight className="w-3 h-3 inline text-slate-400 mx-1" /> {l.end_date}
                    </td>
                    <td className="p-3 text-right font-bold text-slate-900">
                      ₹{Number(l.monthly_rent).toLocaleString('en-IN')}
                    </td>
                    <td className="p-3 text-right text-slate-600 font-mono">
                      ₹{Number(l.security_deposit).toLocaleString('en-IN')}
                    </td>
                    <td className="p-3">
                      {l.is_renewal ? (
                        <Badge variant="purple">
                          RENEWED (#{l.predecessor_lease_id})
                        </Badge>
                      ) : (
                        <Badge variant="success">ORIGINAL</Badge>
                      )}
                    </td>
                    <td className="p-3 text-right">
                      <button
                        onClick={() => handleOpenRenew(l)}
                        className="px-2.5 py-1 bg-brand-50 hover:bg-brand-100 text-brand-700 rounded font-semibold text-xs transition border border-brand-200 inline-flex items-center gap-1"
                      >
                        <RefreshCw className="w-3 h-3" /> Renew Term
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Lease Renewal Modal */}
      <Modal
        isOpen={!!renewLease}
        onClose={() => setRenewLease(null)}
        title={`Renew Lease ${renewLease?.lease_number}`}
        subtitle="Invokes usp_RenewLease: links predecessor lease and rolls security deposit (Rule BR-02)"
      >
        {renewalSuccess ? (
          <div className="text-center py-6 space-y-3">
            <CheckCircle2 className="w-12 h-12 text-emerald-600 mx-auto" />
            <h4 className="text-base font-bold text-slate-900">Lease Renewal Successful!</h4>
            <p className="text-xs text-slate-600">{renewalSuccess}</p>
            <button
              onClick={() => setRenewLease(null)}
              className="px-4 py-2 bg-emerald-600 text-white rounded-lg font-bold text-xs mt-2"
            >
              Close
            </button>
          </div>
        ) : (
          <form onSubmit={handleExecuteRenewal} className="space-y-4 text-xs">
            <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
              <span className="text-slate-500">Current Lease Terms:</span>
              <p className="font-bold text-slate-900 mt-1">
                Unit {renewLease?.unit_number} • ₹{Number(renewLease?.monthly_rent).toLocaleString('en-IN')}/mo • Expires: {renewLease?.end_date}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-slate-600 font-bold mb-1">New Start Date</label>
                <input
                  type="date"
                  required
                  value={newStartDate}
                  onChange={(e) => setNewStartDate(e.target.value)}
                  className="w-full border border-slate-200 rounded-lg p-2 focus:ring-2 focus:ring-brand-500 font-mono"
                />
              </div>
              <div>
                <label className="block text-slate-600 font-bold mb-1">New End Date</label>
                <input
                  type="date"
                  required
                  value={newEndDate}
                  onChange={(e) => setNewEndDate(e.target.value)}
                  className="w-full border border-slate-200 rounded-lg p-2 focus:ring-2 focus:ring-brand-500 font-mono"
                />
              </div>
            </div>

            <div>
              <label className="block text-slate-600 font-bold mb-1">Renewed Monthly Rent (₹)</label>
              <input
                type="number"
                min="1000"
                step="500"
                required
                value={newRent}
                onChange={(e) => setNewRent(Number(e.target.value))}
                className="w-full border border-slate-200 rounded-lg p-2 focus:ring-2 focus:ring-brand-500 font-bold text-slate-900"
              />
              <span className="text-[10px] text-slate-400 mt-0.5">Rule BR-02: Start date must precede end date. Deposit will roll over automatically.</span>
            </div>

            <div className="flex justify-end gap-2 pt-3 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setRenewLease(null)}
                className="px-4 py-2 border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-bold transition disabled:opacity-50"
              >
                {submitting ? 'Executing usp_RenewLease...' : 'Confirm Renewal Term'}
              </button>
            </div>
          </form>
        )}
      </Modal>
    </div>
  );
};
