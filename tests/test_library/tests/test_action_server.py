# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import Command
from odoo.tests import Form, tagged
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install')
class LibraryAutomationsTestCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env['stock.warehouse'].create({
            'name': 'Test Warehouse',
            'code': 'TWH',
        })

        cls.partner = cls.env['res.partner'].create({
            'name': 'Test partner',
        })

        cls.location = cls.env['stock.location'].create({'name': "Test location"})

        cls.warehouse.out_type_id.write({'x_overrule_customer_location': True})

        # add these 2 fields so the default is overridden in _compute_location_id so it's different from default_location_dest_id
        cls.partner.write({'property_stock_customer': cls.location})
        cls.warehouse.out_type_id.default_location_src_id.write({'usage': 'customer'})

    ##################
    # SERVER ACTIONS #
    ##################

    def test_action_stock_rule_set_push_domain_on_create_or_write(self):
        server_action = self.env.ref('library.action_stock_rule_set_push_domain_on_create_or_write')

        rule_standard = self.env['stock.rule'].create({
            'name': 'Test standard rule',
            'action': 'push',
            'route_id': self.warehouse.reception_route_id.id,
            'location_dest_id': self.env.ref('stock.stock_location_suppliers').id,  # idk what to put here
            'picking_type_id': self.env.ref('stock.picking_type_out').id,  # idk what to put here
            'x_standard_rule': True,
        })
        rule_non_standard = self.env['stock.rule'].create({
            'name': 'Test non standard rule',
            'action': 'push',
            'route_id': self.warehouse.reception_route_id.id,
            'location_dest_id': self.env.ref('stock.stock_location_suppliers').id,  # idk what to put here
            'picking_type_id': self.env.ref('stock.picking_type_out').id,  # idk what to put here
        })
        rule_pos_categ = self.env['stock.rule'].create({
            'name': 'Test non standard rule',
            'action': 'push',
            'route_id': self.warehouse.reception_route_id.id,
            'location_dest_id': self.env.ref('stock.stock_location_suppliers').id,  # idk what to put here
            'picking_type_id': self.env.ref('stock.picking_type_out').id,  # idk what to put here
            'x_pos_product_category_ids': [self.env.ref('library.pos_category_2').id, self.env.ref('library.pos_category_4').id],
        })

        self.assertNotEqual(rule_standard.push_domain, '[]',
                            "Test precondition: push domain should be different from expected result")
        server_action.with_context(active_ids=rule_standard.id, active_model='stock.rule').run()
        self.assertEqual(rule_standard.push_domain, '[]',
                         "The action should set an empty push domain on a standard rule")

        self.assertNotEqual(rule_non_standard.push_domain, '[]',
                            "Test precondition: push domain should be different from expected result")
        self.assertNotEqual(rule_pos_categ.push_domain, f'[(\'product_id.pos_categ_ids\', \'in\', {rule_pos_categ.x_pos_product_category_ids.ids})]',
                            "Test precondition: push domain should be different from expected result")
        server_action.with_context(active_ids=[rule_non_standard.id, rule_pos_categ.id], active_model='stock.rule').run()
        self.assertEqual(rule_non_standard.push_domain, '[]',
                         "The action should set an empty push domain for a non standard rule")
        self.assertEqual(rule_pos_categ.push_domain, f'[(\'product_id.pos_categ_ids\', \'in\', {rule_pos_categ.x_pos_product_category_ids.ids})]',
                         "The action should set the domain to be on products with matching categories for a non standard rule with POS categories")

    def test_action_update_automatic_activation_on_product_on_change(self):
        server_action = self.env.ref('library.action_update_automatic_activation_on_product_on_change')

        route_1 = self.env.ref('library.stock_route_4')
        route_1.update({'product_selectable': True})
        route_2 = self.env.ref('library.stock_route_2')
        route_3 = self.env.ref('library.stock_route_3')

        self.assertTrue(route_1.x_automatic_activation_on_product,
                        "Test precondition: x_automatic_activation_on_product should be different from expected result")
        self.assertFalse(route_2.x_automatic_activation_on_product,
                         "Test precondition: x_automatic_activation_on_product should be different from expected result")
        server_action.with_context(active_ids=[route_1.id, route_2.id], active_model='stock.route').run()
        self.assertFalse(route_1.x_automatic_activation_on_product,
                         "The action should set x_automatic_activation_on_product as the opposite value of product_selectable for multiple records")
        self.assertTrue(route_2.x_automatic_activation_on_product,
                        "The action should set x_automatic_activation_on_product as the opposite value of product_selectable for multiple records")

        self.assertFalse(route_3.x_automatic_activation_on_product,
                         "Test precondition: x_automatic_activation_on_product should be different from expected result")
        server_action.with_context(active_ids=route_3.id, active_model='stock.route').run()
        self.assertTrue(route_3.x_automatic_activation_on_product,
                        "The action should set x_automatic_activation_on_product as the opposite value of product_selectable for a single record")

    def test_action_update_destination_location_on_picking_create(self):
        server_action = self.env.ref('library.action_update_destination_location_on_picking_create')

        picking = self.env['stock.picking'].create({
            'name': "Test Picking",
            'partner_id': self.partner.id,
            'picking_type_id': self.warehouse.out_type_id.id,
            'location_dest_id': self.location.id,
            'move_ids': [Command.create({
                'product_id': self.env.ref('library.product_product_9').id,
                'product_uom_qty': 5,
                'quantity': 5,
                'location_id': self.env.ref('stock.stock_location_customers').id,
                'location_dest_id': self.location.id,
            })],
        })
        # creating the above record triggers the automation, and the location will be updated immediately
        # modify the value manually to test the action by itself manually
        picking.write({'location_dest_id': self.location.id})

        self.assertNotEqual(picking.location_dest_id.id, picking.picking_type_id.default_location_dest_id.id,
                            "Test precondition: picking.location_dest_id.id should be different from expected result")
        server_action.with_context(active_ids=picking.id, active_model='stock.picking').run()
        self.assertEqual(picking.location_dest_id.id, picking.picking_type_id.default_location_dest_id.id,
                         "The action should update the location if x_overrule_customer_location is set")

        self.warehouse.out_type_id.write({'x_overrule_customer_location': False})
        picking.write({'location_dest_id': self.location.id})

        self.assertEqual(picking.location_dest_id.id, self.location.id,
                         "Test precondition: picking.location_dest_id.id should be the one just set")
        server_action.with_context(active_ids=picking.id, active_model='stock.picking').run()
        self.assertEqual(picking.location_dest_id.id, self.location.id,
                         "The action should not update the location if x_overrule_customer_location is not set")

    def test_action_make_route_on_product_create(self):
        server_action = self.env.ref('library.action_make_route_on_product_create')

        stock_route = self.env.ref('library.stock_route_4')
        product_template = self.env['product.template'].create({
            'name': 'Test Product Template',
        })
        # clear the route manually because automation is called
        product_template.write({'route_ids': None})

        self.assertNotEqual(product_template.route_ids.id, stock_route.id,
                            "Test precondition: product_template.route_ids.id should not be the expected result")
        server_action.with_context(active_id=product_template.id, active_model='product.template').run()
        self.assertEqual(product_template.route_ids.id, stock_route.id,
                         "The action should set the route_ids to stock_route_4")

    def test_action_add_qty_on_product_create(self):
        server_action = self.env.ref('library.action_add_qty_on_product_create')
        products = [self.env.ref('library.product_product_9').id, self.env.ref('library.product_product_10').id]

        number_before = self.env['stock.quant'].search_count([('quantity', '=', 1.0)])
        server_action.with_context(active_ids=products, active_model='product.product').run()
        self.assertEqual(self.env['stock.quant'].search_count([('quantity', '=', 1.0)]), number_before + 2,  # add 1.0 qty for the two products
                         "The action called on 2 products should add two entries to stock.quant")

    ###############
    # AUTOMATIONS #
    ###############

    def test_automation_update_push_domain_on_create_or_write(self):
        rule_stock_route_4 = self.env['stock.rule'].create({
            'name': 'Test rule stock route 4',
            'action': 'push',
            'route_id': self.env.ref('library.stock_route_4').id,
            'location_dest_id': self.env.ref('stock.stock_location_suppliers').id,  # idk what to put here
            'picking_type_id': self.env.ref('stock.picking_type_out').id,  # idk what to put here
            'x_standard_rule': True,
            'x_pos_product_category_ids': [self.env.ref('library.pos_category_2').id, self.env.ref('library.pos_category_4').id],
        })
        rule_other_route = self.env['stock.rule'].create({
            'name': 'Test other rule',
            'action': 'push',
            'route_id': self.warehouse.reception_route_id.id,
            'location_dest_id': self.env.ref('stock.stock_location_suppliers').id,  # idk what to put here
            'picking_type_id': self.env.ref('stock.picking_type_out').id,  # idk what to put here
            'x_standard_rule': True,
        })
        rule_pos_categ = self.env['stock.rule'].create({
            'name': 'Test non standard rule',
            'action': 'push',
            'route_id': self.env.ref('library.stock_route_4').id,
            'location_dest_id': self.env.ref('stock.stock_location_suppliers').id,  # idk what to put here
            'picking_type_id': self.env.ref('stock.picking_type_out').id,  # idk what to put here
        })
        self.assertEqual(rule_stock_route_4.push_domain, '[]',
                         "The automation should work on targets inside of the domain on create")
        self.assertEqual(rule_other_route.push_domain, False,
                         "The automation should not work on targets outside of the domain on create")
        self.assertEqual(rule_pos_categ.push_domain, '[]',
                         "The automation should work on targets inside of the domain on create")

        rule_stock_route_4.write({'x_standard_rule': False})
        self.assertNotEqual(rule_stock_route_4.push_domain, '[]',
                            "The automation should update the push domain on write of x_standard_rule field")

        rule_other_route.write({'x_pos_product_category_ids': [self.env.ref('library.pos_category_2').id, self.env.ref('library.pos_category_4').id]})
        self.assertEqual(rule_other_route.push_domain, False,
                         "The automation should not work on targets outside of the domain")

        rule_pos_categ.write({'x_pos_product_category_ids': [self.env.ref('library.pos_category_2').id, self.env.ref('library.pos_category_4').id]})
        self.assertNotEqual(rule_pos_categ.push_domain, '[]',
                            "The automation should update the push domain on write of x_pos_product_category_ids field")

    def test_automation_update_automatic_activation_on_product_on_change(self):
        route = self.env.ref('library.stock_route_4')

        self.assertEqual(route.x_automatic_activation_on_product, True,
                         "Test precondition: x_automatic_activation_on_product should be different from expected result")
        with Form(route) as f:
            f.product_selectable = True
        self.assertEqual(route.x_automatic_activation_on_product, False,
                         "The automation should update x_automatic_activation_on_product on change of field product_selectable")

    def test_automation_make_route_on_product_create(self):
        product_template = self.env['product.template'].create({'name': 'Test product template'})
        self.assertEqual(product_template.route_ids, self.env.ref('library.stock_route_4'),
                         "The automation should set stock_route_4 as a template route on product template create")

    def test_automation_update_destination_location_on_picking_create(self):
        picking = self.env['stock.picking'].create({
            'name': "Test Picking",
            'partner_id': self.partner.id,
            'picking_type_id': self.warehouse.out_type_id.id,
            'location_dest_id': self.location.id,
            'move_ids': [Command.create({
                'product_id': self.env.ref('library.product_product_9').id,
                'product_uom_qty': 5,
                'quantity': 5,
                'location_id': self.env.ref('stock.stock_location_customers').id,
                'location_dest_id': self.location.id,
            })],
        })
        self.assertEqual(picking.location_dest_id.id, picking.picking_type_id.default_location_dest_id.id,
                         "The automation should set the picking location destination as the default picking type location destination on picking create")

    def test_automation_add_qty_on_product_create(self):
        product_not_storable = self.env['product.product'].create({'name': "Test product not storable", 'is_storable': False})
        self.assertEqual(self.env['stock.quant'].search_count([('product_id', '=', product_not_storable.id)]), 0,
                         "The automation should not work on targets outside of the domain on create")

        product_storable = self.env['product.product'].create({'name': "Test product storable", 'is_storable': True})
        self.assertEqual(self.env['stock.quant'].search_count([('product_id', '=', product_storable.id)]), 2,
                         "The automation should create a WH/Stock and an inventory adjustment if the product is storable")
