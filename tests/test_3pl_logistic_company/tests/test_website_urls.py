# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import Command
from odoo.tests import HttpCase, tagged


@tagged('post_install', '-at_install')
class UrlsWebsiteTestCase(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_1 = cls.env['res.partner'].create({'name': 'Test Partner 1'})
        cls.user_1 = cls.env['res.users'].create([{
            'name': 'Test User 1',
            'login': 'test_user_1',
            'partner_id': cls.partner_1.id,
            'group_ids': [Command.link(cls.env.ref('base.group_portal').id)],
        }])

    def test_products_stock_portal_open(self):
        with self.assertLogs(level="WARNING"):
            response = self.url_open('/website/action/products')
        self.assertEqual(response.status_code, 403, 'The request should be forbidden when no user is authenticated.')
        self.authenticate('test_user_1', '')
        response = self.url_open('/website/action/products')
        self.assertEqual(response.status_code, 200, 'The request should be successful for authenticated user.')
