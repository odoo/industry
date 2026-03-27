# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta

from odoo import Command
from odoo.exceptions import UserError
from odoo.fields import Datetime
from odoo.tests import tagged, Form, freeze_time
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class BookingEngineAutomationsTestCase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env.ref('website.default_website')
        cls.website.tz = 'UTC'
        recurrence = cls.env.ref('sale_renting.recurrence_nightly')
        cls.recurrence_pickup_time = recurrence.pickup_time
        cls.recurrence_return_time = recurrence.return_time
        cls.partner = cls.env['res.partner'].create({'name': 'Test partner'})
        cls.resource = cls.env['resource.resource'].create({
            'name': 'Room Resource Due Out',
            'resource_type': 'material',
            'calendar_id': False,
        })
        cls.role = cls.env['planning.role'].create({
            'name': 'Role',
            'sync_shift_rental': True,
            'x_is_a_room_offer': True,
            'resource_ids': [Command.link(cls.resource.id)],
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Room offer',
            'type': 'service',
            'planning_enabled': True,
            'planning_role_id': cls.role.id,
            'rent_ok': True,
        })
        cls.room_offer_template = cls.env['product.template'].create({
            'name': 'Room Offer Template',
            'type': 'service',
            'sale_ok': True,
            'x_is_a_room_offer': True,
        })
        cls.project = cls.env['project.project'].create({
            'name': 'Housekeeping Project',
            'x_is_house_keeping_project': True,
        })
        cls.stage_clean = cls.env.ref('booking_engine.project_task_type_17')
        cls.stage_ready = cls.env.ref('booking_engine.project_task_type_18')
        cls.today = Datetime.today()

    def _create_sale_line(self, product):
        order = self.env['sale.order'].with_context(in_rental_app=True).create({
            'partner_id': self.partner.id,
            'rental_start_date': self.today,
            'rental_return_date': self.today + timedelta(days=1),
            'order_line': [
                Command.create({
                    'product_id': product.id,
                    'product_uom_qty': 1,
                }),
            ],
        })
        return order, order.order_line

    def _expected_rental_datetimes(self, start_datetime, end_datetime):
        pickup_hour = int(self.recurrence_pickup_time)
        pickup_minute = int(self.recurrence_pickup_time % 1 * 60)
        return_hour = int(self.recurrence_return_time)
        return_minute = int(self.recurrence_return_time % 1 * 60)

        expected_start = start_datetime.replace(
            hour=pickup_hour,
            minute=pickup_minute,
            second=0,
            microsecond=0,
        )
        expected_end = end_datetime.replace(
            hour=return_hour,
            minute=return_minute,
            second=0,
            microsecond=0,
        )
        return expected_start, expected_end

    def _expected_slot_datetimes(self, start_datetime, end_datetime):
        expected_start, expected_end = self._expected_rental_datetimes(start_datetime, end_datetime)
        if expected_start >= end_datetime:
            expected_start -= timedelta(days=1)
        if expected_start >= expected_end:
            expected_end += timedelta(days=1)
        return expected_start, expected_end

    def _expected_nights(self, start_datetime, end_datetime):
        return int(((end_datetime - start_datetime).total_seconds() + 86399) // 86400)

    def test_automation_fix_slot_times_on_create_and_write(self):
        """Test for the industry_fix_slot_times automation."""
        order, sale_line = self._create_sale_line(self.product)
        expected_start, expected_end = self._expected_slot_datetimes(order.rental_start_date, order.rental_return_date)
        order.action_confirm()
        self.assertEqual(sale_line.planning_slot_ids[0].start_datetime, expected_start,
                         "The slot start time should be updated based on recurrence pickup time")
        self.assertEqual(sale_line.planning_slot_ids[0].end_datetime, expected_end,
                         "The slot end time should be updated with the recurrence return time")
        self.assertEqual(sale_line.start_date, expected_start,
                         "The order line start date should be updated based on recurrence pickup time")
        self.assertEqual(sale_line.return_date, expected_end,
                         "The order line return date should be updated based on recurrence return time")
        self.assertEqual(sale_line.x_nights, self._expected_nights(expected_start, expected_end),
                         "Automation should recompute the number of nights on create")

    def test_automation_set_rental_hours(self):
        """Test for the industry_set_rental_hours server action."""
        start_date = self.today
        return_date = start_date + timedelta(days=1)
        order = self.env['sale.order'].with_context(in_rental_app=True).create({
            'partner_id': self.partner.id,
            'rental_start_date': start_date,
            'rental_return_date': return_date,
        })
        expected_start_date, expected_end_date = self._expected_rental_datetimes(start_date, return_date)

        self.assertEqual(order.rental_start_date, expected_start_date,
                         "The automation should align rental_start_date to the pickup time on write")
        self.assertEqual(order.rental_return_date, expected_end_date,
                         "The automation should align rental_return_date to the return time on write")

    def test_automation_create_role_on_room_offer_create(self):
        room_offer_product_template = self.room_offer_template
        role = room_offer_product_template.planning_role_id

        self.assertTrue(role, "A planning role should be created for a room offer product")
        self.assertEqual(role.name, room_offer_product_template.name,
                         "The planning role should be created with the product name")
        self.assertTrue(role.sync_shift_rental,
                        "The planning role should sync shifts and rentals by default")
        self.assertTrue(role.x_is_a_room_offer,
                        "The planning role should be marked as a room offer")
        self.assertIn(room_offer_product_template, role.product_ids,
                      "The planning role should be linked to the product")

    def test_automation_edit_role_name_on_room_offer_edit(self):
        room_offer_product_template = self.room_offer_template
        role = room_offer_product_template.planning_role_id

        self.assertTrue(role, "A planning role should exist for a room offer product")
        new_name = 'Room Offer Updated'
        room_offer_product_template.write({'name': new_name})

        self.assertEqual(role.name, new_name,
                         "The planning role name should update when the product name changes")

    def test_automation_delete_role_on_room_offer_delete(self):
        room_offer_product_template = self.room_offer_template
        role = room_offer_product_template.planning_role_id

        self.assertTrue(role, "A planning role should exist for a room offer product")

        room_offer_product_template.unlink()
        self.assertFalse(self.env['planning.role'].browse(role.id).exists(),
                         "The planning role should be deleted when the product is deleted")

    def test_automation_set_resources_occupied_on_check_in(self):
        order, sale_line = self._create_sale_line(self.product)
        order.action_confirm()
        resource = sale_line.x_resource_id
        sale_line.write({'qty_delivered': 1.0})
        self.assertEqual(order.rental_status, 'return',
                         "Test precondition: rental_status should be 'return'")
        self.assertEqual(resource.x_occupancy, 'occupied',
                         "The automation should mark room resources as occupied on check in")

    def test_automation_set_resources_vacant_on_check_out(self):
        order, sale_line = self._create_sale_line(self.product)
        order.action_confirm()
        resource = sale_line.x_resource_id
        sale_line.write({'qty_delivered': 1.0, 'qty_returned': 1.0})
        self.assertEqual(order.rental_status, 'returned',
                         "Test precondition: rental_status should be 'returned'")
        self.assertEqual(resource.x_occupancy, 'vacant',
                         "The automation should mark room resources as vacant on check out")

    def test_action_update_rooms_server_action(self):
        order, sale_line = self._create_sale_line(self.product)
        role_has_checkout_cleaning = self.env['planning.role'].create({
            'name': 'Role Has Checkout Cleaning',
            'x_is_a_room_offer': True,
            'x_has_checkout_cleaning': True,
        })
        resource_due_out = self.env['resource.resource'].create({
            'name': 'Room Resource Due Out',
            'resource_type': 'material',
            'role_ids': [Command.link(role_has_checkout_cleaning.id)],
        })

        with freeze_time('2026-03-02 00:00:00'):
            last_midnight = datetime(2026, 3, 2, 0, 0)
            pickup_hour = int(self.recurrence_pickup_time)
            pickup_minute = int(self.recurrence_pickup_time % 1 * 60)
            return_hour = int(self.recurrence_return_time)
            return_minute = int(self.recurrence_return_time % 1 * 60)
            start_previous_day = (last_midnight - timedelta(days=1)).replace(hour=pickup_hour, minute=pickup_minute, second=0, microsecond=0)
            end_today = last_midnight.replace(hour=return_hour, minute=return_minute, second=0, microsecond=0)
            self.env['planning.slot'].create({
                'role_id': role_has_checkout_cleaning.id,
                'resource_id': resource_due_out.id,
                'sale_line_id': sale_line.id,
                'start_datetime': start_previous_day,
                'end_datetime': end_today,
            })
            self.env.ref('booking_engine.server_action_update_rooms').run()

        self.assertEqual(resource_due_out.x_occupancy, 'due_out',
                         "The server action should set due out occupancy for checkout rooms")

        task = self.env['project.task'].search([
            ('name', '=like', 'HK%'),
            ('x_resource_id', '=', resource_due_out.id),
            ('partner_id', '=', order.partner_id.id),
        ])

        self.assertTrue(task, "Housekeeping task should be created for due out resource")
        self.assertEqual(task.x_cleaning, 'checkout',
            "Checkout tasks should be marked as checkout cleaning",
        )
        self.assertEqual(task.date_deadline, last_midnight + timedelta(hours=24),
            "Checkout task deadline should be end of the day",
        )

    def test_automation_on_task_stage_clean(self):
        self.env['ir.config_parameter'].sudo().set_param('booking_engine.x_approvers_setting', '0')
        task = self.env['project.task'].create({
            'name': 'Housekeeping Task',
            'project_id': self.project.id,
            'stage_id': self.stage_clean.id,
        })

        self.assertEqual(task.stage_id, self.stage_ready,
                         "Task should move to ready stage when no approvers are required")
        self.assertEqual(task.state, '1_done',
                         "Task should be done when no approvers are required")

    def test_automation_on_task_stage_ready(self):
        self.env['ir.config_parameter'].sudo().set_param('booking_engine.x_approvers_setting', '1')
        self.env.company.write({'x_setting_approver_users_ids': [(5, 0, 0)]})
        task = self.env['project.task'].create({
            'name': 'Housekeeping Task',
            'project_id': self.project.id,
            'stage_id': self.stage_clean.id,
        })

        with self.assertRaises(UserError):
            with Form(task) as t:
                t.stage_id = self.stage_ready

    def test_automation_update_task_cleaning_state(self):
        self.env['ir.config_parameter'].sudo().set_param('booking_engine.x_approvers_setting', '1')
        task = self.env['project.task'].create({
            'name': 'Housekeeping Task',
            'project_id': self.project.id,
            'x_resource_id': self.resource.id,
            'stage_id': self.stage_clean.id,
        })

        self.assertEqual(self.resource.x_house_keeping_stage_id, self.stage_clean,
                         "Resource cleaning stage should match with task stage on create")
        task.stage_id = self.stage_ready
        self.assertEqual(self.resource.x_house_keeping_stage_id, self.stage_ready,
                         "Resource stage should update on task stage changes")

    def _create_guest_product(self, adults=2, children=1):
        attribute = self.env['product.attribute'].create({
            'name': 'Guest Count',
            'x_captures_guests': True,
        })
        value = self.env['product.attribute.value'].create({
            'name': f'{adults}A{children}C',
            'attribute_id': attribute.id,
            'x_adults': adults,
            'x_children': children,
        })
        product_template = self.env['product.template'].create({
            'name': 'Guest Product',
            'type': 'service',
            'x_is_stay_tax': True,
            'attribute_line_ids': [Command.create({
                'attribute_id': attribute.id,
                'value_ids': [Command.link(value.id)],
            })],
        })
        return product_template.product_variant_id

    def test_action_update_city_tax(self):
        product = self._create_guest_product(adults=2, children=1)
        service_product = self.env['product.template'].create({
            'name': 'Service Product',
            'type': 'service',
            'sale_ok': True,
            'planning_enabled': False,
            'x_is_a_room_offer': True,
            'x_has_city_tax': True,
        })
        role = self.env['planning.role'].create({
            'name': 'Resource Role',
            'product_ids': [Command.link(service_product.id)],
        })

        def _create_order_with_slot(product):
            order, order_line = self._create_sale_line(product)
            order.action_confirm()
            self.env['planning.slot'].create({
                'role_id': role.id,
                'resource_id': self.resource.id,
                'sale_line_id': order_line.id,
                'start_datetime': self.today.replace(hour=9),
                'end_datetime': (self.today + timedelta(days=1)).replace(hour=10),
            })
            order_line_sequence = order_line.sequence
            city_tax = self.env['x_city_tax'].create({'x_sale_order_id': order.id})
            self.env.ref('booking_engine.update_city_tax_action').with_context(active_id=city_tax.id, active_model='x_city_tax').run()
            return order, order_line, order_line_sequence, city_tax

        # ---------- Case 1: Stay tax line should be created ----------
        _, order_line, order_line_sequence, city_tax = _create_order_with_slot(product)

        stay_tax_lines = order_line.filtered(lambda l: l.product_id.x_is_stay_tax)
        self.assertEqual(len(stay_tax_lines), 1,
                         "Server action should create a stay tax line if missing")
        self.assertEqual(stay_tax_lines.sequence, order_line_sequence + 1,
                         "Stay tax line sequence should be updated")
        self.assertEqual(stay_tax_lines.product_uom_qty, city_tax.x_total,
                         "Stay tax line quantity should match city tax total")
        self.assertEqual(stay_tax_lines.qty_delivered, city_tax.x_total,
                         "Stay tax line delivered quantity should match city tax total")

        # ---------- Case 2: Existing order line should be updated ----------
        product.write({'x_is_stay_tax': False})
        order2, order_line2, _, city_tax2 = _create_order_with_slot(product)
        self.assertEqual(len(order2.order_line), 2,
                        "Server action should update existing order line")
        city_tax_line = order2.order_line - order_line2

        self.assertTrue(city_tax_line.product_id.x_is_stay_tax, "City tax order line product should have x_is_stay_tax True")
        self.assertEqual(city_tax_line.product_uom_qty, city_tax2.x_total, "City tax order line quantity should match city tax total")
        self.assertEqual(city_tax_line.qty_delivered, city_tax2.x_total, "City tax order line delivered quantity should match city tax total")

    def test_action_apply_rental_check_out_opens_city_tax(self):
        order, sale_line = self._create_sale_line(self.product)
        self.product.write({'x_is_a_room_offer': True, 'x_has_city_tax': True})
        order.action_confirm()
        sale_line.write({'qty_delivered': 1.0})
        return_action = order.action_open_return()
        wizard = Form(self.env['rental.order.wizard'].with_context(return_action['context'])).save()
        action = self.env.ref('booking_engine.apply_rental_check_out').with_context(
            active_id=wizard.id, active_model='rental.order.wizard'
        ).run()

        self.assertEqual(order.rental_status, 'returned',
                         "Test precondition: rental_status should be 'returned' after return")
        self.assertTrue(action, "Server action should return a City Tax action on checkout")
        self.assertEqual(action.get('res_model'), 'x_city_tax',
                         "Server action should open the City Tax form")
        self.assertEqual(action['context'].get('search_default_x_sale_order_id'), order.id,
                         "City Tax action should search on the current sale order")
        self.assertEqual(action['context'].get('default_x_sale_order_id'), order.id,
                         "City Tax action should default to the current sale order")
