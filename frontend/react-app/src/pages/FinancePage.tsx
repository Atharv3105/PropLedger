import React, { useEffect, useState } from 'react';
import { financeApi } from '../services/api';
import { FinancialSummary } from '../types';
import { Card } from '../components/common/Card';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export const FinancePage: React.FC = () => {
  const [summaries, setSummaries] = useState<FinancialSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    financeApi
      .getSummaries()
      .then(setSummaries)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-xl font-bold text-slate-900">Property Financial Statements & P&L</h2>
        <p className="text-xs text-slate-500">
          Authoritative financial metrics originating from vw_PropertyFinancialSummary (Rule BR-09)
        </p>
      </div>

      {loading ? (
        <LoadingSpinner message="Calculating property P&L summaries..." />
      ) : (
        <Card className="p-0 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-100 text-slate-700 font-bold border-b border-slate-200">
                <tr>
                  <th className="p-3">Code</th>
                  <th className="p-3">Property Name</th>
                  <th className="p-3">City</th>
                  <th className="p-3 text-right">Billed Rent</th>
                  <th className="p-3 text-right">Collected Rent</th>
                  <th className="p-3 text-right">Late Fees</th>
                  <th className="p-3 text-right">Total Revenue</th>
                  <th className="p-3 text-right">Expenses</th>
                  <th className="p-3 text-right">NOI (Profit)</th>
                  <th className="p-3 text-right">Collection %</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-mono">
                {summaries.map((s) => (
                  <tr key={s.property_id} className="hover:bg-slate-50/70">
                    <td className="p-3 font-bold text-slate-900 font-sans">{s.property_code}</td>
                    <td className="p-3 font-bold text-slate-900 font-sans">{s.property_name}</td>
                    <td className="p-3 font-sans text-slate-600">{s.city}</td>
                    <td className="p-3 text-right">₹{Number(s.total_billed_rent).toLocaleString('en-IN')}</td>
                    <td className="p-3 text-right text-emerald-700 font-bold">
                      ₹{Number(s.total_collected_rent).toLocaleString('en-IN')}
                    </td>
                    <td className="p-3 text-right text-amber-700">
                      ₹{Number(s.total_late_fees_collected).toLocaleString('en-IN')}
                    </td>
                    <td className="p-3 text-right font-bold text-slate-900">
                      ₹{Number(s.total_operating_revenue).toLocaleString('en-IN')}
                    </td>
                    <td className="p-3 text-right text-rose-600">
                      ₹{Number(s.total_operating_expenses).toLocaleString('en-IN')}
                    </td>
                    <td className="p-3 text-right font-black text-emerald-800">
                      ₹{Number(s.net_operating_income).toLocaleString('en-IN')}
                    </td>
                    <td className="p-3 text-right font-bold text-slate-900 font-sans">
                      {Number(s.collection_percentage || 0).toFixed(1)}%
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
