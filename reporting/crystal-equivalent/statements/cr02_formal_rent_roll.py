"""
CR-02 / PL-115: Formal Columnar Property Rent Roll Statement.
Institutional investor/lender rent roll featuring multi-level hierarchical grouping,
subtotals, physical vs. economic occupancy reconciliation, and certification signature blocks.
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


class FormalRentRollStatement(BandedReport):
    statement_code = "CR-02"
    title = "Formal Property Rent Roll & Tenancy Certification"
    category = "Investor & Institutional Audit"
    description = (
        "Multi-tier formal columnar rent roll with building subtotals, physical vs. "
        "economic occupancy reconciliation, and executive signature audit blocks."
    )
    orientation = "landscape"
    has_remittance_slip = False
    watermark_text = "CERTIFIED AUDIT"

    parameters = {
        "property_id": {"type": "int", "default": 1, "required": False, "description": "Property ID to audit"},
        "limit": {"type": "int", "default": 100, "required": False, "description": "Maximum units to audit"},
    }

    def fetch_data(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        p = self.validate_params(params)
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # 1. Fetch property metadata
                cur.execute("""
                    SELECT 
                        p.property_id,
                        p.property_code,
                        p.name AS property_name,
                        p.property_type,
                        p.address_line1,
                        p.city,
                        p.state,
                        p.postal_code,
                        p.total_area_sqft,
                        p.year_built,
                        COALESCE(o.company_name, o.contact_name) AS owner_name
                    FROM properties p
                    LEFT JOIN owners o ON p.owner_id = o.owner_id
                    WHERE (%(property_id)s IS NULL OR p.property_id = %(property_id)s)
                    LIMIT 1;
                """, p)
                prop_meta = cur.fetchone()
                if not prop_meta:
                    cur.execute("SELECT property_id, property_code, name AS property_name, property_type, city, total_area_sqft, year_built FROM properties LIMIT 1;")
                    prop_meta = cur.fetchone()

                prop_id = prop_meta["property_id"]

                # 2. Fetch units grouped by building
                cur.execute("""
                    SELECT 
                        b.building_id,
                        b.name AS building_name,
                        u.unit_id,
                        u.unit_number,
                        u.unit_type,
                        u.square_feet,
                        u.market_rent,
                        COALESCE(l.monthly_rent, 0) AS contracted_rent,
                        COALESCE(t.first_name || ' ' || t.last_name, '— VACANT —') AS tenant_name,
                        l.start_date,
                        l.end_date,
                        u.status AS unit_status
                    FROM units u
                    JOIN buildings b ON u.building_id = b.building_id
                    LEFT JOIN leases l ON u.unit_id = l.unit_id AND l.status = 'ACTIVE'
                    LEFT JOIN lease_tenants lt ON l.lease_id = lt.lease_id AND lt.is_primary = TRUE
                    LEFT JOIN tenants t ON lt.tenant_id = t.tenant_id
                    WHERE b.property_id = %(property_id)s
                    ORDER BY b.name, u.floor_number, u.unit_number
                    LIMIT %(limit)s;
                """, {"property_id": prop_id, "limit": p.get("limit", 100)})
                units = [dict(r) for r in cur.fetchall()]

        # Organize into building groups
        buildings_dict = {}
        for u in units:
            bname = u["building_name"]
            if bname not in buildings_dict:
                buildings_dict[bname] = []
            buildings_dict[bname].append(u)

        return {
            "property": dict(prop_meta),
            "buildings": buildings_dict,
            "audit_date": datetime.now().strftime("%d-%b-%Y"),
            "effective_period": datetime.now().strftime("Month of %B %Y"),
        }

    def build_statement_story(self, data: Dict[str, Any], usable_width: float) -> List[Any]:
        story = []
        p = data["property"]
        buildings = data["buildings"]

        # -------------------------------------------------------------
        # BAND 1: REPORT HEADER (RH) — Institutional Audit Header
        # -------------------------------------------------------------
        left_header = [
            Paragraph("<b>PROPLEDGER REAL ESTATE CAPITAL ADVISORS</b>", self.style_issuer_title),
            Paragraph("Institutional Portfolio Asset Audit & Valuation Practice", self.style_meta_label),
            Paragraph("Certified Columnar Rent Roll & Tenancy Schedule", self.style_meta_val),
        ]
        right_header = [
            Paragraph("FORMAL CERTIFIED RENT ROLL", self.style_doc_title),
            Paragraph(f"<b>Audit Date:</b> {data['audit_date']} &nbsp;|&nbsp; <b>Cycle:</b> {data['effective_period']}", self.style_meta_val),
            Paragraph(f"<b>Property Code:</b> {p.get('property_code')} &nbsp;|&nbsp; <b>Asset Type:</b> {p.get('property_type')}", self.style_meta_val),
        ]
        hdr_table = Table([[left_header, right_header]], colWidths=[usable_width * 0.5, usable_width * 0.5])
        hdr_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        story.append(hdr_table)
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1E3A8A"), spaceAfter=8, spaceBefore=4))

        # -------------------------------------------------------------
        # BAND 2: PAGE HEADER (PH) — Asset Profile Summary Box
        # -------------------------------------------------------------
        prop_profile = [
            [
                Paragraph(f"<b>Asset Name:</b> {p.get('property_name')}", self.style_cell_left),
                Paragraph(f"<b>Location:</b> {p.get('city')}, {p.get('state')}", self.style_cell_left),
                Paragraph(f"<b>Year Built:</b> {p.get('year_built')}", self.style_cell_left),
                Paragraph(f"<b>Total Gross Area:</b> {float(p.get('total_area_sqft') or 0):,.0f} Sq.Ft.", self.style_cell_left),
            ]
        ]
        prof_table = Table(prop_profile, colWidths=[usable_width * 0.32, usable_width * 0.28, usable_width * 0.18, usable_width * 0.22])
        prof_table.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#CBD5E1")),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(prof_table)
        story.append(Spacer(1, 8))

        # -------------------------------------------------------------
        # BAND 3 & 4 & 5: HIERARCHICAL GROUP HEADERS, DETAILS & GROUP FOOTERS
        # -------------------------------------------------------------
        tbl_widths = [
            usable_width * 0.08,  # Unit #
            usable_width * 0.11,  # Type
            usable_width * 0.09,  # Sq.Ft.
            usable_width * 0.24,  # Tenant
            usable_width * 0.10,  # Start
            usable_width * 0.10,  # End
            usable_width * 0.13,  # Market Rent
            usable_width * 0.15,  # Contract Rent
        ]

        total_prop_units = 0
        total_prop_occupied = 0
        total_prop_sqft = 0.0
        total_prop_mkt = 0.0
        total_prop_contract = 0.0

        for bname, unit_list in buildings.items():
            # GROUP HEADER (GH)
            b_hdr = Paragraph(f"<b>BUILDING: {bname.upper()} ({len(unit_list)} Units Audited)</b>", ParagraphStyle(
                "BldHdr", parent=self.style_meta_label, fontName="Helvetica-Bold", fontSize=8.5, textColor=colors.HexColor("#1E3A8A")
            ))
            story.append(b_hdr)
            story.append(Spacer(1, 2))

            b_table_data = [
                [
                    Paragraph("<b>Unit</b>", self.style_tbl_hdr),
                    Paragraph("<b>Type</b>", self.style_tbl_hdr),
                    Paragraph("<b>Sq.Ft.</b>", self.style_tbl_hdr_right),
                    Paragraph("<b>Tenant Name</b>", self.style_tbl_hdr),
                    Paragraph("<b>Lease Start</b>", self.style_tbl_hdr),
                    Paragraph("<b>Lease End</b>", self.style_tbl_hdr),
                    Paragraph("<b>Market Rent</b>", self.style_tbl_hdr_right),
                    Paragraph("<b>Contract Rent</b>", self.style_tbl_hdr_right),
                ]
            ]

            b_units = len(unit_list)
            b_occupied = 0
            b_sqft = 0.0
            b_mkt = 0.0
            b_contract = 0.0

            for u in unit_list:
                sqft = float(u.get("square_feet") or 0)
                mkt = float(u.get("market_rent") or 0)
                contract = float(u.get("contracted_rent") or 0)
                is_occ = (u.get("unit_status") == "OCCUPIED")
                if is_occ:
                    b_occupied += 1
                b_sqft += sqft
                b_mkt += mkt
                b_contract += contract

                b_table_data.append([
                    Paragraph(str(u.get("unit_number")), self.style_cell_center),
                    Paragraph(str(u.get("unit_type")), self.style_cell_left),
                    Paragraph(f"{sqft:,.0f}", self.style_cell_right),
                    Paragraph(str(u.get("tenant_name")), self.style_cell_left),
                    Paragraph(str(u.get("start_date") or "—"), self.style_cell_center),
                    Paragraph(str(u.get("end_date") or "—"), self.style_cell_center),
                    Paragraph(f"Rs. {mkt:,.2f}", self.style_cell_right),
                    Paragraph(f"Rs. {contract:,.2f}" if contract > 0 else "VACANT", self.style_cell_right),
                ])

            total_prop_units += b_units
            total_prop_occupied += b_occupied
            total_prop_sqft += b_sqft
            total_prop_mkt += b_mkt
            total_prop_contract += b_contract

            # GROUP FOOTER (GF)
            b_occ_rate = (b_occupied / b_units * 100) if b_units else 0
            b_subtotal_row = [
                Paragraph(f"<b>Subtotal: {bname}</b>", ParagraphStyle("SubTotL", parent=self.style_cell_left, fontName="Helvetica-Bold")),
                Paragraph(f"<b>{b_occupied}/{b_units} Occ ({b_occ_rate:.1f}%)</b>", self.style_cell_left),
                Paragraph(f"<b>{b_sqft:,.0f}</b>", self.style_cell_right),
                Paragraph("", self.style_cell_left),
                Paragraph("", self.style_cell_left),
                Paragraph("", self.style_cell_left),
                Paragraph(f"<b>Rs. {b_mkt:,.2f}</b>", self.style_cell_right),
                Paragraph(f"<b>Rs. {b_contract:,.2f}</b>", self.style_cell_right),
            ]
            b_table_data.append(b_subtotal_row)

            unit_table = Table(b_table_data, colWidths=tbl_widths)
            unit_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#F1F5F9")),
                ("LINEABOVE", (0, -1), (-1, -1), 0.75, colors.HexColor("#0F172A")),
                ("LINEBELOW", (0, -1), (-1, -1), 1, colors.HexColor("#0F172A")),
                ("GRID", (0, 0), (-1, -2), 0.5, colors.HexColor("#CBD5E1")),
                ("TOPPADDING", (0, 0), (-1, -1), 2.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
            ]))
            story.append(unit_table)
            story.append(Spacer(1, 8))

        # -------------------------------------------------------------
        # BAND 6: REPORT FOOTER (RF) — Physical vs. Economic Reconciliation
        # -------------------------------------------------------------
        phys_occ = (total_prop_occupied / total_prop_units * 100) if total_prop_units else 0
        econ_occ = (total_prop_contract / total_prop_mkt * 100) if total_prop_mkt else 0
        vacancy_loss = max(total_prop_mkt - total_prop_contract, 0)
        vac_loss_rate = (vacancy_loss / total_prop_mkt * 100) if total_prop_mkt else 0

        reconciliation_data = [
            [
                Paragraph("<b>PORTFOLIO AUDIT RECONCILIATION SUMMARY</b>", ParagraphStyle("ReconHdr", parent=self.style_cell_left, fontName="Helvetica-Bold", fontSize=8, textColor=colors.HexColor("#1E3A8A"))),
                Paragraph(f"<b>Gross Potential Market Rent:</b> Rs. {total_prop_mkt:,.2f}", self.style_cell_right),
            ],
            [
                Paragraph(f"<b>Physical Occupancy:</b> {total_prop_occupied}/{total_prop_units} Units ({phys_occ:.1f}%) &nbsp;|&nbsp; <b>Total Audited Area:</b> {total_prop_sqft:,.0f} Sq.Ft.", self.style_cell_left),
                Paragraph(f"<b>Contracted In-Place Rent:</b> Rs. {total_prop_contract:,.2f}", self.style_cell_right),
            ],
            [
                Paragraph(f"<b>Economic Occupancy Efficiency:</b> {econ_occ:.1f}% &nbsp;|&nbsp; <b>Gross Vacancy Loss Rate:</b> {vac_loss_rate:.1f}%", self.style_cell_left),
                Paragraph(f"<b>Realized Monthly Vacancy Loss:</b> Rs. {vacancy_loss:,.2f}", ParagraphStyle("LossR", parent=self.style_cell_right, textColor=colors.HexColor("#991B1B"), fontName="Helvetica-Bold")),
            ]
        ]
        recon_table = Table(reconciliation_data, colWidths=[usable_width * 0.6, usable_width * 0.4])
        recon_table.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#94A3B8")),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))

        # Audit Signature Certification Blocks
        sig_data = [
            [
                Paragraph("<b>PREPARED & CERTIFIED BY:</b><br/><br/><br/>______________________________________<br/><b>Lead Property Asset Manager</b><br/>Licence: PropLedger Audit Group", self.style_cell_left),
                Paragraph("<b>AUDITED & COUNTERSIGNED BY:</b><br/><br/><br/>______________________________________<br/><b>Certified Public Accountant / Controller</b><br/>Fellow Member, ICAI #492810", self.style_cell_left),
            ]
        ]
        sig_table = Table(sig_data, colWidths=[usable_width * 0.5, usable_width * 0.5])
        sig_table.setStyle(TableStyle([
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))

        story.append(KeepTogether([
            recon_table,
            Spacer(1, 10),
            sig_table,
        ]))

        return story
