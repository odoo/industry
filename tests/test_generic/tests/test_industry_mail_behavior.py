# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging


from odoo.tests import tagged
from .industry_case import IndustryCase

_logger = logging.getLogger(__name__)


RECORD_CONTEXT_MODELS_DICT = {
    'calendar.event': ['no_mail_to_attendees'],
    'crm.lead': ['mail_auto_subscribe_no_notify'],
    'event.event': ['mail_auto_subscribe_no_notify'],
    'helpdesk.ticket': ['mail_notrack', 'mail_auto_subscribe_no_notify'],
    'hr.applicant': ['mail_notrack'],
    'hr.job': ['mail_auto_subscribe_no_notify'],
    'mail.activity': ['mail_activity_quick_update'],
    'mailing.mailing': ['mail_auto_subscribe_no_notify'],
    'maintenance.request': ['mail_auto_subscribe_no_notify', 'mail_activity_quick_update'],
    'mrp.eco': ['mail_auto_subscribe_no_notify'],
    'pos.session': ['mail_auto_subscribe_no_notify'],
    'project.project': ['mail_auto_subscribe_no_notify'],
    'project.task': ['mail_auto_subscribe_no_notify'],
    'purchase.order': ['mail_auto_subscribe_no_notify'],
    'quality.check': ['mail_auto_subscribe_no_notify'],
    'res.partner': ['mail_auto_subscribe_no_notify'],
    'sale.order': ['mail_auto_subscribe_no_notify'],
    'slide.channel': ['mail_auto_subscribe_no_notify'],
    'stock.picking': ['mail_auto_subscribe_no_notify'],
    'survey.survey': ['mail_auto_subscribe_no_notify'],
}

EXCEPTION_MODELS = [
    'hr.expense',
    'hr.leave',
]


@tagged('post_install', '-at_install')
class IndustryMailBehaviorTestCase(IndustryCase):

    def test_generic_mail_message_generated(self):
        mails = self.env['mail.mail']._read_group([('model', '!=', False), ('model', 'not in', EXCEPTION_MODELS), ('state', '!=', 'outgoing')], ['res_id', 'model'], ['id:count'])

        result = {}
        for res_id, res_model, count in mails:
            record = self.env[res_model].browse(res_id)
            if not record:
                continue
            all_activities = getattr(record, 'activity_ids', False) or self.env['mail.activity']
            upsell_activity = all_activities.filtered(lambda a: a.note and 'upsell' in a.note.lower())
            upsell_activity_external_ids = upsell_activity._get_external_ids()
            upsell_activity_without_external_ids = upsell_activity.filtered(lambda a: not upsell_activity_external_ids.get(a.id))
            if len(upsell_activity_without_external_ids) == count:
                continue

            ext_ids = record._get_external_ids()
            if not any(ext_ids.values()):
                continue
            for ext_id in next(iter(ext_ids.values())):
                ctxs = RECORD_CONTEXT_MODELS_DICT.get(res_model)
                if ctxs:
                    result.setdefault(ext_id, set()).update(ctxs)

                if all_activities:
                    for activity in (all_activities - upsell_activity_without_external_ids):
                        activity_external_ids = activity._get_external_ids().get(activity.id, [])
                        if not activity_external_ids:
                            result.setdefault(ext_id, set()).add('mail_activity_quick_update')
                        else:
                            for activity_ext_id in activity_external_ids:
                                result.setdefault(activity_ext_id, set()).add('mail_activity_quick_update')

                if getattr(record, 'calendar_event_ids', False):
                    for event in record.calendar_event_ids:
                        event_external_ids = event._get_external_ids().get(event.id, [])
                        if not event_external_ids:
                            result.setdefault(ext_id, set()).add('mail_activity_quick_update')
                        else:
                            for event_ext_id in event_external_ids:
                                result.setdefault(event_ext_id, set()).add('mail_activity_quick_update')

        for ext_ids, context in result.items():
            _logger.warning(
                "Messages and mails are generated from record '%s' — use context '%s' to prevent message and mail pollution.",
                ext_ids,
                ', '.join(context)
            )
