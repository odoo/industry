# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo.tests import get_db_name, tagged
from .industry_case import IndustryCase

_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install')
class IndustryMailBehaviorTestCase(IndustryCase):
    def test_user_notification_type(self):
        db_name = get_db_name()
        if db_name.endswith('imported_no_demo'):
            return
        for user in self.env['res.users'].search([('group_ids', 'in', [self.env.ref('base.group_user').id, self.env.ref('base.group_system').id]), ('notification_type', '!=', 'inbox')]):
            _logger.warning("Notification type should remain 'inbox' for all users, not the case for %s (%d).", user.name, user.id)

    def test_mail_generated(self):
        db_name = get_db_name()
        if db_name.endswith('imported_with_demo'):
            return

        mails = self.env['mail.mail'].search([('model', '!=', False), ('model', '!=', 'hr.expense')])
        if mails:
            models = list(set(mails.mapped('model')))
            _logger.warning(
                "Mails are generated from models: %s — use correct context to prevent mail pollution.",
                ', '.join(models)
            )
