"""
Statement Canvas for Crystal Reports-Equivalent Engine.
Provides high-precision vector rendering, two-pass 'Page X of Y' calculations,
formal legal watermarks, and detachable tear-off remittance slips with perforation lines.
"""
from typing import Any
from reportlab.lib import colors
from reportlab.pdfgen import canvas


class NumberedStatementCanvas(canvas.Canvas):
    """
    Two-pass canvas for formal legal and accounting statements.
    Renders official running headers, confidentiality disclaimers,
    page counters, and tear-off perforation lines.
    """
    statement_title = "Official Statement"
    statement_code = "CR-00"
    has_remittance_slip = False
    watermark_text = ""

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_statement_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_statement_decorations(self, page_count: int):
        self.saveState()
        page_width, page_height = self._pagesize

        # Optional diagonal watermark
        if self.watermark_text:
            self.saveState()
            self.setFont("Helvetica-Bold", 42)
            self.setFillColor(colors.HexColor("#E2E8F0"), alpha=0.35)
            self.translate(page_width / 2.0, page_height / 2.0)
            self.rotate(35)
            self.drawCentredString(0, 0, self.watermark_text)
            self.restoreState()

        # Running Header on page > 1
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#1E293B"))
            self.drawString(36, page_height - 25, "PROPLEDGER ENTERPRISE ASSET MANAGEMENT & RECOVERY SERVICES")

            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawRightString(page_width - 36, page_height - 25, f"{self.statement_code} — {self.statement_title}")

            self.setStrokeColor(colors.HexColor("#94A3B8"))
            self.setLineWidth(0.75)
            self.line(36, page_height - 28, page_width - 36, page_height - 28)

        # Standard Page Footer (unless replaced by remittance slip on final page)
        is_final_page = (self._pageNumber == page_count)
        if not (is_final_page and self.has_remittance_slip):
            self.setFont("Helvetica", 7.5)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawString(36, 20, "OFFICIAL RECORD — CONFIDENTIAL FINANCIAL STATEMENT FOR RECIPIENT USE ONLY")
            page_str = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(page_width - 36, 20, page_str)

            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(36, 30, page_width - 36, 30)

        self.restoreState()
