# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import Command
from odoo.tests import HttpCase


class UrlsWebsiteTestCase(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_1 = cls.env['res.users'].create([{
            'name': 'Test User 1',
            'login': 'test_user_1',
            'partner_id': cls.env['res.partner'].create([{
                'name': 'Test Partner 1',
                'email': 'test1@example.com',
            }]).id,
            'group_ids': [Command.link(cls.env.ref('base.group_portal').id)],
        }])

    def test_cv_sent_applicant_portal_opens(self):
        with self.assertLogs(level="WARNING"):
            response = self.url_open('/website/action/cv_sent_applicants')
        self.assertEqual(response.status_code, 403, 'The request should be forbidden when no user is authenticated.')
        self.authenticate('test_user_1', '')
        response = self.url_open('/website/action/cv_sent_applicants')
        self.assertEqual(response.status_code, 200, 'The request should be successful for authenticated user.')
