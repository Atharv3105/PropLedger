"""
PropLedger Synthetic Seed Data Generator (PRD Part N Scale)
Generates:
- System users (Admin, Managers, Accountants, Leasing, Techs)
- 50 Owners
- 500 Properties (Residential, Commercial, Mixed)
- ~1,200 Buildings
- ~3,500 Units
- ~2,500 Tenants & Contacts
- ~2,200 Leases (Active, Expiring, Terminated)
- ~10,000 Rent Charges & Payments
- ~1,500 Maintenance Requests & Work Orders
- 60 Vendors
- ~2,500 Operating Expenses
"""

import os
import sys
import random
from datetime import date, datetime, timedelta
import bcrypt
import psycopg2
from psycopg2.extras import execute_values
from faker import Faker

fake = Faker('en_IN')
Faker.seed(42)
random.seed(42)

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", 5432)),
    "user": os.environ.get("DB_USER", "postgres"),
    "password": os.environ.get("DB_PASSWORD", "postgres"),
    "dbname": os.environ.get("DB_NAME", "propledger")
}

def hash_pw(pw="Admin@123"):
    return bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt(10)).decode('utf-8')

CITIES = [
    ("Mumbai", "Maharashtra", "400001"),
    ("Pune", "Maharashtra", "411001"),
    ("Bengaluru", "Karnataka", "560001"),
    ("Hyderabad", "Telangana", "500001"),
    ("Delhi", "Delhi", "110001"),
    ("Chennai", "Tamil Nadu", "600001")
]

PROPERTY_NAMES = [
    "Greenwood Estate", "Skyline Towers", "Silver Oak Residency", "Regency Park",
    "Prestige Horizon", "Sobha Sapphire", "Godrej Woods", "DLF Cyber Heights",
    "Lodha Bellissimo", "Brigade Gateway", "Hiranandani Gardens", "Phoenix Palladium",
    "Embassy TechZone", "Oberoi Springs", "Puravankara Palm", "Shapoorji Pallonji Park",
    "Tata Primanti", "Mahindra Lifespaces", "K Raheja Vivarea", "Adani Shantigram"
]

