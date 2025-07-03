# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import Command
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
        self.assertEqual(excise_category.x_sales_tax_id.formula, 'quantity * product.x_excise_amount',
            "The sales tax of the excise category should have its formula equal to 'quantity * product.x_excise_amount'")
        self.assertEqual(excise_category.x_sales_tax_id.type_tax_use, 'sale',
            "The sales tax of the excise category should have its type equal to 'sale'")
        self.assertEqual(excise_category.x_sales_tax_id.tax_group_id, self.env.ref('excise_management.excises_tax_group'),
            "The sales tax of the excise category should have its tax group set to the excises tax group")
        self.assertTrue(excise_category.x_purchase_tax_id,
            "Creating an excise category should give it purchase taxes automatically")
        self.assertEqual(excise_category.x_purchase_tax_id.formula, 'quantity * product.x_excise_amount',
            "The purchase tax of the excise category should have its formula equal to 'quantity * product.x_excise_amount'")
        self.assertEqual(excise_category.x_purchase_tax_id.type_tax_use, 'purchase',
            "The purchase tax of the excise category should have its type equal to 'purchase'")
        self.assertEqual(excise_category.x_purchase_tax_id.tax_group_id, self.env.ref('excise_management.excises_tax_group'),
            "The purchase tax of the excise category should have its tax group set to the excises tax group")
        self.assertIn(excise_category.x_sales_tax_id, self.fiscal_position.tax_ids,
            "Fiscal positions that are not deposit should contains the sales taxes of the current category")
        self.assertIn(excise_category.x_purchase_tax_id, self.fiscal_position.tax_ids,
            "Fiscal positions that are not deposit should contains the purchase taxes of the current category")

    def test_add_excise_taxes_fiscal_position_server_action(self):
        excise_taxes = self.env['account.tax'].search([('x_is_excise', '=', True)])
        for tax in excise_taxes:
            self.assertIn(tax, self.fiscal_position.tax_ids,
                "All excise taxes should be added automatically to a fiscal position that is not a deposit")
        self.fiscal_position.x_is_fiscal_deposit = True
        for tax in excise_taxes:
            self.assertNotIn(tax, self.fiscal_position.tax_ids,
                "All excise taxes should be removed automatically of a fiscal position that becomes a fiscal deposit")

    def test_add_remove_excise_tax_fiscal_deposit(self):
        factor_1, factor_2 = 5, 10
        uom = self.env['uom.uom'].create({
            'name': 'uom test',
            'relative_factor': factor_1,
            'relative_uom_id': self.env['uom.uom'].create({
                'name': 'rel uom test',
                'relative_factor': factor_2,
                'relative_uom_id': self.env.ref('uom.product_uom_unit').id,
            }).id,
        })
        server_action = self.env['ir.actions.server'].browse(self.env.ref('excise_management.convert_to_base_unit_server_action').id)
        result = server_action.with_context(active_id=uom.id, active_model="uom.uom").run()
        self.assertEqual(result, factor_1 * factor_2,
            "The convert to base unit server action should return the product of the UOM factor and its relative UOM factor")

    def test_fiscal_deposit_move_computation(self):
        customers = self.env['stock.location'].create({'name': 'Customers', 'usage': 'customer'})
        internal = self.env['stock.location'].create({'name': 'Internal', 'usage': 'internal'})
        internal_fd, internal_fd2 = self.env['stock.warehouse'].create([
            {
                'code': 'FD 1',
                'name': 'FD 2',
                'x_is_fiscal_deposit': True,
                'partner_id': self.env.ref('base.main_partner').id
            }, {
                'code': 'FD 3',
                'name': 'FD 4',
                'x_is_fiscal_deposit': True,
                'partner_id': self.env.ref('base.main_partner').id
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
        product = self.env['product.product'].create({'name': 'product'})

        move = self.env['stock.move'].create({
            'location_id': internal.id,
            'location_dest_id': internal_fd.lot_stock_id.id,
            'product_id': product.id,
            'name': 'move',
            'partner_id': partner_FD.id,
        })
        self.assertEqual(move.x_fiscal_deposit_move, 'entry')
        move = self.env['stock.move'].create({
            'location_id': internal_fd.lot_stock_id.id,
            'location_dest_id': internal.id,
            'product_id': product.id,
            'name': 'move',
            'partner_id': partner_FD.id,
        })
        self.assertEqual(move.x_fiscal_deposit_move, 'exit')
        move = self.env['stock.move'].create({
            'location_id': internal_fd2.lot_stock_id.id,
            'location_dest_id': internal_fd.lot_stock_id.id,
            'product_id': product.id,
            'name': 'move',
            'partner_id': partner_FD.id,
        })
        self.assertEqual(move.x_fiscal_deposit_move, 'transfer')
        picking = self.env['stock.picking'].create({
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            'partner_id': partner_not_FD.id,
            'location_id': internal.id,
            'location_dest_id': customers.id,
            'move_ids': [Command.create({
                'location_id': internal.id,
                'location_dest_id': customers.id,
                'product_id': product.id,
                'name': 'move',
            })]
        })
        self.assertEqual(picking.move_ids[0].x_fiscal_deposit_move, 'none')
        picking = self.env['stock.picking'].create({
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            'partner_id': partner_not_FD.id,
            'location_id': internal_fd.lot_stock_id.id,
            'location_dest_id': customers.id,
            'move_ids': [Command.create({
                'location_id': internal_fd.lot_stock_id.id,
                'location_dest_id': customers.id,
                'product_id': product.id,
                'name': 'move',
            })]
        })
        self.assertEqual(picking.move_ids[0].x_fiscal_deposit_move, 'exit')
        picking = self.env['stock.picking'].create({
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            'partner_id': partner_not_FD.id,
            'location_dest_id': internal_fd.lot_stock_id.id,
            'location_id': customers.id,
            'move_ids': [Command.create({
                'location_dest_id': internal_fd.lot_stock_id.id,
                'location_id': customers.id,
                'product_id': product.id,
                'name': 'move',
            })]
        })
        self.assertEqual(picking.move_ids[0].x_fiscal_deposit_move, 'entry')
        picking = self.env['stock.picking'].create({
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            'partner_id': partner_FD.id,
            'location_id': internal_fd.lot_stock_id.id,
            'location_dest_id': customers.id,
            'move_ids': [Command.create({
                'location_id': internal_fd.lot_stock_id.id,
                'location_dest_id': customers.id,
                'product_id': product.id,
                'name': 'move',
            })]
        })
        self.assertEqual(picking.move_ids[0].x_fiscal_deposit_move, 'exit fd')
        picking = self.env['stock.picking'].create({
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            'partner_id': partner_FD.id,
            'location_dest_id': internal_fd.lot_stock_id.id,
            'location_id': customers.id,
            'move_ids': [Command.create({
                'location_dest_id': internal_fd.lot_stock_id.id,
                'location_id': customers.id,
                'product_id': product.id,
                'name': 'move',
            })]
        })
        self.assertEqual(picking.move_ids[0].x_fiscal_deposit_move, 'entry fd')
        picking = self.env['stock.picking'].create({
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            'partner_id': partner.id,
            'location_id': internal_fd.lot_stock_id.id,
            'location_dest_id': customers.id,
            'move_ids': [Command.create({
                'location_id': internal_fd.lot_stock_id.id,
                'location_dest_id': customers.id,
                'product_id': product.id,
                'name': 'move',
            })]
        })
        self.assertEqual(picking.move_ids[0].x_fiscal_deposit_move, 'exit fd')
        picking = self.env['stock.picking'].create({
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            'partner_id': partner.id,
            'location_dest_id': internal_fd.lot_stock_id.id,
            'location_id': customers.id,
            'move_ids': [Command.create({
                'location_dest_id': internal_fd.lot_stock_id.id,
                'location_id': customers.id,
                'product_id': product.id,
                'name': 'move',
            })]
        })
        self.assertEqual(picking.move_ids[0].x_fiscal_deposit_move, 'entry fd')
