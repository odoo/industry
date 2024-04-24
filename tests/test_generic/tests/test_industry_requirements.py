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

    def test_knowledge_article_notification(self):
        for module in self.installed_modules:
            ref = self.env.ref(module + '.notification_knowledge', raise_if_not_found=False)
            self.assertTrue(ref, "You forgot to define a `mail.message` with `id=notification_knowledge`.")
            notif = self.env['mail.message'].browse(ref.id)
            self.assertIn(
                '<a href="/knowledge/article/',
                notif.body,
                "The notification should contain a link to the knowledge article."
            )
            knowledge = self.env['ir.model.data'].search(
                [('model', '=', 'knowledge.article'), ('module', '=', module)], limit=1
            )
            self.assertTrue(knowledge, "Missing knowledge article for the industry module.")
            knowledge_article = self.env.ref(knowledge.complete_name)
            self.assertIn(
                'href="/knowledge/article/%s' % knowledge_article.id,
                notif.body,
                "The notification link should target the module-related knowledge article."
            )
