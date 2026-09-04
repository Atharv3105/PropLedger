export type UserRole = 
  | 'ADMIN'
  | 'PROPERTY_MANAGER'
  | 'LEASING_STAFF'
  | 'ACCOUNTANT'
  | 'MAINTENANCE_STAFF'
  | 'OWNER'
  | 'TENANT';

export interface UserProfile {
  user_id: number;
  email: string;
  full_name: string;
  phone?: string;
  is_active: boolean;
  roles: UserRole[];
  permissions: string[];
}

export interface Property {
  property_id: number;
  property_code: string;
  property_name: string;
  property_type?: string;
  address_line1: string;
  city: string;
  state: string;
  postal_code: string;
  year_built?: number;
  total_area_sqft?: number;
  total_buildings: number;
  total_units: number;
}

export interface PropertyOccupancy {
  property_id: number;
  property_code: string;
  property_name: string;
  total_units: number;
  occupied_units: number;
  vacant_units: number;
  under_maintenance_units: number;
  occupancy_rate_pct: number;
}

export interface Unit {
  unit_id: number;
  building_id: number;
  building_name?: string;
  property_id: number;
  property_name?: string;
  unit_number: string;
  unit_type?: string;
  status?: string;
  floor_number?: number;
  square_feet?: number;
  market_rent: number;
  is_active: boolean;
}

export interface Tenant {
  tenant_id: number;
  first_name: string;
  last_name: string;
  full_name: string;
  email?: string;
  phone?: string;
  credit_score?: number;
  is_active: boolean;
}

export interface TenantBalance {
  tenant_id: number;
  tenant_name: string;
  tenant_email?: string;
  tenant_phone?: string;
  lease_id: number;
  property_name: string;
  unit_number: string;
  lease_status: string;
  total_billed: number;
  total_paid: number;
  total_late_fees: number;
  outstanding_balance: number;
}

export interface ActiveLease {
  lease_id: number;
  lease_number: string;
  unit_id: number;
  unit_number: string;
  building_name: string;
  property_name: string;
  tenant_id: number;
  primary_tenant_name: string;
  primary_tenant_email?: string;
  primary_tenant_phone?: string;
  start_date: string;
  end_date: string;
  monthly_rent: number;
  security_deposit: number;
  lease_status: string;
  predecessor_lease_id?: number;
  is_renewal: boolean;
}

export interface PaymentResponse {
  payment_id: number;
  lease_id: number;
  amount_paid: number;
  allocated_amount: number;
  unallocated_amount: number;
  remaining_balance: number;
  allocations_count: number;
  message: string;
}

export interface TenantPaymentHistory {
  payment_id: number;
  lease_id: number;
  payment_date: string;
  payment_method: string;
  payment_amount: number;
  running_total_paid: number;
  days_since_last_payment?: number;
  payment_rank: number;
}

export interface DelinquencyItem {
  tenant_id: number;
  tenant_name: string;
  email?: string;
  phone?: string;
  lease_id: number;
  unit_number: string;
  property_name: string;
  current_0_30: number;
  past_due_31_60: number;
  past_due_61_90: number;
  severe_90_plus: number;
  total_delinquent_balance: number;
  max_overdue_days: number;
}

export interface MaintenanceRequest {
  request_id: number;
  request_number: string;
  unit_id: number;
  unit_number: string;
  property_name: string;
  category: string;
  priority: string;
  status: string;
  description?: string;
  reported_date?: string;
}

export interface FinancialSummary {
  property_id: number;
  property_code: string;
  property_name: string;
  property_type?: string;
  city?: string;
  owner_name?: string;
  total_billed_rent: number;
  total_collected_rent: number;
  total_late_fees_collected: number;
  total_operating_revenue: number;
  total_operating_expenses: number;
  net_operating_income: number;
  collection_percentage?: number;
}

export interface HierarchyNode {
  node_id: string;
  parent_node_id?: string;
  node_name: string;
  node_type: string;
  depth_level: number;
  hierarchy_path: string;
}

export interface RentPivot {
  property_id: number;
  property_code: string;
  property_name: string;
  billing_year: number;
  jan_collected: number;
  feb_collected: number;
  mar_collected: number;
  apr_collected: number;
  may_collected: number;
  jun_collected: number;
  jul_collected: number;
  aug_collected: number;
  sep_collected: number;
  oct_collected: number;
  nov_collected: number;
  dec_collected: number;
  annual_total_collected: number;
}

export interface HealthCheck {
  status: string;
  environment: string;
  database: {
    status: string;
    version: string;
    table_count: number;
  };
  pool: {
    engine: string;
    pool_type: string;
    status: string;
  };
  timestamp: string;
}
