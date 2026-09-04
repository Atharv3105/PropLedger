"""
Unit Tests for Authoritative Business Logic & Domain Models (PL-138)
Verifies: Late-fee calculation, balance derivation, lease status state machine, delinquency classification.
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from app.core.finance_rules import (
    calculate_late_fee,
    derive_tenant_balance,
    validate_lease_state_transition,
    classify_delinquency_aging,
    LeaseStatus,
    LateFeeType,
    AgingBucket,
    InvalidStateTransitionError
)

class TestLateFeeCalculation:
    """Tests for late fee calculation models (BR-02, BR-05)."""

    def test_payment_within_grace_period_incurs_zero_fee(self):
        due = date(2026, 9, 1)
        # 5 days grace period -> Sept 6 is boundary (due + 5 days)
        on_boundary = date(2026, 9, 6)
        fee = calculate_late_fee(
            rent_amount=Decimal('2000.00'),
            due_date=due,
            evaluation_date=on_boundary,
            policy_type=LateFeeType.PERCENTAGE,
            fee_rate=Decimal('5.00'),
            grace_period_days=5
        )
        assert fee == Decimal('0.00')

    def test_payment_before_due_date_incurs_zero_fee(self):
        due = date(2026, 9, 1)
        early = date(2026, 8, 28)
        fee = calculate_late_fee(Decimal('1500.00'), due, early)
        assert fee == Decimal('0.00')

    def test_flat_late_fee_policy(self):
        due = date(2026, 9, 1)
        late = date(2026, 9, 7)  # Day 6 past due, 1 day past grace period
        fee = calculate_late_fee(
            rent_amount=Decimal('2000.00'),
            due_date=due,
            evaluation_date=late,
            policy_type=LateFeeType.FLAT,
            fee_rate=Decimal('50.00'),
            grace_period_days=5
        )
        assert fee == Decimal('50.00')

    def test_percentage_late_fee_policy(self):
        due = date(2026, 9, 1)
        late = date(2026, 9, 10)
        # 5% of $2,400.00 = $120.00
        fee = calculate_late_fee(
            rent_amount=Decimal('2400.00'),
            due_date=due,
            evaluation_date=late,
            policy_type=LateFeeType.PERCENTAGE,
            fee_rate=Decimal('5.00'),
            grace_period_days=5
        )
        assert fee == Decimal('120.00')

    def test_daily_accrual_late_fee_policy_with_cap(self):
        due = date(2026, 9, 1)
        # 15 days past due -> 10 days past grace period (5 days)
        # 10 days * $10/day = $100.00
        eval_date = date(2026, 9, 16)
        fee = calculate_late_fee(
            rent_amount=Decimal('1800.00'),
            due_date=due,
            evaluation_date=eval_date,
            policy_type=LateFeeType.DAILY,
            fee_rate=Decimal('10.00'),
            grace_period_days=5,
            daily_cap=Decimal('75.00')  # Capped at $75
        )
        # Should be capped at $75.00 instead of $100.00
        assert fee == Decimal('75.00')


class TestBalanceDerivation:
    """Tests for double-entry tenant balance calculation (BR-01)."""

    def test_clean_zero_balance_when_fully_paid(self):
        charges = [{'amount': Decimal('1500.00')}]
        payments = [{'amount': Decimal('1500.00')}]
        result = derive_tenant_balance(charges, payments)
        assert result['outstanding_balance'] == Decimal('0.00')

    def test_partial_payment_leaves_correct_positive_balance(self):
        charges = [{'amount': Decimal('2000.00')}, {'amount': Decimal('50.00')}]
        payments = [{'amount': Decimal('1200.00')}]
        result = derive_tenant_balance(charges, payments)
        assert result['outstanding_balance'] == Decimal('850.00')
        assert result['total_charges'] == Decimal('2050.00')
        assert result['total_payments'] == Decimal('1200.00')

    def test_overpayment_creates_credit_balance(self):
        charges = [{'amount': Decimal('1000.00')}]
        payments = [{'amount': Decimal('1300.00')}]
        result = derive_tenant_balance(charges, payments)
        assert result['outstanding_balance'] == Decimal('-300.00')

    def test_balance_includes_late_fees_and_credits(self):
        charges = [{'amount': Decimal('1500.00')}]
        late_fees = [{'amount': Decimal('75.00')}]
        credits = [{'amount': Decimal('100.00')}]  # Referral discount
        payments = [{'amount': Decimal('1000.00')}]
        # 1500 + 75 - 1000 - 100 = 475
        result = derive_tenant_balance(charges, payments, credits=credits, late_fees=late_fees)
        assert result['outstanding_balance'] == Decimal('475.00')


class TestLeaseStateMachine:
    """Tests for lease state transitions (BR-03, BR-06)."""

    def test_valid_draft_to_active(self):
        assert validate_lease_state_transition(LeaseStatus.DRAFT, LeaseStatus.ACTIVE) is True

    def test_valid_active_to_expiring(self):
        assert validate_lease_state_transition(LeaseStatus.ACTIVE, LeaseStatus.EXPIRING) is True

    def test_valid_expiring_to_renewed(self):
        assert validate_lease_state_transition(LeaseStatus.EXPIRING, LeaseStatus.RENEWED) is True

    def test_valid_active_to_terminated(self):
        assert validate_lease_state_transition(LeaseStatus.ACTIVE, LeaseStatus.TERMINATED) is True

    def test_forbidden_terminated_to_active_raises_error(self):
        with pytest.raises(InvalidStateTransitionError) as exc_info:
            validate_lease_state_transition(LeaseStatus.TERMINATED, LeaseStatus.ACTIVE)
        assert "Illegal lease transition" in str(exc_info.value)

    def test_forbidden_cancelled_to_renewed_raises_error(self):
        with pytest.raises(InvalidStateTransitionError) as exc_info:
            validate_lease_state_transition(LeaseStatus.CANCELLED, LeaseStatus.RENEWED)
        assert "Illegal lease transition" in str(exc_info.value)

    def test_self_transition_is_noop_true(self):
        assert validate_lease_state_transition(LeaseStatus.ACTIVE, LeaseStatus.ACTIVE) is True


class TestDelinquencyAgingClassification:
    """Tests for arrears aging bucketing (BR-04)."""

    def test_zero_balance_is_current(self):
        due = date(2026, 7, 1)
        today = date(2026, 9, 1)
        # If balance is zero, it cannot be delinquent regardless of dates
        bucket = classify_delinquency_aging(due, today, Decimal('0.00'))
        assert bucket == AgingBucket.CURRENT

    def test_not_yet_due_is_current(self):
        due = date(2026, 9, 15)
        today = date(2026, 9, 5)
        bucket = classify_delinquency_aging(due, today, Decimal('1500.00'))
        assert bucket == AgingBucket.CURRENT

    def test_days_1_to_30_aging(self):
        due = date(2026, 8, 15)
        today = date(2026, 9, 5)  # 21 days past due
        bucket = classify_delinquency_aging(due, today, Decimal('1500.00'))
        assert bucket == AgingBucket.DAYS_1_30

    def test_days_31_to_60_aging(self):
        due = date(2026, 7, 20)
        today = date(2026, 9, 5)  # 47 days past due
        bucket = classify_delinquency_aging(due, today, Decimal('1500.00'))
        assert bucket == AgingBucket.DAYS_31_60

    def test_days_61_to_90_aging(self):
        due = date(2026, 6, 25)
        today = date(2026, 9, 5)  # 72 days past due
        bucket = classify_delinquency_aging(due, today, Decimal('1500.00'))
        assert bucket == AgingBucket.DAYS_61_90

    def test_days_over_90_critical_aging(self):
        due = date(2026, 4, 1)
        today = date(2026, 9, 5)  # 157 days past due
        bucket = classify_delinquency_aging(due, today, Decimal('1500.00'))
        assert bucket == AgingBucket.OVER_90
