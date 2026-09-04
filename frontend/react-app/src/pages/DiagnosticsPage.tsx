import React, { useEffect, useState } from 'react';
import { diagnosticsApi } from '../services/api';
import { HealthCheck } from '../types';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { Database, Server, Cpu, CheckCircle2, ShieldCheck } from 'lucide-react';

export const DiagnosticsPage: React.FC = () => {
  const [health, setHealth] = useState<HealthCheck | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchHealth = () => {
    setLoading(true);
    diagnosticsApi
      .getHealth()
      .then(setHealth)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900">System Diagnostics & Incident Support</h2>
          <p className="text-xs text-slate-500">Live operational diagnostics (PRD Part Z) from /api/v1/diagnostics/health</p>
        </div>
        <button
          onClick={fetchHealth}
          className="px-3 py-1.5 bg-slate-900 text-white rounded-lg text-xs font-bold hover:bg-slate-800 transition"
        >
          Refresh Ping
        </button>
      </div>

      {loading ? (
        <LoadingSpinner message="Pinging database connection pool..." />
      ) : health ? (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="border-l-4 border-l-emerald-500">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-500 uppercase">System Status</span>
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              </div>
              <div className="mt-2 text-2xl font-black text-emerald-700">{health.status}</div>
              <div className="text-[11px] text-slate-400 mt-1">Environment: {health.environment}</div>
            </Card>

            <Card className="border-l-4 border-l-sky-500">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-500 uppercase">Database Engine</span>
                <Database className="w-4 h-4 text-sky-600" />
              </div>
              <div className="mt-2 text-xl font-bold text-slate-900">{health.database.status.toUpperCase()}</div>
              <div className="text-[11px] text-slate-400 mt-1">
                Schema: <strong>{health.database.table_count} tables & views</strong>
              </div>
            </Card>

            <Card className="border-l-4 border-l-purple-500">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-500 uppercase">Connection Pool</span>
                <Server className="w-4 h-4 text-purple-600" />
              </div>
              <div className="mt-2 text-xl font-bold text-slate-900">{health.pool.engine}</div>
              <div className="text-[11px] text-slate-400 mt-1">Pool: {health.pool.pool_type}</div>
            </Card>
          </div>

          <Card title="Raw PostgreSQL Version String" subtitle="Verified from SELECT version();">
            <pre className="bg-slate-950 text-emerald-400 font-mono text-xs p-4 rounded-xl overflow-x-auto whitespace-pre-wrap">
              {health.database.version}
            </pre>
          </Card>
        </div>
      ) : (
        <div className="text-center py-12 text-rose-500">Backend API diagnostics endpoint unreachable.</div>
      )}
    </div>
  );
};
