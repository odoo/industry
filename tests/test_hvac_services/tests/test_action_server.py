# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, Command
from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from odoo.exceptions import UserError


@tagged('post_install', '-at_install')
class AutomationsTestCase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'hvac_partner',
        })
        cls.fsm_project = cls.env['project.project'].create({
            'name': 'Test HVAC FSM Project',
            'is_fsm': True,
            'company_id': cls.env.company.id,
        })
        cls.service_product = cls.env['product.product'].create({
            'name': 'HVAC Maintenance',
            'type': 'service',
            'service_tracking': 'task_in_project',
            'project_template_id': cls.fsm_project.id,
            'x_is_maintenance': True,
        })
        cls.device_product = cls.env['product.product'].create({
            'name': 'HVAC Device',
            'type': 'consu',
            'is_storable': True,
            'tracking': 'serial',
        })
        cls.lot_1 = cls.env['stock.lot'].create({
            'name': 'HVAC-SERIAL-01',
            'product_id': cls.device_product.id,
        })
        cls.lot_2 = cls.env['stock.lot'].create({
            'name': 'HVAC-SERIAL-02',
            'product_id': cls.device_product.id,
        })
        cls.action_server = cls.env.ref('hvac_services.add_new_device_to_customer')

    def test_so_line_quantity_updated_by_automation(self):
        so = self.env['sale.order'].create({
            'partner_id': self.partner.id,
        })
        line = self.env['sale.order.line'].create({
            'order_id': so.id,
            'product_id': self.service_product.id,
        })
        line.write({
            'x_maintained_serials_ids': [
                Command.link(self.lot_1.id),
                Command.link(self.lot_2.id),
            ]
        })

        self.assertEqual(line.product_uom_qty, 2, "SO line quantity must equal number of maintained serials.")

    def test_task_inherits_serials_on_create(self):
        so = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [
                Command.create({
                    'product_id': self.service_product.id,
                    'x_maintained_serials_ids': [
                        Command.link(self.lot_1.id),
                        Command.link(self.lot_2.id),
                    ],
                }),
            ],
        })
        so.action_confirm()
        task = so.tasks_ids.filtered('is_fsm')
        self.assertTrue(task, "FSM task must be created.")
        self.assertEqual(set(task.x_serials.ids), {self.lot_1.id, self.lot_2.id}, "FSM task must inherit serials on creation.")

    def test_task_serials_updated_on_delivery(self):
        so = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [
                Command.create({
                    'product_id': self.device_product.id,
                    'product_uom_qty': 1,
                }),
                Command.create({
                    'product_id': self.service_product.id,
                }),
            ],
        })
        so.action_confirm()
        task = so.tasks_ids.filtered('is_fsm')
        picking = so.picking_ids
        move = picking.move_ids
        move.write({
            'lot_ids': [Command.link(self.lot_1.id)],
        })
        picking.button_validate()
        self.assertIn(self.lot_1, task.x_serials, "Delivered serial must be added to FSM task via automation.")

    def test_add_new_device_duplicate_serial_error(self):
        self.env['stock.lot'].create({
            'name': 'DUPLICATE-001',
            'product_id': self.device_product.id,
        })
        wizard = self.env['x_new_devices'].with_context(
            active_ids=[self.partner.id],
            active_model='res.partner',
        ).create({
            'x_partner_id': self.partner.id,
            'x_device_id': self.device_product.product_tmpl_id.id,
            'x_serial_number': 'DUPLICATE-001',
            'x_delivery_date': fields.Datetime.now(),
        })
        with self.assertRaises(UserError):
            self.action_server.with_context(active_id=wizard.id, active_model='x_new_devices').run()

    def test_add_new_device_success(self):
        wizard = self.env['x_new_devices'].with_context(
            active_ids=[self.partner.id],
            active_model='res.partner',
        ).create({
            'x_partner_id': self.partner.id,
            'x_device_id': self.device_product.product_tmpl_id.id,
            'x_serial_number': 'NEW-HVAC-001',
            'x_delivery_date': fields.Datetime.now(),
        })

        self.action_server.with_context(active_id=wizard.id, active_model='x_new_devices').run()

        lot = self.env['stock.lot'].search([
            ('name', '=', 'NEW-HVAC-001'),
            ('product_id', '=', self.device_product.id),
        ])
        self.assertTrue(lot, "New device lot must be created.")

        picking = self.env['stock.picking'].search([
            ('partner_id', '=', self.partner.id),
            ('state', '=', 'done'),
            ('picking_type_id', '=', self.env.ref('stock.picking_type_out').id),
        ], limit=1)
        self.assertTrue(picking, "Outgoing picking must be validated.")
