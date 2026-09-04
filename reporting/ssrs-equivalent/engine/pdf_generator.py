"""
ReportLab PDF Generation Engine for PropLedger.
Generates publication-quality paginated corporate PDF reports with
running headers, two-pass 'Page X of Y' footers, KPI summary cards,
and auto-wrapped data tables with zebra striping.
"""
import io
from datetime import datetime
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable,
)


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas that counts total pages and draws running headers
    and 'Page X of Y' corporate confidentiality footers.
    """
    report_title = "PropLedger Enterprise Report"
    report_code = "PL-000"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Running header on subsequent pages (page > 1)
        if self._pageNumber > 1:
            self.drawString(36, self._pagesize[1] - 25, f"PropLedger Enterprise — {self.report_title}")
            self.drawRightString(self._pagesize[0] - 36, self._pagesize[1] - 25, f"Report: {self.report_code}")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(36, self._pagesize[1] - 28, self._pagesize[0] - 36, self._pagesize[1] - 28)

        # Corporate footer on all pages
        self.drawString(36, 20, "CONFIDENTIAL — PROPLEDGER ENTERPRISE PROPERTY MANAGEMENT & ANALYTICS")
        self.drawRightString(self._pagesize[0] - 36, 20, f"Page {self._pageNumber} of {page_count}")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(36, 30, self._pagesize[0] - 36, 30)
        self.restoreState()


class PdfGenerator:
    """
    Renders report data into publication-quality paginated PDF reports (.pdf).
    """

    def __init__(self, report: Any):
        self.report = report

    def generate(
        self,
        data: List[Dict[str, Any]],
        params: Dict[str, Any],
        output_path: Optional[str] = None,
    ) -> bytes:
        """Generates formatted PDF report and returns binary bytes."""
        buffer = io.BytesIO()

        # Page setup
        orientation = getattr(self.report, "orientation", "landscape").lower()
        pagesize = landscape(letter) if orientation == "landscape" else letter
        usable_width = pagesize[0] - 72  # 36pt margins on left & right

        doc = SimpleDocTemplate(
            buffer,
            pagesize=pagesize,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=40,
        )

        # Set class-level metadata on NumberedCanvas
        NumberedCanvas.report_title = self.report.title
        NumberedCanvas.report_code = self.report.report_code

        styles = getSampleStyleSheet()

        # Custom Typography Styles
        brand_style = ParagraphStyle(
            "BrandHeader",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            textColor=colors.HexColor("#64748B"),
            leading=10,
        )
        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=15,
            textColor=colors.HexColor("#1E3A8A"),
            leading=18,
            spaceAfter=3,
        )
        meta_style = ParagraphStyle(
            "MetaSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            textColor=colors.HexColor("#475569"),
            leading=11,
            spaceAfter=8,
        )
        col_hdr_style = ParagraphStyle(
            "ColHeader",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            textColor=colors.white,
            leading=10,
            alignment=0,
        )
        col_hdr_right = ParagraphStyle(
            "ColHeaderRight",
            parent=col_hdr_style,
            alignment=2,
        )
        cell_style_left = ParagraphStyle(
            "CellLeft",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=7.5,
            textColor=colors.HexColor("#0F172A"),
            leading=9,
            alignment=0,
        )
        cell_style_right = ParagraphStyle(
            "CellRight",
            parent=cell_style_left,
            alignment=2,
        )
        cell_style_center = ParagraphStyle(
            "CellCenter",
            parent=cell_style_left,
            alignment=1,
        )
        total_style_left = ParagraphStyle(
            "TotalLeft",
            parent=cell_style_left,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#1E3A8A"),
        )
        total_style_right = ParagraphStyle(
            "TotalRight",
            parent=cell_style_right,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#1E3A8A"),
        )

        story = []

        # 1. Corporate Brand Header
        story.append(Paragraph("PROPLEDGER ENTERPRISE PROPERTY MANAGEMENT & ANALYTICS", brand_style))
        story.append(Paragraph(f"{self.report.report_code} — {self.report.title}", title_style))

        # 2. Metadata line
        param_str = ", ".join(f"{k}={v}" for k, v in params.items() if v is not None) or "All Records"
        meta_text = (
            f"<b>Category:</b> {self.report.category} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Filters:</b> [{param_str}]"
        )
        story.append(Paragraph(meta_text, meta_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E1"), spaceAfter=8))

        # 3. Optional KPI Summary Cards
        summary_stats = self.report.get_summary_stats(data)
        if summary_stats:
            kpi_data = []
            hdr_cells = []
            val_cells = []
            for stat in summary_stats[:6]:
                hdr_cells.append(Paragraph(f"<b>{stat.get('label', '').upper()}</b>", ParagraphStyle(
                    "KPIHdr", parent=cell_style_center, fontSize=7, textColor=colors.HexColor("#64748B")
                )))
                val_cells.append(Paragraph(f"<b>{stat.get('value', '')}</b>", ParagraphStyle(
                    "KPIVal", parent=cell_style_center, fontSize=10, textColor=colors.HexColor("#1E3A8A")
                )))
            kpi_data.append(hdr_cells)
            kpi_data.append(val_cells)

            kpi_col_w = usable_width / len(hdr_cells)
            kpi_table = Table(kpi_data, colWidths=[kpi_col_w] * len(hdr_cells))
            kpi_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#BFDBFE")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BFDBFE")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(kpi_table)
            story.append(Spacer(1, 10))

        # 4. Table Construction
        columns = self.report.columns
        num_cols = len(columns)

        # Proportional column width calculation
        total_weight = sum(col.get("width", 15) for col in columns)
        col_widths = [(col.get("width", 15) / total_weight) * usable_width for col in columns]

        table_data = []

        # Table Header
        header_row = []
        for col_def in columns:
            align = col_def.get("align", "left")
            pstyle = col_hdr_right if align == "right" else col_hdr_style
            header_row.append(Paragraph(f"<b>{col_def['label']}</b>", pstyle))
        table_data.append(header_row)

        # Table Data Rows
        for record in data:
            row_cells = []
            for col_def in columns:
                key = col_def["key"]
                raw_val = record.get(key)
                col_type = col_def.get("type", "string")
                align = col_def.get("align", "left")

                if raw_val is None:
                    formatted = "-"
                    pstyle = cell_style_center
                elif col_type == "currency":
                    try:
                        formatted = f"Rs. {float(raw_val):,.2f}"
                    except (ValueError, TypeError):
                        formatted = str(raw_val)
                    pstyle = cell_style_right
                elif col_type == "percent":
                    try:
                        fval = float(raw_val)
                        if fval > 1.0:
                            fval = fval / 100.0
                        formatted = f"{fval * 100:.1f}%"
                    except (ValueError, TypeError):
                        formatted = str(raw_val)
                    pstyle = cell_style_right
                elif col_type == "number":
                    try:
                        fval = float(raw_val)
                        formatted = f"{int(fval):,}" if fval.is_integer() else f"{fval:,.2f}"
                    except (ValueError, TypeError):
                        formatted = str(raw_val)
                    pstyle = cell_style_right
                elif col_type == "date":
                    formatted = str(raw_val)
                    pstyle = cell_style_center
                else:
                    formatted = str(raw_val)
                    pstyle = cell_style_center if align == "center" else (cell_style_right if align == "right" else cell_style_left)

                row_cells.append(Paragraph(formatted, pstyle))
            table_data.append(row_cells)

        # Table Grand Total Row (if numeric/currency columns exist and data present)
        if data:
            total_cells = [Paragraph("<b>Grand Total</b>", total_style_left)]
            has_numeric = False
            for col_def in columns[1:]:
                col_type = col_def.get("type", "string")
                key = col_def["key"]
                if col_type in ("currency", "number"):
                    has_numeric = True
                    try:
                        tot = sum(float(r.get(key) or 0) for r in data)
                        if col_type == "currency":
                            tot_str = f"Rs. {tot:,.2f}"
                        else:
                            tot_str = f"{int(tot):,}" if tot.is_integer() else f"{tot:,.2f}"
                        total_cells.append(Paragraph(f"<b>{tot_str}</b>", total_style_right))
                    except (ValueError, TypeError):
                        total_cells.append(Paragraph("", total_style_right))
                elif col_type == "percent":
                    try:
                        vals = [float(r.get(key)) for r in data if r.get(key) is not None]
                        avg = sum(vals) / len(vals) if vals else 0
                        if avg > 1.0:
                            avg = avg / 100.0
                        total_cells.append(Paragraph(f"<b>{avg * 100:.1f}%</b>", total_style_right))
                    except (ValueError, TypeError):
                        total_cells.append(Paragraph("", total_style_right))
                else:
                    total_cells.append(Paragraph("", cell_style_left))

            if has_numeric:
                table_data.append(total_cells)

        # Apply Table Styling
        t_style = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ]

        # Zebra striping for data rows
        for i in range(1, len(data) + 1):
            bg = colors.HexColor("#F8FAFC") if i % 2 == 0 else colors.white
            t_style.append(("BACKGROUND", (0, i), (-1, i), bg))

        # Format Total row
        if data and len(table_data) > len(data) + 1:
            total_idx = len(table_data) - 1
            t_style.extend([
                ("BACKGROUND", (0, total_idx), (-1, total_idx), colors.HexColor("#F1F5F9")),
                ("LINEABOVE", (0, total_idx), (-1, total_idx), 1, colors.HexColor("#0F172A")),
                ("LINEBELOW", (0, total_idx), (-1, total_idx), 1.5, colors.HexColor("#0F172A")),
            ])

        data_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        data_table.setStyle(TableStyle(t_style))
        story.append(data_table)

        # Build document
        doc.build(story, canvasmaker=NumberedCanvas)

        binary_data = buffer.getvalue()
        if output_path:
            with open(output_path, "wb") as f:
                f.write(binary_data)

        return binary_data
