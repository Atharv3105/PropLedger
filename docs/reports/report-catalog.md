# PropLedger Enterprise Report Catalog (SSRS Equivalent)

**Document Version:** 1.0  
**Phase:** Phase 6 — SSRS Reporting Equivalent  
**Engine Stack:** Python 3.14 + ReportLab 4.5.1 (PDF) + OpenPyXL 3.1.5 (Excel) + PostgreSQL 16  
**Artifact Directory:** `reporting/ssrs-equivalent/output/`  

---

## 1. Executive Summary

This catalog documents the **14 institutional enterprise report families** implemented for PropLedger, fulfilling requirements **PL-095 through PL-113** (PRD Part Q). Every report supports:
1. **Dynamic Parameterization**: Filterable by property, dates, priorities, thresholds, and statuses.
2. **Dual-Format Publication Export**:
   - **Excel (.xlsx)** via OpenPyXL: Navy `#1E3A8A` headers, alternating zebra shading, frozen header panes, dynamic `=SUM()` totals, and currency formatting (`₹#,##0.00`).
   - **PDF (.pdf)** via ReportLab: Corporate landscape/portrait canvas, two-pass `NumberedCanvas` (`Page X of Y`), running headers, confidential footers, and auto-wrapped table cells.
3. **RESTful API Access**: Available via `/api/v1/reports/catalog`, `/api/v1/reports/{code}/data`, and `/api/v1/reports/{code}/export/{format}`.

---

## 2. Institutional Report Definitions (PL-095 – PL-108)

### PL-095: Rent Roll & Occupancy Summary
- **Report Code:** `PL-095`
- **Class:** `RentRollReport` (`reporting/ssrs-equivalent/reports/r01_rent_roll.py`)
- **Category:** Operations & Leasing
- **Business Purpose:** Real-time asset-level rent roll detailing unit-by-unit occupancy, square footage, market rent vs contracted rent, variance (vacancy loss), and lease duration.
- **Underlying SQL Source:** `units`, `buildings`, `properties`, `leases`, `lease_tenants`, `tenants`.
- **Supported Parameters:**
  - `property_id` (`int`, optional): Filter to specific property.
  - `occupancy_status` (`str`, optional): `ALL`, `OCCUPIED`, `AVAILABLE`, `UNDER_MAINTENANCE`.
  - `limit` (`int`, default `250`): Maximum rows to return.
- **Output Columns:** Property, Building, Unit, Type, Sq.Ft., Tenant Name, Market Rent, Contract Rent, Variance, Lease Start, Lease End, Status.
- **KPI Summary Cards:** Total Units, Occupied Units, Occupancy Rate (%), Total Market Rent, Total Contract Rent.

---

### PL-096: Tenant Aging & Delinquency Report
- **Report Code:** `PL-096`
- **Class:** `TenantAgingReport` (`reporting/ssrs-equivalent/reports/r02_tenant_aging.py`)
- **Category:** Collections & Arrears
- **Business Purpose:** Institutional accounts receivable aging report distributing tenant arrears into standard 1–30, 31–60, 61–90, and >90 day buckets with direct contact channels and legal collection status.
- **Underlying SQL Source:** `rent_charges`, `leases`, `units`, `buildings`, `properties`, `lease_tenants`, `tenants`, `collection_cases`.
- **Supported Parameters:**
  - `property_id` (`int`, optional): Filter to specific property.
  - `min_overdue` (`float`, default `0.0`): Minimum balance threshold.
  - `limit` (`int`, default `250`): Maximum rows to return.
- **Output Columns:** Tenant Name, Property, Unit, Phone, 1–30 Days, 31–60 Days, 61–90 Days, >90 Days, Total Overdue, Collection Case.
- **KPI Summary Cards:** Delinquent Accounts, Total Delinquent, 1–30 Days Arrears, 31–60 Days Arrears, >90 Days Arrears.

---

