# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class ComputedFieldsTestCase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_1, cls.partner_2 = cls.env['res.partner'].create([{'name': 'Test Partner 1'}, {'name': 'Test Partner 2'}])
        cls.product = cls.env['product.template'].create({
            'name': 'Test Product',
            'type': 'consu',
        })
        cls.stock_picking = cls.env['stock.picking'].create({
            'location_id': cls.env.ref('stock.stock_location_stock').id,
            'location_dest_id': cls.env.ref('stock.stock_location_customers').id,
            'picking_type_id': cls.env.ref('stock.picking_type_in').id,
            'owner_id': cls.partner_2.id,
        })
        cls.move_line = cls.env['stock.move.line'].create({
            'picking_id': cls.stock_picking.id,
            'product_id': cls.product.id,
            'quantity': 1,
        })
        cls.quality_check = cls.env['quality.check'].create({
            'picking_id': cls.stock_picking.id,
            'move_line_id': cls.move_line.id,
        })

    def test_x_quality_check_owner_sale_order_line_computation(self):
        self.assertEqual(self.quality_check.x_quality_check_owner, self.partner_2, "Quality check owner should be the same as the owner of the picking")

        new_stock_picking = self.env['stock.picking'].create({
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id': self.env.ref('stock.stock_location_customers').id,
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'owner_id': self.partner_1.id,
        })
        self.quality_check.picking_id = new_stock_picking
        self.assertEqual(self.quality_check.x_quality_check_owner, self.partner_1, "Quality check owner should be the same as the owner of the new picking")

    def test_x_package_master_container_id_field_stock_quants_computation(self):
        package_1 = self.env['stock.package'].create({
            'name': 'Package 1',
            'pack_date': fields.Datetime.now(),
        })
        package_2 = self.env['stock.package'].create({
            'name': 'Package 2',
            'pack_date': fields.Datetime.now(),
            'parent_package_id': package_1.id,
        })
        package_3 = self.env['stock.package'].create({
            'name': 'Package 3',
            'pack_date': fields.Datetime.now(),
        })
        package_4 = self.env['stock.package'].create({
            'name': 'Package 3',
            'pack_date': fields.Datetime.now(),
            'parent_package_id': package_3.id,
        })
        stock_history = self.env['x_stock_history'].create({
            'x_date': fields.Datetime.now(),
            'x_package_id': package_2.id,
        })
        self.assertEqual(stock_history.x_package_master_container_id, package_1, "The package master container should be the parent package of the package")

        stock_history.x_package_id = package_4.id
        self.assertEqual(stock_history.x_package_master_container_id, package_3, "The package master container should change when the package is changed")

        package_4.parent_package_id = package_1.id
        self.assertEqual(stock_history.x_package_master_container_id, package_1, "The package master container should be change when the parent package is changed")

        stock_history.x_date = fields.Datetime.now() + relativedelta(days=1)
        self.assertEqual(stock_history.x_package_master_container_id, package_1, "The package master container should not be change when the non dependent field is changed")
