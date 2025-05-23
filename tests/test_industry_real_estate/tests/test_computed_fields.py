# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


class ComputedFieldsTestCase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_x_rental_contract_id_computation(self):
        self.demo_account_analytic_accounts = self.env['account.analytic.account'].search([])
        self.demo_sale_orders = self.env['sale.order'].search([])
        print(self.demo_account_analytic_accounts)
        print(self.demo_sale_orders)
        for sale_order in self.demo_sale_orders:
            if sale_order.x_account_analytic_account_id:
                self.assertEqual(sale_order, sale_order.x_account_analytic_account_id.x_rental_contract_id)
                print(sale_order, sale_order.x_account_analytic_account_id.x_rental_contract_id)