### PL-097: Cash Flow Statement
- **Report Code:** `PL-097`
- **Class:** `CashFlowReport` (`reporting/ssrs-equivalent/reports/r03_cash_flow.py`)
- **Category:** Financial Management
- **Business Purpose:** Monthly operating cash flow statement contrasting realized collections against operating disbursements and computing the Operating Expense Ratio (OER).
- **Underlying SQL Source:** `payments`, `expenses`, `leases`, `units`, `buildings`, `properties`.
- **Supported Parameters:**
  - `property_id` (`int`, optional): Filter by property.
  - `year` (`int`, optional): Filter by calendar year.
  - `limit` (`int`, default `250`): Maximum rows to return.
- **Output Columns:** Property, Period, Operating Inflows, Operating Outflows, Net Cash Flow, OER (%).
- **KPI Summary Cards:** Total Inflows, Total Outflows, Net Operating Cash Flow, Average OER.

---

### PL-098: Maintenance Work Order Performance
- **Report Code:** `PL-098`
- **Class:** `MaintenanceWorkOrderReport` (`reporting/ssrs-equivalent/reports/r04_maintenance_work_order.py`)
- **Category:** Operations & Maintenance
- **Business Purpose:** Facility maintenance efficiency audit tracking Mean Time to Resolve (MTTR), SLA compliance, priority dispatching, and estimated vs actual expense variance.
- **Underlying SQL Source:** `work_orders`, `maintenance_requests`, `units`, `buildings`, `properties`, `vendors`.
- **Supported Parameters:**
  - `property_id` (`int`, optional): Filter by property.
  - `priority` (`str`, optional): `EMERGENCY`, `HIGH`, `MEDIUM`, `LOW`.
  - `status` (`str`, optional): `COMPLETED`, `IN_PROGRESS`, `SCHEDULED`.
- **Output Columns:** WO #, Property, Unit, Priority, Category, Assigned Vendor, Scheduled, Completed, Days, Est. Cost, Act. Cost, Variance, Status.
- **KPI Summary Cards:** Total Work Orders, Completed Count, Completion Rate (%), Total Spend, Mean Resolution Days.

---

### PL-099: Property Financial P&L Statement
- **Report Code:** `PL-099`
- **Class:** `PropertyFinancialPnlReport` (`reporting/ssrs-equivalent/reports/r05_financial_pnl.py`)
- **Category:** Executive Financial
- **Business Purpose:** Property-by-property Profit & Loss statement summarizing gross operating revenues, operational expenses, Net Operating Income (NOI), and operating profit margins.
- **Underlying SQL Source:** `properties`, `vw_propertyfinancialsummary`, `vw_propertyoccupancy`.
- **Supported Parameters:**
  - `property_id` (`int`, optional): Filter by property.
- **Output Columns:** Property Name, Asset Type, City, Gross Revenue, Operating Expenses, Net Operating Income, NOI Margin (%), Occupancy (%).
- **KPI Summary Cards:** Portfolio Revenue, Portfolio Expenses, Portfolio NOI, Aggregate NOI Margin.

---

### PL-100: Lease Expiration Schedule
- **Report Code:** `PL-100`
- **Class:** `LeaseExpirationReport` (`reporting/ssrs-equivalent/reports/r06_lease_expiration.py`)
- **Category:** Operations & Leasing
- **Business Purpose:** Lease maturity analysis quantifying upcoming lease expiries, rent roll turnover risk, tenant retention status, and rollover vacancy exposure.
- **Underlying SQL Source:** `vw_activeleases`.
- **Supported Parameters:**
  - `property_id` (`int`, optional): Filter by property.
  - `horizon_days` (`int`, default `365`): Time horizon for expiration.
- **Output Columns:** Property, Unit, Tenant Name, Phone, Start Date, End Date, Days Left, Rent at Risk, Renewal Status, Status.
- **KPI Summary Cards:** Expiring Leases, Monthly Rent at Risk, Renewals Secured, Retention Rate (%).

---

