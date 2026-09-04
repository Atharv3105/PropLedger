import axios from 'axios';
import {
  UserProfile, Property, PropertyOccupancy, Unit, Tenant, TenantBalance,
  ActiveLease, PaymentResponse, TenantPaymentHistory, DelinquencyItem,
  MaintenanceRequest, FinancialSummary, HierarchyNode, RentPivot, HealthCheck
} from '../types';

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('propledger_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authApi = {
  login: async (email: string, password: string) => {
    const res = await api.post('/auth/login', { email, password });
    return res.data;
  },
  getMe: async (): Promise<UserProfile> => {
    const res = await api.get('/auth/me');
    return res.data;
  },
};

export const propertiesApi = {
  list: async (limit = 50, offset = 0, search = ''): Promise<Property[]> => {
    const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
    if (search) params.append('search', search);
    const res = await api.get(`/properties?${params.toString()}`);
    return res.data;
  },
  getOccupancy: async (propertyId: number): Promise<PropertyOccupancy> => {
    const res = await api.get(`/properties/${propertyId}/occupancy`);
    return res.data;
  },
};

export const unitsApi = {
  list: async (limit = 50, offset = 0, propertyId?: number): Promise<Unit[]> => {
    const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
    if (propertyId) params.append('property_id', String(propertyId));
    const res = await api.get(`/units?${params.toString()}`);
    return res.data;
  },
};

export const tenantsApi = {
  list: async (limit = 50, offset = 0, search = ''): Promise<Tenant[]> => {
    const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
    if (search) params.append('search', search);
    const res = await api.get(`/tenants?${params.toString()}`);
    return res.data;
  },
  getBalance: async (tenantId: number): Promise<TenantBalance> => {
    const res = await api.get(`/tenants/${tenantId}/balance`);
    return res.data;
  },
};

export const leasesApi = {
  listActive: async (limit = 50, offset = 0): Promise<ActiveLease[]> => {
    const res = await api.get(`/leases/active?limit=${limit}&offset=${offset}`);
    return res.data;
  },
  renew: async (leaseId: number, data: { new_start_date: string; new_end_date: string; new_monthly_rent: number }) => {
    const res = await api.post(`/leases/${leaseId}/renew`, data);
    return res.data;
  },
};

export const paymentsApi = {
  record: async (data: { lease_id: number; amount: number; payment_method_id?: number; reference_number?: string }): Promise<PaymentResponse> => {
    const res = await api.post('/payments', data);
    return res.data;
  },
  getHistory: async (tenantId: number): Promise<TenantPaymentHistory[]> => {
    const res = await api.get(`/payments/history/${tenantId}`);
    return res.data;
  },
};

export const billingApi = {
  generateMonthly: async (month: number, year: number) => {
    const res = await api.post('/billing/generate-monthly', { billing_month: month, billing_year: year });
    return res.data;
  },
};

export const collectionsApi = {
  listDelinquent: async (): Promise<DelinquencyItem[]> => {
    const res = await api.get('/collections/delinquent');
    return res.data;
  },
  escalate: async (data: { tenant_id: number; lease_id: number; case_notes?: string }) => {
    const res = await api.post('/collections/escalate', data);
    return res.data;
  },
};

export const maintenanceApi = {
  list: async (limit = 50, status?: string): Promise<MaintenanceRequest[]> => {
    const params = new URLSearchParams({ limit: String(limit) });
    if (status) params.append('status', status);
    const res = await api.get(`/maintenance?${params.toString()}`);
    return res.data;
  },
  reopen: async (requestId: number, reason: string) => {
    const res = await api.post(`/maintenance/${requestId}/reopen`, { reopen_reason: reason });
    return res.data;
  },
};

export const financeApi = {
  getSummaries: async (): Promise<FinancialSummary[]> => {
    const res = await api.get('/finance/financial-summary');
    return res.data;
  },
};

export const reportsApi = {
  getOccupancy: async (): Promise<PropertyOccupancy[]> => {
    const res = await api.get('/reports/occupancy');
    return res.data;
  },
  getHierarchy: async (maxLevel = 3): Promise<HierarchyNode[]> => {
    const res = await api.get(`/reports/hierarchy?max_level=${maxLevel}`);
    return res.data;
  },
  getRentPivot: async (limit = 50): Promise<RentPivot[]> => {
    const res = await api.get(`/reports/rent-pivot?limit=${limit}`);
    return res.data;
  },
};

export const diagnosticsApi = {
  getHealth: async (): Promise<HealthCheck> => {
    const res = await api.get('/diagnostics/health');
    return res.data;
  },
};

export default api;
