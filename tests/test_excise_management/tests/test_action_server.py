# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests import Form
from odoo.tests.common import TransactionCase


class ActionServerTestCase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.fiscal_position = cls.env['account.fiscal.position'].create({
            'name': 'Fiscal Position Test',
            'x_is_fiscal_deposit': False
        })
        cls.excise_category = cls.env.ref("excise_management.x_excise_category_S001")
        cls.product = cls.env['product.product'].create({
            'name': 'product',
            'x_excise_category': cls.excise_category.id,
        })

    def test_add_excise_server_action(self):
        product_template = self.product.product_tmpl_id
        with Form(product_template) as product_form:
            product_form.x_excise_category = self.env.ref("excise_management.x_excise_category_S001")
        self.assertIn(product_form.x_excise_category.x_sales_tax_id, product_template.taxes_id,
            "Adding an excise category should add its sales taxes to the product")
        self.assertIn(product_form.x_excise_category.x_purchase_tax_id, product_template.supplier_taxes_id,
            "Adding an excise category should add its purchase taxes to the product")
        old_category = product_template.x_excise_category
        with Form(product_template) as product_form:
            product_form.x_excise_category = self.env.ref("excise_management.x_excise_category_S135")
        self.assertNotIn(old_category.x_sales_tax_id, product_template.taxes_id,
            "Changing the excise category should remove the old category sales taxes")
        self.assertNotIn(old_category.x_purchase_tax_id, product_template.supplier_taxes_id,
            "Changing the excise category should remove the old category purchase taxes")
        self.assertIn(product_form.x_excise_category.x_sales_tax_id, product_template.taxes_id,
            "Changing the excise category should add the new category sales taxes")
        self.assertIn(product_form.x_excise_category.x_purchase_tax_id, product_template.supplier_taxes_id,
            "Changing the excise category should add the new category purchase taxes")

    def test_create_excise_tax_server_action(self):
        excise_category = self.env.ref("excise_management.x_excise_category_S001")
        self.assertTrue(excise_category.x_sales_tax_id,
            "Creating an excise category should give it sales taxes automatically")
        self.assertEqual(excise_category.x_sales_tax_id.formula, '(quantity * uom.factor) * (product.x_excise_amount + product.x_packaging_units * product.x_excise_packaging_tax)',
            "The sales tax of the excise category should have its formula equal to '(quantity * uom.factor) * (product.x_excise_amount + product.x_packaging_units * product.x_excise_packaging_tax)'")
        self.assertEqual(excise_category.x_sales_tax_id.type_tax_use, 'sale',
            "The sales tax of the excise category should have its type equal to 'sale'")
        self.assertEqual(excise_category.x_sales_tax_id.tax_group_id, self.env.ref('excise_management.excises_tax_group'),
            "The sales tax of the excise category should have its tax group set to the excises tax group")
        self.assertTrue(excise_category.x_purchase_tax_id,
            "Creating an excise category should give it purchase taxes automatically")
        self.assertEqual(excise_category.x_purchase_tax_id.formula, '(quantity * uom.factor) * (product.x_excise_amount + product.x_packaging_units * product.x_excise_packaging_tax)',
            "The purchase tax of the excise category should have its formula equal to '(quantity * uom.factor) * (product.x_excise_amount + product.x_packaging_units * product.x_excise_packaging_tax)'")
        self.assertEqual(excise_category.x_purchase_tax_id.type_tax_use, 'purchase',
            "The purchase tax of the excise category should have its type equal to 'purchase'")
        self.assertEqual(excise_category.x_purchase_tax_id.tax_group_id, self.env.ref('excise_management.excises_tax_group'),
            "The purchase tax of the excise category should have its tax group set to the excises tax group")

    def test_add_excise_taxes_fiscal_position_server_action(self):
        excise_taxes = self.env['account.tax'].search([('x_is_excise', '=', True)])
        sale_excise_taxes = excise_taxes.filtered(lambda t: t.type_tax_use == 'sale')
        purchase_excise_taxes = excise_taxes.filtered(lambda t: t.type_tax_use == 'purchase')
        no_excise_sale = self.env.ref('excise_management.no_excise_tax_sale')
        no_excise_purchase = self.env.ref('excise_management.no_excise_tax_purchase')
        for tax in sale_excise_taxes:
            if tax != no_excise_sale:
                self.assertIn(tax, no_excise_sale.original_tax_ids, "All sale excise taxes should be automatically replaced by the no excise tax")
            else:
                self.assertNotIn(tax, no_excise_sale.original_tax_ids, "No excise tax should not replace itself")
        for tax in purchase_excise_taxes:
            if tax != no_excise_purchase:
                self.assertIn(tax, no_excise_purchase.original_tax_ids, "All purchase excise taxes should be automatically replaced by the no excise tax")
            else:
                self.assertNotIn(tax, no_excise_sale.original_tax_ids, "No excise tax should not replace itself")

        self.assertNotIn(self.fiscal_position, no_excise_sale.fiscal_position_ids,
            "Fiscal positions that are not deposit does not contain the sales no excises tax")
        self.assertNotIn(self.fiscal_position, no_excise_purchase.fiscal_position_ids,
            "Fiscal positions that are not deposit does not contain the purchase no excises tax")
        self.fiscal_position.x_is_fiscal_deposit = True
        for tax in excise_taxes:
            if tax.id not in [no_excise_sale.id, no_excise_purchase.id]:
                self.assertNotIn(tax, self.fiscal_position.tax_ids,
                    "All excise taxes should be removed automatically of a fiscal position that becomes a fiscal deposit")
        self.assertIn(self.fiscal_position, no_excise_sale.fiscal_position_ids,
            "Fiscal positions that are deposit contains the sales no excises tax")
        self.assertIn(self.fiscal_position, no_excise_purchase.fiscal_position_ids,
            "Fiscal positions that are deposit contains the purchase no excises tax")

    def test_sale_order_customer_without_fiscal_deposit(self):
        customer = self.env['res.partner'].create({
            'name': 'Customer Without Deposit',
        })
        template = self.env['product.template'].create({
            'name': 'Product With Excise',
            'list_price': 100,
        })

        with Form(template) as form:
            form.x_excise_category = self.env.ref(
                'excise_management.x_excise_category_S001'
            )

        product = template.product_variant_id
        order = self.env['sale.order'].create({
            'partner_id': customer.id,
        })

        with Form(order) as order_form:
            with order_form.order_line.new() as line_form:
                line_form.product_id = product
                line_form.product_uom_qty = 1

        order_form.save()
        line = order.order_line
        excise_taxes = line.tax_ids.filtered(lambda t: t.tax_group_id.x_is_excise)
        vat_taxes = line.tax_ids - excise_taxes
        tax_result = vat_taxes.compute_all(
            line.price_unit,
            quantity=line.product_uom_qty,
            product=line.product_id,
            partner=line.order_id.partner_id,
        )
        vat_amount = sum(tax['amount'] for tax in tax_result['taxes'])

        self.assertTrue(excise_taxes,
            "Customer without fiscal deposit should have excise taxes applied")
        self.assertEqual(line.price_subtotal, line.price_unit * line.product_uom_qty,
            "The sale order line amount should equal the unit product price times the quantity")
        self.assertEqual(line.price_total, line.price_subtotal + vat_amount,
            "The sale order line tax included amount should equal the amount plus the VAT taxes")

    def test_sale_order_customer_with_fiscal_deposit(self):
        self.fiscal_position.x_is_fiscal_deposit = True
        customer = self.env['res.partner'].create({
            'name': 'Customer With Deposit',
            'property_account_position_id': self.fiscal_position.id,
        })
        template = self.env['product.template'].create({
            'name': 'Product With Excise',
            'list_price': 100,
            'x_excise_amount': 25
        })
        with Form(template) as form:
            form.x_excise_category = self.env.ref(
                'excise_management.x_excise_category_S001'
            )

        product = template.product_variant_id
        order = self.env['sale.order'].create({
            'partner_id': customer.id,
        })

        with Form(order) as order_form:
            with order_form.order_line.new() as line_form:
                line_form.product_id = product
                line_form.product_uom_qty = 1

        order_form.save()
        line = order.order_line

        excise_taxes = line.tax_ids.filtered(
            lambda t: t.tax_group_id.x_is_excise
        )
        vat_taxes = line.tax_ids - excise_taxes
        excise_amount = sum(
            tax['amount']
            for tax in excise_taxes.compute_all(
                line.price_unit,
                quantity=line.product_uom_qty,
                product=line.product_id,
                partner=line.order_id.partner_id,
            )['taxes']
        )
        expected_subtotal = line.price_unit * line.product_uom_qty - excise_amount
        tax_result = vat_taxes.compute_all(
            line.price_subtotal,
            quantity=1,
            product=line.product_id,
            partner=line.order_id.partner_id,
        )
        vat_amount = sum(tax['amount'] for tax in tax_result['taxes'])

        self.assertEqual(excise_amount, 0,
            "Customer with fiscal deposit should not have excise taxes applied")
        self.assertEqual(line.price_subtotal, expected_subtotal,
            "Amount should equal unit price times quantity minus excise taxes")
        self.assertEqual(line.price_total, line.price_subtotal + vat_amount,
            "Tax included amount should equal amount plus VAT taxes")
