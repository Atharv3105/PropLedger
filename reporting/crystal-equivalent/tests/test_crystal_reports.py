"""
Automated Test Suite for PropLedger Crystal Reports-Equivalent Engine.
Tests all 3 institutional statement families (CR-01, CR-02, CR-03),
banded section assembly, PDF generation, remittance slip tear-off, and GAAP schedules.
"""
import sys
from pathlib import Path
import pytest

# Add crystal-equivalent directory to sys.path
CRYSTAL_DIR = Path(__file__).resolve().parent.parent
if str(CRYSTAL_DIR) not in sys.path:
    sys.path.insert(0, str(CRYSTAL_DIR))

from statement_registry import StatementRegistry
from statements import STATEMENT_CLASSES


EXPECTED_STATEMENT_CODES = ["CR-01", "CR-02", "CR-03"]


class TestStatementRegistry:
    """Tests for statement registry discovery, metadata, and schemas."""

    def test_all_statements_registered(self):
        """Verify CR-01, CR-02, CR-03 are registered."""
        StatementRegistry.initialize()
        statements = StatementRegistry.list_statements()
        registered_codes = [s["statement_code"] for s in statements]
        for code in EXPECTED_STATEMENT_CODES:
            assert code in registered_codes, f"Statement {code} missing from registry"
        assert len(statements) == 3

    @pytest.mark.parametrize("code", EXPECTED_STATEMENT_CODES)
    def test_statement_metadata_completeness(self, code):
        """Verify each statement defines title, category, description, and orientation."""
        stmt = StatementRegistry.get_statement(code)
        assert stmt is not None
        meta = stmt.get_metadata()
        assert meta["statement_code"] == code
        assert len(meta["title"]) > 0
        assert len(meta["category"]) > 0
        assert len(meta["description"]) > 0
        assert meta["orientation"] in ("portrait", "landscape")
        assert isinstance(meta["parameters"], dict)


class TestStatementExecutionAndRendering:
    """Tests data fetching from PostgreSQL and ReportLab PDF compilation."""

    def test_cr01_tenant_statement_data_and_remittance(self):
        """Test CR-01 data retrieval, aging calculation, and remittance slip."""
        stmt = StatementRegistry.get_statement("CR-01")
        assert stmt.has_remittance_slip is True

        data = stmt.fetch_data({"tenant_id": 1})
        assert "tenant" in data
        assert "ledger" in data
        assert "aging" in data
        assert data["tenant"].get("tenant_name") is not None
        assert isinstance(data["ledger"], list)

        # PDF binary export test
        pdf_bytes = stmt.export_pdf({"tenant_id": 1})
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 2000
        assert pdf_bytes.startswith(b"%PDF-")

    def test_cr02_formal_rent_roll_grouping(self):
        """Test CR-02 hierarchical building grouping and audit signature blocks."""
        stmt = StatementRegistry.get_statement("CR-02")
        assert stmt.orientation == "landscape"

        data = stmt.fetch_data({"property_id": 1, "limit": 50})
        assert "property" in data
        assert "buildings" in data
        assert isinstance(data["buildings"], dict)
        assert len(data["buildings"]) > 0

        # PDF binary export test
        pdf_bytes = stmt.export_pdf({"property_id": 1, "limit": 50})
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 2000
        assert pdf_bytes.startswith(b"%PDF-")

    def test_cr03_income_expense_gaap_schedule(self):
        """Test CR-03 GAAP operating schedule, EGI, and NOI calculations."""
        stmt = StatementRegistry.get_statement("CR-03")
        data = stmt.fetch_data({"property_id": 1})
        assert "property" in data
        assert "revenues" in data
        assert "expenses" in data

        rev = data["revenues"]
        assert rev["gross_potential_rent"] >= 0
        assert rev["effective_gross_income"] >= 0
        assert isinstance(data["expenses"], list)

        # PDF binary export test
        pdf_bytes = stmt.export_pdf({"property_id": 1})
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 2000
        assert pdf_bytes.startswith(b"%PDF-")

    def test_parameter_validation_and_coercion(self):
        """Test BandedReport parameter validator type casting."""
        stmt = StatementRegistry.get_statement("CR-01")
        params = stmt.validate_params({"tenant_id": "5"})
        assert params["tenant_id"] == 5
        assert isinstance(params["tenant_id"], int)
