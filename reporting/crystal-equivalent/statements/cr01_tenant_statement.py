"""
CR-01 / PL-114: Formal Tenant Billing & Payment History Statement.
Institutional customer statement with dual address frames, double-entry ledger,
aging analysis, and detachable perforated remittance advice slip.
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether

try:
    from crystal_engine.banded_report import BandedReport
except ImportError:
    from crystal_engine.banded_report import BandedReport


class TenantStatementReport(BandedReport):
    statement_code = "CR-01"
    title = "Tenant Statement of Account & Rent Demand"
    category = "Accounting & Billing Statements"
    description = (
        "Formal tenant billing and payment history statement with itemized charges, "
        "reconciliation ledger, arrears aging summary, and detachable remittance slip."
    )
    orientation = "portrait"
    has_remittance_slip = True
    watermark_text = "OFFICIAL STATEMENT"

    parameters = {
        "tenant_id": {"type": "int", "default": 1, "required": False, "description": "Tenant ID to generate statement for"},
        "lease_id": {"type": "int", "default": None, "required": False, "description": "Optional Lease ID filter"},
    }

    def fetch_data(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        p = self.validate_params(params)
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # 1. Fetch tenant, active lease, and unit info
                cur.execute("""
                    SELECT 
                        t.tenant_id,
                        t.first_name || ' ' || t.last_name AS tenant_name,
                        t.email,
                        t.phone,
                        t.tax_id AS pan_number,
                        p.name AS property_name,
                        p.address_line1,
                        p.city,
                        p.state,
                        p.postal_code,
                        b.name AS building_name,
                        u.unit_number,
                        u.unit_type,
                        l.lease_id,
                        l.start_date,
                        l.end_date,
                        l.monthly_rent,
                        l.security_deposit,
                        l.rent_due_day,
                        l.status AS lease_status
                    FROM tenants t
                    JOIN lease_tenants lt ON t.tenant_id = lt.tenant_id AND lt.is_primary = TRUE
                    JOIN leases l ON lt.lease_id = l.lease_id
                    JOIN units u ON l.unit_id = u.unit_id
                    JOIN buildings b ON u.building_id = b.building_id
                    JOIN properties p ON b.property_id = p.property_id
                    WHERE (%(tenant_id)s IS NULL OR t.tenant_id = %(tenant_id)s)
                      AND (%(lease_id)s IS NULL OR l.lease_id = %(lease_id)s)
                    ORDER BY l.start_date DESC
                    LIMIT 1;
                """, p)
                tenant_info = cur.fetchone()
                if not tenant_info:
                    # Fallback to first available lease if tenant_id didn't match
                    cur.execute("""
                        SELECT 
                            t.tenant_id,
                            t.first_name || ' ' || t.last_name AS tenant_name,
                            t.email,
                            t.phone,
                            t.tax_id AS pan_number,
                            p.name AS property_name,
                            p.address_line1,
                            p.city,
                            p.state,
                            p.postal_code,
                            b.name AS building_name,
                            u.unit_number,
                            u.unit_type,
                            l.lease_id,
                            l.start_date,
                            l.end_date,
                            l.monthly_rent,
                            l.security_deposit,
                            l.rent_due_day,
                            l.status AS lease_status
                        FROM leases l
                        JOIN units u ON l.unit_id = u.unit_id
                        JOIN buildings b ON u.building_id = b.building_id
                        JOIN properties p ON b.property_id = p.property_id
                        JOIN lease_tenants lt ON l.lease_id = lt.lease_id AND lt.is_primary = TRUE
                        JOIN tenants t ON lt.tenant_id = t.tenant_id
                        WHERE l.status = 'ACTIVE'
                        LIMIT 1;
                    """)
                    tenant_info = cur.fetchone()

                lease_id = tenant_info["lease_id"]

                # 2. Fetch line-item ledger
                cur.execute("""
                    WITH raw_events AS (
                        SELECT 
                            rc.charge_date AS txn_date,
                            'INV-' || rc.charge_id AS ref_no,
                            'Rent Assessment (' || TO_CHAR(rc.charge_date, 'Mon YYYY') || ')' AS description,
                            rc.charge_amount AS debit,
                            0.00 AS credit,
                            1 AS sort_order
                        FROM rent_charges rc
                        WHERE rc.lease_id = %(lease_id)s
                        UNION ALL
                        SELECT 
                            p.payment_date AS txn_date,
                            COALESCE(p.reference_number, 'RCT-' || p.payment_id) AS ref_no,
                            'Payment Received — ' || p.payment_method AS description,
                            0.00 AS debit,
                            p.amount AS credit,
                            2 AS sort_order
                        FROM payments p
                        WHERE p.lease_id = %(lease_id)s
                    )
                    SELECT 
                        txn_date,
                        ref_no,
                        description,
                        debit,
                        credit,
                        SUM(debit - credit) OVER (ORDER BY txn_date, sort_order) AS balance
                    FROM raw_events
                    ORDER BY txn_date ASC, sort_order ASC
                    LIMIT 20;
                """, {"lease_id": lease_id})
                ledger_rows = [dict(r) for r in cur.fetchall()]

                # 3. Calculate aging buckets
                cur.execute("""
                    SELECT 
                        COALESCE(SUM(CASE WHEN CURRENT_DATE - rc.due_date <= 30 THEN (rc.charge_amount - rc.amount_paid) ELSE 0 END), 0) AS cur_30,
                        COALESCE(SUM(CASE WHEN CURRENT_DATE - rc.due_date BETWEEN 31 AND 60 THEN (rc.charge_amount - rc.amount_paid) ELSE 0 END), 0) AS age_60,
                        COALESCE(SUM(CASE WHEN CURRENT_DATE - rc.due_date BETWEEN 61 AND 90 THEN (rc.charge_amount - rc.amount_paid) ELSE 0 END), 0) AS age_90,
                        COALESCE(SUM(CASE WHEN CURRENT_DATE - rc.due_date > 90 THEN (rc.charge_amount - rc.amount_paid) ELSE 0 END), 0) AS age_90_plus,
                        COALESCE(SUM(rc.charge_amount - rc.amount_paid), 0) AS total_overdue
                    FROM rent_charges rc
                    WHERE rc.lease_id = %(lease_id)s
                      AND rc.status != 'PAID';
                """, {"lease_id": lease_id})
                aging_info = cur.fetchone()

        return {
            "tenant": dict(tenant_info) if tenant_info else {},
            "ledger": ledger_rows,
            "aging": dict(aging_info) if aging_info else {},
            "statement_date": datetime.now().strftime("%d-%b-%Y"),
            "due_date": datetime.now().strftime("05-%b-%Y"),
        }

    def build_statement_story(self, data: Dict[str, Any], usable_width: float) -> List[Any]:
        story = []
        t = data["tenant"]
        aging = data["aging"]
        ledger = data["ledger"]

        # -------------------------------------------------------------
        # BAND 1: REPORT HEADER (RH) — Corporate Letterhead & Document Title
        # -------------------------------------------------------------
        issuer_content = [
            Paragraph("<b>PROPLEDGER ENTERPRISE ASSET HOLDINGS</b>", self.style_issuer_title),
            Paragraph("Property Management & Financial Recovery Division", self.style_meta_label),
            Paragraph("Tower A, Financial District, Gachibowli, Hyderabad 500032", self.style_meta_val),
            Paragraph("GSTIN: 36AAACP1234F1Z8 | CIN: U70100TG2022PTC154876", self.style_meta_val),
        ]
        title_content = [
            Paragraph("STATEMENT OF ACCOUNT", self.style_doc_title),
            Paragraph(f"<b>Statement #:</b> STMT-{t.get('lease_id', 1000):06d}", self.style_meta_val),
            Paragraph(f"<b>Date Issued:</b> {data['statement_date']}", self.style_meta_val),
            Paragraph(f"<b>Rent Due Date:</b> {data['due_date']}", self.style_meta_val),
        ]
        hdr_table = Table([[issuer_content, title_content]], colWidths=[usable_width * 0.55, usable_width * 0.45])
        hdr_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        story.append(hdr_table)
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1E3A8A"), spaceAfter=10, spaceBefore=6))

        # -------------------------------------------------------------
        # BAND 2: PAGE HEADER (PH) — Dual Recipient & Tenancy Frames
        # -------------------------------------------------------------
        bill_to_box = [
            Paragraph("<b>BILLED TO (TENANT):</b>", self.style_meta_label),
            Paragraph(f"<b>{t.get('tenant_name', 'Valued Resident')}</b>", ParagraphStyle("TN", parent=self.style_meta_val, fontName="Helvetica-Bold", fontSize=9)),
            Paragraph(f"Unit {t.get('unit_number', '-')}, {t.get('building_name', '-')}", self.style_meta_val),
            Paragraph(f"{t.get('property_name', '-')}, {t.get('city', '-')}, {t.get('state', '-')} {t.get('postal_code', '-')}", self.style_meta_val),
            Paragraph(f"Email: {t.get('email', '-')} | Phone: {t.get('phone', '-')}", self.style_meta_val),
        ]
        tenancy_box = [
            Paragraph("<b>TENANCY DETAILS:</b>", self.style_meta_label),
            Paragraph(f"<b>Lease Agreement:</b> LEASE-{t.get('lease_id', 0):05d} ({t.get('lease_status', 'ACTIVE')})", self.style_meta_val),
            Paragraph(f"<b>Lease Term:</b> {t.get('start_date', '-')} to {t.get('end_date', '-')}", self.style_meta_val),
            Paragraph(f"<b>Contract Monthly Rent:</b> Rs. {float(t.get('monthly_rent') or 0):,.2f}", self.style_meta_val),
            Paragraph(f"<b>Security Deposit Held:</b> Rs. {float(t.get('security_deposit') or 0):,.2f}", self.style_meta_val),
        ]

        party_table = Table([[bill_to_box, tenancy_box]], colWidths=[usable_width * 0.52, usable_width * 0.48])
        party_table.setStyle(TableStyle([
            ("BOX", (0, 0), (0, 0), 0.75, colors.HexColor("#CBD5E1")),
            ("BOX", (1, 0), (1, 0), 0.75, colors.HexColor("#CBD5E1")),
            ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#F8FAFC")),
            ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#F8FAFC")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(party_table)
        story.append(Spacer(1, 10))

        # -------------------------------------------------------------
        # BAND 3: FINANCIAL RECAP BAR (Summary Metrics)
        # -------------------------------------------------------------
        tot_overdue = float(aging.get("total_overdue") or 0)
        recap_cells = [
            [
                Paragraph("<b>PREVIOUS BALANCE</b>", self.style_cell_center),
                Paragraph("<b>CURRENT CHARGES</b>", self.style_cell_center),
                Paragraph("<b>CREDITS APPLIED</b>", self.style_cell_center),
                Paragraph("<b>TOTAL DUE NOW</b>", self.style_cell_center),
            ],
            [
                Paragraph("Rs. 0.00", self.style_cell_center),
                Paragraph(f"Rs. {float(t.get('monthly_rent') or 0):,.2f}", self.style_cell_center),
                Paragraph("Rs. 0.00", self.style_cell_center),
                Paragraph(f"<b>Rs. {tot_overdue:,.2f}</b>", ParagraphStyle("TotDue", parent=self.style_cell_center, fontSize=11, fontName="Helvetica-Bold", textColor=colors.HexColor("#991B1B"))),
            ]
        ]
        recap_table = Table(recap_cells, colWidths=[usable_width * 0.25] * 4)
        recap_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
            ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#EFF6FF")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#94A3B8")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(recap_table)
        story.append(Spacer(1, 10))

        # -------------------------------------------------------------
        # BAND 4: DETAILS (D) — Itemized Transaction Ledger
        # -------------------------------------------------------------
        story.append(Paragraph("<b>ACCOUNT ACTIVITY & TRANSACTION LEDGER</b>", ParagraphStyle("LedgerTitle", parent=self.style_meta_label, fontSize=8.5, textColor=colors.HexColor("#1E3A8A"))))
        story.append(Spacer(1, 3))

        ledger_headers = [
            Paragraph("<b>Date</b>", self.style_tbl_hdr),
            Paragraph("<b>Reference</b>", self.style_tbl_hdr),
            Paragraph("<b>Transaction Description</b>", self.style_tbl_hdr),
            Paragraph("<b>Charges (Dr)</b>", self.style_tbl_hdr_right),
            Paragraph("<b>Payments (Cr)</b>", self.style_tbl_hdr_right),
            Paragraph("<b>Balance</b>", self.style_tbl_hdr_right),
        ]
        ledger_table_data = [ledger_headers]

        for r in ledger:
            ledger_table_data.append([
                Paragraph(str(r.get("txn_date", "")), self.style_cell_center),
                Paragraph(str(r.get("ref_no", "")), self.style_cell_left),
                Paragraph(str(r.get("description", "")), self.style_cell_left),
                Paragraph(f"Rs. {float(r.get('debit') or 0):,.2f}" if float(r.get("debit") or 0) > 0 else "-", self.style_cell_right),
                Paragraph(f"Rs. {float(r.get('credit') or 0):,.2f}" if float(r.get("credit") or 0) > 0 else "-", self.style_cell_right),
                Paragraph(f"<b>Rs. {float(r.get('balance') or 0):,.2f}</b>", self.style_cell_right),
            ])

        col_w = [usable_width * 0.13, usable_width * 0.15, usable_width * 0.36, usable_width * 0.12, usable_width * 0.12, usable_width * 0.12]
        ledger_table = Table(ledger_table_data, colWidths=col_w)
        ledger_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(ledger_table)
        story.append(Spacer(1, 8))

        # -------------------------------------------------------------
        # BAND 5: AGING BUCKETS ANALYSIS (GF)
        # -------------------------------------------------------------
        aging_cells = [
            [
                Paragraph("<b>Current (1-30d)</b>", self.style_cell_center),
                Paragraph("<b>31 - 60 Days</b>", self.style_cell_center),
                Paragraph("<b>61 - 90 Days</b>", self.style_cell_center),
                Paragraph("<b>Over 90 Days</b>", self.style_cell_center),
                Paragraph("<b>Total Outstanding</b>", self.style_cell_center),
            ],
            [
                Paragraph(f"Rs. {float(aging.get('cur_30') or 0):,.2f}", self.style_cell_center),
                Paragraph(f"Rs. {float(aging.get('age_60') or 0):,.2f}", self.style_cell_center),
                Paragraph(f"Rs. {float(aging.get('age_90') or 0):,.2f}", self.style_cell_center),
                Paragraph(f"Rs. {float(aging.get('age_90_plus') or 0):,.2f}", self.style_cell_center),
                Paragraph(f"<b>Rs. {tot_overdue:,.2f}</b>", ParagraphStyle("TotOut", parent=self.style_cell_center, fontName="Helvetica-Bold", textColor=colors.HexColor("#991B1B"))),
            ]
        ]
        aging_table = Table(aging_cells, colWidths=[usable_width * 0.2] * 5)
        aging_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
            ("BACKGROUND", (0, 1), (-1, 1), colors.white),
            ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#94A3B8")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(aging_table)
        story.append(Spacer(1, 10))

        # -------------------------------------------------------------
        # BAND 6: REPORT FOOTER (RF) — Settlement Bank Details & Notice
        # -------------------------------------------------------------
        bank_instructions = [
            Paragraph("<b>SETTLEMENT INSTRUCTIONS & WIRE DETAILS:</b>", self.style_meta_label),
            Paragraph("Beneficiary: <b>PropLedger Enterprise Collections Account</b>", self.style_cell_left),
            Paragraph("Bank Name: HDFC Bank Ltd | Account #: 50200084920192 | IFSC: HDFC0001234", self.style_cell_left),
            Paragraph("UPI ID: propledger@hdfcbank | Remittance Reference: LEASE-" + str(t.get('lease_id', 0)), self.style_cell_left),
        ]
        notice_box = [
            Paragraph("<b>NOTICE TO TENANT:</b>", self.style_meta_label),
            Paragraph("Rent is strictly payable on or before the due date. Payments received after the 5-day grace period incur late penalties per policy BR-05. Direct all accounting inquiries to accounts@propledger.com.", self.style_cell_left),
        ]
        notes_table = Table([[bank_instructions, notice_box]], colWidths=[usable_width * 0.5, usable_width * 0.5])
        notes_table.setStyle(TableStyle([
            ("BOX", (0, 0), (0, 0), 0.5, colors.HexColor("#CBD5E1")),
            ("BOX", (1, 0), (1, 0), 0.5, colors.HexColor("#CBD5E1")),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(notes_table)
        story.append(Spacer(1, 10))

        # -------------------------------------------------------------
        # BAND 7: PAGE FOOTER (PF) — Perforated Tear-off Remittance Slip
        # -------------------------------------------------------------
        remit_header = Paragraph(
            "✂ - - - - - - - - - - - - - - - - PLEASE DETACH AND RETURN WITH YOUR PAYMENT - - - - - - - - - - - - - - - - ✂",
            ParagraphStyle("CutLine", parent=self.style_cell_center, fontSize=7, textColor=colors.HexColor("#64748B"))
        )
        slip_data = [
            [
                Paragraph("<b>PROPLEDGER REMITTANCE ADVICE</b>", self.style_issuer_title),
                Paragraph(f"<b>Statement #:</b> STMT-{t.get('lease_id', 0):06d}", self.style_cell_right),
            ],
            [
                Paragraph(f"<b>Tenant:</b> {t.get('tenant_name', '')} (ID: {t.get('tenant_id', '')})<br/>Unit: {t.get('unit_number', '')}, {t.get('property_name', '')}", self.style_cell_left),
                Paragraph(f"<b>Amount Due:</b> Rs. {tot_overdue:,.2f}<br/><b>Due Date:</b> {data['due_date']}<br/><b>Amount Enclosed:</b> Rs. [____________]", self.style_cell_right),
            ]
        ]
        slip_table = Table(slip_data, colWidths=[usable_width * 0.55, usable_width * 0.45])
        slip_table.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#94A3B8")),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))

        story.append(KeepTogether([
            remit_header,
            Spacer(1, 4),
            slip_table,
        ]))

        return story
