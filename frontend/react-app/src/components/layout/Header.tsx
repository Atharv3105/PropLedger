import React, { useEffect, useState } from 'react';
import { RoleSwitcher } from './RoleSwitcher';
import { diagnosticsApi } from '../../services/api';
import { Database, ShieldCheck } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export const Header: React.FC<{ title: string }> = ({ title }) => {
  const { currentRole } = useAuth();
  const [dbStatus, setDbStatus] = useState<string>('checking...');
  const [tableCount, setTableCount] = useState<number>(0);

  useEffect(() => {
    diagnosticsApi
      .getHealth()
      .then((data) => {
        setDbStatus(data.database.status);
        setTableCount(data.database.table_count);
      })
      .catch(() => setDbStatus('offline'));
  }, []);

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between shadow-xs sticky top-0 z-30">
      <div className="flex items-center gap-3">
        <h2 className="text-lg font-bold text-slate-900 tracking-tight">{title}</h2>
        <span className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-md font-mono border border-slate-200">
          Role: {currentRole}
        </span>
      </div>

      <div className="flex items-center gap-4">
        {/* DB Connection Health Pill */}
        <div className="flex items-center gap-1.5 text-xs text-slate-600 bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1">
          <Database className="w-3.5 h-3.5 text-slate-500" />
          <span>PostgreSQL:</span>
          <span
            className={`font-semibold flex items-center gap-1 ${
              dbStatus === 'connected' ? 'text-emerald-600' : 'text-rose-500'
            }`}
          >
            <span
              className={`w-2 h-2 rounded-full ${
                dbStatus === 'connected' ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'
              }`}
            />
            {dbStatus === 'connected' ? `${tableCount} Tables` : 'Offline'}
          </span>
        </div>

        {/* Demo Role Switcher */}
        <RoleSwitcher />
      </div>
    </header>
  );
};
