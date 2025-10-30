# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime
from odoo.tests.common import TransactionCase


class ComputedFieldsTestCase(TransactionCase):

    def test_x_rental_contract_id_computation(self):
        for sale_order in self.env['sale.order'].search([('x_account_analytic_account_id', '!=', False)]):
            aa = sale_order.x_account_analytic_account_id
            if rental_contract := aa.x_rental_contract_id:
                start_date = sale_order.x_rental_start_date
                self.assertTrue(
                    (sale_order == rental_contract) or (
                        aa == rental_contract.x_account_analytic_account_id and (
                            (start_date < rental_contract.x_rental_start_date) or
                            (start_date > datetime.date.today())
                        )
                    )
                )
            else:
                self.assertTrue(
                    sale_order.subscription_state in ['5_renewed', '6_churn']
                    or sale_order.x_rental_start_date > datetime.date.today()
                )
