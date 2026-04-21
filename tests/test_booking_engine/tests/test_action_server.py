# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta

from odoo import Command
from odoo.exceptions import UserError
from odoo.fields import Datetime
from odoo.tests import Form, freeze_time
from odoo.tests.common import TransactionCase


class BookingEngineAutomationsTestCase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env.ref('website.default_website')
        cls.website.tz = 'UTC'
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
            'rent_periodicity': 'nights',
            'pickup_time': 18.0,
            'return_time': 9.0,
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
        expected_start = start_datetime.replace(
            hour=18,
            minute=0,
            second=0,
            microsecond=0,
        )
        expected_end = end_datetime.replace(
            hour=9,
            minute=0,
            second=0,
            microsecond=0,
        )
        return expected_start, expected_end

    def _expected_slot_datetimes(self, start_datetime, end_datetime):
        expected_start, expected_end = self._expected_rental_datetimes(start_datetime, end_datetime)
        expected_end += timedelta(
            days=(end_datetime - start_datetime).days - (expected_end - expected_start).days
        )
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

    def test_automation_set_rental_hours(self):
        """Test for the industry_set_rental_hours automation on write."""
        order, sale_line = self._create_sale_line(self.product)
        order.action_confirm()

        expected_start_date, expected_end_date = self._expected_slot_datetimes(order.rental_start_date, order.rental_return_date)
        self.assertEqual(sale_line.planning_slot_ids[0].start_datetime, expected_start_date,
                         "The automation should align slot start time to the pickup time on write")
        self.assertEqual(sale_line.planning_slot_ids[0].end_datetime, expected_end_date,
                         "The automation should align slot end time to the return time on write")

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
        resources = sale_line.x_resource_ids
        sale_line.write({'qty_delivered': 1.0})
        self.assertEqual(order.rental_status, 'return',
                         "Test precondition: rental_status should be 'return'")
        self.assertEqual(resources[:1].x_occupancy, 'occupied',
                         "The automation should mark room resources as occupied on check in")

    def test_automation_set_resources_vacant_on_check_out(self):
        order, sale_line = self._create_sale_line(self.product)
        order.action_confirm()
        resources = sale_line.x_resource_ids
        sale_line.write({'qty_delivered': 1.0, 'qty_returned': 1.0})
        self.assertEqual(order.rental_status, 'returned',
                         "Test precondition: rental_status should be 'returned'")
        self.assertEqual(resources[:1].x_occupancy, 'vacant',
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
            start_previous_day = (last_midnight - timedelta(days=1)).replace(hour=18, minute=0, second=0, microsecond=0)
            end_today = last_midnight.replace(hour=9, minute=0, second=0, microsecond=0)
            self.env['planning.slot'].create({
                'role_id': role_has_checkout_cleaning.id,
                'resource_ids': resource_due_out.ids,
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
        self.env['ir.config_parameter'].sudo().set_bool('booking_engine.x_approvers_setting', False)

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
        self.env['ir.config_parameter'].sudo().set_bool('booking_engine.x_approvers_setting', True)

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
        self.env['ir.config_parameter'].sudo().set_bool('booking_engine.x_approvers_setting', True)

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
                'resource_ids': self.resource.ids,
                'sale_line_id': order_line.id,
                'start_datetime': self.today.replace(hour=9),
                'end_datetime': (self.today + timedelta(days=1)).replace(hour=10),
            })
            order_line_sequence = order_line.sequence
            city_tax = self.env['x_city_tax'].create({'x_sale_order_id': order.id})
            self.env.ref('booking_engine.update_city_tax_action').with_context(active_id=city_tax.id, active_model='x_city_tax').run()
            return order, order_line, order_line_sequence, city_tax

        # ----------- Case 1: Stay tax line should be created -----------
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

        # ----------- Case 2: Existing order line should be updated -----------
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

    ### Availability / Occupancy
    def test_automation_availability_product(self):
        """Test the lifecycle of x_availability records tied to a room offer (create, update, delete)."""

        # Setup
        tmpl = self.product.product_tmpl_id

        order, order_line = self._create_sale_line(self.product)
        tmpl.write({'x_is_a_room_offer': True})
        order.action_confirm()

        slot = order_line.planning_slot_ids[0]
        slot.write({
            'resource_ids': [Command.link(self.resource.id)],
            'start_datetime': self.today.replace(hour=9),
            'end_datetime': (self.today + timedelta(days=1)).replace(hour=10),
        })

        # Assert availabilities exist after creating the product
        avails = self.env['x_availability'].search([('x_stay_offer_id', '=', tmpl.id)])
        self.assertTrue(avails, "Availabilities should be created when a room offer is created.")
        self.assertEqual(len(avails), 500, "Exactly 500 days of availability should be generated.")

        # --- TEST 1: Change the room offer status changes the availabilities ---

        tmpl.write({'x_is_a_room_offer': False})

        avails = self.env['x_availability'].search([('x_stay_offer_id', '=', tmpl.id)])
        self.assertFalse(avails, "Availabilities should be removed when product is no longer a room offer.")

        tmpl.write({'x_is_a_room_offer': True})

        avails = self.env['x_availability'].search([('x_stay_offer_id', '=', tmpl.id)])
        self.assertEqual(len(avails), 500, "Availabilities should be recreated when toggled back.")

        # --- TEST 2: Archiving changes the availabilities ---

        tmpl.write({'active': False})

        avails = self.env['x_availability'].with_context(active_test=False).search([('x_stay_offer_id', '=', tmpl.id)])
        self.assertFalse(avails, "Availabilities should be unlinked when the product is archived.")

        tmpl.write({'active': True})

        avails = self.env['x_availability'].search([('x_stay_offer_id', '=', tmpl.id)])
        self.assertEqual(len(avails), 500, "Availabilities should be restored when the product is unarchived.")

        # --- TEST 3: Deleting the product changes the availabilities ---

        slot.unlink()
        order.action_cancel()
        order.unlink()
        tmpl.unlink()

        avails = self.env['x_availability'].search([('x_stay_offer_id', '=', tmpl.id)])
        self.assertFalse(avails, "Availabilities should be completely deleted when the product is deleted.")

    def test_automation_availability_resource_change(self):
        """Test that changing a room's active state or calendar marks its availabilities for recomputation."""

        # Setup
        self.room_offer_template.write({
            'x_resource_ids': [Command.link(self.resource.id)],
        })

        avails = self.env['x_availability'].search([('x_stay_offer_id', '=', self.room_offer_template.id)])
        self.assertTrue(avails, "Availabilities should exist for the room offer after linking the resource.")

        # --- CRITICAL ISOLATION STEP ---
        # Disable the master computation action so it doesn't instantly reset our flags to False
        master_action = self.env.ref('booking_engine.server_action_update_availabilities')
        master_action.write({'code': '# Master action disabled for flag testing'})

        # --- TEST 1: Changing the calendar_id flags the correct availabilities ---

        # Reset the dirty flags to False so we can detect the change
        avails.write({'x_to_recompute': False})

        new_calendar = self.env['resource.calendar'].create({'name': 'New Test Calendar'})
        self.resource.write({'calendar_id': new_calendar.id})

        avails = self.env['x_availability'].search([('x_stay_offer_id', '=', self.room_offer_template.id)])
        self.assertTrue(
            all(a.x_to_recompute for a in avails),
            "Changing calendar_id on the resource should flag its linked availabilities to recompute.",
        )

        # --- TEST 2: Archiving the resource flags the correct availabilities ---

        avails.write({'x_to_recompute': False})
        self.resource.write({'active': False})

        avails = self.env['x_availability'].search([('x_stay_offer_id', '=', self.room_offer_template.id)])
        self.assertTrue(
            all(a.x_to_recompute for a in avails),
            "Archiving the resource should flag its linked availabilities to recompute.",
        )

        # --- TEST 3: Test a non-triggering field ---

        avails.write({'x_to_recompute': False})

        # Change the name (which is NOT in the automation's trigger_field_ids)
        self.resource.write({'name': 'Test Room Due Out Renamed'})

        avails = self.env['x_availability'].search([('x_stay_offer_id', '=', self.room_offer_template.id)])
        self.assertFalse(
            any(a.x_to_recompute for a in avails),
            "Changing an untriggered field (like name) should NOT flag availabilities to recompute.",
        )

    def test_automation_availability_leave_change(self):
        """Test that creating or modifying a resource leave correctly links and flags availabilities."""

        # Setup
        calendar = self.env.company.resource_calendar_id
        self.resource.write({'calendar_id': calendar.id})

        self.room_offer_template.write({
            'x_resource_ids': [Command.link(self.resource.id)],
        })

        # --- CRITICAL ISOLATION STEP ---
        # Disable the master computation action so it doesn't instantly reset our flags to False.
        master_action = self.env.ref('booking_engine.server_action_update_availabilities')
        master_action.write({'code': '# Master action disabled for flag testing'})

        # --- TEST 1: Creating a direct resource leave ---

        leave_start = self.today
        leave_end = self.today + timedelta(days=2)

        leave = self.env['resource.calendar.leaves'].create({
            'name': 'Test Room Maintenance',
            'resource_id': self.resource.id,
            'calendar_id': calendar.id,
            'date_from': leave_start,
            'date_to': leave_end,
        })

        self.assertTrue(leave.x_availability_ids, "Creating a leave should link it to the corresponding daily availabilities.")
        self.assertTrue(
            all(a.x_to_recompute for a in leave.x_availability_ids),
            "Newly linked availabilities from the leave should be flagged to recompute.",
        )

        # --- TEST 2: Modify the dates ---

        leave.x_availability_ids.write({'x_to_recompute': False})

        leave.write({'date_to': leave_end + timedelta(days=1)})

        # Because the dates changed, the helper should have re-evaluated the links and flagged them
        self.assertTrue(
            all(a.x_to_recompute for a in leave.x_availability_ids),
            "Changing the leave dates should flag the updated availabilities to recompute.",
        )

        # --- TEST 3: Modify to a Global Leave (Remove resource_id) ---

        leave.x_availability_ids.write({'x_to_recompute': False})

        # Changing from a specific resource leave to a global calendar leave
        leave.write({'resource_id': False})

        # The automation should catch the change, evaluate the calendar_id, find our resource, and flag it
        self.assertTrue(
            all(a.x_to_recompute for a in leave.x_availability_ids),
            "Changing to a global calendar leave should flag the affected resource availabilities.",
        )

        # --- TEST 4: Change a non-triggering field ---

        leave.x_availability_ids.write({'x_to_recompute': False})

        # Change the name (NOT in the automation's trigger_field_ids)
        leave.write({'name': 'Test Room Maintenance Updated'})

        self.assertFalse(
            any(a.x_to_recompute for a in leave.x_availability_ids),
            "Changing an untriggered field (like name) should NOT flag availabilities to recompute.",
        )

    def test_automation_availability_slot_change(self):
        """Test that creating or modifying a planning slot correctly links and flags availabilities."""

        # Setup
        self.room_offer_template.write({
            'x_resource_ids': [Command.link(self.resource.id)],
        })

        # --- CRITICAL ISOLATION STEP ---
        # Disable the master computation action so it doesn't instantly reset our flags to False.
        master_action = self.env.ref('booking_engine.server_action_update_availabilities')
        master_action.write({'code': '# Master action disabled for flag testing'})

        # --- TEST 1: Create a Slot ---

        # We use the sale order to generate the slot
        order, order_line = self._create_sale_line(self.product)
        order.action_confirm()

        slot = order_line.planning_slot_ids[0]

        # Trigger the automation by setting the resource and dates
        slot.write({
            'resource_ids': [Command.link(self.resource.id)],
            'start_datetime': self.today.replace(hour=9),
            'end_datetime': (self.today + timedelta(days=2)).replace(hour=10),
        })

        self.assertTrue(slot.x_availability_ids, "Setting a resource and dates on a slot should link it to daily availabilities.")
        self.assertTrue(
            all(a.x_to_recompute for a in slot.x_availability_ids),
            "Newly linked availabilities from the slot should be flagged to recompute.",
        )

        # --- TEST 2: Modify the Dates ---

        # Reset the flags on the currently linked availabilities
        slot.x_availability_ids.write({'x_to_recompute': False})

        # Extend the slot by 1 day
        slot.write({'end_datetime': (self.today + timedelta(days=3)).replace(hour=10)})

        self.assertTrue(
            all(a.x_to_recompute for a in slot.x_availability_ids),
            "Changing the slot dates should flag the updated availabilities to recompute.",
        )

        # --- TEST 3: Modify the Resource (Drag & Drop behavior) ---

        # Create a second physical room and link it to the offer
        resource_2 = self.env['resource.resource'].create({
            'name': 'Test Room 2',
            'resource_type': 'material',
        })
        self.room_offer_template.write({
            'x_resource_ids': [Command.link(resource_2.id)],
        })

        old_avails = slot.x_availability_ids
        old_avails.write({'x_to_recompute': False})

        # Remove the previous one
        slot.write({'resource_ids': [Command.set([resource_2.id])]})

        # 1. Did the old availabilities get flagged before unlinking? (Freeing up Room 1)
        self.assertTrue(
            all(a.x_to_recompute for a in old_avails),
            "The previously linked availabilities should be flagged so the old room is freed up.",
        )

        # 2. Did the new availabilities get linked and flagged? (Occupying Room 2)
        self.assertTrue(
            all(a.x_to_recompute for a in slot.x_availability_ids),
            "The newly linked availabilities should be flagged when the slot moves to a new resource.",
        )

        # --- TEST 4: Change a non-triggering field ---

        # Reset the flags
        slot.x_availability_ids.write({'x_to_recompute': False})

        # Change allocated percentage (NOT in the automation's trigger_field_ids)
        slot.write({'allocated_percentage': 50})

        self.assertFalse(
            any(a.x_to_recompute for a in slot.x_availability_ids),
            "Changing an untriggered field (like allocated_percentage) should NOT flag availabilities.",
        )

    def test_availability_flow_double_book_then_cancel(self):
        """Integration test to verify the actual math of availability computations during a booking flow."""

        # Setup
        resource_1 = self.resource
        resource_2 = self.env['resource.resource'].create({
            'name': 'Test Room 2',
            'resource_type': 'material',
            'calendar_id': False,
        })

        tmpl = self.product.product_tmpl_id
        tmpl.write({
            'x_is_a_room_offer': True,
            'x_resource_ids': [Command.link(resource_1.id), Command.link(resource_2.id)],
        })

        # Helper to force the master computation action (in case any triggers use async crons)
        def force_computation():
            self.env.ref('booking_engine.server_action_update_availabilities').run()

        force_computation()

        target_date = self.today.date()
        avail = self.env['x_availability'].search([
            ('x_stay_offer_id', '=', tmpl.id),
            ('x_date', '=', target_date),
        ])

        # --- INITIAL STATE CHECK ---
        self.assertEqual(avail.x_total_units, 2, "There are 2 physical rooms linked to the offer.")
        self.assertEqual(avail.x_booked, 0, "No bookings yet, booked count should be 0.")

        # --- FLOW 1: First Reservation ---
        order1, order_line1 = self._create_sale_line(self.product)
        order1.action_confirm()
        slot1 = order_line1.planning_slot_ids[0]
        slot1.write({
            'resource_ids': [Command.set([resource_1.id])],
            'start_datetime': self.today.replace(hour=15),
            'end_datetime': (self.today + timedelta(days=1)).replace(hour=11),
        })

        force_computation()
        avail.invalidate_recordset()  # Clear ORM cache so we pull the fresh computed values from the DB

        self.assertEqual(avail.x_booked, 1, "First booking should increase x_booked to 1.")

        # --- FLOW 2: Second Reservation (Overlapping on the same day) ---
        order2, order_line2 = self._create_sale_line(self.product)
        order2.action_confirm()
        slot2 = order_line2.planning_slot_ids[0]
        slot2.write({
            'resource_ids': [Command.set([resource_2.id])],
            'start_datetime': self.today.replace(hour=15),
            'end_datetime': (self.today + timedelta(days=1)).replace(hour=11),
        })

        force_computation()
        avail.invalidate_recordset()

        self.assertEqual(avail.x_booked, 2, "Second booking should increase x_booked to 2.")

        # --- FLOW 3: Cancellation ---
        # Unlinking the slot simulates the user freeing up the resource on the Gantt chart
        slot1.unlink()
        order1.action_cancel()

        force_computation()
        avail.invalidate_recordset()

        self.assertEqual(avail.x_booked, 1, "Canceling the first booking should reduce x_booked back to 1.")
        self.assertEqual(avail.x_total_units, 2, "Total units should remain unaffected by bookings/cancellations.")
