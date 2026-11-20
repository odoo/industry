# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ast import literal_eval
from datetime import timedelta

from odoo import Command, fields
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, new_test_user


class TestReception(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.reception = new_test_user(
            cls.env,
            login='reception-test@example.com',
            groups='appointment.group_appointment_user,sales_team.group_sale_salesman_all_leads',
        )
        cls.patient = cls.env['res.partner'].create({'name': 'Calendar Quotation Patient'})
        cls.opportunity = cls.env['crm.lead'].create({
            'name': 'First examination enquiry',
            'type': 'opportunity',
            'partner_id': cls.patient.id,
            'team_id': cls.env.ref('dentist_practice.crm_team_patient_journey').id,
            'user_id': cls.reception.id,
        })
        start = fields.Datetime.now() + timedelta(days=1)
        cls.appointment = cls.env['calendar.event'].with_context(no_mail_to_attendees=True).create({
            'name': 'First examination',
            'user_id': cls.reception.id,
            'start': start,
            'stop': start + timedelta(minutes=30),
            'privacy': 'confidential',
            'appointment_type_id': cls.env.ref('dentist_practice.appointment_new_patient').id,
            'appointment_booker_id': cls.patient.id,
            'opportunity_id': cls.opportunity.id,
            'partner_ids': [Command.set((cls.reception.partner_id | cls.patient).ids)],
        })
        cls.quote_action = cls.env.ref('dentist_practice.action_calendar_event_dental_quotation').with_user(
            cls.reception,
        ).with_context(
            active_model='calendar.event', active_id=cls.appointment.id, active_ids=cls.appointment.ids,
        )

    def test_quotation_uses_patient_and_reuses_linked_order(self):
        action = self.quote_action.run()
        order = self.env['sale.order'].browse(action['res_id'])
        self.assertEqual(order.state, 'draft')
        self.assertEqual(order.partner_id, self.patient)
        self.assertEqual(order.opportunity_id, self.opportunity)
        self.assertEqual(order.x_dental_appointment_id, self.appointment)
        self.assertEqual(self.quote_action.run()['res_id'], order.id)
        self.assertEqual(self.appointment.x_dental_sale_order_ids, order)

        appointment_action = self.env.ref('dentist_practice.action_sale_order_dental_appointment').with_user(
            self.reception,
        ).with_context(active_model='sale.order', active_id=order.id, active_ids=order.ids).run()
        self.assertEqual(appointment_action['res_model'], 'calendar.event')
        self.assertEqual(appointment_action['res_id'], self.appointment.id)

    def test_quotation_requires_resolving_conflicting_contacts(self):
        other_contact = self.env['res.partner'].create({'name': 'Guest Booker'})
        self.appointment.write({
            'appointment_booker_id': other_contact.id,
            'partner_ids': [Command.set((self.reception.partner_id | other_contact).ids)],
        })
        with self.assertRaisesRegex(UserError, 'have different contacts'):
            self.quote_action.run()
        self.assertFalse(self.appointment.x_dental_sale_order_ids)

    def test_lab_queue_tracks_remaining_service_quantity(self):
        product = self.env.ref('dentist_practice.product_dental_lab_service')
        vendor = self.env['res.partner'].create({'name': 'Test Dental Lab'})
        order = self.env['purchase.order'].create({
            'partner_id': vendor.id,
            'order_line': [Command.create({
                'product_id': product.id,
                'product_qty': 2,
                'price_unit': 50,
            })],
        })
        order.button_confirm()
        outstanding = self.env.ref('dentist_practice.filter_lab_orders_outstanding')
        domain = literal_eval(outstanding.domain)
        self.assertTrue(order.filtered_domain(domain))
        order.order_line.qty_received = 1
        self.assertTrue(order.filtered_domain(domain))
        order.order_line.qty_received = 2
        self.assertFalse(order.filtered_domain(domain))
