from odoo.tests.common import TransactionCase
from odoo.tests import Form


class ActionServerTestCase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_1 = cls.env['res.partner'].create({'name': 'Test Partner 1'})
        cls.test_product = cls.env['product.product'].create({'name': 'Test Product'})
        cls.uom_1 = cls.env['uom.uom'].create({'name': 'Unit of Measure 1', 'rounding': 0.01})
        cls.test_template_work_item = cls.env['x_work_item'].create({
            'x_is_template': True,
            'x_product_id': cls.test_product.id,
            'x_name': cls.test_product.name,
        })

    def test_create_work_item_for_sale_order(self):
        test_sale_order_1 = self.env['sale.order'].create({
            'partner_id': self.partner_1.id,
        })
        new_work_item = self.env['x_work_item'].create({
            'x_is_template': False,
            'x_name': "Test work item on sol",
            'x_targeted_so_id': test_sale_order_1.id,
            'x_unit_custom_id': self.uom_1.id,
        })
        self.assertTrue(new_work_item.x_product_id, "A new product should be created and assigned to this work item after creating it")
        self.assertEqual(new_work_item.x_unit_id.id, self.uom_1.id, "The unit in work item should be the one assigned to the temporary field when creating the work item")

    def test_keeping_last_wi_template_created(self):
        self.assertTrue(self.test_template_work_item.x_active, "The work item template should be active after being created")
        self.assertEqual(self.test_product.x_work_item_template_id.id, self.test_template_work_item.id, "The work item template registered on the product should be the last template created")
        self.test_template_work_item_2 = self.env['x_work_item'].create({
            'x_is_template': True,
            'x_product_id': self.test_product.id,
            'x_name': self.test_product.name,
        })
        self.assertFalse(self.test_template_work_item.x_active, "The old work item template should be inactive after the new one is created")
        self.assertTrue(self.test_template_work_item_2.x_active, "The new work item template should be active after being created")
        self.test_product._invalidate_cache()
        self.assertEqual(self.test_product.x_work_item_template_id.id, self.test_template_work_item_2.id, "The work item template registered on the product should be the last template created")

    def test_wi_prices_correctly_computed(self):
        component_product_1 = self.env['product.product'].create({
            'name': 'Component Product 1',
            'lst_price': 15,
            'standard_price': 7.5,
        })
        component_product_2 = self.env['product.product'].create({
            'name': 'Component Product 2',
            'lst_price': 40,
            'standard_price': 20,
        })
        wi_form = Form(self.test_template_work_item)
        with wi_form.x_work_item_line_ids.new() as wi_line:
            wi_line.x_product_id = component_product_1
            wi_line.x_quantity = 4
        with wi_form.x_work_item_line_ids.new() as wi_line:
            wi_line.x_product_id = component_product_2
        wi_form.save()
        test_template_work_item_lines = self.test_template_work_item.x_work_item_line_ids
        self.assertEqual(test_template_work_item_lines[0].x_unit_cost, 7.5, "Assignation error: The first work item line should have a cost of 7.5")
        self.assertEqual(test_template_work_item_lines[0].x_unit_price, 15.0, "Assignation error: The first work item line should have a price of 15.0")
        self.assertEqual(test_template_work_item_lines[1].x_unit_cost, 20.0, "Assignation error: The second work item line should have a cost of 20.0")
        self.assertEqual(test_template_work_item_lines[1].x_unit_price, 40.0, "Assignation error: The second work item line should have a price of 40.0")
        self.assertEqual(self.test_template_work_item.x_unit_cost, 50.0, "The cost of work item is not computed correctly: it should be the sum of the product of components costs by quantity")
        self.assertEqual(self.test_template_work_item.x_unit_price, 100.0, "The price of work item is not computed correctly: it should be the sum of the product of components prices by quantity")
        self.assertEqual(self.test_template_work_item.x_unit_margin, 1.0, "The margin of work item is not computed correctly: it should be equal to 1.0 at this point")
        test_template_work_item_lines[0].x_unit_cost = 20
        self.assertEqual(self.test_template_work_item.x_unit_cost, 100.0, "The cost of work item is not recomputed correctly when the cost of a component changes")
        self.assertEqual(self.test_template_work_item.x_unit_price, 100.0, "The price of work item changes when the cost of a component changes but it should not happen")
        self.assertEqual(self.test_template_work_item.x_unit_margin, 0.0, "The margin of work item is not correct after the cost of a component changes: it should be recomputed to represent the new value")
        test_template_work_item_lines[1].x_unit_price = 240
        self.assertEqual(self.test_template_work_item.x_unit_cost, 100.0, "The cost of work item changes after the price of a component changes while it should not happen")
        self.assertEqual(self.test_template_work_item.x_unit_price, 300.0, "The price of work item is not recomputed correctly when the price of a component changes")
        self.assertEqual(self.test_template_work_item.x_unit_margin, 2.0, "The margin of work item is not correct after the price of a component changes: it should be recomputed to represent the new value")
        self.test_template_work_item.x_is_margin_fixed = True
        self.test_template_work_item.x_unit_price = 200
        self.assertEqual(self.test_template_work_item.x_unit_margin, 1.0, "When margin is fixed, the margin should be recomputed if we change manually the price of work item")
        self.test_template_work_item.x_unit_margin = 0.5
        self.assertEqual(self.test_template_work_item.x_unit_price, 150.0, "When margin is fixed, the price should be recomputed if we change manually the margin of work item")
        test_template_work_item_lines[1].x_unit_cost = 10
        self.assertEqual(self.test_template_work_item.x_unit_margin, 0.5, "When margin is fixed, the margin of work item should stay the same when the cost of a component changes")
        self.assertEqual(self.test_template_work_item.x_unit_cost, 90.0, "When margin is fixed, the cost of work item should be recomputed when the cost of a component changes")
        self.assertEqual(self.test_template_work_item.x_unit_price, 135.0, "When margin is fixed, the price of work item should be recomputed when the cost of a component changes")
