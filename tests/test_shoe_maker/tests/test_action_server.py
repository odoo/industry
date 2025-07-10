# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, Command
from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class ShoeMakerAutomationsTestCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_a = cls.env['res.partner'].create({'name': 'partner_a', 'email': 'partner_a@example.com'})
        cls.product_1 = cls.env['product.product'].create({
            'name': 'Product 1',
            'type': 'service',
            'service_tracking': 'task_in_project',
            'project_template_id': cls.env.ref('industry_fsm.fsm_project').id,
        })
        cls.product_2 = cls.env['product.product'].create({
            'name': 'Product 2',
            'type': 'service',
            'service_tracking': 'task_in_project',
            'project_template_id': cls.env.ref('industry_fsm.fsm_project').id,
        })
        cls.so3 = cls.env['sale.order'].create({
            'partner_id': cls.partner_a.id,
            'order_line': [
                Command.create({
                    'product_id': cls.product_1.id,
                    'product_uom_qty': 1.0,
                }),
                Command.create({
                    'product_id': cls.product_2.id,
                    'product_uom_qty': 1.0,
                }),
            ]
        })

    def test_cancel_task_null_so(self):
        # Create a sale order for a product with a null quantity
        self.so1 = self.env['sale.order'].create({
            'partner_id': self.partner_a.id,
            'order_line': [
                Command.create({
                    'product_id': self.product_1.id,
                    'product_uom_qty': 0.0,
                })
            ],
        })
        self.so1.action_confirm()
        # Check that the task is canceled
        self.assertEqual(self.so1.tasks_ids.stage_id.id, self.env.ref('industry_fsm.planning_project_stage_4').id,
                         "The task created from a sale order line with a null quantity should be in the 'Canceled' stage.")
    
    def test_set_state_done_cancel(self):
        self.so2 = self.env['sale.order'].create({
            'partner_id': self.partner_a.id,
            'order_line': [
                Command.create({
                    'product_id': self.product_2.id,
                    'product_uom_qty': 1.0,
                })
            ],
        })
        self.so2.action_confirm()
        # mark the task as done
        self.so2.tasks_ids.write({
            'stage_id': self.env.ref('industry_fsm.planning_project_stage_3').id,
        })
        self.assertEqual(self.so2.tasks_ids.state, '1_done',
                            "The task should be in the 'Done' state after being set to Done stage.")

        # mark the task as canceled
        self.so2.tasks_ids.write({
            'stage_id': self.env.ref('industry_fsm.planning_project_stage_4').id,
        })
        self.assertEqual(self.so2.tasks_ids.state, '1_canceled',
                            "The task should be in the 'Canceled' state after being set to Canceled stage.")

    def test_email_sales_order_ready(self):
        self.so3.action_confirm()
        
        # mark the first task as done
        self.so3.tasks_ids[0].action_fsm_validate()
        # Check that the email is not sent yet
        mail_after = self.env['mail.mail'].search([('res_id', '=', self.so3.tasks_ids[0].id)])
        self.assertEqual(len(mail_after), 0, "An email should not be sent until all tasks are done.")

        # mark the second task as done
        self.so3.tasks_ids[1].action_fsm_validate()
        # Check that the emails are sent after both tasks are done
        mail_after = self.env['mail.mail'].search([('res_id', '=', self.so3.tasks_ids[1].id)])
        self.assertGreater(len(mail_after), 0, "An email should be sent when all tasks are done.")
