"""
Central Statement Registry for Crystal Reports-Equivalent Engine.
Provides lookup, instantiation, and metadata enumeration for formal statements.
"""
from typing import Any, Dict, List, Optional
try:
    from .statements import STATEMENT_CLASSES
    from .engine.banded_report import BandedReport
except ImportError:
    from statements import STATEMENT_CLASSES
    from crystal_engine.banded_report import BandedReport


class StatementRegistry:
    """
    Registry maintaining all active institutional formal statement definitions.
    """
    _registry: Dict[str, BandedReport] = {}

    @classmethod
    def initialize(cls):
        """Instantiates and registers all statement classes."""
        cls._registry.clear()
        for stmt_cls in STATEMENT_CLASSES:
            instance = stmt_cls()
            cls._registry[instance.statement_code.upper()] = instance

    @classmethod
    def get_statement(cls, statement_code: str) -> Optional[BandedReport]:
        """Retrieves a statement instance by code (e.g. 'CR-01')."""
        if not cls._registry:
            cls.initialize()
        return cls._registry.get(statement_code.upper())

    @classmethod
    def list_statements(cls) -> List[Dict[str, Any]]:
        """Returns metadata for all registered statements."""
        if not cls._registry:
            cls.initialize()
        return [stmt.get_metadata() for stmt in cls._registry.values()]


# Initialize registry on import
StatementRegistry.initialize()