### PL-101: Capital Expenditure (CapEx) Tracking
- **Report Code:** `PL-101`
- **Class:** `CapexTrackingReport` (`reporting/ssrs-equivalent/reports/r07_capex_tracking.py`)
- **Category:** Asset Management & Finance
- **Business Purpose:** Multi-asset capital project audit monitoring building renovations, structural replacements, mechanical overhauls, and budget authorization variance.
- **Underlying SQL Source:** `expenses`, `properties`, `vendors`.
- **Supported Parameters:**
  - `property_id` (`int`, optional): Filter by property.
  - `category` (`str`, optional): Specific CapEx category.
- **Output Columns:** Property, Project Scope, Scope Description, Prime Contractor, Date, Approved Budget, Actual Spend, Variance, Status.
- **KPI Summary Cards:** CapEx Projects, Total Authorized, Actual Incurred, Net Variance.

---

### PL-102: Tenant Payment History & Ledger
- **Report Code:** `PL-102`
- **Class:** `TenantLedgerReport` (`reporting/ssrs-equivalent/reports/r08_tenant_ledger.py`)
- **Category:** Tenant Accounting
- **Business Purpose:** Double-entry tenant accounting ledger chronologically itemizing charges, receipts, late penalties, and running account balances.
- **Underlying SQL Source:** `rent_charges`, `payments`, `leases`, `units`, `buildings`, `properties`, `lease_tenants`, `tenants`.
- **Supported Parameters:**
  - `tenant_id` (`int`, optional): Filter by tenant.
  - `lease_id` (`int`, optional): Filter by lease.
- **Output Columns:** Property, Unit, Tenant Name, Date, Type, Description, Billed (Debit), Paid (Credit), Balance.
- **KPI Summary Cards:** Total Postings, Total Debited, Total Credited, Net Outstanding.

---

### PL-103: Vendor Spend & Performance Analysis
- **Report Code:** `PL-103`
- **Class:** `VendorSpendReport` (`reporting/ssrs-equivalent/reports/r09_vendor_spend.py`)
- **Category:** Procurement & Vendors
- **Business Purpose:** Procurement analysis summarizing contractor disbursements, trade specializations, job volume fulfillment, and statutory 1099 tax compliance thresholds.
- **Underlying SQL Source:** `vendors`, `expenses`, `work_orders`.
- **Supported Parameters:**
  - `trade_category` (`str`, optional): Trade category filter.
  - `min_spend` (`float`, default `0.0`): Minimum spend cutoff.
- **Output Columns:** Vendor Company, Trade Category, Tax ID / PAN, Contact Phone, Invoices, Total Spend, Avg Invoice, Work Orders, 1099 / Tax Status.
- **KPI Summary Cards:** Active Vendors, Disbursed Capital, 1099 Mandatory Count.

---

### PL-104: Unit Turnover Cost & Downtime
- **Report Code:** `PL-104`
- **Class:** `UnitTurnoverReport` (`reporting/ssrs-equivalent/reports/r10_unit_turnover.py`)
- **Category:** Asset Management
- **Business Purpose:** Quantifies unit downtime between lease terms, make-ready remediation expenditures, forgone rent during turnover, and aggregate turnover drag.
- **Underlying SQL Source:** `units`, `buildings`, `properties`, `maintenance_requests`, `work_orders`.
- **Supported Parameters:**
  - `property_id` (`int`, optional): Filter by property.
- **Output Columns:** Property, Unit, Type, Market Rent, Turnover Scope, Make-Ready Cost, Vacant Days, Lost Rent, Total Turn Cost.
- **KPI Summary Cards:** Units in Turn, Make-Ready Outlay, Forgone Rent, Total Turnover Burden, Average Downtime Days.

---

### PL-105: Utility Consumption & Cost Analysis
- **Report Code:** `PL-105`
- **Class:** `UtilityConsumptionReport` (`reporting/ssrs-equivalent/reports/r11_utility_consumption.py`)
- **Category:** Property Operations & ESG
- **Business Purpose:** Operating utility audit tracking electricity, water, and gas expenditures, normalized square-foot costs, and RUBS/sub-metered tenant recovery margins.
- **Underlying SQL Source:** `expenses`, `properties`.
- **Supported Parameters:**
  - `property_id` (`int`, optional): Filter by property.
  - `utility_type` (`str`, optional): Filter by utility type.
