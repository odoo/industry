# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields
from odoo.tests.common import TransactionCase
from odoo.tests import tagged, Form


@tagged('post_install', '-at_install')
class TattooShopAutomationsTestCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Tattoo Customer',
            'email': 'customer@example.com',
        })
        # Create a lead to use in tests
        cls.lead = cls.env['crm.lead'].create({
            'name': 'Tattoo Inquiry',
            'partner_id': cls.partner.id,
            'stage_id': cls.env.ref('crm.stage_lead1').id,
        })

    def test_booking_link_sent_automation(self):
        nb_mail = self.env['mail.mail'].search_count([])
        # Trigger automation
        with Form(self.lead) as lead_form:
            lead_form.stage_id = self.env.ref('crm.stage_lead3')
        nb_mail_after = self.env['mail.mail'].search_count([])
        self.assertEqual(nb_mail_after, nb_mail + 1, "An email should be sent when the stage is changed to 'Booking Link Sent'")

    def test_aftercare_automation(self):
        nb_mail = self.env['mail.mail'].search_count([])
        # Trigger automation
        with Form(self.lead) as lead_form:
            lead_form.stage_id = self.env.ref('tattoo_shop.crm_stage_7')
        nb_mail_after = self.env['mail.mail'].search_count([])
        self.assertEqual(nb_mail_after, nb_mail + 1, "An email should be sent when the stage is changed to 'Aftercare'")
