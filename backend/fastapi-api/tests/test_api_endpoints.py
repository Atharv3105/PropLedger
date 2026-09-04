import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import init_db_pool, close_db_pool
import sys

sys.stdout.reconfigure(encoding='utf-8')

client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown():
    init_db_pool()
    yield
    close_db_pool()

def get_auth_token(email: str, password: str = "Admin@123") -> str:
    res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, f"Login failed for {email}: {res.text}"
    return res.json()["access_token"]

# 1. Health & Diagnostics
def test_health_check_endpoint():
    res = client.get("/api/v1/diagnostics/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "HEALTHY"
    assert data["database"]["status"] == "connected"
    assert data["database"]["table_count"] > 30

# 2. Authentication
def test_auth_valid_login():
    res = client.post("/api/v1/auth/login", json={"email": "admin@propledger.com", "password": "Admin@123"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert "ADMIN" in data["roles"]

def test_auth_invalid_credentials():
    res = client.post("/api/v1/auth/login", json={"email": "admin@propledger.com", "password": "WrongPassword!"})
    assert res.status_code == 401
    data = res.json()
    assert data["code"] == "UNAUTHORIZED"

def test_auth_me_endpoint():
    token = get_auth_token("admin@propledger.com")
    res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == "admin@propledger.com"
    assert "ADMIN" in data["roles"]
    assert len(data["permissions"]) > 0

# 3. RBAC Enforcement (Rule BR-09)
def test_rbac_accountant_allowed_on_finance():
    token = get_auth_token("accountant1@propledger.com")
    res = client.get("/api/v1/finance/financial-summary", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_rbac_tenant_forbidden_on_finance():
    token = get_auth_token("tenant1@propledger.com")
    res = client.get("/api/v1/finance/financial-summary", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403
    data = res.json()
    assert data["code"] == "FORBIDDEN_ACTION"

# 4. Properties API
def test_list_properties():
    token = get_auth_token("admin@propledger.com")
    res = client.get("/api/v1/properties?limit=10", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    props = res.json()
    assert len(props) > 0
    first_prop = props[0]
    assert "property_id" in first_prop
    assert "property_name" in first_prop
    assert first_prop["total_units"] >= 0

def test_get_property_occupancy():
    token = get_auth_token("admin@propledger.com")
    res = client.get("/api/v1/properties/1/occupancy", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["property_id"] == 1
    assert "occupancy_rate_pct" in data

# 5. Units & Tenants
def test_list_units():
    token = get_auth_token("admin@propledger.com")
    res = client.get("/api/v1/units?limit=5", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    units = res.json()
    assert len(units) > 0

def test_list_tenants_and_balances():
    token = get_auth_token("admin@propledger.com")
    res = client.get("/api/v1/tenants?limit=5", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    tenants = res.json()
    assert len(tenants) > 0
    first_tenant_id = tenants[0]["tenant_id"]

    bal_res = client.get(f"/api/v1/tenants/{first_tenant_id}/balance", headers={"Authorization": f"Bearer {token}"})
    assert bal_res.status_code == 200
    bal_data = bal_res.json()
    assert "outstanding_balance" in bal_data

# 6. Active Leases & Leases API
def test_list_active_leases():
    token = get_auth_token("admin@propledger.com")
    res = client.get("/api/v1/leases/active?limit=10", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    leases = res.json()
    assert len(leases) > 0
    assert "lease_number" in leases[0]
    assert "is_renewal" in leases[0]

def test_lease_renewal_date_validation():
    token = get_auth_token("admin@propledger.com")
    payload = {
        "new_start_date": "2027-01-01",
        "new_end_date": "2026-01-01",
        "new_monthly_rent": 30000.00
    }
    res = client.post("/api/v1/leases/1/renew", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 422
    data = res.json()
    assert data["code"] == "REQUEST_VALIDATION_FAILED"

# 7. Payments API & Business Rule BR-10
def test_payment_negative_amount_rejected():
    token = get_auth_token("admin@propledger.com")
    payload = {
        "lease_id": 1,
        "amount": -500.00,
        "payment_method_id": 1
    }
    res = client.post("/api/v1/payments", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 422
    data = res.json()
    assert data["code"] == "REQUEST_VALIDATION_FAILED"

def test_payment_recording_with_fifo_allocation():
    token = get_auth_token("admin@propledger.com")
    leases_res = client.get("/api/v1/leases/active?limit=1", headers={"Authorization": f"Bearer {token}"})
    active_lease = leases_res.json()[0]
    lease_id = active_lease["lease_id"]

    payload = {
        "lease_id": lease_id,
        "amount": 250.00,
        "payment_method_id": 1,
        "reference_number": f"TEST-PAY-{lease_id}"
    }
    res = client.post("/api/v1/payments", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 201
    pay_data = res.json()
    assert pay_data["payment_id"] > 0
    assert pay_data["lease_id"] == lease_id
    assert float(pay_data["amount_paid"]) == 250.00
    assert "remaining_balance" in pay_data

# 8. Delinquency & Collections
def test_delinquency_report_endpoint():
    token = get_auth_token("admin@propledger.com")
    res = client.get("/api/v1/collections/delinquent", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    delinq = res.json()
    assert isinstance(delinq, list)
    if len(delinq) > 0:
        item = delinq[0]
        assert "total_delinquent_balance" in item
        assert "max_overdue_days" in item
        assert "current_0_30" in item

# 9. Maintenance API
def test_list_maintenance_requests():
    token = get_auth_token("admin@propledger.com")
    res = client.get("/api/v1/maintenance?limit=5", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    requests = res.json()
    assert len(requests) > 0

# 10. Advanced SQL Reporting Endpoints
def test_asset_hierarchy_cte_report():
    token = get_auth_token("admin@propledger.com")
    res = client.get("/api/v1/reports/hierarchy?max_level=3", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    nodes = res.json()
    assert len(nodes) > 0
    assert "hierarchy_path" in nodes[0]
    assert "depth_level" in nodes[0]

def test_monthly_rent_pivot_report():
    token = get_auth_token("admin@propledger.com")
    res = client.get("/api/v1/reports/rent-pivot?limit=10", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    pivots = res.json()
    assert len(pivots) > 0
    assert "annual_total_collected" in pivots[0]
    assert "jan_collected" in pivots[0]


# 11. Workflow Endpoint: Lease Renewal
def test_lease_renewal_execution():
    token = get_auth_token("admin@propledger.com")
    leases_res = client.get("/api/v1/leases/active?limit=5", headers={"Authorization": f"Bearer {token}"})
    assert leases_res.status_code == 200
    leases = leases_res.json()
    assert len(leases) > 0
    target_lease_id = leases[0]["lease_id"]

    payload = {
        "new_start_date": "2026-10-01",
        "new_end_date": "2027-09-30",
        "new_monthly_rent": 35000.00
    }
    res = client.post(f"/api/v1/leases/{target_lease_id}/renew", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert "new_lease_id" in data
    assert data["predecessor_lease_id"] == target_lease_id
    assert "Successfully renewed" in data["message"]

# 12. Workflow Endpoint: Generate Monthly Rent
def test_generate_monthly_rent():
    token = get_auth_token("admin@propledger.com")
    payload = {
        "billing_month": 9,
        "billing_year": 2026
    }
    res = client.post("/api/v1/billing/generate-monthly", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["billing_month"] == 9
    assert data["billing_year"] == 2026
    assert "charges_created" in data

# 13. Workflow Endpoint: Maintenance Reopening (Rule BR-08)
def test_reopen_maintenance_request():
    token = get_auth_token("admin@propledger.com")
    # First query for a closed request or list requests
    reqs_res = client.get("/api/v1/maintenance?limit=50", headers={"Authorization": f"Bearer {token}"})
    assert reqs_res.status_code == 200
    requests = reqs_res.json()
    closed_reqs = [r for r in requests if r["status"] == "CLOSED"]
    
    if closed_reqs:
        req_id = closed_reqs[0]["request_id"]
        payload = {"reopen_reason": "Tenant reported recurrence of leak after technician left"}
        res = client.post(f"/api/v1/maintenance/{req_id}/reopen", json=payload, headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        data = res.json()
        assert data["request_id"] == req_id
        assert data["new_status"] == "OPEN"
    else:
        # If none closed, ensure reopening non-existent returns 400/422/404
        res = client.post("/api/v1/maintenance/999999/reopen", json={"reopen_reason": "Valid reason with enough length"}, headers={"Authorization": f"Bearer {token}"})
        assert res.status_code in [400, 404, 422]

# 14. Tenant Payment History Endpoint (Window Functions)
def test_tenant_payment_history_window_functions():
    token = get_auth_token("admin@propledger.com")
    # Get a tenant
    tenants_res = client.get("/api/v1/tenants?limit=1", headers={"Authorization": f"Bearer {token}"})
    tenant_id = tenants_res.json()[0]["tenant_id"]

    res = client.get(f"/api/v1/payments/history/{tenant_id}", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    history = res.json()
    assert isinstance(history, list)
    if len(history) > 0:
        item = history[0]
        assert "payment_rank" in item
        assert "running_total_paid" in item
        assert "payment_amount" in item

# 15. Expenses & Financial Summaries
def test_finance_expenses_endpoint():
    token = get_auth_token("admin@propledger.com")
    res = client.get("/api/v1/finance/expenses?limit=10", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    expenses = res.json()
    assert len(expenses) > 0
    assert "amount" in expenses[0]
    assert "property_name" in expenses[0]

# 16. Diagnostics Incidents Log
def test_diagnostics_incidents_endpoint():
    token = get_auth_token("admin@propledger.com")
    res = client.get("/api/v1/diagnostics/incidents", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert "incident_count" in data
    assert "recent_incidents" in data
