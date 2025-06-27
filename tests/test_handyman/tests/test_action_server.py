# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests import tagged, Form
from odoo.tests.common import TransactionCase
from odoo import fields, Command


@tagged('post_install', '-at_install')
class ActionServerTestCase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_a = cls.env['res.partner'].create({
                'name': 'partner_a',
        })
        cls.demo_account_move = cls.env['account.move'].create({
            'move_type': 'out_refund',
            'partner_id': cls.partner_a.id,
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
        cls.sale_order_1 = cls.env['sale.order'].create({
            'name': 'order_item_1',
            'partner_id': cls.partner_a.id,
        })
        sale_order_form = Form(cls.sale_order_1)
        with sale_order_form.order_line.new() as order_line:
            order_line.display_type = 'line_section'
            order_line.name = 'section_1'
        with sale_order_form.order_line.new() as order_line:
            order_line.product_id = cls.env.ref("handyman.product_product_5")
        sale_order_form.save()
        cls.sale_order_1.action_confirm()

    def test_base_automation_create_move_line_add_automatic_account(self):
        self.move_line = self.demo_account_move.invoice_line_ids[0]
        self.assertEqual(self.move_line.analytic_distribution, {f'{self.move_line.move_id.x_task_id.project_id.account_id.id}': 100.0})

    def test_add_default_analytic_account_server_action(self):
        self.move_line = self.demo_account_move.invoice_line_ids[0]
        self.move_line.analytic_distribution = False
        # Check that the automation is not triggered when move_line changes
        self.assertEqual(self.move_line.analytic_distribution, False)
        server_action = self.env['ir.actions.server'].browse(self.env.ref('handyman.action_add_default_analytic_account').id)
        server_action.with_context(active_id=self.move_line.id, active_model="account.move.line").run()
        self.assertEqual(self.move_line.analytic_distribution, {f'{self.move_line.move_id.x_task_id.project_id.account_id.id}': 100.0})

    def test_add_section_task_name_base_automation(self):
        for project_task in self.sale_order_1.tasks_ids:
            self.assertEqual(project_task.name[-12:], " - section_1")

    def test_add_section_task_name_server_action(self):
        for project_task in self.sale_order_1.tasks_ids:
            project_task.name = "project_task_1"
            # Check that the automation is not triggered when project task is changed
            self.assertEqual(project_task.name, "project_task_1")
            server_action = self.env['ir.actions.server'].browse(self.env.ref('handyman.action_add_section_task_name').id)
            server_action.with_context(active_ids=[project_task.id], active_model="project.task").run()
            self.assertEqual(project_task.name, "project_task_1 - section_1")
