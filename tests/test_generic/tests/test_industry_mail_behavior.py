# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests import get_db_name, tagged
from .industry_case import IndustryCase


@tagged('post_install', '-at_install')
class IndustryMailBehaviorTestCase(IndustryCase):
    def test_no_unexpected_mails_or_messages(self):
        for _ in self.installed_industries:
            db_name = get_db_name()
            if db_name.endswith('imported_no_demo'):
                return

            # Ensure admin notification type remains correct
            admin = self.env.ref('base.user_admin')

            self.assertEqual(
                admin.notification_type, "inbox",
                "Admin notification type should remain 'inbox' for all industries."
            )
