# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase
from odoo.tests import tagged, Form


@tagged('post_install', '-at_install')
class TeamSportsClubActionServerTestCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Sports Club Player',
            'email': 'player@example.com',
            'grade_id': cls.env.ref('team_sports_club.res_partner_grade_9').id,
        })
        cls.tags_1 = cls.env['res.partner.category'].create({'name': '25/26'})
        cls.tags_2 = cls.env['res.partner.category'].create({'name': 'Player'})
        cls.product = cls.env['product.product'].create({
            'name': 'Contribution',
            'type': 'service',
            'list_price': 350.0,
        })
        cls.action_server = cls.env.ref('team_sports_club.generate_contribution_sale_order_action')

    def test_generate_contribution_sale_order_action(self):
        so_count = self.env['sale.order'].search_count([])
        with Form(self.env['x_contribution'].with_context(active_ids=[self.partner.id], active_model="res.partner")) as wizard_form:
            wizard_form.x_product_id = self.product
            wizard_form.x_tag_ids.add(self.tags_1)
            wizard_form.x_tag_ids.add(self.tags_2)
            wizard = wizard_form.save()

        with self.assertRaises(UserError):
            self.action_server.with_context(active_ids=[wizard.id], active_model="x_contribution").run()

        wizard.x_partner_ids = [Command.set([self.partner.id])]
        self.action_server.with_context(active_ids=[wizard.id], active_model="x_contribution").run()
        self.assertEqual(self.env['sale.order'].search_count([]), so_count + 1, "A sale order should be generated")

        sale_order = self.env['sale.order'].search([('partner_id', '=', self.partner.id)], limit=1)
        self.assertTrue(sale_order, "A sale order should be generated")

        self.assertEqual(sale_order.order_line.product_id, self.product, "The sale order should have the correct product")
        self.assertEqual(sale_order.state, 'sale', "The sale order should be in 'sale' state")

        self.assertIn(self.tags_1, self.partner.category_id, "Tags should be added to the partner")
        self.assertIn(self.tags_2, self.partner.category_id, "Tags should be added to the partner")
