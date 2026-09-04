import React from 'react';
import { RentPivot } from '../../types';

export const MonthlyRentChart: React.FC<{ data: RentPivot[] }> = ({ data }) => {
  if (!data || data.length === 0) {
    return <div className="text-sm text-slate-400 py-8 text-center">No collection data available.</div>;
  }

  // Aggregate collections across properties per month
  const months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'] as const;
  const monthLabels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  
  const monthlyTotals = months.map((m) => {
    return data.reduce((sum, item) => sum + (Number(item[`${m}_collected`]) || 0), 0);
  });

  const maxVal = Math.max(...monthlyTotals, 1000);

  return (
    <div className="w-full">
      <div className="h-56 flex items-end justify-between gap-2 pt-6 pb-2 px-2">
        {monthlyTotals.map((val, idx) => {
          const heightPercent = Math.min(100, Math.max(10, Math.round((val / maxVal) * 100)));
          return (
            <div key={idx} className="flex-1 flex flex-col items-center gap-1 group relative">
              <div className="absolute -top-7 opacity-0 group-hover:opacity-100 transition bg-slate-900 text-white text-[10px] font-semibold py-1 px-1.5 rounded whitespace-nowrap z-10">
                ₹{(val / 1000).toFixed(1)}k
              </div>
              <div className="w-full bg-slate-100 rounded-t-md h-44 flex items-end p-1">
                <div
                  style={{ height: `${heightPercent}%` }}
                  className="w-full bg-gradient-to-t from-brand-600 to-emerald-400 rounded-t-sm transition-all duration-500 group-hover:from-brand-700 group-hover:to-emerald-500"
                />
              </div>
              <span className="text-[11px] font-medium text-slate-500">{monthLabels[idx]}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
