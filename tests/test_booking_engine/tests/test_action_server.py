# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests import tagged, Form, freeze_time
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class BookingEngineAutomationsTestCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env.ref('website.default_website')
        cls.website.tz = 'UTC'
        cls.recurrence = cls.env.ref('sale_renting.recurrence_nightly')
        cls.partner = cls.env['res.partner'].create({'name': 'Test partner'})
        cls.room_role = cls.env['planning.role'].create({
            'name': 'Room role',
            'x_is_a_room_offer': True,
        })
        cls.other_role = cls.env['planning.role'].create({
            'name': 'Other role',
            'x_is_a_room_offer': False,
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Room offer',
            'type': 'service',
            'planning_enabled': True,
            'planning_role_id': cls.room_role.id,
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

    def _create_sale_line(self):
        order = self.env['sale.order'].with_context(in_rental_app=True).create({
            'partner_id': self.partner.id,
            'rental_start_date': datetime(2026, 2, 1, 0, 0),
            'rental_return_date': datetime(2026, 2, 2, 0, 0),
            'order_line': [
                Command.create({
                    'product_id': self.product.id,
                    'product_uom_qty': 1,
                }),
            ],
        })
        return order, order.order_line

    def _expected_slot_datetimes(self, start_datetime, end_datetime):
        pickup_hour = int(self.recurrence.pickup_time)
        pickup_minute = int(self.recurrence.pickup_time % 1 * 60)
        return_hour = int(self.recurrence.return_time)
        return_minute = int(self.recurrence.return_time % 1 * 60)

        expected_start = start_datetime.replace(
            hour=pickup_hour,
            minute=pickup_minute,
            second=0,
            microsecond=0,
        )
        if expected_start >= end_datetime:
            expected_start -= timedelta(days=1)

        expected_end = end_datetime.replace(
            hour=return_hour,
            minute=return_minute,
            second=0,
            microsecond=0,
        )
        if expected_start >= expected_end:
            expected_end += timedelta(days=1)
        return expected_start, expected_end

    def _expected_nights(self, start_datetime, end_datetime):
        return int(((end_datetime - start_datetime).total_seconds() + 86399) // 86400)

    def _expected_rental_datetimes(self, start_datetime, end_datetime):
        pickup_hour = int(self.recurrence.pickup_time)
        pickup_minute = int(self.recurrence.pickup_time % 1 * 60)
        return_hour = int(self.recurrence.return_time)
        return_minute = int(self.recurrence.return_time % 1 * 60)

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

    def _create_room_offer_product(self, name):
        product = self.room_offer_template.copy({'name': name})
        return product, product.planning_role_id

    def test_industry_fix_slot_times_server_action(self):
        """Test for the industry_fix_slot_times server action."""
        server_action = self.env.ref('booking_engine.industry_fix_slot_times')
        _order, sale_line = self._create_sale_line()

        start_datetime = datetime(2026, 2, 23, 3, 0)
        end_datetime = datetime(2026, 2, 24, 4, 0)
        expected_start, expected_end = self._expected_slot_datetimes(start_datetime, end_datetime)

        slot = self.env['planning.slot'].create({
            'role_id': self.other_role.id,
            'sale_line_id': sale_line.id,
            'start_datetime': start_datetime,
            'end_datetime': end_datetime,
        })

        self.assertNotEqual(slot.start_datetime, expected_start,
                            "Test precondition: start_datetime should not be aligned yet")
        self.assertNotEqual(slot.end_datetime, expected_end,
                            "Test precondition: end_datetime should not be aligned yet")

        slot.role_id = self.room_role.id
        server_action.with_context(active_ids=[slot.id], active_model='planning.slot').run()

        # self.assertEqual(slot.start_datetime, expected_start,
        #                  "The action should align start_datetime to the pickup time")
        # self.assertEqual(slot.end_datetime, expected_end,
        #                  "The action should align end_datetime to the return time")
        self.assertEqual(sale_line.start_date, expected_start,
                         "The action should update sale_line start_date")
        self.assertEqual(sale_line.return_date, expected_end,
                         "The action should update sale_line return_date")
        self.assertEqual(sale_line.x_nights, self._expected_nights(expected_start, expected_end),
                         "The action should recompute the number of nights on the sale line")

    def test_automation_set_rental_hours(self):
        """Test for the industry_set_rental_hours server action."""
        # check set_rental_hours on create
        order, sale_line = self._create_sale_line()
        expected_start, expected_end = self._expected_rental_datetimes(order.rental_start_date, order.rental_return_date)

        self.assertEqual(order.rental_start_date, expected_start,
                         "The action should align rental_start_date to the pickup time")
        self.assertEqual(order.rental_return_date, expected_end,
                         "The action should align rental_return_date to the return time")

        # check set_rental_hours on write with new dates

        new_start_datetime = datetime(2026, 2, 25, 5, 45)
        new_end_datetime = datetime(2026, 2, 26, 8, 10)

        expected_start, expected_end = self._expected_rental_datetimes(new_start_datetime, new_end_datetime)

        order.write({
            'rental_start_date': new_start_datetime,
            'rental_return_date': new_end_datetime,
        })

        self.assertEqual(order.rental_start_date, expected_start,
                         "The automation should align rental_start_date to the pickup time on write")
        self.assertEqual(order.rental_return_date, expected_end,
                         "The automation should align rental_return_date to the return time on write")

    def test_automation_create_role_on_room_offer_create(self):
        product, role = self._create_room_offer_product('Test Room Offer')
        self.assertTrue(role, "A planning role should be created for a room offer product")
        self.assertEqual(role.name, product.name,
                         "The planning role should be created with the product name")
        self.assertTrue(role.sync_shift_rental,
                        "The planning role should sync shifts and rentals by default")
        self.assertTrue(role.x_is_a_room_offer,
                        "The planning role should be marked as a room offer")
        self.assertIn(product, role.product_ids,
                      "The planning role should be linked to the product")

    def test_automation_edit_role_name_on_room_offer_edit(self):
        product, role = self._create_room_offer_product('Room Offer Original')
        self.assertTrue(role, "A planning role should exist for a room offer product")
        new_name = 'Room Offer Updated'
        product.write({'name': new_name})

        self.assertEqual(role.name, new_name,
                         "The planning role name should update when the product name changes")

    def test_automation_delete_role_on_room_offer_delete(self):
        product, role = self._create_room_offer_product('Room Offer To Delete')
        self.assertTrue(role, "A planning role should exist for a room offer product")

        product.unlink()

        self.assertFalse(self.env['planning.role'].browse(role.id).exists(),
                         "The planning role should be deleted when the product is deleted")

    def test_automation_set_resources_occupied_on_check_in(self):
        order, sale_line = self._create_sale_line()
        print('at this stage order.rental_status is draft')

        resource = self.env['resource.resource'].create({
            'name': 'Room Resource',
            'resource_type': 'material',
            'default_role_id': self.room_role.id,
            'role_ids': [Command.link(self.room_role.id)],
        })
        self.env['planning.slot'].create({
            'role_id': self.room_role.id,
            'resource_id': resource.id,
            'sale_line_id': sale_line.id,
            'start_datetime': datetime(2026, 2, 1, 12, 0),
            'end_datetime': datetime(2026, 2, 2, 12, 0),
        })
        order.action_confirm()
        print('at this stage  order.rental_status is pickup')

        sale_line.write({'qty_delivered': 1.0})
        print('at this stage  order.rental_status is return')


        self.assertEqual(order.rental_status, 'return',
                         "Test precondition: rental_status should be 'return' after pickup")
        self.assertEqual(resource.x_occupancy, 'occupied',
                         "The automation should mark room resources as occupied on check in")
    # here
    def test_automation_set_resources_vacant_on_check_out(self):
        order, sale_line = self._create_sale_line()

        resource = self.env['resource.resource'].create({
            'name': 'Room Resource',
            'resource_type': 'material',
            'default_role_id': self.room_role.id,
            'role_ids': [Command.link(self.room_role.id)],
            'x_occupancy': 'occupied',
        })
        self.env['planning.slot'].create({
            'role_id': self.room_role.id,
            'resource_id': resource.id,
            'sale_line_id': sale_line.id,
            'start_datetime': datetime(2026, 2, 1, 12, 0),
            'end_datetime': datetime(2026, 2, 2, 12, 0),
        })
        order.action_confirm()

        sale_line.write({'qty_delivered': 1.0})
        sale_line.write({'qty_returned': 1.0})

        self.assertEqual(order.rental_status, 'returned',
                         "Test precondition: rental_status should be 'returned' after return")
        self.assertEqual(resource.x_occupancy, 'vacant',
                         "The automation should mark room resources as vacant on check out")

    def test_action_update_rooms_server_action(self):
        self.room_role.write({
            'x_has_checkout_cleaning': True,
        })
        order, sale_line = self._create_sale_line()
        # order.action_confirm()

        resource_due_out = self.env['resource.resource'].create({
            'name': 'Room Resource Due Out',
            'resource_type': 'material',
            'default_role_id': self.room_role.id,
            'role_ids': [Command.link(self.room_role.id)],
        })
        # resource_stayover = self.env['resource.resource'].create({
        #     'name': 'Room Resource Stayover',
        #     'resource_type': 'material',
        #     'default_role_id': self.room_role.id,
        #     'role_ids': [Command.link(self.room_role.id)],
        # })


        with freeze_time('2026-03-02 00:00:00'):
            last_midnight = datetime(2026, 3, 2, 0, 0)
            pickup_hour = int(self.recurrence.pickup_time)
            pickup_minute = int(self.recurrence.pickup_time % 1 * 60)
            return_hour = int(self.recurrence.return_time)
            return_minute = int(self.recurrence.return_time % 1 * 60)
            start_previous_day = (last_midnight - timedelta(days=1)).replace(
                hour=pickup_hour,
                minute=pickup_minute,
                second=0,
                microsecond=0,
            )
            end_today = last_midnight.replace(
                hour=return_hour,
                minute=return_minute,
                second=0,
                microsecond=0,
            )
            end_next_day = (last_midnight + timedelta(days=1)).replace(
                hour=return_hour,
                minute=return_minute,
                second=0,
                microsecond=0,
            )

            self.env['planning.slot'].create({
                'role_id': self.room_role.id,
                'resource_id': resource_due_out.id,
                'sale_line_id': sale_line.id,
                'start_datetime': start_previous_day,
                'end_datetime': end_today,
            })
            # self.env['planning.slot'].create({
            #     'role_id': self.room_role.id,
            #     'resource_id': resource_stayover.id,
            #     'sale_line_id': sale_line.id,
            #     'start_datetime': start_previous_day,
            #     'end_datetime': end_next_day,
            # })

            self.env.ref('booking_engine.server_action_update_rooms').run()

        self.assertEqual(resource_due_out.x_occupancy, 'due_out',
                         "The server action should set due out occupancy for checkout rooms")
        # self.assertEqual(resource_stayover.x_occupancy, 'stayover',
        #                  "The server action should set stayover occupancy for stayover rooms")

        tasks = self.env['project.task'].search([
            ('name', '=like', 'HK%'),
            ('x_resource_id', '=', resource_due_out.id),
            ('partner_id', '=', order.partner_id.id),
        ])

        task_by_resource = {task.x_resource_id.id: task for task in tasks}
        # self.assertSetEqual(
        #     set(task_by_resource.keys()),
        #     {resource_due_out.id, resource_stayover.id},
        #     "Housekeeping tasks should be created for both due out and stayover resources",
        # )
        self.assertEqual(task_by_resource[resource_due_out.id].x_cleaning, 'checkout',
                         "Checkout tasks should be marked as checkout cleaning")
        # self.assertEqual(task_by_resource[resource_stayover.id].x_cleaning, 'stayover',
        #                  "Stayover tasks should be marked as stayover cleaning")
        self.assertEqual(task_by_resource[resource_due_out.id].date_deadline, last_midnight + timedelta(hours=24),
                         "Checkout task deadline should be end of the day")
        # self.assertEqual(task_by_resource[resource_stayover.id].date_deadline, last_midnight + timedelta(hours=24),
        #                  "Stayover task deadline should be end of the day")

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
        resource = self.env['resource.resource'].create({
            'name': 'Housekeeping Resource',
            'resource_type': 'material',
        })

        task = self.env['project.task'].create({
            'name': 'Housekeeping Task',
            'project_id': self.project.id,
            'x_resource_id': resource.id,
            'stage_id': self.stage_clean.id,
        })

        self.assertEqual(resource.x_house_keeping_stage_id, self.stage_clean,
                         "Resource cleaning stage should match task stage on create")

        task.stage_id = self.stage_ready
        self.assertEqual(resource.x_house_keeping_stage_id, self.stage_ready,
                         "Resource cleaning stage should update when task stage changes")


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

        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
        })

        order_line = self.env['sale.order.line'].create({
            'order_id': order.id,
            'product_id': product.id,
            'product_uom_qty': 1,
        })

        order.action_confirm()
        service_product = self.env['product.template'].create({
            'name': 'Service Product',
            'type': 'service',
            'sale_ok': True,
            'planning_enabled': False,
            'x_is_a_room_offer': True,
            'x_has_city_tax': True,
        })
        new_role = self.env['planning.role'].create({
            'name': 'Resource Role',
            'product_ids': [Command.link(service_product.id)],
        })
        new_resource = self.env['resource.resource'].create({
            'name': 'Resource 1',
            'resource_type': 'material',
        })
        self.env['planning.slot'].create({
            'role_id': new_role.id,
            'resource_id': new_resource.id,
            'sale_line_id': order_line.id,
            'start_datetime': datetime(2026, 2, 5, 9, 0),
            'end_datetime': datetime(2026, 2, 6, 9, 0),
        })
        city_tax = self.env['x_city_tax'].create({'x_sale_order_id': order.id})

        order_line_sequence = order_line.sequence
        self.env.ref('booking_engine.update_city_tax_action').with_context(active_id=city_tax.id, active_model='x_city_tax').run()

        stay_tax_lines = order_line.filtered(lambda l: l.product_id.x_is_stay_tax)
        self.assertEqual(len(stay_tax_lines), 1,
                         "Server action should create a stay tax line if missing")
        self.assertEqual(stay_tax_lines.sequence, order_line_sequence + 1,
                         "Stay tax line sequence should be updated")
        self.assertEqual(stay_tax_lines.product_uom_qty, city_tax.x_total,
                         "Stay tax line quantity should match city tax total")
        self.assertEqual(stay_tax_lines.qty_delivered, city_tax.x_total,
                         "Stay tax line delivered quantity should match city tax total")

        order_2 = self.env['sale.order'].create({
            'partner_id': self.partner.id,
        })

        product.write({'x_is_stay_tax': False})

        order_line_2 = self.env['sale.order.line'].create({
            'order_id': order_2.id,
            'product_id': product.id,
            'product_uom_qty': 1,
        })

        order_2.action_confirm()
        service_product_2 = self.env['product.template'].create({
            'name': 'Service Product',
            'type': 'service',
            'sale_ok': True,
            'planning_enabled': False,
            'x_is_a_room_offer': True,
            'x_has_city_tax': True,
        })
        new_role_2 = self.env['planning.role'].create({
            'name': 'Resource Role',
            'product_ids': [Command.link(service_product_2.id)],
        })
        new_resource_2 = self.env['resource.resource'].create({
            'name': 'Resource 1',
            'resource_type': 'material',
        })
        self.env['planning.slot'].create({
            'role_id': new_role_2.id,
            'resource_id': new_resource_2.id,
            'sale_line_id': order_line_2.id,
            'start_datetime': datetime(2026, 2, 5, 9, 0),
            'end_datetime': datetime(2026, 2, 6, 9, 0),
        })
        city_tax = self.env['x_city_tax'].create({'x_sale_order_id': order_2.id})
        self.env.ref('booking_engine.update_city_tax_action').with_context(active_id=city_tax.id, active_model='x_city_tax').run()

        self.assertEqual(len(order_2.order_line), 2,
                         "Server action should update existing order line")
        
        city_tax_order_line = order_2.order_line - order_line_2
                
        self.assertEqual(city_tax_order_line.product_id.x_is_stay_tax, True,
                         "City tax order line product have a x_is_stay_tax true")
        self.assertEqual(city_tax_order_line.product_uom_qty, city_tax.x_total,
                         "City tax order line quantity should match city tax total")
        self.assertEqual(city_tax_order_line.qty_delivered, city_tax.x_total,
                         "City tax order line delivered quantity should match city tax total") 

    def test_action_apply_rental_check_out_opens_city_tax(self):
        order, sale_line = self._create_sale_line()
        self.product.write({'x_has_city_tax': True})
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
