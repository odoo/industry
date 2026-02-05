# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import Command
from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class ComputedFieldsTestCase(TransactionCase):

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

    def test_sale_order_serials(self):
        so1 = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [
                Command.create({
                    'product_id': self.service_product.id,
                    'x_maintained_serials_ids': [Command.link(self.lot_1.id), Command.link(self.lot_2.id)],
                }),
            ],
        })

        self.assertEqual(set(so1.x_maintained_serials_ids.ids), {self.lot_1.id, self.lot_2.id}, "Sale order serials must be aggregated from order lines.")

        so2 = self.env['sale.order'].create({
            'partner_id': self.partner.id,
        })
        line = self.env['sale.order.line'].create({
            'order_id': so2.id,
            'product_id': self.service_product.id,
        })
        line.write({
            'x_maintained_serials_ids': [
                Command.link(self.lot_1.id),
                Command.link(self.lot_2.id),
            ]
        })
        self.assertEqual(set(so2.x_maintained_serials_ids.ids), {self.lot_1.id, self.lot_2.id}, "Sale order serials must be aggregated from order lines.")

    def test_lot_sale_order_count(self):
        self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'x_maintained_serials_ids': [Command.link(self.lot_1.id)],
        })
        self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'x_maintained_serials_ids': [Command.link(self.lot_1.id)],
        })
        self.assertEqual(self.lot_1.x_sale_order_count, 2, "Lot must count how many sale orders reference it.")
        self.assertEqual(self.lot_2.x_sale_order_count, 0, "Lot without sale orders must have zero count.")

    def test_lot_project_task_count(self):
        self.env['project.task'].create({
            'name': 'FSM Task 1',
            'project_id': self.fsm_project.id,
            'is_fsm': True,
            'x_serials': [Command.link(self.lot_1.id)],
        })
        self.env['project.task'].create({
            'name': 'FSM Task 2',
            'project_id': self.fsm_project.id,
            'is_fsm': True,
            'x_serials': [Command.link(self.lot_1.id)],
        })

        self.assertEqual(self.lot_1.x_project_task_count, 2, "Lot must count related FSM tasks.")
        self.assertEqual(self.lot_2.x_project_task_count, 0, "Lot without tasks must have zero task count.")

    def test_lot_delivery_date(self):
        so = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [
                Command.create({
                    'product_id': self.device_product.id,
                    'product_uom_qty': 1,
                }),
            ],
        })
        so.action_confirm()

        picking = so.picking_ids
        move = picking.move_ids
        move.write({'lot_ids': [Command.link(self.lot_1.id)]})
        picking.button_validate()
        self.assertTrue(self.lot_1.x_delivery, "Lot delivery date must be set after outgoing picking is done.")

    def test_lot_maintenances_ids(self):
        so = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [
                Command.create({
                    'product_id': self.service_product.id,
                    'x_maintained_serials_ids': [Command.link(self.lot_1.id)],
                }),
            ],
        })
        self.assertIn(so, self.lot_1.x_maintenances_ids, "Lot must collect maintenance sale orders from SO lines.")

    def test_lot_maintenance_state(self):
        self.assertEqual(self.lot_1.x_maintenance, 'N/A', "Lot without deliveries or maintenance must be N/A.")

        so = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [
                Command.create({
                    'product_id': self.device_product.id,
                    'product_uom_qty': 1,
                }),
            ],
        })
        so.action_confirm()
        picking = so.picking_ids
        picking.move_ids.write({'lot_ids': [Command.link(self.lot_1.id)]})
        picking.button_validate()

        self.lot_1._invalidate_cache()

        self.assertEqual(self.lot_1.x_maintenance, 'No Maintenance', "Delivered lot without active maintenance must show 'No Maintenance'.")

        maintenance_so = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [
                Command.create({
                    'product_id': self.service_product.id,
                    'x_maintained_serials_ids': [Command.link(self.lot_1.id)],
                }),
            ],
        })
        maintenance_so.subscription_state = '3_progress'

        self.lot_1._invalidate_cache()

        self.assertEqual(self.lot_1.x_maintenance, 'Maintained', "Lot must show 'Maintained' when an active maintenance exists.")
