# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ast import literal_eval
import logging
import os
import pathlib
import re
from lxml import etree
from collections import defaultdict

from odoo.tests.common import tagged
from .industry_case import IndustryCase, get_industry_path

_logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 100 * 1024 * 1024  # in megabytes
FIELDS_NOT_TO_SET_DIRECTLY = {
    'crm.lead': [
        'city', 'street', 'zip', 'state_id', 'country_id', 'email', 'email_from',
        'mobile', 'contact_name', 'partner_name', 'title', 'function',
        'website', 'street2', 'company_name', 'phone',
    ],
    'sale.order': [
        'amount_untaxed', 'amount_tax', 'amount_total', 'amount_discount',
        'pricelist_id', 'currency_id', 'partner_invoice_id', 'partner_shipping_id',
        'invoice_status',
    ],
    'sale.order.line': [
        'price_subtotal', 'price_total', 'price_tax', 'currency_id',
        'price_reduce', 'price_reduce_taxinc', 'price_reduce_taxexcl',
        'state', 'order_partner_id',
    ],
    'purchase.order': [
        'amount_untaxed', 'amount_tax', 'amount_total', 'currency_id',
        'invoice_status',
    ],
    'purchase.order.line': [
        'price_subtotal', 'price_total', 'price_tax', 'currency_id',
        'date_planned', 'state', 'move_dest_ids',
    ],
    'stock.picking': [
        'state', 'origin', 'location_id', 'location_dest_id',
        'move_line_ids', 'move_ids_without_package', 'scheduled_date',
        'date_done', 'picking_type_id', 'partner_id',
    ],
    'stock.move': [
        'state', 'product_qty', 'quantity_done', 'reserved_availability',
        'product_uom_qty', 'price_unit', 'location_id', 'location_dest_id',
        'date_expected', 'picking_id',
    ],
    'account.move': [
        'amount_untaxed', 'amount_tax', 'amount_total', 'amount_residual',
        'state', 'partner_bank_id', 'payment_state', 'currency_id',
        'amount_total_signed', 'amount_untaxed_signed', 'amount_residual_signed',
        'date', 'journal_id', 'invoice_date', 'invoice_date_due',
    ],
    'account.move.line': [
        'balance', 'debit', 'credit', 'amount_currency', 'currency_id',
        'amount_residual', 'amount_residual_currency', 'account_id', 'date_maturity',
        'partner_id',
    ],
    'product.template': [
        'qty_available', 'virtual_available',
        'incoming_qty', 'outgoing_qty', #standard_price should be also, too much refactoring
    ],
    'product.product': [
        'qty_available', 'virtual_available',
        'incoming_qty', 'outgoing_qty','lst_price', #standard_price should be also, too much refactoring
    ],
    'account.invoice': [
        'amount_untaxed', 'amount_tax', 'amount_total', 'residual', 'state',
        'currency_id', 'partner_id',
    ],
    'mrp.production': [
        'state', 'date_planned_start', 'date_planned_finished', 'product_qty',
        'qty_produced', 'availability', 'reserved_availability',
    ],
    'project.task': [
        'user_id', 'planned_hours', 'remaining_hours', 'total_hours_spent', 'progress',
    ],
    'account.payment': [
        'state', 'amount', 'currency_id', 'payment_date', 'payment_type',
        'partner_id', 'partner_type', 'journal_id', 'payment_method_id',
    ],
    'maintenance.request': [
        'request_date', 'schedule_date', 'close_date',
        'technician_user_id', 'maintenance_team_id',
    ],
    'helpdesk.ticket': [
        'email', 'phone', 'user_id',
        'priority', 'category_id', 'sla_id',
    ],
    'calendar.event': [
        'allday', 'duration',
        'privacy', 'show_as', 'event_type_id',
    ],
    'sale.subscription': [
        'partner_id', 'pricelist_id', 'recurring_total', 'state',
        'date_start', 'date_end', 'template_id', 'user_id', 'company_id',
        'recurring_invoice_line_ids', 'invoice_ids',
    ],
    'pos.order': [
        'date_order', 'tracking_number', 'pos_reference', 'company_id', 'state',
        'pricelist_id', 'currency_id', 'picking_count', 'failed_pickings',
        'is_total_cost_computed', 'date_order', 'currency_rate', 'margin_percent'
        'has_refundable_lines', 'country_code', 'pos_reference', 'margin', 
        'last_order_preparation_change', 
    ],
    'pos.order.line': [
        'price_unit', 'total_cost', 'is_total_cost_computed',
        'company_id', 'margin_percent', 'margin',
        'full_product_name', 'product_uom_id', ''
    ],
}
EXCLUDED_READONLY_FIELDS = {
    'lot_id',
}
USELESS_FIELDS = {
    'account.analytic.plan': ['color'],
    'account.analytic.account': ['root_plan_id'],
    'appointment.type': [
        'has_message',
        'resource_total_capacity',
    ],  
    'base.automation': ['last_run'],
    'crm.lead': ['copied'],
    'crm.tag': ['color'],
    'hr.applicant': ['last_stage_id'],
    'ir.attachment': ['access_token'],
    'ir.model.fields': [
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
        'valid_product_ids',
    ],
    'mrp.bom.byproduct': [
        'company_id',
        'product_uom_category_id',
    ],
    'planning.role': ['color'],
    'planning.slot': [
        'access_token',
        'allocated_hours',
        'department_id',
        'sale_order_id',
        'work_address_id',
        'working_days_count',
    ],
    'product.attribute': ['product_tmpl_ids'],
    'product.attribute.value': ['color'],
    'product.packaging': ['product_uom_id'],
    'product.pricelist.item': [
        'name',
        'price',
    ],
    'product.template': [
        'can_image_1024_be_zoomed',
        'has_configurable_attributes',
    ],
    'product.template.attribute.line': ['value_count'],
    'product.template.attribute.value': [
        'attribute_id',
        'color',
        'product_tmpl_id',
    ],
    'project.tags': ['color'],
    'project.task': [
        'working_days_close',
        'working_hours_close',
    ],
    'purchase.order': [
        'receipt_status',
        'state',
    ],
    'purchase.order.line': [
        'date_order',
        'name',
        'state',
    ],
    'res.partner': [
        'commercial_company_name',
        'tz',
    ],
    'sale.order': [
        'access_token',
        'amount_tax',
        'amount_to_invoice',
        'amount_total',
        'amount_untaxed',
        'currency_id',
        'currency_rate',
        'date_order',
        'delivery_status',
        'health',
        'invoice_status',
        'is_subscription',
        'origin',
        'partner_invoice_id',
        'partner_shipping_id',
        'percentage_satisfaction',
        'recurring_monthly',
        'recurring_total',
        'state',
        'validity_date',
        'warehouse_id',
    ],
    'sale.order.line': [
        'currency_id',
        'invoice_status',
        'is_service',
        #  # need to handle down payments and options & templates properly
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
    # 'sale.order.template.line': ['name'],  # check as could be meaningful and different
    'sign.template': [
        'has_sign_requests',
        'is_sharing',
        'name',
        'signed_count',
    ],
    'stock.lot': ['product_uom_id'],
    'worksheet.template': ['color'],
}
MODELS_TO_UPDATE = [
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
MODELS_NOT_TO_UPDATE = [
    "account.analytic.account",
    "account.analytic.plan",
    "account.cash.rounding",
    "appointment.resource",
    "appointment.type",
    "calendar.event",
    "crm.lead",
    "crm.stage",
    "crm.tag",
    "document.document",
    "document.folder",
    "event.event.ticket",
    "helpdesk.ticket",
    "hr.applicant",
    "hr.department",
    "hr.employee",
    "hr.job",
    "hr.recruitment.stage",
    "ir.attachment",
    "ir.default",
    "ir.rule",
    "knowledge.article.favorite",
    "knowledge.attachment",
    "knowledge.cover",
    "loyalty.program",
    "loyalty.reward",
    "loyalty.rule",
    "mail.template",
    "maintenance.equipment",
    "mrp.bom",
    "mrp.bom.line",
    "mrp.production",
    "mrp.routing.workcenter",
    "mrp.workcenter",
    "pos.category",
    "pos.config",
    "pos.order",
    "pos.order.line",
    "pos.payment.method",
    "pos.session",
    "pos_preparation_display.display",
    "pos_preparation_display.order",
    "pos_preparation_display.orderline",
    "product.attribute",
    "product.attribute.value",
    "product.category",
    "product.packaging",
    "product.pricelist",
    "product.pricelist.item",
    "product.product",
    "product.public.category",
    "product.supplierinfo",
    "product.template",
    "product.template.attribute.line",
    "product.template.attribute.value",
    "project.project",
    "project.task",
    "project.task.type",
    "purchase.order",
    # "purchase.order.line",  # need to handle in functions
    "planning.recurrency",
    "planning.role",
    "planning.slot",
    "quality.point",
    "repair.order",
    "res.config.settings",
    "res.partner",
    "restaurant.floor",
    "restaurant.table",
    "sale.order",
    "sale.order.line",
    "sale.order.template",
    "sale.order.template.line",
    "sign.item",
    "sign.request",
    "sign.template",
    # "stock.lot",  # need to handle in functions
    "stock.quant",
    "stock.warehouse.orderpoint",
    "uom.category",
    "uom.uom",
    "website",
    "website.base.unit",
    "website.menu",
    "website.page",
]
@tagged('post_install', '-at_install')
class TestEnv(IndustryCase):

    def test_xml_files(self):
        for module in self.installed_modules:
            self._check_files_in_path(module)

    def _check_files_in_path(self, module):
        path = get_industry_path() + module
        is_studio_required = False
        static_files = set()
        in_use_files = set()
        for root, dirs, files in os.walk(path):
            # sort the directory by alphabetical order so static directory is read first.
            dirs.sort(reverse=True)
            for file_name in files:
                file_path = os.path.join(root, file_name)
                ext = os.path.splitext(file_path)[1].lower()
                if 'static/' in file_path and 'src/js/' not in file_path:
                    static_files.add(os.path.relpath(file_path, start=get_industry_path()))
                if ext not in ['.py', '.xml']:
                    continue
                if os.path.getsize(file_path) > MAX_FILE_SIZE:
                    raise "Max file size exceeded"
                content = pathlib.Path(file_path).read_bytes().decode('utf8')
                if ext == '.py':
                    if file_name != '__manifest__.py':
                        _logger.warning(
                            "No python file is allowed in an industry module, except __manifest__.py."
                            " Please remove %s.",
                            file_name,
                        )
                    else:
                        manifest_content = content
                    continue

                self._check_xml_style(content, module, file_name)
                self._check_update_status(content, file_name)
                self._check_useless_models(content, file_name)
                self._check_knowledge_article_is_published(content, file_name)
                self._check_duplicate_records(content, file_name)
                self._check_website_published_false(content, file_name)
                self._check_static_files_usage_in_xml(content, in_use_files)
                self._check_fields(content, file_name)
                if root.split('/')[-1] == 'data':
                    self._check_view_active(content, file_name)
                    self._check_is_published_false(content, file_name)
                    if not is_studio_required:
                        is_studio_required = self._check_studio(content, file_name)
        self._check_manifest(manifest_content, is_studio_required)
        in_use_files = {file.lstrip('/') for file in in_use_files}
        for file in static_files - in_use_files:
            if 'description' not in file:
                _logger.warning("Unused static file: %s.", file)
        for file in in_use_files - static_files:
            _logger.warning("No reference found for this file: %s.", file)

    def _check_static_files_usage_in_xml(self, content, in_use_files):
        tree = etree.fromstring(content.encode('utf8'))
        for element in tree.iter():
            file_names = {element.attrib.get(key) for key in ['file', 'src', 'data-original-src']}
            if element.text:
                if element.get("name") == "cover_properties":
                    file_names.update(re.findall(r"url\(['\"]?([^'\")]+)['\"]?\)", element.text))
                file_names.update(re.findall(r'src="([^"]+)"', element.text))
            in_use_files.update(
                {
                    file
                    for file in file_names
                    if file and not file.startswith(('web', '/web', 'https', '/unsplash'))
                }
            )

    def _check_manifest(self, s, need_studio):
        if (first_line := s.split('\n')[0]) != '{':
            message = "First line of the manifest should be the sole symbol '{'. "
            if not first_line:
                message += "No need for an empty line."
            elif "coding" in first_line:
                message += "No need to specify the encoding since python3."
            else:
                message += "Got '%s'." % first_line
            _logger.warning(message)
        dependency_list = literal_eval(s)['depends']
        if 'payment_demo' in dependency_list:
            _logger.warning(
                "'payment_demo' should not be in the dependencies. Instead, call "
                "'button_immediate_install' on 'base.module_payment_demo' in demo."
            )
        base_automation = (
            'base_automation' in dependency_list and 'sale_subscription' not in dependency_list
        )
        studio_required = need_studio or base_automation
        studio_dependency = any(
            studio in dependency_list for studio in ['web_studio', 'website_studio']
        )
        if studio_required and not studio_dependency:
            _logger.warning("'web_studio' is missing in the dependencies.")
        elif not studio_required and studio_dependency:
            _logger.warning("'web_studio' should not be in the dependencies.")

    def _check_studio(self, xml_content, file_name):
        try:
            root = etree.fromstring(xml_content.encode('utf-8'))
        except etree.XMLSyntaxError as e:
            _logger.error("XML syntax error in file %s: %s", file_name, e)
            return False

        models_for_studio = [
            "ir.actions.act_window",
            "ir.actions.server",
            "ir.model",
            "ir.model.fields",
            "ir.ui.menu",
        ]
        for model in models_for_studio:
            # Find records with model=model
            records = root.xpath(f"//record[@model='{model}']")
            # Exclude records where model=model is inside field or function elements
            field_models = root.xpath(f"//field[@model='{model}']")
            function_models = root.xpath(f"//function[@model='{model}']")
            if records and not field_models and not function_models:
                _logger.info("%s found in %s, needs studio", model, file_name)
                return True

        for record in root.xpath("//record[@model='ir.ui.view']"):
            website_id_field = record.xpath(".//field[@name='website_id']")
            if not website_id_field:
                return True
        return False

    def _check_xml_style(self, s, module, file_name):
        starts_with = [
            "<?xml version='1.0' encoding='UTF-8'?>",
            "<?xml version='1.0' encoding=\"UTF-8\"?>",
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
            "<?xml version=\"1.0\" encoding='UTF-8'?>",
            "<?xml version=\"1.0\" encoding=\"utf-8\"?>",
        ]
        first_line = s.split('\n')[0]
        if not any(first_line == start_line for start_line in starts_with):
            _logger.warning(
                "XML files should begin with the following line: %s, but %s starts with %s",
                starts_with[0],
                file_name,
                first_line,
            )

        try:
            root = etree.fromstring(s.encode('utf-8'))
        except etree.XMLSyntaxError as e:
            _logger.error("XML syntax error in file %s: %s", file_name, e)
            return

        count = 0
        for element in root.iter():
            element_id = element.get('id')
            if element_id and element_id.startswith(module + '.'):
                count += 1

        if count:
            _logger.warning(
                "Defining an xmlid with the current module name is useless, module name will be "
                "added automatically. Found %d occurence(s) of ' id=\"%s.ID' in %s.",
                count,
                module,
                file_name,
            )

        count = 0
        for element in root.iter():
            for attr in ['ref', 'src', 'data-original-src']:
                ref_value = element.get(attr)
                if ref_value and ref_value.startswith(module + '.'):
                    count += 1
        if count:
            _logger.warning(
                "Referring to an xmlid created within the current module name is useless. If none is"
                " provided, it will check in current module. Found %d occurence(s) of ref=\"%s.ID\""
                " in %s.",
                count,
                module,
                file_name,
            )

        useless_attributes = [
            "context.get('studio')",
            "data-last-history-steps",
            "context=\"{'studio'",
        ]
        for attr in useless_attributes:
            if attr in s:
                _logger.warning("Please remove '%s' in %s.", attr, file_name)

        end_of_file = repr(s).split('\\')
        if 'n' not in end_of_file[-1] or len(end_of_file[-1]) > 2:
            _logger.warning(
                "It looks like you forgot to add an empty line at the end of %s.", file_name
            )
        elif 'n' in end_of_file[-2] and len(end_of_file[-2]) <= 2:
            _logger.warning(
                "One empty line at the end of %s is enough, please remove others.", file_name
            )

    def _check_update_status(self, xml_content, filename):
        try:
            root = etree.fromstring(xml_content.encode('utf-8'))
        except etree.XMLSyntaxError as e:
            _logger.error("XML syntax error in file %s: %s", filename, e)
            return

        noupdate = root.get('noupdate', '0') in ('1', 'True', 'true')

        for model in MODELS_TO_UPDATE:
            records = root.xpath(f"//record[@model='{model}']")
            field_models = root.xpath(f"//field[@model='{model}']")
            function_models = root.xpath(f"//function[@model='{model}']")
            if records and not field_models and not function_models and noupdate:
                _logger.warning(
                    "Model %s should be updated, please remove 'noupdate=\"1\"' in the header of %s.",
                    model,
                    filename,
                )
        for model in MODELS_NOT_TO_UPDATE:
            records = root.xpath(f"//record[@model='{model}']")
            field_models = root.xpath(f"//field[@model='{model}']")
            function_models = root.xpath(f"//function[@model='{model}']")
            if records and not field_models and not function_models and not noupdate:
                _logger.warning(
                    "Model %s should not be updated, please add 'noupdate=\"1\"' in the header of %s.",
                    model,
                    filename,
                )

    def _check_useless_models(self, xml_content, filename):
        try:
            root = etree.fromstring(xml_content.encode('utf-8'))
        except etree.XMLSyntaxError as e:
            _logger.error("XML syntax error in file %s: %s", filename, e)
            return

        useless_models = {
            "knowledge.article.member": "Model knowledge.article.member should be replaced by write"
            " access to all users",
        }
        for model, warning in useless_models.items():
            records = root.xpath(f"//record[@model='{model}']")
            if records:
                _logger.warning(warning)

    def _check_knowledge_article_is_published(self, xml_content, file_name):
        try:
            root = etree.fromstring(xml_content.encode('utf-8'))
        except etree.XMLSyntaxError as e:
            _logger.error("XML syntax error in file %s: %s", file_name, e)
            return

        for record in root.xpath("//record[@model='knowledge.article']"):
            is_published_fields = record.xpath(".//field[@name='is_published' and @eval='True']")
            if is_published_fields:
                _logger.warning(
                    f"Knowledge article in {file_name} should not have 'is_published' set to True."
                )

    def _check_is_published_false(self, xml_content, file_name):
        try:
            root = etree.fromstring(xml_content.encode('utf-8'))
        except etree.XMLSyntaxError as e:
            _logger.error("XML syntax error in file %s: %s", file_name, e)
            return
        for record in root.xpath("//record"):
            model = record.get('model')
            if model == 'website.page':
                continue
            is_published_field = record.xpath(".//field[@name='is_published']/@eval")
            if is_published_field and is_published_field[0] == "True":
                _logger.warning(
                    "Model in %s should not have 'is_published' set to True in data.",
                    file_name,
                )

    def _check_website_published_false(self, xml_content, file_name):
        try:
            root = etree.fromstring(xml_content.encode('utf-8'))
        except etree.XMLSyntaxError as e:
            _logger.error("XML syntax error in file %s: %s", file_name, e)
            return

        for record in root.xpath("//record"):
            model = record.get('model')
            if model == 'website.controller.page':
                continue
            website_published_fields = record.xpath(".//field[@name='website_published' and @eval='True']")
            if website_published_fields:
                _logger.warning(
                    f"Model in {file_name} should not have 'website_published' set to True, 'is_published' is preferred in demo only."
                )

    def _check_duplicate_records(self, xml_content, file_name):
        records = defaultdict(set)
        xml_content = xml_content.encode('utf-8')

        try:
            root = etree.fromstring(xml_content)
            for record in root.xpath("//record"):
                record_id = record.get("id")
                model = record.get("model")
                fields_list = [
                    (
                        field.get("name"),
                        field.getparent().get('id', field.getparent().tag),
                        field.get("position", None),
                        (
                            field.xpath("ancestor::page[1]")[0].get("name")
                            if field.xpath("ancestor::page[1]")
                            else None
                        ),
                    )
                    for field in record.xpath(".//field")
                ]
                fields = frozenset(fields_list)
                if len(fields_list) != len(fields):
                    _logger.warning(
                        f"Duplicate field updates in record {record_id} of model {model} in {file_name}: {', '.join(field[0] for field in fields if fields_list.count(field) > 1)}"
                    )
                record_key = (record_id, model)
                if fields & records[record_key]:
                    _logger.warning(
                        f"Duplicate record updates in {file_name}: {record_id} in model {model}"
                    )
                records[record_key] |= fields
        except etree.XMLSyntaxError as e:
            _logger.error("XML syntax error in file %s: %s", file_name, e)

    def _check_view_active(self, xml_content, file_name):
        try:
            root = etree.fromstring(xml_content.encode('utf-8'))
        except etree.XMLSyntaxError as e:
            _logger.error("XML syntax error in file %s: %s", file_name, e)
            return
        for record in root.xpath("//record[@model='ir.ui.view']"):
            active_field = record.xpath(".//field[@name='active']/@eval")
            if not active_field or active_field[0] != "True":
                _logger.warning(
                    "You forgot to enforce active=True on ir.ui.view record (id=%s in data/%s).",
                    record.get('id'),
                    file_name,
                )
    def _check_fields(self, xml_content, file_name):
        try:
            root = etree.fromstring(xml_content.encode('utf-8'))
        except etree.XMLSyntaxError as e:
            _logger.error("XML syntax error in file %s: %s", file_name, e)
            return
        for record in root.xpath("//record"):
            model_name = record.get('model')
            if not model_name:
                continue
            model = self.env.get(model_name)
            fields_set_in_record = set(field.get('name') for field in record.xpath('.//field'))
            fields_not_to_set = FIELDS_NOT_TO_SET_DIRECTLY.get(model_name, [])
            fields_useless = USELESS_FIELDS.get(model_name, [])
            for field_name in fields_set_in_record:
                field = model._fields.get(field_name)
                if 'x_' in field_name :
                    continue
                if field_name in fields_not_to_set :
                    _logger.warning(
                        "Field '%s' in model '%s' should not be set directly in XML data (file: %s). "
                        "It is a computed field dependent on a related model."
                        "Set the corresponding field on the related model instead.",
                        field_name,
                        model_name,
                        file_name,
                    )        
                if field_name in fields_useless:
                    _logger.warning(
                        "Field '%s' in model '%s' is useless and should not be set in XML data (file: %s). ",
                        field_name,
                        model_name,
                        file_name,
                    )                       
                if field and field.compute and field.readonly and field_name not in EXCLUDED_READONLY_FIELDS:
                    _logger.warning(
                        "Field '%s' in model '%s' is a readonly computed field without inverse and should not be set directly in XML data (file: %s).",
                        field_name,
                        model_name,
                        file_name,
                    )