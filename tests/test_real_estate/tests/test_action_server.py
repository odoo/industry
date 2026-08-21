# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests.common import TransactionCase
import logging
_logger = logging.getLogger(__name__)


class RealEstateAutomationsTestCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_commission_plan(self):
        seller = self.env['res.users'].create({'name': 'Seller', 'login': 'seller@example.com'})
        commission_plan_seller = self.env['sale.commission.plan.user'].create({
            'user_id': seller.id,
            'plan_id': self.env['sale.commission.plan'].search([('state', '=', 'approved')], limit=1).id
        })
        finder = self.env['res.users'].create({'name': 'Finder', 'login': 'finder@example.com'})
        self.env['sale.commission.plan.user'].create({
            'user_id': finder.id,
            'plan_id': self.env['sale.commission.plan'].search([('state', '=', 'approved')], limit=1).id
        })
        product = self.env['product.product'].create({
            'name': 'Test Property',
            'type': 'consu',
        })
        partner = self.env['res.partner'].create({'name': 'Customer'})
        sale_order = self.env['sale.order'].create({
            'partner_id': partner.id,
            'user_id': finder.id,
            'company_id': self.env.ref('base.main_company').id,
        })
        self.env['sale.order.line'].create({
            'order_id': sale_order.id,
            'product_id': product.id,
        })
        # Confirm the sale order
        sale_order.action_confirm()
        # Create the invoice
        invoice_wizard = self.env['sale.advance.payment.inv'].with_context(active_ids=sale_order.ids).create({'advance_payment_method': 'delivered'})
        invoice_wizard.create_invoices()
        invoice = sale_order.invoice_ids[0]
        # Set x_seller and post the invoice
        invoice.x_seller = seller.id
        invoice.action_post()

        # Check that a commission achievement was created
        achievement = self.env['sale.commission.achievement'].search([
            ('add_user_id', '=', commission_plan_seller.id),
        ])
        self.assertTrue(achievement, "A commission achievement should be created for the seller")
