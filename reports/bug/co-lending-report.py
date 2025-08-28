"""CO-Lending Report."""

import pandas as pd

from api.models import ServiceDetail

from loan.choices import LoanApprovalStatus
from loan.models import ApprovedLoan

def fetch_post_disbursal_details():
    """Fn for checking post disbursal data."""
    services = ServiceDetail.objects.filter(
        service__key='post-disbursement-details'
    ).values(
        'object_id',
        'request_data',
    )
    post_disbursal_details = {}
    for service in services:
        post_disbursal_details[service['object_id']] = service['request_data']
    return post_disbursal_details


def main(temp_dir, **kwargs):
    """Co-lending report."""
    headers = [
        "Customer Name",
        "Flow Status",
        "Flow Stage",
        "Application Created At",
        "Loan Acc No1",
        "Partner Loan Id",
        "Sanctioned Loan Amount",
        "Disb Amount",
        "Disbursement Date",
        "Bre Approved Installation Address State",
        "Dealer Code",
        "Disbursal UTR",
        # CO-Lending Details
        "EMI",
        "Repayment Mode",
        "Loan First Installment Date",
        "Bureau Score",
        "Emi Day of Month",
        "Insuance Premium Amount",
        "Loan Details Repayment Frequency",
        # Post Disbursal Details
        "UMRN",
        "Vehicle Idv",
        "Life Insurance",
        "Health Insurance",
        "Addon Insurance Price",
        "Is Insurance Applicable",
        "Vehicle Registration Number",
        "Vehicle Insurance Validity Date",
        "Rc Number",
        "Chassis Number",
        "Vehicle Battery Type",
        "Vehicle On Road Price",
        "Vehicle Insuurance Provider",
        "Vehicle Insurance Policy Number",
    ]

    loans = ApprovedLoan.objects.filter(
        approval_status__in=LoanApprovalStatus.disbursed_status_list,
        product__name__icontains="Co-Lending",
    ).values_list(
        'profile__full_name', #0
        'loan_request__created_at', #1
        'loan_agreement_id', #2
        'loan_request__lead__partner_loan_id', #3
        'approved_loan_amount', #4
        'disbursal_amount', #5
        'disbursement_date', #6
        'disbursal_txn', #7
        'loan_request_id', #8
        'loan_request__original_request_data', #9
        'loan_request__loan_application_status', #10
        'loan_request__loan_application_stage', #11
    )

    post_disbursal_details = fetch_post_disbursal_details()

    data = []
    for loan in loans:
        post_disbursal = post_disbursal_details.get(loan[8], {})
        co_lending_details = loan[9].get('co_lending_details', {})

        data.append([
                loan[0],  # Customer Name
                loan[10],  # Flow Status
                loan[11],  # Flow Stage
                loan[1].strftime("%d-%m-%Y"),  # Application Created At
                loan[2],  # Loan Acc No
                loan[3],  # Partner Loan Id
                co_lending_details.get('sa'),  # Sanctioned Loan Amount                                          |
                co_lending_details.get('dis_a'),  # Disb Amount                                                  |
                loan[6],  # Disbursement Date
                loan[9].get('vehicle_details',
                            {}).get('dealer_state', ''),  # Dealer State
                loan[9].get('dealer_code'),  # Dealer Code
                loan[7],  # Disbursal UTR
                co_lending_details.get('emi'),  # EMI
                co_lending_details.get('repayment_mode'),  # Repayment Mode
                co_lending_details.get('loan_first_installment_date'),  # First EMI Date
                co_lending_details.get('bureau_score'),  # Bureau Score
                co_lending_details.get('emi_day_of_month'),  # EMI Day
                co_lending_details.get('insurance_premium_amount'),  # Insurance Premium
                co_lending_details.get('loan_details_repayment_frequency'),  # Repayment Frequency
                loan[9].get('nach_details', {}).get('umrn'),  # UMRN
                loan[9].get('vehicle_details', {}).get('vehicle_idv', ''),  # Vehicle IDV
                post_disbursal.get('life_insurance'),  # Life Insurance
                post_disbursal.get('health_insurance'),  # Health Insurance
                post_disbursal.get('addon_insurance_price'),  # Add-on Insurance
                loan[9].get('is_insurance_applicable',{}),   # Is Insurance Applicable
                post_disbursal.get('vehicle_registration_number'),  # Vehicle Registration
                loan[9].get('vehicle_details',
                            {}).get('vehicle_insurance_validity_date', ''),  # Insurance Validity
                post_disbursal.get('rc_number'),  # RC Number
                loan[9].get('vehicle_details', {}).get('chassis_number', ''),  # Chassis No
                loan[9].get('vehicle_details', {}).get('vehicle_battery_type', ''),  # Battery Type
                post_disbursal.get(road_price),  # On Road Price                                                       |
                loan[9].get('vehicle_details', {}).get('vehicle_insurance_provider', ''),  # Insurance Provider
                loan[9].get('vehicle_details',
                            {}).get('vehicle_insurance_policy_number', ''),  # Policy Number
            ])    

    file_name = f"{temp_dir}/co-lending-report.xlsx"
    df = pd.DataFrame(data, columns=headers)
    df.to_excel(file_name, index=False)
    return file_name
