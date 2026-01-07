# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo.tests import tagged
from .industry_case import IndustryCase

_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install')
class IndustryMailBehaviorTestCase(IndustryCase):
    def test_user_notification_type(self):
        if not self.env['ir.module.module'].search_count([('demo', '=', True)], limit=1):
            return
        for user in self.env['res.users'].search([('group_ids', 'in', [self.env.ref('base.group_user').id, self.env.ref('base.group_system').id]), ('notification_type', '!=', 'inbox')]):
            _logger.warning("Notification type should remain 'inbox' for all users, not the case for %s (%d).", user.name, user.id)

    def test_mail_generated(self):
        if self.env['ir.module.module'].search_count([('demo', '=', True)], limit=1):
            return

        mails = self.env['mail.mail'].search([('model', '!=', False), ('model', '!=', 'hr.expense')])
        if mails:
            models = list(set(mails.mapped('model')))
            _logger.warning(
                "Mails are generated from models: %s — use correct context to prevent mail pollution.",
                ', '.join(models)
            )
