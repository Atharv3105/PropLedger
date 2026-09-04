import React, { createContext, useContext, useState, useEffect } from 'react';
import { UserProfile, UserRole } from '../types';
import { authApi } from '../services/api';

export interface DemoUser {
  role: UserRole;
  label: string;
  email: string;
  description: string;
}

export const DEMO_USERS: DemoUser[] = [
  { role: 'ADMIN', label: 'System Admin', email: 'admin@propledger.com', description: 'Full executive & system control' },
  { role: 'PROPERTY_MANAGER', label: 'Property Manager', email: 'manager1@propledger.com', description: 'Parcels, units, leases & operations' },
  { role: 'ACCOUNTANT', label: 'Senior Accountant', email: 'accountant1@propledger.com', description: 'Financials, payments, P&L & rent rolls' },
  { role: 'LEASING_STAFF', label: 'Leasing Agent', email: 'leasing1@propledger.com', description: 'Tenant applications & renewals' },
  { role: 'MAINTENANCE_STAFF', label: 'Maintenance Tech', email: 'tech1@propledger.com', description: 'Work orders & ticket dispatch' },
  { role: 'OWNER', label: 'Property Owner', email: 'owner1@propledger.com', description: 'Performance & occupancy reports' },
  { role: 'TENANT', label: 'Tenant Self-Service', email: 'tenant1@propledger.com', description: 'Lease view, balance & ticketing' },
];

interface AuthContextType {
  user: UserProfile | null;
  token: string | null;
  currentRole: UserRole;
  isLoading: boolean;
  loginAs: (email: string) => Promise<void>;
  logout: () => void;
  hasRole: (roles: UserRole[]) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('propledger_token'));
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const fetchProfile = async () => {
    try {
      const profile = await authApi.getMe();
      setUser(profile);
    } catch {
      localStorage.removeItem('propledger_token');
      setToken(null);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      fetchProfile();
    } else {
      // Auto-login as default System Admin for demo convenience
      loginAs('admin@propledger.com');
    }
  }, []);

  const loginAs = async (email: string) => {
    setIsLoading(true);
    try {
      const data = await authApi.login(email, 'Admin@123');
      localStorage.setItem('propledger_token', data.access_token);
      setToken(data.access_token);
      const profile = await authApi.getMe();
      setUser(profile);
    } catch (err) {
      console.error('Login failed', err);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('propledger_token');
    setToken(null);
    setUser(null);
  };

  const currentRole: UserRole = (user?.roles[0] as UserRole) || 'ADMIN';

  const hasRole = (roles: UserRole[]): boolean => {
    if (!user) return false;
    if (user.roles.includes('ADMIN')) return true;
    return roles.some((r) => user.roles.includes(r));
  };

  return (
    <AuthContext.Provider value={{ user, token, currentRole, isLoading, loginAs, logout, hasRole }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
