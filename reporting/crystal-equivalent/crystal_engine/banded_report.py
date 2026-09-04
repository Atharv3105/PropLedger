"""
Banded Report Base Class for Crystal Reports-Equivalent Engine.
Implements the 7-band reporting lifecycle:
- Report Header (RH)
- Page Header (PH)
- Group Header (GH)
- Details (D)
- Group Footer (GF)
- Report Footer (RF)
- Page Footer / Remittance Slip (PF)
"""
import io
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import psycopg2
from psycopg2.extras import RealDictCursor
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable,
)

try:
    from .statement_canvas import NumberedStatementCanvas
except ImportError:
    from crystal_engine.statement_canvas import NumberedStatementCanvas


DEFAULT_DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/propledger")


class BandedReport(ABC):
    """
    Abstract base class for Crystal Reports-style section-banded statements.
    """
    statement_code: str = "CR-00"
    title: str = "Formal Statement Title"
    category: str = "Accounting Statements"
    description: str = "Formal accounting statement description."
    orientation: str = "portrait"  # 'portrait' or 'landscape'
    has_remittance_slip: bool = False
    watermark_text: str = ""

    # Supported parameters
    parameters: Dict[str, Dict[str, Any]] = {}

    def __init__(self, db_url: Optional[str] = None):
        self.db_url = db_url or DEFAULT_DB_URL
        self._init_styles()

    def _init_styles(self):
        styles = getSampleStyleSheet()
        self.styles = styles
        self.style_issuer_title = ParagraphStyle(
            "IssuerTitle", parent=styles["Normal"],
            fontName="Helvetica-Bold", fontSize=13, textColor=colors.HexColor("#0F172A"), leading=15
        )
        self.style_doc_title = ParagraphStyle(
            "DocTitle", parent=styles["Heading1"],
            fontName="Helvetica-Bold", fontSize=16, textColor=colors.HexColor("#1E3A8A"), leading=19, alignment=2
        )
        self.style_meta_label = ParagraphStyle(
            "MetaLabel", parent=styles["Normal"],
            fontName="Helvetica-Bold", fontSize=7.5, textColor=colors.HexColor("#64748B"), leading=10
        )
        self.style_meta_val = ParagraphStyle(
            "MetaVal", parent=styles["Normal"],
            fontName="Helvetica", fontSize=8, textColor=colors.HexColor("#0F172A"), leading=10
        )
        self.style_cell_left = ParagraphStyle(
            "CellLeft", parent=styles["Normal"],
            fontName="Helvetica", fontSize=7.5, textColor=colors.HexColor("#0F172A"), leading=9.5
        )
        self.style_cell_right = ParagraphStyle(
            "CellRight", parent=self.style_cell_left, alignment=2
        )
        self.style_cell_center = ParagraphStyle(
            "CellCenter", parent=self.style_cell_left, alignment=1
        )
        self.style_tbl_hdr = ParagraphStyle(
            "TblHdr", parent=styles["Normal"],
            fontName="Helvetica-Bold", fontSize=7.5, textColor=colors.white, leading=9.5
        )
        self.style_tbl_hdr_right = ParagraphStyle(
            "TblHdrRight", parent=self.style_tbl_hdr, alignment=2
        )

    def get_connection(self):
        """Returns PostgreSQL connection with RealDictCursor."""
        return psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)

    def validate_params(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Validates and coerces parameters according to schema."""
        resolved = {}
        input_params = params or {}
        for param_name, param_def in self.parameters.items():
            val = input_params.get(param_name)
            if val is None or val == "":
                if param_def.get("required", False):
                    raise ValueError(f"Missing required parameter '{param_name}' for {self.statement_code}")
                resolved[param_name] = param_def.get("default")
            else:
                expected_type = param_def.get("type", "str")
                try:
                    if expected_type == "int":
                        resolved[param_name] = int(val)
                    elif expected_type == "float":
                        resolved[param_name] = float(val)
                    else:
                        resolved[param_name] = str(val)
                except (ValueError, TypeError) as exc:
                    raise ValueError(f"Invalid parameter '{param_name}': expected {expected_type}, got {val}") from exc
        return resolved

    @abstractmethod
    def fetch_data(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Retrieves statement payload containing headers, account summaries,
        line items, and totals.
        """
        pass

    @abstractmethod
    def build_statement_story(self, data: Dict[str, Any], usable_width: float) -> List[Any]:
        """
        Assembles report bands into ReportLab Platypus flowable story.
        """
        pass

    def export_pdf(self, params: Optional[Dict[str, Any]] = None, output_path: Optional[str] = None) -> bytes:
        """Generates pixel-precise banded formal statement PDF."""
        valid_params = self.validate_params(params)
        data = self.fetch_data(valid_params)

        buffer = io.BytesIO()
        pagesize = landscape(letter) if self.orientation == "landscape" else letter
        usable_width = pagesize[0] - 72  # 36pt margins on left & right

        doc = SimpleDocTemplate(
            buffer,
            pagesize=pagesize,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        # Set canvas metadata
        NumberedStatementCanvas.statement_title = self.title
        NumberedStatementCanvas.statement_code = self.statement_code
        NumberedStatementCanvas.has_remittance_slip = self.has_remittance_slip
        NumberedStatementCanvas.watermark_text = self.watermark_text

        story = self.build_statement_story(data, usable_width)
        doc.build(story, canvasmaker=NumberedStatementCanvas)

        pdf_bytes = buffer.getvalue()
        if output_path:
            with open(output_path, "wb") as f:
                f.write(pdf_bytes)

        return pdf_bytes

    def get_metadata(self) -> Dict[str, Any]:
        """Returns JSON-serializable statement metadata."""
        return {
            "statement_code": self.statement_code,
            "title": self.title,
            "category": self.category,
            "description": self.description,
            "orientation": self.orientation,
            "has_remittance_slip": self.has_remittance_slip,
            "parameters": self.parameters,
        }
