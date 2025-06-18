# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields
from odoo.tests.common import TransactionCase
from odoo.tests import tagged, Form


@tagged('post_install', '-at_install')
class BookstoreAutomationsTestCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env['product.template'].create({
            'name': 'Test Book',
            'list_price': 20.0,
        })

    def test_update_inventory_description_automation(self):
        # Empty description case
        self.assertEqual(self.product['description_pickingin'], '[20.0]')
        self.product.write({'list_price': 24.99})
        self.assertEqual(self.product['description_pickingin'], '[24.99]')

        # Description should be overridden
        self.product.write({'description_pickingin': 'Updated description'})
        self.product.write({'list_price': 30.0})
        self.assertEqual(self.product['description_pickingin'], '[30.0]')

        # Tes the form view
        with Form(self.product) as product_form:
            product_form.list_price = 35.0
        self.assertEqual(self.product['description_pickingin'], '[35.0]')

    def test_update_supplierinfo_on_incoming_picking(self):
        StockPicking = self.env['stock.picking']
        supplierinfo = self.env['product.supplierinfo']
        Product = self.env['product.product']
        Partner = self.env['res.partner']

        vendor = Partner.create({'name': 'Test Vendor'})
        vendor2 = Partner.create({'name': 'Test Vendor 2'})
        product = Product.create({
            'name': 'Test Product',
            'list_price': 10.0,
        })
        supplierinfo.create({
            'partner_id': vendor.id,
            'product_id': product.id,
            'price': 5.0,
            'delay': 0,
            'min_qty': 1,
        })

        self.assertEqual(product.seller_ids[:1].partner_id, vendor,
                        "The product should have a supplierinfo for the vendor")

        # Create an incoming picking with another vendor
        picking = StockPicking.create({
            'partner_id': vendor2.id,
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'location_id': self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id': self.env.ref('stock.stock_location_stock').id,
            'move_ids_without_package': [(0, 0, {
                'name': product.name,
                'product_id': product.id,
                'product_uom_qty': 1,
            })],
        })

        picking.button_validate()
        self.assertEqual(product.seller_ids[-1].partner_id, vendor2,
                        "Vendor should be updated to the new supplierinfo from the incoming picking")
        self.assertEqual(product.seller_ids[-1].date_start, fields.Date.today(),
                        "The new supplierinfo should have today's date as start date")
        self.assertEqual(product.seller_ids[-2].partner_id, vendor,
                        "The previous supplierinfo should still exist")
        self.assertEqual(product.seller_ids[-2].date_end, fields.Date.today(),
                        "The previous supplierinfo should be closed with today's date")
