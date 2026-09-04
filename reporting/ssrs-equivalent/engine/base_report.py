"""
Base Report class for PropLedger SSRS-Equivalent Enterprise Reporting Engine.
Provides database connectivity, parameter validation, metadata discovery,
and orchestration for OpenPyXL Excel and ReportLab PDF exporters.
"""
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor


DEFAULT_DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/propledger")


class BaseReport(ABC):
    """
    Abstract base class for all enterprise reports.
    Corresponds to an SSRS Report Definition (.rdl) specification.
    """

    report_code: str = "PL-000"
    title: str = "Base Report Title"
    category: str = "General"
    description: str = "Base report description."
    orientation: str = "landscape"  # 'portrait' or 'landscape'

    # Schema definition for columns
    # Example: [{"key": "property_name", "label": "Property Name", "type": "string", "width": 25, "align": "left"}]
    columns: List[Dict[str, Any]] = []

    # Supported parameters and definitions
    # Example: {"property_id": {"type": "int", "default": None, "required": False, "description": "Filter by property"}}
    parameters: Dict[str, Dict[str, Any]] = {}

    def __init__(self, db_url: Optional[str] = None):
        self.db_url = db_url or DEFAULT_DB_URL

    def get_connection(self):
        """Creates a PostgreSQL connection with RealDictCursor."""
        return psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)

    def validate_params(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Validates, coerces, and applies defaults to supplied report parameters."""
        resolved = {}
        input_params = params or {}

        for param_name, param_def in self.parameters.items():
            val = input_params.get(param_name)
            if val is None or val == "":
                if param_def.get("required", False):
                    raise ValueError(f"Missing required parameter '{param_name}' for report {self.report_code}")
                resolved[param_name] = param_def.get("default")
            else:
                expected_type = param_def.get("type", "str")
                try:
                    if expected_type == "int":
                        resolved[param_name] = int(val)
                    elif expected_type == "float":
                        resolved[param_name] = float(val)
                    elif expected_type == "bool":
                        if isinstance(val, str):
                            resolved[param_name] = val.lower() in ("true", "1", "yes")
                        else:
                            resolved[param_name] = bool(val)
                    else:
                        resolved[param_name] = str(val)
                except (ValueError, TypeError) as exc:
                    raise ValueError(f"Invalid parameter '{param_name}': expected {expected_type}, got {val}") from exc

        return resolved

    @abstractmethod
    def fetch_data(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Executes query against PostgreSQL database and returns list of record dictionaries.
        """
        pass

    def get_summary_stats(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Computes high-level KPI cards for report header/dashboard.
        Returns list of dicts: [{"label": "...", "value": "..."}]
        """
        return []

    def get_metadata(self) -> Dict[str, Any]:
        """Returns JSON-serializable report definition metadata."""
        return {
            "report_code": self.report_code,
            "title": self.title,
            "category": self.category,
            "description": self.description,
            "orientation": self.orientation,
            "columns": self.columns,
            "parameters": self.parameters,
        }

    def export_excel(self, params: Optional[Dict[str, Any]] = None, output_path: Optional[str] = None) -> bytes:
        """Renders report data into a publication-grade Excel workbook (.xlsx)."""
        try:
            from .excel_generator import ExcelGenerator
        except ImportError:
            from engine.excel_generator import ExcelGenerator
        valid_params = self.validate_params(params)
        data = self.fetch_data(valid_params)
        generator = ExcelGenerator(self)
        return generator.generate(data, valid_params, output_path)

    def export_pdf(self, params: Optional[Dict[str, Any]] = None, output_path: Optional[str] = None) -> bytes:
        """Renders report data into a publication-grade paginated PDF report (.pdf)."""
        try:
            from .pdf_generator import PdfGenerator
        except ImportError:
            from engine.pdf_generator import PdfGenerator
        valid_params = self.validate_params(params)
        data = self.fetch_data(valid_params)
        generator = PdfGenerator(self)
        return generator.generate(data, valid_params, output_path)
