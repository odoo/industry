# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.fields import Command
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestPosOrderAccount(TransactionCase):

    def setUp(self):
        super().setUp()

        self.partner = self.env['res.partner'].create({'name': 'Test Customer'})
        self.product = self.env['product.product'].create({'name': 'Test Product', 'lst_price': 100.0})
        self.account_payment_method = self.env['pos.payment.method'].create({
            'name': 'Customer Account',
            'split_transactions': True,
        })

        self.pos_config = self.env['pos.config'].create({
            'name': 'Test Shop',
            'payment_method_ids': [Command.set(self.account_payment_method.ids)],
        })

    def test_pos_order_state_flow(self):
        self.pos_config.open_ui()
        session = self.pos_config.current_session_id

        self.assertEqual(self.account_payment_method.type, 'pay_later')

        order_data = {
            'amount_paid': 100.0,
            'amount_return': 0,
            'amount_tax': 0,
            'amount_total': 100.0,
            'lines': [Command.create({
                'product_id': self.product.id,
                'qty': 1,
                'price_unit': 100.0,
                'price_subtotal': 100.0,
                'price_subtotal_incl': 100.0,
                'full_product_name': 'Test Product',
            })],
            'name': 'Order 00001-001-0001',
            'partner_id': self.partner.id,
            'payment_ids': [Command.create({
                'amount': 100.0,
                'payment_method_id': self.account_payment_method.id,
                'name': '2023-01-01 10:00:00',
            })],
            'session_id': session.id,
            'to_invoice': False,
            'uuid': '00001-001-0001',
        }
        result = self.env['pos.order'].sync_from_ui([order_data])
        order_id = result['pos.order'][0].get('id')
        pos_order = self.env['pos.order'].browse(order_id)

        self.assertEqual(pos_order.state, 'paid', "Order should be in 'Paid' state while session is open.")
        self.assertEqual(pos_order.customer_due_total, 100)
        self.assertFalse(pos_order.account_move)

        move = self.env['account.move'].with_context(default_move_type='out_invoice').create({'partner_id': self.partner.id})

        self.assertEqual(len(move.invoice_line_ids), 2, "There should be two lines in the invoice")
        self.assertEqual(move.invoice_line_ids[0].display_type, 'line_section')
        self.assertEqual(move.invoice_line_ids[0].display_name, "Customer account balance")
        self.assertEqual(move.invoice_line_ids[1].price_unit, 100)
        self.assertEqual(move.invoice_line_ids[1].x_pos_order_id, pos_order)
        move.unlink()

        session.action_pos_session_closing_control()
        self.assertEqual(pos_order.state, 'done', "Order should be in 'Done' state while session is closed.")

        move = self.env['account.move'].with_context(default_move_type='out_invoice').create({'partner_id': self.partner.id})
        self.assertEqual(len(move.invoice_line_ids), 2, "There should be two lines in the invoice")
        self.assertEqual(move.invoice_line_ids[0].display_type, 'line_section')
        self.assertEqual(move.invoice_line_ids[0].display_name, "Customer account balance")
        self.assertEqual(move.invoice_line_ids[1].price_unit, 100)
        self.assertEqual(move.invoice_line_ids[1].x_pos_order_id, pos_order)

        self.assertEqual(pos_order.customer_due_total, 100)
        self.assertFalse(pos_order.account_move)
        move.action_post()
        self.assertEqual(pos_order.customer_due_total, 0)
        self.assertEqual(pos_order.account_move, move)
