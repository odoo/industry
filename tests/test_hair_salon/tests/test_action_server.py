# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime
from dateutil.relativedelta import relativedelta

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class ActionServerTestCase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_a = cls.env['res.partner'].create({'name': 'Partner A'})

    def test_break_subpart_calendar_event_server_action(self):
        appointment = self.env['appointment.type'].create({
            'name': 'Haircut and Color',
            'appointment_duration': 2.0,
            'appointment_tz': 'UTC',
            'assign_method': 'time_auto_assign',
            'schedule_based_on': 'resources',
            'x_break': True,
            'x_break_start_appointment': 0.8,
            'x_break_end_appointment': 1.2
        })
        event = self.env['calendar.event'].create({
            'name': 'Event test',
            'appointment_type_id': appointment.id,
            'partner_ids': [(6, 0, [self.partner_a.id])],
            'start': datetime.datetime.today().date() + relativedelta(hours=10),
            'stop': datetime.datetime.today().date() + relativedelta(hours=12),
        })
        event_part_1 = self.env['calendar.event'].search([("name", "ilike", "[PART 1]" + event.name)])
        event_part_2 = self.env['calendar.event'].search([("name", "ilike", "[PART 2]" + event.name)])
        self.assertTrue(event_part_1, f"Creating an event with break times should create an event with name '[PART 1]{event.name}'")
        self.assertTrue(event_part_2, f"Creating an event with break times should create an event with name '[PART 2]{event.name}'")

        self.assertEqual(event_part_1.start, event.start, "The part 1 event should start at the same time as the event")
        self.assertEqual(event_part_1.stop, event.start + datetime.timedelta(hours=event.x_break_start),
            f"The part 1 event should stop {event.x_break_start} hours after starting (Based on the break start time)")
        self.assertEqual(event_part_1.x_parent_id, event, "The part 1 event should have the event as its parent")

        self.assertEqual(event_part_2.start, event.start + datetime.timedelta(hours=event.x_break_end),
            f"The part 2 event should start {event.x_break_end} hours after starting (Based on the break end time)")
        self.assertEqual(event_part_2.stop, event.stop, "The part 2 event should stop at the same time as the event")
        self.assertEqual(event_part_2.x_parent_id, event, "The part 2 event should have the event as its parent")

        self.assertEqual(event.x_appointment_part_1, event_part_1, "The part 1 event should be assigned as the appointment part 1 of the event")
        self.assertEqual(event.x_appointment_part_2, event_part_2, "The part 2 event should be assigned as the appointment part 2 of the event")

    def test_not_triggered_break_subpart_calendar_event_server_action(self):
        appointment = self.env['appointment.type'].create({
            'name': 'Haircut',
            'appointment_duration': 1.0,
            'appointment_tz': 'UTC',
            'assign_method': 'time_auto_assign',
            'schedule_based_on': 'resources',
        })
        event = self.env['calendar.event'].create({
            'name': 'Event test',
            'appointment_type_id': appointment.id,
            'partner_ids': [(6, 0, [self.partner_a.id])],
            'start': datetime.datetime.today().date() + relativedelta(hours=10),
            'stop': datetime.datetime.today().date() + relativedelta(hours=11),
        })
        event_part_1 = self.env['calendar.event'].search([("name", "ilike", "[PART 1]" + event.name)])
        event_part_2 = self.env['calendar.event'].search([("name", "ilike", "[PART 2]" + event.name)])
        self.assertFalse(event_part_1, f"Creating an event without break times should not create an event with name '[PART 1]{event.name}'")
        self.assertFalse(event_part_2, f"Creating an event without break times should not create an event with name '[PART 2]{event.name}'")
