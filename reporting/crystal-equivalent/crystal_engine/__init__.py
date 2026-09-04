"""
PropLedger Crystal Reports Equivalent Engine.
Section-banded layout, precision typography, and formal statement outputs.
"""
from .banded_report import BandedReport
from .statement_canvas import NumberedStatementCanvas

__all__ = ["BandedReport", "NumberedStatementCanvas"]
