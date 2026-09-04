"""
Central Report Registry for PropLedger SSRS-Equivalent Engine.
Provides lookup, instantiation, metadata enumeration, and dispatching.
"""
from typing import Any, Dict, List, Optional
try:
    from reports import REPORT_CLASSES
    from engine.base_report import BaseReport
except ImportError:
    from .reports import REPORT_CLASSES
    from .engine.base_report import BaseReport


class ReportRegistry:
    """
    Registry maintaining all active institutional report definitions.
    """
    _registry: Dict[str, BaseReport] = {}

    @classmethod
    def initialize(cls):
        """Discovers and instantiates all report definitions."""
        cls._registry.clear()
        for report_cls in REPORT_CLASSES:
            instance = report_cls()
            cls._registry[instance.report_code.upper()] = instance

    @classmethod
    def get_report(cls, report_code: str) -> Optional[BaseReport]:
        """Retrieves a report instance by code (e.g. 'PL-095')."""
        if not cls._registry:
            cls.initialize()
        return cls._registry.get(report_code.upper())

    @classmethod
    def list_reports(cls) -> List[Dict[str, Any]]:
        """Returns metadata for all registered reports."""
        if not cls._registry:
            cls.initialize()
        return [report.get_metadata() for report in cls._registry.values()]


# Initialize registry on import
ReportRegistry.initialize()
