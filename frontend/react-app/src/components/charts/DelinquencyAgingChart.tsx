import React from 'react';
import { DelinquencyItem } from '../../types';

export const DelinquencyAgingChart: React.FC<{ data: DelinquencyItem[] }> = ({ data }) => {
  const buckets = [
    { label: '0–30 Days', key: 'current_0_30', color: 'bg-emerald-500', text: 'text-emerald-700' },
    { label: '31–60 Days', key: 'past_due_31_60', color: 'bg-amber-500', text: 'text-amber-700' },
    { label: '61–90 Days', key: 'past_due_61_90', color: 'bg-orange-500', text: 'text-orange-700' },
    { label: '90+ Days', key: 'severe_90_plus', color: 'bg-rose-500', text: 'text-rose-700' },
  ] as const;

  const totals = buckets.map((b) => {
    return data.reduce((sum, item) => sum + Number(item[b.key] || 0), 0);
  });

  const grandTotal = totals.reduce((a, b) => a + b, 0);

  return (
    <div className="space-y-3.5 pt-2">
      {buckets.map((b, idx) => {
        const amt = totals[idx];
        const pct = grandTotal > 0 ? Math.round((amt / grandTotal) * 100) : 0;
        return (
          <div key={idx} className="space-y-1">
            <div className="flex justify-between text-xs font-semibold text-slate-700">
              <span>{b.label}</span>
              <span className={b.text}>
                ₹{amt.toLocaleString('en-IN', { maximumFractionDigits: 0 })} ({pct}%)
              </span>
            </div>
            <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
              <div
                className={`h-full rounded-full ${b.color} transition-all duration-500`}
                style={{ width: `${Math.max(2, pct)}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
};
