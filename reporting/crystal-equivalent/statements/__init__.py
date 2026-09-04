"""
Crystal Reports Equivalent Statements Package.
Exports the three institutional formal statement definitions.
"""
try:
    from .cr01_tenant_statement import TenantStatementReport
    from .cr02_formal_rent_roll import FormalRentRollStatement
    from .cr03_income_expense_statement import FormalIncomeExpenseStatement
except ImportError:
    from statements.cr01_tenant_statement import TenantStatementReport
    from statements.cr02_formal_rent_roll import FormalRentRollStatement
    from statements.cr03_income_expense_statement import FormalIncomeExpenseStatement

STATEMENT_CLASSES = [
    TenantStatementReport,
    FormalRentRollStatement,
    FormalIncomeExpenseStatement,
]

__all__ = [
    "STATEMENT_CLASSES",
    "TenantStatementReport",
    "FormalRentRollStatement",
    "FormalIncomeExpenseStatement",
]
