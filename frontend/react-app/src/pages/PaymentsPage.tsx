import React, { useState } from 'react';
import { paymentsApi, billingApi } from '../services/api';
import { PaymentResponse, TenantPaymentHistory } from '../types';
import { Card } from '../components/common/Card';
import { Modal } from '../components/common/Modal';
import { CreditCard, CheckCircle2, Calendar, History, ShieldAlert } from 'lucide-react';

export const PaymentsPage: React.FC = () => {
  // Payment recording form state
  const [leaseId, setLeaseId] = useState<number>(1);
  const [amount, setAmount] = useState<number>(15000);
  const [submitting, setSubmitting] = useState(false);
  const [paymentResult, setPaymentResult] = useState<PaymentResponse | null>(null);

  // Billing trigger state
  const [billingMonth, setBillingMonth] = useState(9);
  const [billingYear, setBillingYear] = useState(2026);
  const [billingResult, setBillingResult] = useState<any | null>(null);

  // Window functions payment history lookup
  const [tenantId, setTenantId] = useState<number>(1);
  const [history, setHistory] = useState<TenantPaymentHistory[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  const handleRecordPayment = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const res = await paymentsApi.record({
        lease_id: leaseId,
        amount: amount,
        payment_method_id: 1,
        reference_number: `WEB-PAY-${Date.now()}`,
      });
      setPaymentResult(res);
    } catch (err: any) {
      alert(`Payment rejected: ${err?.response?.data?.detail || err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  const handleGenerateBilling = async () => {
    try {
      const res = await billingApi.generateMonthly(billingMonth, billingYear);
      setBillingResult(res);
    } catch (err: any) {
      alert(`Billing generation error: ${err?.response?.data?.detail || err.message}`);
    }
  };

  const handleQueryHistory = async () => {
    setLoadingHistory(true);
    try {
      const data = await paymentsApi.getHistory(tenantId);
      setHistory(data);
    } finally {
      setLoadingHistory(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-900">Payments & Transactional FIFO Allocations</h2>
        <p className="text-xs text-slate-500">
          Transactional payment execution via usp_RecordPayment and window-function history from usp_GetTenantPaymentHistory
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Record Payment Card */}
        <Card title="Record Tenant Payment (FIFO Engine)" subtitle="Invokes usp_RecordPayment: validates positive amount (Rule BR-10) and settles oldest charges">
          <form onSubmit={handleRecordPayment} className="space-y-4 text-xs">
            <div>
              <label className="block text-slate-600 font-bold mb-1">Target Lease ID</label>
              <input
                type="number"
                required
                min="1"
                value={leaseId}
                onChange={(e) => setLeaseId(Number(e.target.value))}
                className="w-full border border-slate-200 rounded-lg p-2.5 font-mono text-slate-900"
              />
            </div>

            <div>
              <label className="block text-slate-600 font-bold mb-1">Payment Amount (₹)</label>
              <input
                type="number"
                required
                step="100"
                min="1"
                value={amount}
                onChange={(e) => setAmount(Number(e.target.value))}
                className="w-full border border-slate-200 rounded-lg p-2.5 font-bold text-slate-900 text-sm"
              />
              <span className="text-[11px] text-slate-400 mt-0.5">
                Rule BR-10: Negative amounts will be rejected with HTTP 422 immediately.
              </span>
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-lg transition shadow-sm disabled:opacity-50"
            >
              {submitting ? 'Executing usp_RecordPayment...' : 'Post Transactional Payment'}
            </button>
          </form>
        </Card>

        {/* Generate Monthly Rent Batch */}
        <Card title="Monthly Rent Batch Generation" subtitle="Invokes usp_GenerateMonthlyRent for entire active property catalog">
          <div className="space-y-4 text-xs">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-slate-600 font-bold mb-1">Billing Month</label>
                <select
                  value={billingMonth}
                  onChange={(e) => setBillingMonth(Number(e.target.value))}
                  className="w-full border border-slate-200 rounded-lg p-2.5 bg-white font-semibold"
                >
                  {[...Array(12)].map((_, i) => (
                    <option key={i + 1} value={i + 1}>
                      Month {i + 1}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-slate-600 font-bold mb-1">Billing Year</label>
                <input
                  type="number"
                  value={billingYear}
                  onChange={(e) => setBillingYear(Number(e.target.value))}
                  className="w-full border border-slate-200 rounded-lg p-2.5 font-bold"
                />
              </div>
            </div>

            <button
              onClick={handleGenerateBilling}
              className="w-full py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-lg transition"
            >
              Run Batch Generation (usp_GenerateMonthlyRent)
            </button>

            {billingResult && (
              <div className="bg-emerald-50 border border-emerald-200 p-3 rounded-lg text-emerald-800 space-y-1">
                <div className="font-bold">{billingResult.message}</div>
                <div>Charges Created: <strong>{billingResult.charges_created}</strong></div>
                <div>Total Amount: <strong>₹{Number(billingResult.total_amount).toLocaleString('en-IN')}</strong></div>
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* Tenant Payment History Window Functions Inspector */}
      <Card
        title="Tenant Payment History (Window Functions Inspection)"
        subtitle="Queries usp_GetTenantPaymentHistory utilizing ROW_NUMBER(), SUM() OVER (running total), and LAG (days gap)"
      >
        <div className="flex items-center gap-3 mb-4 text-xs">
          <label className="font-bold text-slate-700">Enter Tenant ID:</label>
          <input
            type="number"
            min="1"
            value={tenantId}
            onChange={(e) => setTenantId(Number(e.target.value))}
            className="border border-slate-200 rounded p-1.5 w-24 font-mono font-bold"
          />
          <button
            onClick={handleQueryHistory}
            disabled={loadingHistory}
            className="px-3 py-1.5 bg-slate-800 text-white rounded font-semibold hover:bg-slate-700"
          >
            {loadingHistory ? 'Querying...' : 'Fetch History'}
          </button>
        </div>

        {history.length > 0 ? (
          <div className="overflow-x-auto border border-slate-200 rounded-lg">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-100 text-slate-700 font-bold">
                <tr>
                  <th className="p-2.5">Rank (ROW_NUMBER)</th>
                  <th className="p-2.5">Payment Date</th>
                  <th className="p-2.5">Method</th>
                  <th className="p-2.5 text-right">Amount</th>
                  <th className="p-2.5 text-right">Running Total (OVER)</th>
                  <th className="p-2.5 text-right">Days Gap (LAG)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {history.map((h, i) => (
                  <tr key={i} className="hover:bg-slate-50">
                    <td className="p-2.5 font-bold text-slate-500">#{h.payment_rank}</td>
                    <td className="p-2.5 font-mono">{h.payment_date}</td>
                    <td className="p-2.5">{h.payment_method}</td>
                    <td className="p-2.5 text-right font-bold text-emerald-700">
                      ₹{Number(h.payment_amount).toLocaleString('en-IN')}
                    </td>
                    <td className="p-2.5 text-right font-bold font-mono text-slate-900">
                      ₹{Number(h.running_total_paid).toLocaleString('en-IN')}
                    </td>
                    <td className="p-2.5 text-right font-mono text-slate-500">
                      {h.days_since_last_payment !== null ? `${h.days_since_last_payment} days` : 'First'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-6 text-slate-400 text-xs">
            Query tenant payment history to inspect SQL window functions.
          </div>
        )}
      </Card>

      {/* Payment Receipt Modal */}
      <Modal
        isOpen={!!paymentResult}
        onClose={() => setPaymentResult(null)}
        title="Payment Recorded & Allocated"
        subtitle="FIFO allocation complete via usp_RecordPayment"
      >
        {paymentResult && (
          <div className="space-y-4 text-xs">
            <div className="flex items-center gap-2 text-emerald-700 bg-emerald-50 p-3 rounded-lg border border-emerald-200">
              <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
              <div>
                <strong>{paymentResult.message}</strong>
                <p className="text-[11px] text-emerald-600">Payment ID #{paymentResult.payment_id} logged to audit ledger.</p>
              </div>
            </div>

            <div className="space-y-2 pt-2">
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Amount Received:</span>
                <span className="font-bold text-slate-900">₹{Number(paymentResult.amount_paid).toLocaleString('en-IN')}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Allocated to Rent Charges:</span>
                <span className="font-bold text-emerald-700">₹{Number(paymentResult.allocated_amount).toLocaleString('en-IN')}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Unallocated Credit:</span>
                <span className="font-mono text-slate-600">₹{Number(paymentResult.unallocated_amount).toLocaleString('en-IN')}</span>
              </div>
              <div className="flex justify-between py-2 bg-slate-50 px-3 rounded text-sm font-bold">
                <span>Remaining Lease Balance:</span>
                <span className="text-rose-600">₹{Number(paymentResult.remaining_balance).toLocaleString('en-IN')}</span>
              </div>
            </div>

            <button
              onClick={() => setPaymentResult(null)}
              className="w-full py-2 bg-slate-900 text-white rounded-lg font-bold text-xs"
            >
              Done
            </button>
          </div>
        )}
      </Modal>
    </div>
  );
};
