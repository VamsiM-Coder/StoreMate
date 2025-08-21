def reverse_subvention_accrual(self):
    
        """Reverse subvention accrual."""
        if self.no_subvention_refund:
            return

        refund_calculator = self.approved_loan.product.foreclosure_config.get(
            'SUBVENTION_REFUND'
        )

        if refund_calculator:
            subvention_refund_data = {
                'TRANSACTION_DATE': self.foreclosure_txn_date,
                'LOAN': self.approved_loan,
            }
            subvention_amount = ProductBasedLoanTerms().calculate_loan_terms(
                subvention_refund_data,
                refund_calculator,
            )['SUBVENTION_REFUND']['value']
            subvention_tax_amnt = ProductBasedLoanTerms().calculate_loan_terms(
                subvention_refund_data,
                refund_calculator,
            )['SUBVENTION_TAX_REFUND']['value']
        else:
            book_name = (
                self.approved_loan.product.bookkeeping_configs.get(
                    'subvention_book_name', 'Subvention A/c')
            )
            _, subvention_amount = calculate_balance_for_book(
                book_name,
                approved_loan=self.approved_loan,
                as_of_date=self.foreclosure_txn_date
            )
            subvention_tax_amnt = to_decimal(
                subvention_amount * Decimal('0.18')
            )

        if subvention_amount:
            Allocation.objects.create(
                pmt_txn=self.foreclosure_txn,
                allocated_amount=-subvention_amount,
                approved_loan=self.approved_loan,
                loan_tranche=self.loan_tranche,
                borrower=self.approved_loan.loan_request.borrower,
                charge_type=RepaymentChargeType.SUBVENTION,
                allocation_date=self.foreclosure_txn_date
            )
            Allocation.objects.create(
                pmt_txn=self.foreclosure_txn,
                allocated_amount=-subvention_tax_amnt,
                approved_loan=self.approved_loan,
                loan_tranche=self.loan_tranche,
                borrower=self.approved_loan.loan_request.borrower,
                charge_type=RepaymentChargeType.SUBVENTION_TAX,
                allocation_date=self.foreclosure_txn_date
            )
