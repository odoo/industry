# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import os
import re

from odoo.tests.common import tagged

from .industry_case import IndustryCase, get_industry_path

_logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 100 * 1024 * 1024  # in megabytes


@tagged('post_install', '-at_install')
class TestEnv(IndustryCase):

    def test_xml_files(self):
        for module in self.installed_modules:
            self._check_files_in_path(module)

    def _check_files_in_path(self, module):
        path = get_industry_path() + module
        for root, dirs, files in os.walk(path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                ext = os.path.splitext(file_path)[1].lower()
                if ext not in ['.py', '.xml']:
                    continue
                if os.path.getsize(file_path) > MAX_FILE_SIZE:
                    raise "Max file size exceeded"
                with open(file_path, 'rb') as f:
                    content = f.read().decode('utf8')
                if ext == '.py':
                    if file_name != '__manifest__.py':
                        _logger.warning(
                            "No python file is allowed in an industry module, except __manifest__.py."
                            " Please remove %s.", file_name
                        )
                    else:
                        self._check_manifest(content, file_name)
                    continue
                self._check_xml_style(content, module, file_name)
                self._check_update_status(content, file_name)
                self._check_useless_models(content, file_name)
                self._check_useless_fields_on_models(content, file_name)

    def _check_manifest(self, s, file_name):
        if (first_line := s.split('\n')[0]) != '{':
            message = "First line of the manifest should be the sole symbol '{'. "
            if not first_line:
                message += "No need for an empty line."
            elif "coding" in first_line:
                message += "No need to specify the encoding since python3."
            else:
                message += "Got '%s'." % first_line
            _logger.warning(message)

    def _check_xml_style(self, s, module, file_name):
        starts_with = [
            "<?xml version='1.0' encoding='UTF-8'?>",
            "<?xml version='1.0' encoding=\"UTF-8\"?>",
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
            "<?xml version=\"1.0\" encoding='UTF-8'?>",
        ]
        first_line = s.split('\n')[0]
        if not any(first_line == start_line for start_line in starts_with):
            _logger.warning(
                "XML files should begin with the following line: %s, but %s starts with %s",
                starts_with[0], file_name, first_line
            )

        if count := (s.count(' id="'+module+'.') + s.count(" id='"+module+'.')):
            _logger.warning(
                "Defining an xmlid with the current module name is useless, module name will be "
                "added automatically. Found %d occurence(s) of ' id=\"%s.ID' in %s.",
                count, module, file_name
            )

        count = (s.count('ref("'+module+'.') + s.count("ref('"+module+'.')) - (
            s.count('env.ref("'+module+'.') + s.count("env.ref('"+module+'.'))
        if count:
            _logger.warning(
                "Referring to an xmlid created within the current module name is useless. If none is"
                " provided, it will check in current module. Found %d occurence(s) of ref(\"%s.ID\")"
                " in %s (this remark does not apply to 'env.ref(\"%s.ID\")' where it is required).",
                count, module, file_name, module
            )
        if s.count("x_studio"):
            _logger.warning("Please remove 'studio' from 'x_studio' in %s.", file_name)
        useless_attributes = [
            "context.get('studio')",
            "data-last-history-steps",
            "context=\"{'studio'",
        ]
        for attr in useless_attributes:
            if s.count(attr):
                _logger.warning("Please remove '%s' in %s.", attr, file_name)

        end_of_file = repr(s).split('\\')
        if 'n' not in end_of_file[-1] or len(end_of_file[-1]) > 2:
            _logger.warning("It looks like you forgot to add an empty line at the end of %s.", file_name)
        elif 'n' in end_of_file[-2] and len(end_of_file[-2]) <= 2:
            _logger.warning("One empty line at the end of %s is enough, please remove others.", file_name)

    def _check_update_status(self, s, filename):
        models_to_update = [
            "base.automation",
            "ir.actions.act_window",
            "ir.actions.server",
            "ir.model",
            "ir.model.access",
            "ir.model.fields",
            "ir.ui.view",
            "knowledge.article",
            "loyalty.generate.wizard",
        ]
        models_not_to_update = [
            "appointment.type",
            "calendar.event",
            "crm.lead",
            "crm.stage",
            "crm.tag",
            "event.event.ticket",
            "hr.applicant",
            "hr.department",
            "hr.job",
            "hr.recruitment.stage",
            "ir.attachment",
            "ir.rule",
            "knowledge.attachment",
            "knowledge.cover",
            "loyalty.program",
            "loyalty.reward",
            "loyalty.rule",
            "mail.template",
            "mrp.bom",
            "mrp.bom.line",
            "pos.category",
            "pos.config",
            "product.attribute.value",
            "product.category",
            "product.packaging",
            "product.product",
            "product.template",
            "product.template.attribute.line",
            "product.template.attribute.value",
            "res.config.settings",
            "res.partner",
            "sale.order",
            "sale.order.line",
            "sign.item",
            "sign.request",
            "sign.template",
            "stock.warehouse.orderpoint",
            "uom.category",
            "uom.uom",
            "website",
        ]
        for model in models_to_update:
            if re.search('model="'+model+'"', s) and not re.search('<field .+model="'+model, s) and not s.count('<odoo>'):
                _logger.warning(
                    "Model %s should be updated, please remove 'noupdate=\"1\"' in the header of %s.",
                    model, filename,
                )
        for model in models_not_to_update:
            if (re.search('model="'+model+'"', s)
                and not re.search('<field .+model="'+model, s)
                and not re.search('<function.+model="'+model, s)
                and not s.count('<odoo noupdate="1">')
            ):
                _logger.warning(
                    "Model %s should not be updated, please add 'noupdate=\"1\"' in the header of %s.",
                    model, filename,
                )

    def _check_useless_models(self, s, filename):
        useless_models = {
            "knowledge.article.member": "Model knowledge.article.member should be replaced by write"
                " access to all users",
        }
        for model, warning in useless_models.items():
            if re.search('model="'+model, s):
                _logger.warning(warning)

    def _check_useless_fields_on_models(self, s, filename):
        useless_model_fields = {
            'account.analytic.plan': ['color'],
            'crm.lead': ['copied'],
            'crm.tag': ['color'],
            'hr.applicant': ['last_stage_id'],
            'ir.attachment': ['access_token'],
            'ir.model.fields': [
                'copied',
                'model',
            ],
            'knowledge.article': [
                'article_member_ids',
                'inherited_permission',
            ],
            'loyalty.reward': [
                'description',
                'is_global_discount',
                'program_type',
                'reward_product_ids',
                'reward_product_uom_id',
            ],
            'loyalty.rule': [
                'company_id',
                'currency_id',
                'mode',
                'program_type',
                'promo_barcode',
            ],
            'planning.role': ['color'],
            'planning.slot': [
                'access_token',
                'sale_order_id',
            ],
            'product.attribute': ['product_tmpl_ids'],
            'product.attribute.value': ['color'],
            'product.packaging': ['product_uom_id'],
            'product.pricelist.item': [
                'name',
                'price',
            ],
            'product.template.attribute.line': ['value_count'],
            'product.template.attribute.value': [
                'attribute_id',
                'color',
                'product_tmpl_id',
            ],
            'project.tags': ['color'],
            'purchase.order.line': ['name'],
            'res.partner': ['tz'],
            'sale.order': [
                'access_token',
                'amount_tax',
                'amount_to_invoice',
                'amount_total',
                'amount_untaxed',
                'currency_rate',
                'date_order',
                'health',
                'invoice_status',
                'is_subscription',
                'partner_invoice_id',
                'partner_shipping_id',
                'percentage_satisfaction',
                'recurring_monthly',
                'recurring_total',
                'state',
                'validity_date',
            ],
            'sale.order.line': [
                'invoice_status',
                'is_service',
                # 'name',  # need to handle down payments and options & templates properly
                'order_partner_id',
                'planning_hours_planned',
                'planning_hours_to_plan',
                'price_reduce_taxinc',
                'price_reduce_taxexcl',
                'price_subtotal',
                'price_tax',
                'price_total',
                'qty_delivered',
                'qty_delivered_method',
                'qty_invoiced',
                'qty_to_invoice',
                'state',
                'untaxed_amount_invoiced',
                'untaxed_amount_to_invoice',
            ],
            'sign.template': [
                'has_sign_requests',
                'is_sharing',
                'name',
                'signed_count',
            ],
            'stock.lot': ['product_uom_id'],
            'worksheet.template': ['color'],
        }
        for model, fields in useless_model_fields.items():
            if re.search('model="'+model, s):
                for field in fields:
                    if re.search('field name="'+field+'"', s):
                        _logger.warning(
                            "You shouldn't define the %s on %s (%s). Please refer to other modules for examples.",
                            field, model, filename
                        )