def run_seed():
    print("=" * 60)
    print("PropLedger Synthetic Data Generation (Scale: 500+ Properties)")
    print("=" * 60)

    db_url = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")
    if db_url:
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        conn = psycopg2.connect(dsn=db_url)
    else:
        conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Clean previous domain data if present for clean idempotent rerun
    print("--> Clearing existing domain data for clean seed ...", end=" ", flush=True)
    cur.execute("""
        TRUNCATE TABLE 
            payment_allocations, late_fees, rent_charges, payments, tenant_balances, security_deposits,
            lease_tenants, lease_history, payment_audit, leases,
            maintenance_requests, work_orders, expenses, invoices, invoice_items,
            collection_activities, collection_cases, status_history, system_audit_log,
            tenant_contacts, tenants, units, buildings, properties, owners, vendors
        RESTART IDENTITY CASCADE;
    """)
    conn.commit()
    print("[OK]")

    default_pw_hash = hash_pw("Admin@123")

    # 1. Users & Roles
    print("--> Seeding Users and Roles ...", end=" ", flush=True)
    users_data = [
        ("admin@propledger.com", default_pw_hash, "System Administrator", "9876543210", 1),
    ]
    for i in range(1, 11):
        users_data.append((f"manager{i}@propledger.com", default_pw_hash, f"Property Manager {i}", f"98765432{i:02d}", 2))
    for i in range(1, 6):
        users_data.append((f"leasing{i}@propledger.com", default_pw_hash, f"Leasing Agent {i}", f"98765442{i:02d}", 3))
    for i in range(1, 6):
        users_data.append((f"accountant{i}@propledger.com", default_pw_hash, f"Senior Accountant {i}", f"98765452{i:02d}", 4))
    for i in range(1, 11):
        users_data.append((f"tech{i}@propledger.com", default_pw_hash, f"Maintenance Tech {i}", f"98765462{i:02d}", 5))

    execute_values(cur, """
        INSERT INTO users (email, password_hash, full_name, phone, is_active)
        VALUES %s
        ON CONFLICT (email) DO NOTHING
    """, [(u[0], u[1], u[2], u[3], True) for u in users_data])

    cur.execute("SELECT user_id, email FROM users;")
    user_map = {row[1]: row[0] for row in cur.fetchall()}
    admin_id = user_map["admin@propledger.com"]

    user_roles_data = []
    for u in users_data:
        uid = user_map.get(u[0])
        if uid:
            user_roles_data.append((uid, u[4], admin_id))
    execute_values(cur, """
        INSERT INTO user_roles (user_id, role_id, assigned_by)
        VALUES %s
        ON CONFLICT DO NOTHING
    """, user_roles_data)
    print(f"[OK] ({len(user_map)} users)")

    # 2. Owners (50)
    print("--> Seeding 50 Owners ...", end=" ", flush=True)
    owners_data = []
    for i in range(1, 51):
        c_name = fake.company() if random.random() > 0.4 else None
        owners_data.append((
            c_name,
            fake.name(),
            f"owner{i}_{fake.user_name()}@investors.com",
            fake.phone_number()[:20],
            f"PAN{fake.bothify(text='?????####?')}",
            fake.address(),
            admin_id
        ))
    execute_values(cur, """
        INSERT INTO owners (company_name, contact_name, email, phone, tax_id, address, created_by)
        VALUES %s
    """, owners_data)
    cur.execute("SELECT owner_id FROM owners;")
    owner_ids = [r[0] for r in cur.fetchall()]
    print(f"[OK] ({len(owner_ids)} owners)")

    # 3. Properties (500)
    print("--> Seeding 500 Properties ...", end=" ", flush=True)
    properties_data = []
    p_types = ["RESIDENTIAL", "COMMERCIAL", "MIXED"]
    p_weights = [0.65, 0.20, 0.15]

    for i in range(1, 501):
        ptype = random.choices(p_types, weights=p_weights)[0]
        city, state, pcode = random.choice(CITIES)
        base_name = random.choice(PROPERTY_NAMES)
        name = f"{base_name} Phase {((i - 1) % 5) + 1} - #{i}"
        code = f"PROP-{i:04d}"
        sqft = round(random.uniform(25000, 250000), 2)
        yr = random.randint(2005, 2024)
        owner_id = random.choice(owner_ids)

        properties_data.append((
            owner_id, code, name, ptype,
            fake.street_address(), city, state, pcode,
            sqft, yr, admin_id
        ))

    execute_values(cur, """
        INSERT INTO properties (owner_id, property_code, name, property_type, address_line1, city, state, postal_code, total_area_sqft, year_built, created_by)
        VALUES %s
        ON CONFLICT (property_code) DO NOTHING
    """, properties_data)
    cur.execute("SELECT property_id FROM properties ORDER BY property_id;")
    property_ids = [r[0] for r in cur.fetchall()]
    print(f"[OK] ({len(property_ids)} properties)")

    # 4. Buildings (~1,200)
    print("--> Seeding Buildings ...", end=" ", flush=True)
    buildings_data = []
    for pid in property_ids:
        num_bldgs = random.randint(2, 3)
        for b_idx in range(1, num_bldgs + 1):
            b_code = f"BLD-{pid}-{chr(64 + b_idx)}"
            b_name = f"Tower {chr(64 + b_idx)}" if num_bldgs > 1 else "Main Building"
            floors = random.randint(5, 20)
            buildings_data.append((pid, b_code, b_name, floors, admin_id))

    execute_values(cur, """
        INSERT INTO buildings (property_id, building_code, name, total_floors, created_by)
        VALUES %s
    """, buildings_data)
    cur.execute("SELECT building_id, total_floors FROM buildings ORDER BY building_id;")
    building_records = cur.fetchall()
    print(f"[OK] ({len(building_records)} buildings)")

    # 5. Units (~3,500)
    print("--> Seeding 3,500+ Units ...", end=" ", flush=True)
    unit_types_list = ["STUDIO", "1BHK", "2BHK", "3BHK", "OFFICE_SMALL", "OFFICE_LARGE", "RETAIL_SHOP"]
    unit_rents = {
        "STUDIO": (12000, 18000, 450),
        "1BHK": (18000, 26000, 650),
        "2BHK": (28000, 42000, 1050),
        "3BHK": (45000, 75000, 1600),
        "OFFICE_SMALL": (35000, 60000, 800),
        "OFFICE_LARGE": (80000, 200000, 3000),
        "RETAIL_SHOP": (40000, 90000, 900)
    }

    units_data = []
    for b_id, floors in building_records:
        units_in_bldg = random.randint(2, 4)
        for u_idx in range(1, units_in_bldg + 1):
            floor = random.randint(1, floors)
            u_number = f"{floor}{u_idx:02d}"
            utype = random.choices(unit_types_list, weights=[0.15, 0.35, 0.30, 0.10, 0.04, 0.03, 0.03])[0]
            min_r, max_r, avg_sqft = unit_rents[utype]
            m_rent = round(random.uniform(min_r, max_r) / 500) * 500
            sqft = round(avg_sqft * random.uniform(0.9, 1.15), 2)
            
            # Status distribution: Occupied 72%, Available 16%, Maintenance 7%, Reserved 5%
            ustatus = random.choices(
                ["OCCUPIED", "AVAILABLE", "MAINTENANCE", "RESERVED"],
                weights=[0.72, 0.16, 0.07, 0.05]
            )[0]

            units_data.append((
                b_id, u_number, floor, utype, sqft, m_rent, m_rent, ustatus, admin_id
            ))

    execute_values(cur, """
        INSERT INTO units (building_id, unit_number, floor_number, unit_type, square_feet, market_rent, target_rent, status, created_by)
        VALUES %s
        ON CONFLICT DO NOTHING
    """, units_data)
    cur.execute("SELECT unit_id, status, market_rent FROM units ORDER BY unit_id;")
    unit_records = cur.fetchall()
    print(f"[OK] ({len(unit_records)} units)")

    # 6. Tenants (~2,500) & Contacts
    print("--> Seeding 2,500 Tenants & Contacts ...", end=" ", flush=True)
    tenants_data = []
    for i in range(1, 2501):
        first = fake.first_name()
        last = fake.last_name()
        email = f"tenant_{i}_{first.lower()}.{last.lower()}@domain.com"
        phone = fake.phone_number()[:20]
        id_ref = f"AADHAAR-{fake.bothify(text='####-####-####')}"
        tax_id = f"PAN{fake.bothify(text='?????####?')}"
        dob = fake.date_of_birth(minimum_age=21, maximum_age=65)
        credit = random.randint(620, 850)
        em_name = fake.name()
        em_phone = fake.phone_number()[:20]

        tenants_data.append((
            first, last, email, phone, id_ref, tax_id, dob, credit, em_name, em_phone, admin_id
        ))

    execute_values(cur, """
        INSERT INTO tenants (first_name, last_name, email, phone, id_reference, tax_id, date_of_birth, credit_score, emergency_contact_name, emergency_contact_phone, created_by)
        VALUES %s
        ON CONFLICT (email) DO NOTHING
    """, tenants_data)
    cur.execute("SELECT tenant_id FROM tenants ORDER BY tenant_id;")
    tenant_ids = [r[0] for r in cur.fetchall()]

    contacts_data = []
    for tid in tenant_ids[:1000]:
        contacts_data.append((tid, fake.name(), random.choice(["Spouse", "Parent", "Sibling", "Colleague"]), fake.phone_number()[:20], fake.email(), True))
    execute_values(cur, """
        INSERT INTO tenant_contacts (tenant_id, contact_name, relationship, phone, email, is_emergency_contact)
        VALUES %s
    """, contacts_data)
    print(f"[OK] ({len(tenant_ids)} tenants)")

    # 7. Leases & LeaseTenants (~2,200)
    print("--> Seeding Leases & LeaseTenants ...", end=" ", flush=True)
    occupied_units = [u for u in unit_records if u[1] == 'OCCUPIED']
    leases_data = []
    lease_tenants_data = []
    tenant_idx = 0

    today = date.today()

    for u_id, status, m_rent in occupied_units:
        if tenant_idx >= len(tenant_ids):
            break
        t_id = tenant_ids[tenant_idx]
        tenant_idx += 1

        # Start dates between 14 months ago and 1 month ago
        start_offset = random.randint(30, 420)
        start_d = today - timedelta(days=start_offset)
        duration_months = random.choice([12, 24])
        end_d = start_d + timedelta(days=duration_months * 30)

        # Check BR-02
        if start_d > end_d:
            end_d = start_d + timedelta(days=365)

        # Status: Expiring if end_d within 60 days, else Active
        days_left = (end_d - today).days
        l_status = "EXPIRING" if 0 < days_left <= 60 else ("EXPIRED" if days_left <= 0 else "ACTIVE")
        sec_dep = round(float(m_rent) * random.choice([1.0, 2.0, 3.0]), 2)
        due_day = random.choice([1, 5])
        policy_id = random.choice([1, 2, 3])

        leases_data.append((
            u_id, start_d, end_d, float(m_rent), sec_dep, due_day, policy_id, l_status, "PENDING", admin_id
        ))

    execute_values(cur, """
        INSERT INTO leases (unit_id, start_date, end_date, monthly_rent, security_deposit, rent_due_day, late_fee_policy_id, status, renewal_status, created_by)
        VALUES %s
    """, leases_data)
    cur.execute("SELECT lease_id, unit_id, monthly_rent, start_date FROM leases ORDER BY lease_id;")
    lease_records = cur.fetchall()

    for idx, (l_id, u_id, m_rent, start_d) in enumerate(lease_records):
        t_id = tenant_ids[idx % len(tenant_ids)]
        lease_tenants_data.append((l_id, t_id, True))

    execute_values(cur, """
        INSERT INTO lease_tenants (lease_id, tenant_id, is_primary)
        VALUES %s
        ON CONFLICT DO NOTHING
    """, lease_tenants_data)
    print(f"[OK] ({len(lease_records)} leases)")

    # 8. Rent Charges, Payments, and Balances
    print("--> Seeding Rent Charges, Payments & Ledger ...", end=" ", flush=True)
    charges_data = []
    payments_data = []
    balances_data = []

    for l_id, u_id, m_rent, start_d in lease_records:
        t_id = tenant_ids[l_id % len(tenant_ids)]
        total_billed = 0.0
        total_paid = 0.0

        for m_back in [3, 2, 1]:
            chg_year = today.year if today.month > m_back else today.year - 1
            chg_month = today.month - m_back if today.month > m_back else 12 + (today.month - m_back)
            chg_date = date(chg_year, chg_month, 1)
            due_date = date(chg_year, chg_month, 5)

            pay_behavior = random.random()
            if pay_behavior > 0.35: # Fully paid
                c_status = "PAID"
                paid_amt = float(m_rent)
            elif pay_behavior > 0.15: # Partially paid
                c_status = "PARTIALLY_PAID"
                paid_amt = round(float(m_rent) * random.choice([0.4, 0.5, 0.6]), 2)
            else: # Unpaid / Overdue
                c_status = "OVERDUE"
                paid_amt = 0.0

            charges_data.append((
                l_id, chg_month, chg_year, chg_date, due_date, float(m_rent), paid_amt, c_status, admin_id
            ))
            total_billed += float(m_rent)
            total_paid += paid_amt

            if paid_amt > 0:
                payments_data.append((
                    l_id, due_date + timedelta(days=random.randint(0, 4)), paid_amt,
                    random.choice(["BANK_TRANSFER", "UPI", "CHECK"]),
                    f"REF-{l_id}-{chg_year}{chg_month:02d}", admin_id
                ))

        outstanding = round(total_billed - total_paid, 2)
        balances_data.append((
            t_id, l_id, total_billed, total_paid, 0.00, outstanding
        ))

    execute_values(cur, """
        INSERT INTO rent_charges (lease_id, billing_month, billing_year, charge_date, due_date, charge_amount, amount_paid, status, created_by)
        VALUES %s
        ON CONFLICT DO NOTHING
    """, charges_data)

    execute_values(cur, """
        INSERT INTO payments (lease_id, payment_date, amount, payment_method, reference_number, recorded_by)
        VALUES %s
    """, payments_data)

    execute_values(cur, """
        INSERT INTO tenant_balances (tenant_id, lease_id, total_billed, total_paid, total_late_fees, outstanding_balance)
        VALUES %s
        ON CONFLICT (lease_id) DO NOTHING
    """, balances_data)
    print(f"[OK] ({len(charges_data)} charges, {len(payments_data)} payments)")

    # 9. Vendors & Maintenance
    print("--> Seeding Vendors, Maintenance & Expenses ...", end=" ", flush=True)
    trades = ["PLUMBING", "ELECTRICAL", "HVAC", "ROOFING", "GENERAL", "LANDSCAPING", "ELEVATOR", "FIRE_SAFETY"]
    vendors_data = []
    for i in range(1, 61):
        v_trade = random.choice(trades)
        vendors_data.append((
            f"{fake.company()} {v_trade.title()} Services",
            v_trade, fake.name(), fake.phone_number()[:20], f"vendor{i}@{fake.domain_name()}",
            fake.address(), f"GST{fake.bothify(text='##?????####?#?#')}", admin_id
        ))
    execute_values(cur, """
        INSERT INTO vendors (company_name, trade_category, contact_name, phone, email, address, tax_id, created_by)
        VALUES %s
    """, vendors_data)
    cur.execute("SELECT vendor_id FROM vendors;")
    vendor_ids = [r[0] for r in cur.fetchall()]

    m_categories = ["Plumbing Leak", "HVAC Failure", "Electrical Short", "Appliance Repair", "Door Lock", "Ceiling Dampness"]
    maint_data = []
    for _ in range(1500):
        u_rec = random.choice(unit_records)
        m_cat = random.choice(m_categories)
        m_prior = random.choices(["LOW", "MEDIUM", "HIGH", "EMERGENCY"], weights=[0.3, 0.45, 0.2, 0.05])[0]
        m_stat = random.choices(["OPEN", "ASSIGNED", "IN_PROGRESS", "RESOLVED", "CLOSED"], weights=[0.15, 0.15, 0.20, 0.30, 0.20])[0]
        rep_date = today - timedelta(days=random.randint(1, 180))
        res_date = rep_date + timedelta(days=random.randint(1, 7)) if m_stat in ["RESOLVED", "CLOSED"] else None

        maint_data.append((
            u_rec[0], None, m_cat, m_prior, fake.sentence(nb_words=10), m_stat, rep_date, res_date,
            "Issue verified and rectified." if res_date else None, admin_id
        ))

    execute_values(cur, """
        INSERT INTO maintenance_requests (unit_id, tenant_id, category, priority, description, status, reported_date, resolved_date, resolution_notes, created_by)
        VALUES %s
    """, maint_data)

    # 10. Expenses
    expenses_data = []
    exp_cats = ["MAINTENANCE", "UTILITIES", "ADMIN", "INSURANCE", "TAXES", "CLEANING"]
    for pid in property_ids:
        for _ in range(random.randint(3, 6)):
            cat = random.choice(exp_cats)
            amt = round(random.uniform(5000, 75000), 2)
            e_date = today - timedelta(days=random.randint(1, 120))
            expenses_data.append((
                pid, random.choice(vendor_ids), cat, amt, e_date, f"{cat} expense for property", admin_id
            ))

    execute_values(cur, """
        INSERT INTO expenses (property_id, vendor_id, category, amount, expense_date, description, created_by)
        VALUES %s
    """, expenses_data)
    print(f"[OK] (60 vendors, 1500 maintenance, {len(expenses_data)} expenses)")

    conn.commit()
    cur.close()
    conn.close()
    print("=" * 60)
    print("Synthetic Seed Generation Completed Successfully!")
    print("=" * 60)

if __name__ == "__main__":
    run_seed()