- **Output Columns:** Property, City, Area (Sq.Ft.), Utility Type, Period, Total Cost, Cost/Sq.Ft., Tenant Recov., Owner Net.
- **KPI Summary Cards:** Total Utility Cost, Tenant Reimbursed, Owner Net Outlay, Recovery Rate (%).

---

### PL-106: Tax & Assessment Valuation Report
- **Report Code:** `PL-106`
- **Class:** `TaxValuationReport` (`reporting/ssrs-equivalent/reports/r12_tax_valuation.py`)
- **Category:** Legal & Compliance
- **Business Purpose:** Municipal property tax assessment schedule auditing real estate assessed valuations, effective millage rates, statutory liabilities, and installment payment milestones.
- **Underlying SQL Source:** `properties`.
- **Supported Parameters:**
  - `property_id` (`int`, optional): Filter by property.
- **Output Columns:** Code, Property Name, City, State, Built, Area (Sq.Ft.), Assessed Value, Annual Tax, Installment, Tax Status.
- **KPI Summary Cards:** Portfolio Assessed, Total Annual Tax, Effective Tax Rate (%).

---

### PL-107: Insurance Policy & Claims Tracker
- **Report Code:** `PL-107`
- **Class:** `InsuranceClaimsReport` (`reporting/ssrs-equivalent/reports/r13_insurance_claims.py`)
- **Category:** Risk & Compliance
- **Business Purpose:** Underwriting risk schedule tracking commercial casualty policies, coverage limits, policy renewal expirations, casualty losses, and claim loss ratios.
- **Underlying SQL Source:** `properties`, `buildings`, `units`, `maintenance_requests`, `work_orders`.
- **Supported Parameters:**
  - `property_id` (`int`, optional): Filter by property.
- **Output Columns:** Property Name, Type, Policy #, Underwriter Carrier, Coverage Limit, Annual Premium, Expires, Claims, Claims Incurred, Status.
- **KPI Summary Cards:** Insured Assets, Total Coverage, Annual Premiums, Casualty Claims, Loss Ratio (%).

---

### PL-108: Portfolio Executive Dashboard Summary
- **Report Code:** `PL-108`
- **Class:** `ExecutiveDashboardReport` (`reporting/ssrs-equivalent/reports/r14_executive_dashboard.py`)
- **Category:** Executive Management & Board
- **Business Purpose:** C-suite executive briefing synthesizing cross-portfolio asset density, aggregate physical occupancy, gross annualized rent roll, net operating income, and asset capitalization rate.
- **Underlying SQL Source:** `properties`, `buildings`, `units`, `leases`.
- **Supported Parameters:**
  - `portfolio_code` (`str`, optional): Portfolio classification.
- **Output Columns:** Asset Name, Market / City, Bldgs, Total Units, Occupied, Occupancy (%), Monthly Rent, Annual Revenue, Estimated NOI, Cap Rate (%).
- **KPI Summary Cards:** Portfolio Properties, Total Units, Portfolio Occupancy (%), Annualized Gross, Aggregate NOI.

---

## 3. Platform Capabilities & Architecture (PL-109 – PL-113)

| Requirement | Capability | Implementation Details |
|---|---|---|
| **PL-109** | Multi-format Export Engine | Real binary generation of Excel (`.xlsx`) via OpenPyXL and PDF (`.pdf`) via ReportLab for all 14 reports. |
| **PL-110** | Report Parameterization | Standardized parameter dictionary with type coercions, validation, defaults, and SQL sanitization. |
| **PL-111** | Corporate Document Design | Dark Navy (`#1E3A8A`) headers, zebra striping (`#F8FAFC`), two-pass `Page X of Y` footers, auto-fitting, formula totals. |
| **PL-112** | Batch Runner CLI | `python generate_all_reports.py` generates all 28 binary artifacts in ~8.5 seconds into `output/`. |
| **PL-113** | Catalog & Case Study Docs | Complete catalog documentation (`report-catalog.md`) and architectural enterprise case study (`client-requirement-case-study.md`). |
