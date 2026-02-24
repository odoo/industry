# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta

from odoo import Command
from odoo.tests import tagged
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
        product = self.env['product.template'].create({
            'name': 'Test Room Offer',
            'type': 'service',
            'sale_ok': True,
            'x_is_a_room_offer': True,
        })

        role = product.planning_role_id
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
        product = self.env['product.template'].create({
            'name': 'Room Offer Original',
            'type': 'service',
            'sale_ok': True,
            'x_is_a_room_offer': True,
        })
        role = product.planning_role_id
        self.assertTrue(role, "A planning role should exist for a room offer product")

        new_name = 'Room Offer Updated'
        product.write({'name': new_name})
        role.invalidate_cache()

        self.assertEqual(role.name, new_name,
                         "The planning role name should update when the product name changes")

    def test_automation_delete_role_on_room_offer_delete(self):
        product = self.env['product.template'].create({
            'name': 'Room Offer To Delete',
            'type': 'service',
            'sale_ok': True,
            'x_is_a_room_offer': True,
        })
        role = product.planning_role_id
        self.assertTrue(role, "A planning role should exist for a room offer product")

        role_id = role.id
        product.unlink()

        self.assertFalse(self.env['planning.role'].browse(role_id).exists(),
                         "The planning role should be deleted when the product is deleted")
