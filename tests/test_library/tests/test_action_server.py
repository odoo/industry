# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import Command
from odoo.tests import Form, tagged
from odoo.tests.common import TransactionCase


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

        cls.warehouse.out_type_id.x_overrule_customer_location = True

        # add these 2 fields so the default is overridden in _compute_location_id so it's different from default_location_dest_id
        cls.partner.property_stock_customer = cls.location
        cls.warehouse.out_type_id.default_location_src_id.usage = 'customer'

    ##################
    # SERVER ACTIONS #
    ##################

    def test_stock_rule_set_push_domain_server_action(self):
        """Test for the stock_rule_set_push_domain_server_action action"""
        server_action = self.env.ref('library.stock_rule_set_push_domain_server_action')

        common_values = {
            'name': 'dummy rule',
            'action': 'push',
            'route_id': self.warehouse.reception_route_id.id,
            'location_dest_id': self.env.ref('stock.stock_location_suppliers').id,
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
        }
        rule_standard, rule_non_standard, rule_pos_categ = self.env['stock.rule'].create([
            {
                'x_standard_rule': True,
                **common_values,
            }, {
                **common_values,
            }, {
                'x_pos_product_category_ids': [Command.link(self.env.ref('library.pos_category_2').id), Command.link(self.env.ref('library.pos_category_4').id)],
                **common_values,
            },
        ])

        self.assertNotEqual(rule_standard.push_domain, '[]',
                            "Test precondition: push domain should be different from expected result")
        self.assertNotEqual(rule_non_standard.push_domain, '[]',
                            "Test precondition: push domain should be different from expected result")
        self.assertNotEqual(rule_pos_categ.push_domain, f'[(\'product_id.pos_categ_ids\', \'in\', {rule_pos_categ.x_pos_product_category_ids.ids})]',
                            "Test precondition: push domain should be different from expected result")
        server_action.with_context(active_ids=[rule_standard.id, rule_non_standard.id, rule_pos_categ.id], active_model='stock.rule').run()
        self.assertEqual(rule_standard.push_domain, '[]',
                         "The action should set an empty push domain on a standard rule")
        self.assertEqual(rule_non_standard.push_domain, '[]',
                         "The action should set an empty push domain for a non standard rule")
        self.assertEqual(rule_pos_categ.push_domain, f'[(\'product_id.pos_categ_ids\', \'in\', {rule_pos_categ.x_pos_product_category_ids.ids})]',
                         "The action should set the domain to be on products with matching categories for a non standard rule with POS categories")

    def test_action_update_automatic_activation_on_product(self):
        """Test for the action_update_automatic_activation_on_product action"""
        server_action = self.env.ref('library.action_update_automatic_activation_on_product')

        route_1 = self.env.ref('library.stock_route_4')
        route_1.product_selectable = True
        route_2 = self.env.ref('library.stock_route_2')

        self.assertTrue(route_1.x_automatic_activation_on_product,
                        "Test precondition: x_automatic_activation_on_product should be different from expected result")
        self.assertFalse(route_2.x_automatic_activation_on_product,
                         "Test precondition: x_automatic_activation_on_product should be different from expected result")
        server_action.with_context(active_ids=[route_1.id, route_2.id], active_model='stock.route').run()
        self.assertFalse(route_1.x_automatic_activation_on_product,
                         "The action should set x_automatic_activation_on_product as the opposite value of product_selectable")
        self.assertTrue(route_2.x_automatic_activation_on_product,
                        "The action should set x_automatic_activation_on_product as the opposite value of product_selectable")

    def test_action_update_destination_location_on_picking(self):
        """Test the `action_update_destination_location_on_picking` server action
        and the `automation_make_route_on_product_create` automation."""
        server_action = self.env.ref('library.action_update_destination_location_on_picking')

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

        picking.location_dest_id = self.location.id

        self.assertNotEqual(picking.location_dest_id.id, picking.picking_type_id.default_location_dest_id.id,
                            "Test precondition: picking.location_dest_id.id should be different from expected result")
        server_action.with_context(active_ids=picking.id, active_model='stock.picking').run()
        self.assertEqual(picking.location_dest_id.id, picking.picking_type_id.default_location_dest_id.id,
                         "The action should update the location if x_overrule_customer_location is set")

        self.warehouse.out_type_id.x_overrule_customer_location = False
        picking.location_dest_id = self.location.id

        self.assertEqual(picking.location_dest_id.id, self.location.id,
                         "Test precondition: picking.location_dest_id.id should be the one just set")
        server_action.with_context(active_ids=picking.id, active_model='stock.picking').run()
        self.assertEqual(picking.location_dest_id.id, self.location.id,
                         "The action should not update the location if x_overrule_customer_location is not set")

    def test_make_route_on_product_create(self):
        """Test for the add_qty_on_product_create action
        and the automation_make_route_on_product_create automation"""
        server_action = self.env.ref('library.make_route_on_product_create')

        stock_route = self.env.ref('library.stock_route_4')
        product_template = self.env['product.template'].create({
            'name': 'Test Product Template',
        })
        self.assertEqual(product_template.route_ids, self.env.ref('library.stock_route_4'),
                         "The automation should set stock_route_4 as a template route on product template create")

        product_template.route_ids = [Command.clear()]

        self.assertNotEqual(product_template.route_ids.id, stock_route.id,
                            "Test precondition: product_template.route_ids.id should not be the expected result")
        server_action.with_context(active_id=product_template.id, active_model='product.template').run()
        self.assertEqual(product_template.route_ids.id, stock_route.id,
                         "The action should set the route_ids to stock_route_4")

    def test_add_qty_on_product_create(self):
        """Test for the add_qty_on_product_create action"""
        server_action = self.env.ref('library.add_qty_on_product_create')
        products = [self.env.ref('library.product_product_9').id, self.env.ref('library.product_product_10').id]

        self.env['stock.quant'].search([('product_id', 'in', products), ('quantity', '=', 1.0)]).unlink()
        self.assertEqual(self.env['stock.quant'].search_count([('product_id', 'in', products), ('quantity', '=', 1.0)]), 0,
                         "Test precondition: the products should have no quantity entries")
        server_action.with_context(active_ids=products, active_model='product.product').run()
        self.assertEqual(self.env['stock.quant'].search_count([('product_id', 'in', products), ('quantity', '=', 1.0)]), 2,  # add 1.0 qty for the two products
                         "The action called on 2 products should add two entries to stock.quant")

    ###############
    # AUTOMATIONS #
    ###############

    def test_automation_update_push_domain(self):
        """Test for the automation_update_push_domain automation."""
        common_values = {
            'name': 'dummy rule',
            'action': 'push',
            'location_dest_id': self.env.ref('stock.stock_location_suppliers').id,
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
        }
        rule_stock_route_4, rule_other_route, rule_pos_categ = self.env['stock.rule'].create([
            {
                'route_id': self.env.ref('library.stock_route_4').id,
                'x_standard_rule': True,
                'x_pos_product_category_ids': [Command.link(self.env.ref('library.pos_category_2').id), Command.link(self.env.ref('library.pos_category_4').id)],
                **common_values,
            }, {
                'route_id': self.warehouse.reception_route_id.id,
                'x_standard_rule': True,
                **common_values,
            }, {
                'route_id': self.env.ref('library.stock_route_4').id,
                **common_values,
            },
        ])

        self.assertEqual(rule_stock_route_4.push_domain, '[]',
                         "The automation should work on targets inside of the domain on create")
        self.assertEqual(rule_other_route.push_domain, False,
                         "The automation should not work on targets outside of the domain on create")
        self.assertEqual(rule_pos_categ.push_domain, '[]',
                         "The automation should work on targets inside of the domain on create")

        rule_stock_route_4.x_standard_rule = False
        self.assertNotEqual(rule_stock_route_4.push_domain, '[]',
                            "The automation should update the push domain on write of x_standard_rule field")

        rule_other_route.x_pos_product_category_ids = [Command.link(self.env.ref('library.pos_category_2').id), Command.link(self.env.ref('library.pos_category_4').id)]
        self.assertEqual(rule_other_route.push_domain, False,
                         "The automation should not work on targets outside of the domain")

        rule_pos_categ.x_pos_product_category_ids = [Command.link(self.env.ref('library.pos_category_2').id), Command.link(self.env.ref('library.pos_category_4').id)]
        self.assertNotEqual(rule_pos_categ.push_domain, '[]',
                            "The automation should update the push domain on write of x_pos_product_category_ids field")

    def test_update_automatic_activation_on_product(self):
        """Test for the update_automatic_activation_on_product automation."""
        route = self.env.ref('library.stock_route_4')

        self.assertEqual(route.x_automatic_activation_on_product, True,
                         "Test precondition: x_automatic_activation_on_product should be different from expected result")
        with Form(route) as f:
            f.product_selectable = True
        self.assertEqual(route.x_automatic_activation_on_product, False,
                         "The automation should update x_automatic_activation_on_product on change of field product_selectable")

    def test_automation_add_qty_on_product_create(self):
        """Test for the automation_add_qty_on_product_create automation."""
        product_not_storable = self.env['product.product'].create({'name': "Test product not storable", 'is_storable': False})
        self.assertEqual(self.env['stock.quant'].search_count([('product_id', '=', product_not_storable.id)]), 0,
                         "The automation should not work on targets outside of the domain on create")

        product_storable = self.env['product.product'].create({'name': "Test product storable", 'is_storable': True})
        self.assertEqual(self.env['stock.quant'].search_count([('product_id', '=', product_storable.id)]), 2,
                         "The automation should create a WH/Stock and an inventory adjustment if the product is storable")
        self.assertEqual(product_storable.qty_available, 1, "A product is automatically made available")
