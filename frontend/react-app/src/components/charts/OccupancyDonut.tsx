import React from 'react';

interface OccupancyDonutProps {
  rate: number;
  total: number;
  occupied: number;
  vacant: number;
}

export const OccupancyDonut: React.FC<OccupancyDonutProps> = ({ rate, total, occupied, vacant }) => {
  const radius = 42;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (rate / 100) * circumference;

  return (
    <div className="flex items-center justify-around py-2">
      <div className="relative flex items-center justify-center">
        <svg className="w-32 h-32 transform -rotate-90">
          <circle
            cx="64"
            cy="64"
            r={radius}
            stroke="#f1f5f9"
            strokeWidth="12"
            fill="transparent"
          />
          <circle
            cx="64"
            cy="64"
            r={radius}
            stroke="#16a34a"
            strokeWidth="12"
            fill="transparent"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        <div className="absolute text-center">
          <span className="text-2xl font-bold text-slate-900">{rate.toFixed(1)}%</span>
          <p className="text-[10px] font-medium text-slate-400 uppercase tracking-wider">Occupied</p>
        </div>
      </div>
      <div className="space-y-2 text-xs">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-emerald-600" />
          <span className="text-slate-600">Occupied Units:</span>
          <span className="font-bold text-slate-900">{occupied.toLocaleString()}</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-slate-200" />
          <span className="text-slate-600">Vacant Units:</span>
          <span className="font-bold text-slate-900">{vacant.toLocaleString()}</span>
        </div>
        <div className="pt-1 border-t border-slate-100 text-slate-500">
          Total Inventory: <strong className="text-slate-900">{total.toLocaleString()}</strong> units
        </div>
      </div>
    </div>
  );
};
