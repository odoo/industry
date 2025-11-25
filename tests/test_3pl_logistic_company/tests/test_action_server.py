# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import Command, fields
from odoo.tests.common import TransactionCase
from odoo.tests import Form, tagged


@tagged('post_install', '-at_install')
class AutomationsTestCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_1, cls.partner_2 = cls.env['res.partner'].create([{'name': 'Test Partner 1'}, {'name': 'Test Partner 2'}])
        cls.product_template_1, cls.product_template_2 = cls.env['product.template'].create([{'name': 'Test Product 1'}, {'name': 'Test Product 2'}])

    def test_base_automation_on_owner_set_change_tracking(self):
        product_form = Form(self.product_template_1)
        product_form['x_owner_id'] = self.partner_1
        product_form.save()
        self.assertTrue(self.product_template_1.is_storable, "The is_storable field should be set to True when the owner is set.")
        self.assertEqual(self.product_template_1.tracking, 'lot', "The tracking should be set to 'lot' when the owner is set.")

    def test_base_automation_on_move_line_created(self):
        self.product_template_1.x_owner_id = self.partner_1
        so = self.env['sale.order'].create({
            'partner_id': self.partner_2.id,
            'order_line': [
                Command.create({'product_id': self.product_template_1.id, 'product_uom_qty': 1}),
            ]
        })
        so.action_confirm()
        move_line_owner_id = self.env['stock.move.line'].search([('product_id', '=', self.product_template_1.id)], limit=1).owner_id
        self.assertEqual(move_line_owner_id, self.partner_1, "Move line owner should match product owner")

    def test_base_automation_on_stock_move_changed(self):
        self.product_template_1.x_owner_id, self.product_template_2.x_owner_id = self.partner_1, self.partner_1
        stock_picking_1 = self.env['stock.picking'].create({
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'move_type': 'direct',
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id': self.env.ref('stock.stock_location_customers').id,
            'move_ids': [
                Command.create({'product_id': self.product_template_1.id, 'product_uom_qty': 1}),
                Command.create({'product_id': self.product_template_2.id, 'product_uom_qty': 1}),
            ]
        })
        self.assertEqual(stock_picking_1.owner_id, self.partner_1, "Picking owner should match product owner if all are same.")

    def test_base_automation_on_stock_move_changed_when_have_different_owner(self):
        self.product_template_1.x_owner_id, self.product_template_2.x_owner_id = self.partner_1, self.partner_2
        stock_picking_1 = self.env['stock.picking'].create({
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'move_type': 'direct',
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id': self.env.ref('stock.stock_location_customers').id,
            'move_ids': [
                Command.create({'product_id': self.product_template_1.id, 'product_uom_qty': 1}),
                Command.create({'product_id': self.product_template_2.id, 'product_uom_qty': 1}),
            ]
        })
        self.assertFalse(stock_picking_1.owner_id, "Owner should NOT be updated if products have different owners.")


class ServerActionTestCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Test Partner'})
        cls.product = cls.env['product.product'].create({'name': 'Test Product', 'recurring_invoice': True, 'type': 'service'})
        cls.period = cls.env['sale.subscription.plan'].create({
            'name': 'Monthly',
            'billing_period_value': 1,
            'billing_period_unit': 'month',
        })
        cls.invoice = cls.env['account.move'].create({
            'partner_id': cls.partner.id,
            'move_type': 'out_invoice',
            'invoice_date': fields.Datetime.now(),
            'x_invoice_period_id': cls.period.id,
            'invoice_line_ids': [
                Command.create({'product_id': cls.product.id, 'price_unit': 100, 'quantity': 1})],
        })
        cls.server_action = cls.env.ref('3pl_logistic_company.server_action_account_move_create_next')

    def test_server_action_account_move_create_next(self):
        self.server_action.with_context(active_id=self.invoice.id, active_model='account.move').run()
        new_invoice = self.env['account.move'].search([('id', '!=', self.invoice.id)], limit=1, order="id desc")

        self.assertTrue(new_invoice, "Server action should create a new invoice.")

        expected_date = self.invoice.invoice_date + relativedelta(months=1)
        self.assertEqual(new_invoice.invoice_date, expected_date, "Invoice date should be one month after the original invoice.")
        self.assertTrue(all(qty == 0 for qty in new_invoice.mapped('invoice_line_ids.quantity')), "Invoice line quantity should be zero.")
