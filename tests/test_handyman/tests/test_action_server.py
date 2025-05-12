# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests.common import TransactionCase
from odoo import fields, Command


class ActionServerTestCase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.demo_account_move = cls.env['account.move'].create({
            'move_type': 'out_refund',
            'partner_id': cls.env['res.partner'].create({
                'name': 'partner_a',
            }).id,
            'invoice_date': fields.Date.today().strftime("%Y-%m-02"),
            'delivery_date': fields.Date.today().strftime("%Y-%m-02"),
            'invoice_line_ids': [
                Command.create({'quantity': 5, 'display_type': 'product'}),
            ],
            'x_task_id': cls.env['project.task'].create({
                'name': 'project_task',
                'project_id': cls.env['project.project'].create({
                    'name': 'project',
                }).id,
            }).id,
        })

    def test_add_default_analytic_account_server_action(self):
        self.move_line = self.demo_account_move.invoice_line_ids[0]
        self.move_line.analytic_distribution = False
        self.assertEqual(self.move_line.analytic_distribution, False)
        server_action = self.env['ir.actions.server'].search([('name', '=', 'Add default analytic account')])
        server_action.with_context(active_id=self.move_line.id).run()
        self.assertEqual(self.move_line.analytic_distribution, {self.move_line.move_id.x_task_id.project_id.account_id.id: 100})

    def test_add_section_task_name_server_action(self):
        self.assertEqual(1, None)
