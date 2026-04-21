# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta

from odoo.addons.payment.tests.http_common import PaymentHttpCommon
from odoo import Command
from odoo.exceptions import ValidationError


class TestOverbooking(PaymentHttpCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.partner = cls.env['res.partner'].create({'name': 'Test partner'})
        cls.resource = cls.env['resource.resource'].create({
            'name': 'Room 101',
            'resource_type': 'material',
        })
        cls.role = cls.env['planning.role'].create({
            'name': 'Stay Offer Role',
            'sync_shift_rental': True,
            'x_is_a_room_offer': True,
            'resource_ids': [Command.link(cls.resource.id)],
        })
        cls.product = cls.env['product.template'].create({
            'name': 'Standard Room',
            'type': 'service',
            'planning_enabled': True,
            'planning_role_id': cls.role.id,
            'sale_ok': True,
            'list_price': 10,
            'rent_periodicity': 'days',
            'is_published': True,
        })
        cls.express_checkout_billing_values = {
            'name': 'Demo User',
            'email': 'demo@test.com',
            'street': 'ooo',
            'street2': 'ppp',
            'city': 'ooo',
            'zip': '1200',
            'country': "US",
        }
        cls.provider = cls._prepare_provider('demo')
        cls.payment_method = cls.env['payment.method'].search([('code', '=', 'demo')], limit=1)
        cls.start_date = datetime.today() + timedelta(days=1)
        cls.end_date = datetime.today() + timedelta(days=2)
        cls.date_format = "%Y-%m-%d %H:%M:%S"

        def create_sale_order(cls):
            return cls.env['sale.order'].with_context(in_rental_app=True).create({
                'partner_id': cls.partner.id,
                'rental_start_date': cls.start_date,
                'rental_return_date': cls.end_date,
                'order_line': [
                    Command.create({
                        'product_id': cls.product.id,
                        'product_uom_qty': 1,
                    }),
                ],
            })
        cls.create_sale_order = create_sale_order

        def create_planning_slot(cls):
            cls.env['planning.slot'].create({
                'resource_id': cls.resource.id,
                'role_id': cls.role.id,
                'start_datetime': cls.start_date,
                'end_datetime': cls.end_date,
            })
        cls.create_planning_slot = create_planning_slot

    def test_user_book_stay_offer_available(self):
        """
        Scenario: User can book a stay offer when resources are available
        """
        sale_order = self.create_sale_order()
        sale_order.action_confirm()
        slot = sale_order.order_line.planning_slot_ids
        self.assertEqual(len(slot), 1, "One planning slot should be created.")
        self.assertEqual(slot.resource_id, self.resource, "The slot should be assigned to the available room.")
        self.assertEqual(slot.start_datetime, sale_order.rental_start_date, "Slot start should match SO rental start.")
        self.assertEqual(slot.end_datetime, sale_order.rental_return_date, "Slot end should match SO rental return.")

    def test_user_cant_book_stay_offer_unavailable_shift_conflicts(self):
        """
        Scenario: User can't book a stay offer when resources are not available due to shift conflicts
        """
        self.create_planning_slot()
        sale_order = self.create_sale_order()
        with self.assertRaises(ValidationError, msg="This Sales Order can't be confirmed. No resources are available for the shifts in: %s." % self.product.name):
            sale_order.action_confirm()

    def test_user_cant_book_stay_offer_unavailable_leaves_for_resource(self):
        """
        Scenario: User can't book a stay offer when resources are not available due to leaves for a resource
        """
        self.env['resource.calendar.leaves'].create([{
            'name': 'Maintenance',
            'date_from': self.start_date,
            'date_to': self.end_date,
            'resource_id': self.resource.id,
            'time_type': 'leave',
        }])
        sale_order = self.create_sale_order()
        with self.assertRaises(ValidationError, msg="This Sales Order can't be confirmed. No resources are available for the shifts in: %s." % self.product.name):
            sale_order.action_confirm()

    def _test_user_cant_book_stay_offer_unavailable_leaves_without_resource(self):
        """
        Scenario: User can't book a stay offer when resources are not available due to leaves without a resource
        """
        self.env['resource.calendar.leaves'].create([{
            'name': 'Maintenance',
            'date_from': self.start_date,
            'date_to': self.end_date,
            'time_type': 'leave',
        }])
        sale_order = self.create_sale_order()
        with self.assertRaises(ValidationError, msg="This Sales Order can't be confirmed. No resources are available for the shifts in: %s." % self.product.name):
            sale_order.action_confirm()

    def test_ecommerce_book_stay_offer_available(self):
        """
        Scenario: Customer from ecommerce can book a stay offer when resources are available
        """
        self.authenticate(None, None)
        response = self.make_jsonrpc_request("/shop/cart/add", {
            'product_template_id': self.product.id,
            'product_id': self.product.product_variant_id.id,
            'quantity': 1,
            'start_date': self.start_date.strftime(self.date_format),
            'end_date': self.end_date.strftime(self.date_format),
        })
        self.assertEqual(response['tracking_info'][0]['item_id'], self.product.id, "No item found in shopping cart.")
        sale_order = self.env['sale.order'].search([], limit=1)
        self.assertTrue(sale_order, "No sale order was created from ecommerce.")
        self.assertEqual(sale_order.order_line.product_id.id, self.product.id, "product doesn't exist in sale order.")
        self.assertEqual(sale_order.state, 'draft', "The order should be in 'draft' state.")
        self.assertTrue(self.payment_method, "No payment method.")
        self.assertTrue(self.provider, "No provider.")
        self.make_jsonrpc_request("/shop/express_checkout", {
            'billing_address': self.express_checkout_billing_values,
        })
        response = self.make_jsonrpc_request(
            f"/shop/payment/transaction/{sale_order.id}",
            {
                'access_token': sale_order._portal_ensure_token(),
                'flow': 'direct',
                'landing_route': '/shop/payment/validate',
                'payment_method_id': self.payment_method.id,
                'provider_id': self.provider.id,
                'token_id': None,
                'tokenization_requested': False,
            }
        )
        self.assertEqual(response['reference'], sale_order.name, "Purchase reference should be order name.")
        response = self.make_jsonrpc_request(
            "/payment/demo/simulate_payment",
            {
                'reference': response['reference'],
                'simulated_state': 'done',
            }
        )
        tx = self.env['payment.transaction'].search([])
        self.assertTrue(tx, "No transaction was created from ecommerce")
        self.assertIn(sale_order.id, tx.sale_order_ids.ids, "Sale order not in transaction.")
        tx._post_process()
        self.assertEqual(sale_order.state, 'sale', "The order should be in 'sale' state.")
        planning_slot = sale_order.order_line.planning_slot_ids
        self.assertTrue(planning_slot, "There should be planning slots assigned for this product rental.")
        self.assertEqual(len(planning_slot), 1, "There should be exactly 1 slot allocated to the rental Period.")
        self.assertLess(abs(planning_slot.start_datetime - self.start_date).total_seconds(), 86400, "The planning slot should begin at the same time as the rental date.")
        self.assertLess(abs(planning_slot.end_datetime - self.end_date).total_seconds(), 86400, "The planning slot should end at the same time as the rental date.")

    def test_ecommerce_book_stay_offer_unavailable(self):
        """
        Scenario: Customer from ecommerce can't book a stay offer when resources are not available
        """
        self.create_planning_slot()
        self.authenticate(None, None)
        response = self.make_jsonrpc_request("/shop/cart/add", {
            'product_template_id': self.product.id,
            'product_id': self.product.product_variant_id.id,
            'quantity': 1,
            'start_date': self.start_date.strftime(self.date_format),
            'end_date': self.end_date.strftime(self.date_format),
        })
        self.assertEqual(response['tracking_info'][0]['item_id'], self.product.id, "No item found in shopping cart.")
        sale_order = self.env['sale.order'].search([], limit=1)
        self.assertTrue(sale_order, "No sale order was created from ecommerce.")
        self.assertEqual(sale_order.order_line.product_id.id, self.product.id, "product doesn't exist in sale order.")
        self.assertEqual(sale_order.state, 'draft', "The order should be in 'draft' state.")
        self.make_jsonrpc_request("/shop/express_checkout", {
            'billing_address': self.express_checkout_billing_values,
        })
        response = self.make_jsonrpc_request(
            f"/shop/payment/transaction/{sale_order.id}",
            {
                'access_token': sale_order._portal_ensure_token(),
                'flow': 'direct',
                'landing_route': '/shop/payment/validate',
                'payment_method_id': self.payment_method.id,
                'provider_id': self.provider.id,
                'token_id': None,
                'tokenization_requested': False,
            }
        )
        self.assertEqual(response['reference'], sale_order.name, "Purchase reference should be order name.")
        response = self.make_jsonrpc_request(
            "/payment/demo/simulate_payment",
            {
                'reference': response['reference'],
                'simulated_state': 'done',
            }
        )
        tx = self.env['payment.transaction'].search([])
        self.assertTrue(tx, "No transaction was created from ecommerce")
        self.assertIn(sale_order.id, tx.sale_order_ids.ids, "Sale order not in transaction.")
        with self.assertRaises(ValidationError, msg="This Sales Order can't be confirmed. No resources are available for the shifts in: %s." % self.product.product_variant_id.display_name):
            tx._post_process()

    def test_ecommerce_ui_booking_flow(self):
        """ Test the UI flow from the product page """
        if not self.env['ir.module.module'].search_count([('demo', '=', True)], limit=1):
            return

        self.create_planning_slot()
        self.start_tour("/shop", "shop_booking_flow", login="admin")
        sale_order = self.env['sale.order'].search([], limit=1)
        self.assertTrue(sale_order, "No sale order was created from ecommerce.")
        self.assertEqual(sale_order.state, 'sale', "The order should be in 'sale' state.")
        planning_slot = sale_order.order_line.planning_slot_ids
        self.assertTrue(planning_slot, "There should be planning slots assigned for this product rental.")
        self.assertEqual(len(planning_slot), 1, "There should be exactly 1 slot allocated to the rental Period.")
