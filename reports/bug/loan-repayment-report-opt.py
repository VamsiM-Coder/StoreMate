from collections import defaultdict
from openpyxl import Workbook
from accounting.choices import RepaymentChargeType
from accounting.models import Allocation
from base.utils.date import parse_date
from loan.choices import LoanRepaymentStatus
from loan.models import LoanRepayment
from nach.models import NachMandate


def get_dpd(repayment, collected, as_of_date):
    """Calculate Days Past Due (DPD)."""
    if repayment['repayment_status'] in [LoanRepaymentStatus.PAID, LoanRepaymentStatus.PREPAID]:
        return 0

    if repayment['principal_amount'] > collected and repayment['due_date'] < as_of_date:
        return (as_of_date - repayment['due_date']).days + 1

    return 0


def main(temp_dir, **kwargs):
    """Execute report."""
    as_of_date = parse_date(kwargs.get('as_of_date'))

    filter = {
        'loan__disbursement_date__gte': parse_date(kwargs['from_date']) if kwargs.get('from_date') else None,
        'loan__disbursement_date__lte': parse_date(kwargs['to_date']) if kwargs.get('to_date') else None,
        'due_date__gte': parse_date(kwargs['due_date_from']) if kwargs.get('due_date_from') else None,
        'due_date__lte': parse_date(kwargs['due_date_to']) if kwargs.get('due_date_to') else None,
        'loan__product__name__in': kwargs.get('product_name') if kwargs.get('product_name') else None,
    }
    filter = {k: v for k, v in filter.items() if v is not None}

    repayments = list(
        LoanRepayment.objects.filter(**filter)
        .values(
            'uuid',
            'due_date',
            'repayment_amount',
            'principal_amount',
            'interest_amount',
            'loan__loan_request__lead__partner_loan_id',
            'loan__loan_agreement_id',
            'loan__disbursement_date',
            'loan__product__name',
            'loan__loan_request__source_identifier',
            'loan__profile__full_name',
            'loan__approved_loan_amount',
            'repayment_status',
            'remaining_amount',
            'remaining_principal',
            'remaining_interest',
            'loan_tranche_id'
        )
        .order_by('loan__loan_agreement_id', 'due_date')
    )

    lans = {x['loan__loan_agreement_id'] for x in repayments}

    allocations = Allocation.objects.filter(
        approved_loan__loan_agreement_id__in=lans,
        charge_type=RepaymentChargeType.PRINCIPAL,
        allocation_date__lte=as_of_date
    ).values('loan_repayment_id', 'allocated_amount')

    remapped_allocations = defaultdict(int)
    for alloc in allocations:
        remapped_allocations[alloc['loan_repayment_id']] += alloc['allocated_amount']

    mandates = (
        NachMandate.objects.filter(approved_loan__loan_agreement_id__in=lans)
        .values('approved_loan__loan_agreement_id', 'umrn')
    )
    latest_mandates = {}
    for m in mandates:
        latest_mandates[m['approved_loan__loan_agreement_id']] = m['umrn']

    headers = [
        'Product', 'Partner Name', 'LAN', 'Partner Loan Id', 'Full Name', 'Loan Amount',
        'Disbursal Date', 'EMI Date', 'EMI Amount', 'Principal Amount', 'Interest Amount',
        'Repayment Status', 'Remaining Principal', 'Remaining Interest', 'Remaining Total',
        'Paid Principal', 'Paid Interest', 'Paid Total', 'Loan Tranche Id', 'UMRN', 'DPD'
    ]

    file_name = temp_dir + '/repayment_schedule_report.xlsx'
    wb = Workbook()
    ws = wb.active
    ws.append(headers)

    for repayment in repayments:
        repayment_id = repayment['uuid']
        lan = repayment['loan__loan_agreement_id']

        collected = remapped_allocations.get(repayment_id, 0)
        mandate_umrn = latest_mandates.get(lan, '')

        ws.append([
            repayment['loan__product__name'],
            repayment['loan__loan_request__source_identifier'],
            lan,
            repayment['loan__loan_request__lead__partner_loan_id'],
            repayment['loan__profile__full_name'],
            repayment['loan__approved_loan_amount'],
            repayment['loan__disbursement_date'],
            repayment['due_date'],
            repayment['repayment_amount'],
            repayment['principal_amount'],
            repayment['interest_amount'],
            LoanRepaymentStatus(repayment['repayment_status']).name,
            repayment['remaining_principal'],
            repayment['remaining_interest'],
            repayment['remaining_principal'] + repayment['remaining_interest'],
            repayment['principal_amount'] - repayment['remaining_principal'],
            repayment['interest_amount'] - repayment['remaining_interest'],
            repayment['repayment_amount'] - repayment['remaining_amount'],
            str(repayment['loan_tranche_id']),
            mandate_umrn,
            get_dpd(repayment, collected, as_of_date),
        ])

    wb.save(file_name)
    return file_name
