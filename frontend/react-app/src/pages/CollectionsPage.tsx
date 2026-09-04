import React, { useEffect, useState } from 'react';
import { collectionsApi } from '../services/api';
import { DelinquencyItem } from '../types';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { Modal } from '../components/common/Modal';
import { AlertCircle, ShieldAlert, ArrowUpRight, CheckCircle2 } from 'lucide-react';

export const CollectionsPage: React.FC = () => {
  const [items, setItems] = useState<DelinquencyItem[]>([]);
  const [loading, setLoading] = useState(true);

  // Escalation modal
  const [escalateItem, setEscalateItem] = useState<DelinquencyItem | null>(null);
  const [notes, setNotes] = useState('Delinquency threshold breach - escalated via Operations Portal');
  const [submitting, setSubmitting] = useState(false);
  const [escalateSuccess, setEscalateSuccess] = useState<string | null>(null);

  const fetchDelinquency = () => {
    setLoading(true);
    collectionsApi
      .listDelinquent()
      .then(setItems)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchDelinquency();
  }, []);

  const handleEscalate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!escalateItem) return;
    setSubmitting(true);
    try {
      const res = await collectionsApi.escalate({
        tenant_id: escalateItem.tenant_id,
        lease_id: escalateItem.lease_id,
        case_notes: notes,
      });
      setEscalateSuccess(`Case #${res.collection_case_id} established: ${res.message}`);
      fetchDelinquency();
    } catch (err: any) {
      alert(`Escalation error: ${err?.response?.data?.detail || err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-xl font-bold text-slate-900">Delinquency Aging & Collection Escalations</h2>
        <p className="text-xs text-slate-500">
          Aging categories (0-30, 31-60, 61-90, 90+ days) and escalation workflow to collection_cases
        </p>
      </div>

      {loading ? (
        <LoadingSpinner message="Evaluating accounts past grace period..." />
      ) : (
        <Card className="p-0 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-100 text-slate-700 font-bold border-b border-slate-200">
                <tr>
                  <th className="p-3">Tenant Name</th>
                  <th className="p-3">Property / Unit</th>
                  <th className="p-3 text-right">0–30 Days</th>
                  <th className="p-3 text-right">31–60 Days</th>
                  <th className="p-3 text-right">61–90 Days</th>
                  <th className="p-3 text-right text-rose-600">90+ Days</th>
                  <th className="p-3 text-right">Total Overdue</th>
                  <th className="p-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {items.map((item, i) => (
                  <tr key={i} className="hover:bg-slate-50/70">
                    <td className="p-3 font-bold text-slate-900">{item.tenant_name}</td>
                    <td className="p-3 text-slate-600">
                      {item.property_name} • Unit {item.unit_number}
                    </td>
                    <td className="p-3 text-right font-mono text-slate-600">
                      ₹{Number(item.current_0_30).toLocaleString('en-IN')}
                    </td>
                    <td className="p-3 text-right font-mono text-amber-700">
                      ₹{Number(item.past_due_31_60).toLocaleString('en-IN')}
                    </td>
                    <td className="p-3 text-right font-mono text-orange-700">
                      ₹{Number(item.past_due_61_90).toLocaleString('en-IN')}
                    </td>
                    <td className="p-3 text-right font-mono font-bold text-rose-600">
                      ₹{Number(item.severe_90_plus).toLocaleString('en-IN')}
                    </td>
                    <td className="p-3 text-right font-bold text-slate-900">
                      ₹{Number(item.total_delinquent_balance).toLocaleString('en-IN')}
                    </td>
                    <td className="p-3 text-right">
                      <button
                        onClick={() => {
                          setEscalateItem(item);
                          setEscalateSuccess(null);
                        }}
                        className="px-2.5 py-1 bg-rose-50 hover:bg-rose-100 text-rose-700 rounded font-semibold text-xs border border-rose-200 inline-flex items-center gap-1"
                      >
                        <ShieldAlert className="w-3 h-3" /> Escalate
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Escalation Modal */}
      <Modal
        isOpen={!!escalateItem}
        onClose={() => setEscalateItem(null)}
        title={`Escalate Account: ${escalateItem?.tenant_name}`}
        subtitle={`Lease #${escalateItem?.lease_id} • Total Due: ₹${Number(escalateItem?.total_delinquent_balance).toLocaleString('en-IN')}`}
      >
        {escalateSuccess ? (
          <div className="text-center py-6 space-y-3">
            <CheckCircle2 className="w-12 h-12 text-emerald-600 mx-auto" />
            <h4 className="text-base font-bold text-slate-900">Account Escalated to Collections</h4>
            <p className="text-xs text-slate-600">{escalateSuccess}</p>
            <button
              onClick={() => setEscalateItem(null)}
              className="px-4 py-2 bg-slate-900 text-white rounded font-bold text-xs"
            >
              Done
            </button>
          </div>
        ) : (
          <form onSubmit={handleEscalate} className="space-y-4 text-xs">
            <div className="bg-rose-50 p-3 rounded-lg border border-rose-200 text-rose-900">
              <span className="font-bold">Severe Delinquency Action:</span>
              <p className="text-[11px] mt-0.5">
                This account will be formally submitted into `collection_cases` and assigned to collection officers.
              </p>
            </div>

            <div>
              <label className="block text-slate-600 font-bold mb-1">Escalation Justification & Notes</label>
              <textarea
                required
                rows={3}
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="w-full border border-slate-200 rounded-lg p-2 focus:ring-2 focus:ring-rose-500"
              />
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setEscalateItem(null)}
                className="px-4 py-2 border border-slate-200 rounded-lg text-slate-600"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting}
                className="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-lg font-bold disabled:opacity-50"
              >
                {submitting ? 'Escalating...' : 'Confirm Escalation'}
              </button>
            </div>
          </form>
        )}
      </Modal>
    </div>
  );
};
