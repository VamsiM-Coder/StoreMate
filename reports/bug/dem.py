"""Test for checking pos before closing loan"""

from decimal import Decimal
from unittest.mock import patch

from django.db.models import Sum


from accounting.choices import CashFlowType, RepaymentChargeType
from accounting.factories import AllocationFactory, CashFlowFactory
from accounting.models import Allocation

class TestForeClosureSubventionRefund(BaseAPITestCase):
    """Test foreclosure refund flow for subvention & GST reversal."""

    def test_reverse_subvention_accrual_with_refund(self):
        """Test refund when foreclosure_config provides SUBVENTION_REFUND."""
        loan_request = LoanRequestFactory()
        approved_loan = ApprovedLoanFactory(
            loan_request=loan_request,
            approved_loan_amount=Decimal('500000'),
            product__foreclosure_config={
                'SUBVENTION_REFUND': {'key': 'dummy'}
            },
        )
        pmt_txn = PaymentTransactionFactory(
            profile=approved_loan.loan_request.profile
        )

        approved_loan.product.foreclosure_config['SUBVENTION_REFUND']['value'] = Decimal('25000') # noqa
        approved_loan.product.foreclosure_config['SUBVENTION_TAX_REFUND'] = {'value': Decimal('4500')} # noqa

        foreclosure_handler = ForeClosure(
            loan=approved_loan,
            loan_tranche=None,
            foreclosure_txn=pmt_txn,
            validated_data={},
            cashflow_type=None,
        )
        foreclosure_handler.reverse_subvention_accrual()

        allocations = Allocation.objects.filter(pmt_txn=pmt_txn)
        self.assertEqual(
            allocations.get(charge_type=RepaymentChargeType.SUBVENTION).allocated_amount, Decimal('-25000')) # noqa

        self.assertEqual(
            allocations.get(charge_type=RepaymentChargeType.SUBVENTION_TAX).allocated_amount, Decimal('-4500')) # noqa

    def test_reverse_subvention_accrual_with_no_refund_flag(self):
        """Should not create allocations if no_subvention_refund is True."""
        loan_request = LoanRequestFactory()
        approved_loan = ApprovedLoanFactory(loan_request=loan_request)
        pmt_txn = PaymentTransactionFactory(
            profile=approved_loan.loan_request.profile
        )

        foreclosure_handler = ForeClosure(
            loan=approved_loan,
            loan_tranche=None,
            foreclosure_txn=pmt_txn,
            validated_data={},
            cashflow_type=None,
        )
        foreclosure_handler.no_subvention_refund = True
        foreclosure_handler.reverse_subvention_accrual()

        self.assertFalse(Allocation.objects.filter(pmt_txn=pmt_txn).exists())

    def test_reverse_subvention_accrual_without_config(self):
        """Should not create allocations if foreclosure_config is missing."""
        loan_request = LoanRequestFactory()
        approved_loan = ApprovedLoanFactory(
            loan_request=loan_request,
            approved_loan_amount=Decimal('300000'),
            product__foreclosure_config={}
        )
        pmt_txn = PaymentTransactionFactory(
            profile=approved_loan.loan_request.profile
        )

        foreclosure_handler = ForeClosure(
            loan=approved_loan,
            loan_tranche=None,
            foreclosure_txn=pmt_txn,
            validated_data={},
            cashflow_type=None,
        )
        foreclosure_handler.reverse_subvention_accrual()

        self.assertFalse(Allocation.objects.filter(pmt_txn=pmt_txn).exists())

    def test_reverse_subvention_accrual_with_zero_amount(self):
        """Should not create allocations if subvention refund is zero."""
        loan_request = LoanRequestFactory()
        approved_loan = ApprovedLoanFactory(
            loan_request=loan_request,
            product__foreclosure_config={
                'SUBVENTION_REFUND': {'key': 'dummy'}},
        )
        pmt_txn = PaymentTransactionFactory(
            profile=approved_loan.loan_request.profile)

        approved_loan.product.foreclosure_config = {
            'SUBVENTION_REFUND': {'value': Decimal('0')},
            'SUBVENTION_TAX_REFUND': {'value': Decimal('0')},
        }
        approved_loan.product.save()

        foreclosure_handler = ForeClosure(
            loan=approved_loan,
            loan_tranche=None,
            foreclosure_txn=pmt_txn,
            validated_data={},
            cashflow_type=None,
        )
        foreclosure_handler.reverse_subvention_accrual()
        self.assertFalse(Allocation.objects.filter(pmt_txn=pmt_txn).exists())
