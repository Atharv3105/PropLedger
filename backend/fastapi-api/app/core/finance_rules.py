"""
PropLedger Business Rules & Financial Accounting Domain Models (BR-01 to BR-06)
Authoritative domain logic implementing late fee policies, running balance derivation,
lease state transitions, and delinquency aging classifications.
"""

from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import List, Dict, Any, Optional

class LeaseStatus(str, Enum):
    DRAFT = 'Draft'
    ACTIVE = 'Active'
    EXPIRING = 'Expiring'
    RENEWED = 'Renewed'
    TERMINATED = 'Terminated'
    CANCELLED = 'Cancelled'

class AgingBucket(str, Enum):
    CURRENT = 'Current'
    DAYS_1_30 = '1-30 Days'
    DAYS_31_60 = '31-60 Days'
    DAYS_61_90 = '61-90 Days'
    OVER_90 = '>90 Days'

class LateFeeType(str, Enum):
    FLAT = 'FLAT'
    PERCENTAGE = 'PERCENTAGE'
    DAILY = 'DAILY'

class InvalidStateTransitionError(ValueError):
    """Raised when a lease status transition violates business rule BR-03/BR-06."""
    pass

# Valid state machine transitions
ALLOWED_LEASE_TRANSITIONS = {
    LeaseStatus.DRAFT: {LeaseStatus.ACTIVE, LeaseStatus.CANCELLED},
    LeaseStatus.ACTIVE: {LeaseStatus.EXPIRING, LeaseStatus.RENEWED, LeaseStatus.TERMINATED},
    LeaseStatus.EXPIRING: {LeaseStatus.RENEWED, LeaseStatus.TERMINATED, LeaseStatus.ACTIVE},
    LeaseStatus.RENEWED: {LeaseStatus.ACTIVE, LeaseStatus.TERMINATED},
    LeaseStatus.TERMINATED: set(),  # Terminal state
    LeaseStatus.CANCELLED: set()    # Terminal state
}

def validate_lease_state_transition(current_status: LeaseStatus, target_status: LeaseStatus) -> bool:
    """
    Enforces the lease lifecycle state machine.
    Raises InvalidStateTransitionError if transition is forbidden.
    """
    if current_status == target_status:
        return True
    allowed = ALLOWED_LEASE_TRANSITIONS.get(current_status, set())
    if target_status not in allowed:
        raise InvalidStateTransitionError(
            f"Illegal lease transition from {current_status.value} to {target_status.value}. "
            f"Allowed transitions: {[s.value for s in allowed]}"
        )
    return True

def calculate_late_fee(
    rent_amount: Decimal,
    due_date: date,
    evaluation_date: date,
    policy_type: LateFeeType = LateFeeType.PERCENTAGE,
    fee_rate: Decimal = Decimal('5.00'),
    grace_period_days: int = 5,
    daily_cap: Optional[Decimal] = Decimal('150.00')
) -> Decimal:
    """
    Rule BR-02 & BR-05: Calculates late fees based on configured policy and grace period.
    - If payment is made within grace period (due_date + grace_period_days), fee is $0.00.
    - FLAT: fixed fee.
    - PERCENTAGE: percentage of billed rent.
    - DAILY: accrues daily after grace period up to optional cap.
    """
    if evaluation_date <= due_date + timedelta(days=grace_period_days):
        return Decimal('0.00')

    days_overdue = (evaluation_date - due_date).days

    if policy_type == LateFeeType.FLAT:
        return fee_rate.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    elif policy_type == LateFeeType.PERCENTAGE:
        fee = (rent_amount * (fee_rate / Decimal('100.00'))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return fee
    elif policy_type == LateFeeType.DAILY:
        accrual_days = days_overdue - grace_period_days
        fee = (fee_rate * Decimal(accrual_days)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        if daily_cap is not None and fee > daily_cap:
            return daily_cap.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return fee
    else:
        raise ValueError(f"Unknown policy type: {policy_type}")

def derive_tenant_balance(
    charges: List[Dict[str, Any]],
    payments: List[Dict[str, Any]],
    credits: List[Dict[str, Any]] = None,
    late_fees: List[Dict[str, Any]] = None
) -> Dict[str, Decimal]:
    """
    Rule BR-01: Derives double-entry tenant balance.
    Net Outstanding = Total Charges + Total Late Fees - Total Payments - Total Credits
    """
    credits = credits or []
    late_fees = late_fees or []

    total_charges = sum((Decimal(str(c.get('amount', 0))) for c in charges), Decimal('0.00'))
    total_payments = sum((Decimal(str(p.get('amount', 0))) for p in payments), Decimal('0.00'))
    total_credits = sum((Decimal(str(cr.get('amount', 0))) for cr in credits), Decimal('0.00'))
    total_late_fees = sum((Decimal(str(lf.get('amount', 0))) for lf in late_fees), Decimal('0.00'))

    outstanding_balance = total_charges + total_late_fees - total_payments - total_credits

    return {
        'total_charges': total_charges.quantize(Decimal('0.01')),
        'total_payments': total_payments.quantize(Decimal('0.01')),
        'total_credits': total_credits.quantize(Decimal('0.01')),
        'total_late_fees': total_late_fees.quantize(Decimal('0.01')),
        'outstanding_balance': outstanding_balance.quantize(Decimal('0.01'))
    }

def classify_delinquency_aging(due_date: date, evaluation_date: date, balance_due: Decimal) -> AgingBucket:
    """
    Rule BR-04: Classifies unpaid charges into standardized aging buckets.
    """
    if balance_due <= Decimal('0.00'):
        return AgingBucket.CURRENT

    days_past_due = (evaluation_date - due_date).days

    if days_past_due <= 0:
        return AgingBucket.CURRENT
    elif 1 <= days_past_due <= 30:
        return AgingBucket.DAYS_1_30
    elif 31 <= days_past_due <= 60:
        return AgingBucket.DAYS_31_60
    elif 61 <= days_past_due <= 90:
        return AgingBucket.DAYS_61_90
    else:
        return AgingBucket.OVER_90
