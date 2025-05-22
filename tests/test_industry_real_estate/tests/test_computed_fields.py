# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime
from odoo.tests.common import TransactionCase


class ComputedFieldsTestCase(TransactionCase):

    def test_x_rental_contract_id_computation(self):
        for sale_order in self.env['sale.order'].search([('x_account_analytic_account_id', '!=', False)]):
            if sale_order.x_account_analytic_account_id:
                aa = sale_order.x_account_analytic_account_id
                start_date = sale_order.x_rental_start_date
                self.assertTrue(
                    (sale_order == aa.x_rental_contract_id) or (
                        aa == aa.x_rental_contract_id.x_account_analytic_account_id and (
                            (start_date < aa.x_rental_contract_id.x_rental_start_date) or
                            (start_date > datetime.date.today())
                        )
                    )
                )
