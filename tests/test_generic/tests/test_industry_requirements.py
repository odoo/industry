# Part of Odoo. See LICENSE file for full copyright and licensing details.

import sys

from odoo.tests.common import tagged

from .industry_case import IndustryCase


@tagged('post_install', '-at_install')
class TestEnv(IndustryCase):

    def test_payment_demo(self):
        if self.env['ir.module.module']._get('payment_demo').state != 'installed':
            return
        demo_provider = self.env.ref('payment.payment_provider_demo')
        sys_args = sys.argv
        index_database = sys_args.index('-d')
        if sys_args[index_database + 1].endswith('imported_no_demo'):
            self.assertEqual(demo_provider.state, 'disabled', "Payment provider demo should be disabled in data")
            self.assertFalse(demo_provider.is_published, "Payment provider demo should be unpublished in data")
        elif sys_args[index_database + 1].endswith('imported_with_demo'):
            self.assertEqual(demo_provider.state, 'test', "Payment provider demo should be enabled (test) in demo")
            self.assertTrue(demo_provider.is_published, "Payment provider demo should be published in demo")
