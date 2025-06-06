# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests.common import TransactionCase
from odoo.tests import Form, tagged


@tagged('post_install', '-at_install')
class ServerActionsTestCase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tax_1 = cls.env['account.tax'].create([{
            'name': "tax_1",
            'amount_type': 'percent',
            'amount': 10.0,
        }])
        cls.tax_2 = cls.env['account.tax'].create([{
            'name': "tax_2",
            'amount_type': 'percent',
            'amount': 5.0,
            'type_tax_use': 'purchase',
        }])
        cls.tax_3 = cls.env['account.tax'].create([{
            'name': "tax_3",
            'amount_type': 'percent',
            'amount': 20.0,
        }])
        cls.tax_4 = cls.env['account.tax'].create([{
            'name': "tax_4",
            'amount_type': 'percent',
            'amount': 15.0,
            'type_tax_use': 'purchase',
        }])
        cls.product_template_deposit = cls.env['product.template'].create({
            'name': 'product template deposit',
            'categ_id': cls.env['product.category'].create({
                'name': 'Deposit Category',
                'x_is_a_deposit_category': True,
            }).id,
            'invoice_policy': 'order',
            'type': 'consu',
            'is_storable': False,
            'purchase_ok': True,
            'taxes_id': cls.tax_1,
            'supplier_taxes_id': cls.tax_2,
        })
        cls.product_template = cls.env['product.template'].create({
            'name': 'product template',
            'x_is_a_deposit': False,
            'x_deposit_product_1': cls.product_template_deposit.id,
            'x_quantity_by_deposit_product': 6,
            'purchase_ok': True,
            'taxes_id': cls.tax_3,
            'supplier_taxes_id': cls.tax_4,
            'x_unit_sale_product': cls.env['product.template'].create({
                'name': 'sale product',
            }).id,
        })
        cls.product_uom = cls.env['uom.uom'].create({
            'name': 'Unit of Measure 1',
            'category_id': cls.env['uom.category'].create({'name': 'Uom Category'}).id,
            'uom_type': 'reference',
            'rounding': 0.01
        })
        cls.manfacturing_order = cls.env['mrp.production'].create({
            'name': 'Manufacturing Order 1',
            'date_finished': fields.Datetime.now() - relativedelta(days=2),
            'product_qty': 2,
            'priority': '1',
            'is_locked': False,
            'state': 'confirmed',
            'product_id': cls.env['product.product'].create({
                'name': 'Product 1',
                'standard_price': 600.0,
                'list_price': 699.0,
                'type': 'service',
                'uom_id': cls.product_uom.id,
            }).id,
            'product_uom_id': cls.product_uom.id,
        })

    def test_make_deposit_storable_delivery_invoice_automation(self):
        product_form = Form(self.product_template_deposit)
        new_category = self.env['product.category'].create({
                'name': 'Deposit Category 2',
                'x_is_a_deposit_category': True,
            })
        product_form['categ_id'] = new_category
        product_form.save()

        self.assertEqual(self.product_template_deposit.invoice_policy, 'delivery', "Changing the product template to a deposit should set its invoice policy to delivery")
        self.assertEqual(self.product_template_deposit.type, 'consu', "Changing the product template to a deposit should set its type to consu")
        self.assertEqual(self.product_template_deposit.is_storable, True, "Changing the product template to a deposit should make it storable")

    def test_update_sales_taxes_automation(self):
        self.assertEqual(self.product_template.taxes_id, self.tax_1 + self.tax_3)
        self.assertEqual(self.product_template.supplier_taxes_id, self.tax_2 + self.tax_4)

    def test_update_state_automation(self):
        self.assertEqual(self.manfacturing_order.date_finished.date(), fields.Datetime.today().date())
        self.assertEqual(self.manfacturing_order.priority, '0')
        self.assertEqual(self.manfacturing_order.is_locked, True)
        self.assertEqual(self.manfacturing_order.state, 'done')

    def test_bom_automation(self):
        existing_bom = self.env['mrp.bom'].search([('product_tmpl_id', '=', self.product_template.x_unit_sale_product.id)], limit=1)
        self.assertEqual(existing_bom.product_qty, self.product_template.x_quantity_by_deposit_product)
        self.assertEqual(existing_bom.type, 'normal')
        self.assertEqual(existing_bom.x_parent_product.id, self.product_template.id)
        self.assertEqual(existing_bom.x_auto_production, True)
