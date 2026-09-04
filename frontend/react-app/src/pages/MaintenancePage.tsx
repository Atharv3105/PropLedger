import React, { useEffect, useState } from 'react';
import { maintenanceApi } from '../services/api';
import { MaintenanceRequest } from '../types';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { Modal } from '../components/common/Modal';
import { Wrench, AlertTriangle, RotateCcw, CheckCircle2 } from 'lucide-react';

export const MaintenancePage: React.FC = () => {
  const [requests, setRequests] = useState<MaintenanceRequest[]>([]);
  const [loading, setLoading] = useState(true);

  // Reopen modal (Rule BR-08)
  const [reopenItem, setReopenItem] = useState<MaintenanceRequest | null>(null);
  const [reopenReason, setReopenReason] = useState('Tenant reported recurring fault after technician signoff');
  const [submitting, setSubmitting] = useState(false);
  const [reopenSuccess, setReopenSuccess] = useState<string | null>(null);

  const fetchRequests = () => {
    setLoading(true);
    maintenanceApi
      .list(100)
      .then(setRequests)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchRequests();
  }, []);

  const handleReopen = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reopenItem) return;
    setSubmitting(true);
    try {
      const res = await maintenanceApi.reopen(reopenItem.request_id, reopenReason);
      setReopenSuccess(res.message);
      fetchRequests();
    } catch (err: any) {
      alert(`Reopen error: ${err?.response?.data?.detail || err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-xl font-bold text-slate-900">Maintenance Tickets & Work Orders</h2>
        <p className="text-xs text-slate-500">
          Ticket lifecycles and Rule BR-08 closed-request reopen guards via usp_ReopenMaintenanceRequest
        </p>
      </div>

      {loading ? (
        <LoadingSpinner message="Querying maintenance tickets..." />
      ) : (
        <Card className="p-0 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-100 text-slate-700 font-bold border-b border-slate-200">
                <tr>
                  <th className="p-3">Ticket #</th>
                  <th className="p-3">Property / Unit</th>
                  <th className="p-3">Category</th>
                  <th className="p-3">Priority</th>
                  <th className="p-3">Description</th>
                  <th className="p-3">Status</th>
                  <th className="p-3 text-right">Rule BR-08 Guard</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {requests.map((r) => (
                  <tr key={r.request_id} className="hover:bg-slate-50/70">
                    <td className="p-3 font-mono font-bold text-slate-900">{r.request_number}</td>
                    <td className="p-3">
                      <div className="font-bold text-slate-900">{r.property_name}</div>
                      <div className="text-[11px] text-slate-500">Unit {r.unit_number}</div>
                    </td>
                    <td className="p-3 font-medium text-slate-700">{r.category}</td>
                    <td className="p-3">
                      <Badge
                        variant={
                          r.priority === 'EMERGENCY' ? 'danger' : r.priority === 'HIGH' ? 'warning' : 'neutral'
                        }
                      >
                        {r.priority}
                      </Badge>
                    </td>
                    <td className="p-3 text-slate-600 max-w-xs truncate">{r.description}</td>
                    <td className="p-3">
                      <Badge
                        variant={
                          r.status === 'CLOSED'
                            ? 'neutral'
                            : r.status === 'IN_PROGRESS'
                            ? 'warning'
                            : 'success'
                        }
                      >
                        {r.status}
                      </Badge>
                    </td>
                    <td className="p-3 text-right">
                      {r.status === 'CLOSED' ? (
                        <button
                          onClick={() => {
                            setReopenItem(r);
                            setReopenSuccess(null);
                          }}
                          className="px-2.5 py-1 bg-amber-50 hover:bg-amber-100 text-amber-800 rounded font-semibold text-xs border border-amber-200 inline-flex items-center gap-1"
                        >
                          <RotateCcw className="w-3 h-3" /> Reopen Ticket
                        </button>
                      ) : (
                        <span className="text-[11px] text-slate-400 font-mono">Work Order Open</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Reopen Modal */}
      <Modal
        isOpen={!!reopenItem}
        onClose={() => setReopenItem(null)}
        title={`Reopen Ticket: ${reopenItem?.request_number}`}
        subtitle="Rule BR-08: Closed requests cannot receive work orders without an audited reopening"
      >
        {reopenSuccess ? (
          <div className="text-center py-6 space-y-3">
            <CheckCircle2 className="w-12 h-12 text-emerald-600 mx-auto" />
            <h4 className="text-base font-bold text-slate-900">Ticket Reopened</h4>
            <p className="text-xs text-slate-600">{reopenSuccess}</p>
            <button
              onClick={() => setReopenItem(null)}
              className="px-4 py-2 bg-slate-900 text-white rounded font-bold text-xs"
            >
              Done
            </button>
          </div>
        ) : (
          <form onSubmit={handleReopen} className="space-y-4 text-xs">
            <div className="bg-amber-50 p-3 rounded-lg border border-amber-200 text-amber-900">
              <span className="font-bold">Audit Justification Required:</span>
              <p className="text-[11px] mt-0.5">
                Reopening records a state transition in status_history and unblocks work order attachments.
              </p>
            </div>

            <div>
              <label className="block text-slate-600 font-bold mb-1">Reason for Reopening</label>
              <textarea
                required
                rows={3}
                value={reopenReason}
                onChange={(e) => setReopenReason(e.target.value)}
                className="w-full border border-slate-200 rounded-lg p-2 focus:ring-2 focus:ring-amber-500"
              />
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setReopenItem(null)}
                className="px-4 py-2 border border-slate-200 rounded-lg text-slate-600"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting}
                className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg font-bold disabled:opacity-50"
              >
                {submitting ? 'Executing...' : 'Reopen with Audit Log'}
              </button>
            </div>
          </form>
        )}
      </Modal>
    </div>
  );
};
