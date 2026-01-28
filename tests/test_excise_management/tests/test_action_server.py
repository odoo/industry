# Part of Odoo. See LICENSE file for full copyright and licensing details.
from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import tagged, Form
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class ActionServerTestCase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.fiscal_position = cls.env['account.fiscal.position'].create({
            'name': 'Fiscal Position Test',
            'x_is_fiscal_deposit': False
        })

    def test_add_excise_server_action(self):
        product_template = self.env['product.template'].create({
            'name': 'Product Test',
        })
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

    def test_fiscal_deposit_move_computation(self):
        server_action = self.env['ir.actions.server'].browse(self.env.ref('excise_management.ir_action_compute_excise_report_line')).id
        customers = self.env['stock.location'].create({'name': 'Customers', 'usage': 'customer'})
        license1, license2 = self.env['x_excise_license'].create([
            {'x_name': 'License 1', 'x_active': True},
            {'x_name': 'License 2', 'x_active': True},
        ])
        internal_fd, internal_fd2, internal_fd3, internal_not_fd = self.env['stock.warehouse'].create([
            {
                'code': 'FD 1',
                'name': 'FD 2',
                'x_is_fiscal_deposit': True,
                'partner_id': self.env.ref('base.main_partner').id,
                'x_excise_license_id': license1.id,
            }, {
                'code': 'FD 3',
                'name': 'FD 4',
                'x_is_fiscal_deposit': True,
                'partner_id': self.env.ref('base.main_partner').id,
                'x_excise_license_id': license1.id,
            },
            {
                'code': 'FD 5',
                'name': 'FD 6',
                'x_is_fiscal_deposit': True,
                'partner_id': self.env.ref('base.main_partner').id,
                'x_excise_license_id': license2.id,
            },
            {
                'code': 'Non FD 1',
                'name': 'Non FD 1',
                'x_is_fiscal_deposit': False,
                'partner_id': self.env.ref('base.main_partner').id,
            },
        ])
        fiscal_position = self.env['account.fiscal.position'].create({
            'name': 'Fiscal Position',
            'x_is_fiscal_deposit': True,
        })
        partner, partner_FD, partner_not_FD = self.env['res.partner'].create([
            {'name': 'dummy'},
            {'name': 'FD', 'property_account_position_id': fiscal_position.id},
            {'name': 'Not FD', 'property_account_position_id': self.fiscal_position.id},
        ])
        excise_category = self.env.ref("excise_management.x_excise_category_S001")
        product = self.env['product.product'].create({'name': 'product', 'x_excise_category': excise_category.id})
        excise_report = self.env['x_excise_report'].create({
            'x_name': 'Report 1',
            'x_excise_license_id': license1.id,
            'x_from_date': fields.Datetime.now(),
            'x_to_date': fields.Datetime.now() + relativedelta(days=7),
        })

        same_license_diff_warehouse_move = self.env['stock.move'].create({
            'location_id': internal_fd.lot_stock_id.id,
            'location_dest_id': internal_fd2.lot_stock_id.id,
            'product_id': product.id,
            'inventory_name': 'move',
            'state': 'done',
        })
        diff_license_diff_warehouse_move = self.env['stock.move'].create({
            'location_id': internal_fd.lot_stock_id.id,
            'location_dest_id': internal_fd3.lot_stock_id.id,
            'product_id': product.id,
            'inventory_name': 'move',
            'state': 'done',
        })
        fd_warehouse_to_not_fd_warehouse_move = self.env['stock.move'].create({
            'location_id': internal_fd.lot_stock_id.id,
            'location_dest_id': internal_not_fd.lot_stock_id.id,
            'product_id': product.id,
            'inventory_name': 'move',
            'state': 'done',
        })
        not_fd_warehouse_to_fd_warehouse_move = self.env['stock.move'].create({
            'location_id': internal_not_fd.lot_stock_id.id,
            'location_dest_id': internal_fd.lot_stock_id.id,
            'product_id': product.id,
            'inventory_name': 'move',
            'state': 'done',
        })
        internal_not_fd.x_excise_license_id = license1.id
        not_fd_warehouse_to_not_fd_warehouse_move = self.env['stock.move'].create({
            'location_id': internal_not_fd.lot_stock_id.id,
            'location_dest_id': internal_not_fd.lot_stock_id.id,
            'product_id': product.id,
            'inventory_name': 'move',
            'state': 'done',
        })

        move_to_partner = self.env['stock.move'].create({
            'location_id': internal_fd.lot_stock_id.id,
            'location_dest_id': customers.id,
            'product_id': product.id,
            'inventory_name': 'move',
            'partner_id': partner.id,
            'state': 'done',
        })
        move_to_fd_partner = self.env['stock.move'].create({
            'location_id': internal_fd.lot_stock_id.id,
            'location_dest_id': customers.id,
            'product_id': product.id,
            'inventory_name': 'move',
            'partner_id': partner_FD.id,
            'state': 'done',
        })
        move_to_not_fd_partner = self.env['stock.move'].create({
            'location_id': internal_fd.lot_stock_id.id,
            'location_dest_id': customers.id,
            'product_id': product.id,
            'inventory_name': 'move',
            'partner_id': partner_not_FD.id,
            'state': 'done',
        })
        move_from_partner = self.env['stock.move'].create({
            'location_dest_id': internal_fd.lot_stock_id.id,
            'location_id': customers.id,
            'product_id': product.id,
            'inventory_name': 'move',
            'partner_id': partner.id,
            'state': 'done',
        })
        move_from_fd_partner = self.env['stock.move'].create({
            'location_dest_id': internal_fd.lot_stock_id.id,
            'location_id': customers.id,
            'product_id': product.id,
            'inventory_name': 'move',
            'partner_id': partner_FD.id,
            'state': 'done',
        })
        move_from_not_fd_partner = self.env['stock.move'].create({
            'location_dest_id': internal_fd.lot_stock_id.id,
            'location_id': customers.id,
            'product_id': product.id,
            'inventory_name': 'move',
            'partner_id': partner_not_FD.id,
            'state': 'done',
        })
        server_action.with_context(active_ids=[excise_report.id], active_model="x_excise_report").sudo().run()
        line = self.env['x_excise_report_line'].search([('x_excise_report_id', '=', excise_report.id)])

        # Exit
        self.assertEqual(line.filtered(lambda x: move_to_partner in x.x_move_ids).x_excise_move_type, 'exit')
        self.assertEqual(line.filtered(lambda x: move_to_fd_partner in x.x_move_ids).x_excise_move_type, 'exit fd')
        self.assertEqual(line.filtered(lambda x: move_to_not_fd_partner in x.x_move_ids).x_excise_move_type, 'exit')

        # Entry
        self.assertEqual(line.filtered(lambda x: move_from_partner in x.x_move_ids).x_excise_move_type, 'entry')
        self.assertEqual(line.filtered(lambda x: move_from_fd_partner in x.x_move_ids).x_excise_move_type, 'entry fd')
        self.assertEqual(line.filtered(lambda x: move_from_not_fd_partner in x.x_move_ids).x_excise_move_type, 'entry')

        # Between FD and non-FD warehouse
        self.assertEqual(line.filtered(lambda x: fd_warehouse_to_not_fd_warehouse_move in x.x_move_ids).x_excise_move_type, 'exit')
        self.assertEqual(line.filtered(lambda x: not_fd_warehouse_to_fd_warehouse_move in x.x_move_ids).x_excise_move_type, 'entry')
        self.assertEqual(line.filtered(lambda x: not_fd_warehouse_to_not_fd_warehouse_move in x.x_move_ids).x_excise_move_type, 'none')

        # Transfers
        self.assertEqual(line.filtered(lambda x: same_license_diff_warehouse_move in x.x_move_ids).x_excise_move_type, 'transfer')
        self.assertEqual(line.filtered(lambda x: diff_license_diff_warehouse_move in x.x_move_ids).x_excise_move_type, 'exit fd')

        excise_report_2 = self.env['x_excise_report'].create({
            'x_name': 'Report 2',
            'x_excise_license_id': license2.id,
            'x_from_date': fields.Datetime.now(),
            'x_to_date': fields.Datetime.now() + relativedelta(days=7),
        })
        server_action.with_context(active_ids=[excise_report_2.id], active_model="x_excise_report").sudo().run()
        line_2 = self.env['x_excise_report_line'].search([('x_excise_report_id', '=', excise_report_2.id)])
        self.assertEqual(line_2.filtered(lambda x: diff_license_diff_warehouse_move in x.x_move_ids).x_excise_move_type, 'entry fd')
