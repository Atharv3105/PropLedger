import React from 'react';
import { useAuth, DEMO_USERS } from '../../context/AuthContext';
import { UserCheck } from 'lucide-react';

export const RoleSwitcher: React.FC = () => {
  const { currentRole, loginAs, isLoading } = useAuth();

  return (
    <div className="flex items-center gap-2 bg-slate-100 border border-slate-200 rounded-lg px-2.5 py-1">
      <UserCheck className="w-4 h-4 text-slate-500" />
      <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Demo Role:</span>
      <select
        value={DEMO_USERS.find((u) => u.role === currentRole)?.email || DEMO_USERS[0].email}
        onChange={(e) => loginAs(e.target.value)}
        disabled={isLoading}
        className="bg-transparent text-xs font-bold text-slate-800 focus:outline-none cursor-pointer pr-1"
      >
        {DEMO_USERS.map((user) => (
          <option key={user.role} value={user.email}>
            {user.role} — {user.label}
          </option>
        ))}
      </select>
    </div>
  );
};
