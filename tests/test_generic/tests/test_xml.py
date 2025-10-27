# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ast import literal_eval
import logging
import os
import pathlib
import re
from lxml import etree
from collections import defaultdict

from odoo.tests import tagged, get_db_name
from .industry_case import IndustryCase, get_industry_path

_logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 100 * 1024 * 1024  # in megabytes

EXCLUDED_READONLY_FIELDS = {'lot_id', 'url', 'user_id', 'test_type_id'}

USELESS_FIELDS = {
    'account.analytic.account': ['company_id'],
    'account.analytic.plan': ['color'],
    'crm.lead': [
        'city', 'street', 'zip', 'state_id', 'country_id', 'email', 'email_from', 'mobile', 'contact_name',
        'partner_name', 'title', 'function', 'website', 'street2', 'phone', 'company_id'
    ],
    'crm.tag': ['color'],
    'hr.applicant': ['last_stage_id'],
    'hr.employee': ['company_id'],
    'ir.attachment': ['access_token'],
    'ir.model.fields': ['model'],
    'knowledge.article': ['article_member_ids'],
    'loyalty.reward': ['description'],
    'loyalty.rule': ['promo_barcode'],
    'maintenance.request': ['maintenance_team_id', 'owner_user_id'],
    'planning.role': ['color'],
    'planning.slot': ['access_token', 'allocated_hours'],
    'pos.order': ['date_order', 'pos_reference', 'company_id', 'state', 'currency_id', 'last_order_preparation_change'],
    'pos.order.line': ['total_cost', 'company_id', 'full_product_name'],
    'product.attribute.value': ['color'],
    'product.product': ['lst_price'],
    'product.template.attribute.value': ['color'],
    'project.tags': ['color'],
    'project.task': ['company_id'],
    'purchase.order': ['currency_id', 'state'],
    'purchase.order.line': ['date_planned', 'move_dest_ids', 'company_id'],
    'res.partner': ['tz'],
    'sale.order': [
        'access_token', 'date_order', 'health', 'origin', 'partner_invoice_id', 'partner_shipping_id',
        'validity_date', 'warehouse_id', 'company_id'
    ],
    'sale.order.line': ['qty_delivered', 'company_id'],
    'sign.template': ['name'],
    'worksheet.template': ['color'],
}

MODELS_TO_UPDATE = {
    "base.automation",
    "ir.actions.act_window",
    "ir.actions.report",
    "ir.actions.server",
    "ir.cron",
    "ir.model",
    "ir.model.access",
    "ir.model.fields",
    "ir.model.fields.selection",
    "ir.module.module",
    "ir.ui.menu",
    "ir.ui.view",
    "knowledge.article",
    "theme.utils",
    "website.assets",
    "website.controller.page",
}

MODELS_WITH_USER_ID = {
    'crm.lead',
    'event.event',
    'knowledge.article.favorite',
    'project.project',
    'purchase.order',
    'sale.order',
}

ALLOWED_PYTHON_FILES = [
    '__init__.py',
    '__manifest__.py',
]

ESCAPE_STUDIO_TEST = [
    'accounting_firm',
    'construction',
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
        checked_records_with_user = {}
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
                encoded_content = pathlib.Path(file_path).read_bytes()
                decoded_content = encoded_content.decode('utf8')
                if ext == '.py':
                    if file_name not in ALLOWED_PYTHON_FILES:
                        _logger.warning(
                            "Python file %s is not allowed in industry modules.",
                            file_name,
                        )
                    elif file_name == '__manifest__.py':
                        manifest_content = decoded_content
                    continue

                if root.split('/')[-1] == 'demo' and get_db_name().endswith('imported_no_demo'):
                    continue
                try:
                    tree = etree.fromstring(encoded_content)
                except etree.XMLSyntaxError as e:
                    _logger.error("XML syntax error in file %s: %s", file_name, e)
                    return

                self._check_xml_style(decoded_content, tree, module, file_name)
                self._check_forcecreate_external_xmlid(tree, file_name, module)
                self._check_update_status(tree, file_name)
                self._check_knowledge_article_is_published(tree, file_name)
                self._check_knowledge_article_is_locked(tree, file_name)
                checked_records_with_user = self._check_user_is_set(tree, checked_records_with_user)
                self._check_duplicate_records(tree, file_name)
                self._check_website_published_false(tree, file_name)
                self._check_static_files_usage_in_xml(tree, in_use_files)
                self._check_fields(tree, file_name)
                self._check_change_theme_method(tree, file_name)
                self._check_dates_are_relative(tree, file_name)
                self._check_model_has_no_field(tree, file_name)
                self._check_static_values_in_inputs(tree, file_name)
                if root.split('/')[-1] == 'data':
                    self._check_view_active(tree, file_name)
                    self._check_is_published_false(tree, file_name)
                    if not is_studio_required:
                        is_studio_required = self._check_studio(tree, file_name)
        self._check_manifest(manifest_content, is_studio_required, escape_studio_test=module in ESCAPE_STUDIO_TEST)
        self._check_records_without_user_id(checked_records_with_user)
        if not get_db_name().endswith('imported_no_demo'):
            in_use_files = {file.lstrip('/') for file in in_use_files}
            for file in static_files - in_use_files:
                if 'description' not in file:
                    _logger.warning("Unused static file: %s.", file)
            for file in in_use_files - static_files:
                _logger.warning("No reference found for this file: %s.", file)

    def _check_static_files_usage_in_xml(self, root, in_use_files):
        for element in root.iter():
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

    def _check_manifest(self, s, need_studio, escape_studio_test):
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

        if escape_studio_test:
            # Exception for some edge cases with studio, checking by hand
            return

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

    def _check_studio(self, root, file_name):
        MODELS_FOR_STUDIO = [
            "ir.actions.act_window",
            "ir.actions.server",
            "ir.model",
            "ir.model.fields",
        ]
        for model in MODELS_FOR_STUDIO:
            if root.xpath(f"//record[@model='{model}']"):
                _logger.info("%s found in %s, needs studio", model, file_name)
                return True

        for record in root.xpath("//record[@model='ir.ui.view']"):
            website_id_field = record.xpath(".//field[@name='website_id']")
            if not website_id_field:
                _logger.info("ir.ui.view found in %s, needs studio", file_name)
                return True
        return False

    def _check_xml_style(self, s, root, module, file_name):
        STARTS_WITH = [
            "<?xml version='1.0' encoding='UTF-8'?>",
            "<?xml version='1.0' encoding=\"UTF-8\"?>",
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
            "<?xml version=\"1.0\" encoding='UTF-8'?>",
            "<?xml version=\"1.0\" encoding=\"utf-8\"?>",
        ]
        first_line = s.split('\n')[0]
        if not any(first_line == start_line for start_line in STARTS_WITH):
            _logger.warning(
                "XML files should begin with the following line: %s, but %s starts with %s",
                STARTS_WITH[0],
                file_name,
                first_line,
            )

        elements = [
            value for element in root.iter() for attr in ['id', 'ref', 'src', 'data-original-src', 'name']
            if (value := element.get(attr)) and value.startswith(module + '.')
        ]
        if elements:
            _logger.warning(
                "Defining or referring to an xmlid with the current module name is useless, module name will be added automatically. "
                "Found occurence(s) of ' id=\"%s.ID' in %s: %s. "
                "This remark does not apply to 'env.ref(\"%s.ID\")' where it is required.",
                module, file_name, ', '.join(elements), module
            )
        elements = [value for element in root.iter() if (value := element.get('id')) and value.startswith('x_studio')]
        if elements:
            _logger.warning("Please remove 'studio' from 'x_studio' in %s.", ', '.join(elements))

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

    def _check_update_status(self, root, filename):
        for record in root.xpath("//record") + root.xpath("//function"):
            model = record.get('model')
            noupdate = False
            parent = record.getparent()
            data_tag = False
            while parent is not None:  # Find nearest parent with 'noupdate' attribute (data tag or odoo header tag)
                if 'noupdate' in parent.attrib:
                    if data_tag:
                        _logger.warning(
                            "Avoid setting 'noupdate' around an already existing 'data' tag in %s",
                            filename,
                        )
                    noupdate = noupdate or parent.attrib['noupdate'] in ('1', 'True', 'true')
                if parent.tag == 'data':
                    data_tag = True
                parent = parent.getparent()

            if model not in MODELS_TO_UPDATE and not noupdate:
                _logger.warning(
                    "Model %s should not be updated, please add 'noupdate=\"1\"' in the header of %s, or in a data tag around it.",
                    model,
                    filename,
                )
            elif model in MODELS_TO_UPDATE and noupdate:
                _logger.warning(
                    "Model %s should be updated, please remove 'noupdate=\"1\"' attribute tied to it in %s",
                    model,
                    filename,
                )

    def _check_knowledge_article_is_published(self, root, file_name):
        for record in root.xpath("//record[@model='knowledge.article']"):
            is_published_fields = record.xpath(".//field[@name='is_published' and @eval='True']")
            if is_published_fields:
                _logger.warning(
                    f"Knowledge article in {file_name} should not have 'is_published' set to True."
                )

    def _check_knowledge_article_is_locked(self, root, file_name):
        for record in root.xpath("//record[@model='knowledge.article']"):
            is_locked_fields = record.xpath(".//field[@name='is_locked']/@eval")
            if not is_locked_fields:
                _logger.warning(
                    f"Knowledge article in {file_name} should have 'is_locked' set to True."
                )

    def _check_is_published_false(self, root, file_name):
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

    def _check_website_published_false(self, root, file_name):
        for record in root.xpath("//record"):
            model = record.get('model')
            if model == 'website.controller.page':
                continue
            website_published_fields = record.xpath(".//field[@name='website_published' and @eval='True']")
            if website_published_fields:
                _logger.warning(
                    f"Model in {file_name} should not have 'website_published' set to True, 'is_published' is preferred in demo only."
                )

    def _check_duplicate_records(self, root, file_name):
        records = defaultdict(set)
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

    def _check_fields(self, root, file_name):
        warned_records = set()
        for record in root.xpath("//record"):
            model_name = record.get('model')
            if not model_name:
                continue
            model = self.env.get(model_name)
            if model_name == "ir.model.fields":
                for ttype_element in record.xpath(".//field[@name='ttype'][text()='selection']"):
                    record_id = record.get('id')
                    if record_id in warned_records:
                        continue
                    if ttype_element.getparent().xpath(".//field[@name='selection']"):
                        _logger.warning(
                            "Inline selection values defined in %s. "
                            "Remove inline 'selection' field and define values in ir.model.fields.selection.",
                            record_id
                        )
                        warned_records.add(record_id)
            fields_set_in_record = {
                field.get('name') for field in record.xpath('.//field')
                if field.getparent().get('id', False) == record.get('id')  # nested record definitions
            }
            for field_name in fields_set_in_record:
                field = model._fields.get(field_name)
                useless = USELESS_FIELDS.get(model_name, [])
                if field_name in useless:
                    if field_name == 'company_id' and self.env['res.company'].search_count([]) > 1:
                        continue  # company_id only matters in a multi-company setup
                    if 'crm.lead' in self.env and model == self.env['crm.lead']:
                        if 'partner_id' in fields_set_in_record:
                            _logger.warning(
                                "Field '%s' in model 'crm.lead' is useless if a partner_id is set (file: %s). ",
                                field_name,
                                file_name,
                            )
                        continue
                    else:
                        _logger.warning(
                            "Field '%s' in model '%s' is useless and should not be set in XML data (file: %s). ",
                            field_name,
                            model_name,
                            file_name,
                        )
                        continue
                if field and field.compute and field.readonly and field_name not in EXCLUDED_READONLY_FIELDS:
                    _logger.warning(
                        "Field '%s' in model '%s' is a readonly computed field without inverse and should not be set "
                        "directly in XML data (file: %s). If you think this field should be maintained, please edit "
                        "the EXCLUDED_READONLY_FIELDS list in tests/test_generic/tests/test_xml.py",
                        field_name,
                        model_name,
                        file_name,
                    )
                    continue
                if field and field.related and field.readonly:
                    _logger.warning(
                        "Field '%s' in model '%s' is a readonly related field and should not be set directly in XML data (file: %s).",
                        field_name,
                        model_name,
                        file_name,
                    )
                    continue
                if not field and model_name != 'ir.ui.view':
                    _logger.warning("Field %s not defined for model %s", field_name, model_name)

    def _check_view_active(self, root, file_name):
        for record in root.xpath("//record[@model='ir.ui.view']"):
            active_field = record.xpath(".//field[@name='active']/@eval")
            if not active_field or active_field[0] != "True":
                _logger.warning(
                    "You forgot to enforce active=True on ir.ui.view record (id=%s in data/%s).",
                    record.get('id'),
                    file_name,
                )

    def _check_model_has_no_field(self, root, file_name):
        for record in root.xpath("//record[@model='ir.model']"):
            active_field = record.xpath(".//field[@name='field_id']/@eval")
            if not active_field or active_field[0] != "[Command.clear()]":
                _logger.warning("You forgot to empty fields of ir.model record (id=%s in data/%s).", record.get('id'), file_name,)

    def _check_user_is_set(self, root, previous_records):
        records = previous_records
        for model in MODELS_WITH_USER_ID:
            for record in root.xpath(f"//record[@model='{model}']"):
                record_id = record.get('id')
                user_field = record.xpath(".//field[@name='user_id']")
                records[record_id] = records.get(record_id) or bool(user_field)
        return records

    def _check_records_without_user_id(self, records):
        for record, has_user in records.items():
            if not has_user:
                _logger.warning("You forgot to assign user_id(s) to the record with id=%s.", record)

    def _check_change_theme_method(self, root, file_name):
        for record in root.xpath("//function[@name='button_immediate_install' and @model='ir.module.module']"):
            if 'theme' in record.get('eval', ''):
                _logger.warning(
                    "You should use button_choose_theme instead of button_immediate_install in %s.",
                    file_name,
                )
        if root.xpath("//function[@name='_theme_load' and @model='ir.module.module']"):
            _logger.warning(
                "You should use button_choose_theme instead of _theme_load in %s.",
                file_name,
            )

    def _check_forcecreate_external_xmlid(self, root, file_name, module):
        for record in root.xpath("//record"):
            record_id = record.get('id')
            if '.' in record_id and not record_id.startswith(module + '.'):
                if not record.get('forcecreate'):
                    _logger.warning(
                        "You should use forcecreate when using an external XML ID in %s: %s",
                        file_name,
                        record_id,
                    )

    def _check_dates_are_relative(self, root, file_name):
        RELATIVE_DATES = [
            'Time.',
            'time.',
            'time(',
        ]
        for record in root.xpath("//record"):
            model_name = record.get('model')
            if not model_name:
                continue
            model = self.env.get(model_name)
            fields_set_in_record = {
                field for field in record.xpath('.//field')
                if field.getparent().get('id', False) == record.get('id')  # nested record definitions
            }
            for field in fields_set_in_record:
                field_name = field.get('name')
                field_type = model._fields.get(field_name).type
                if field_type not in ('date', 'datetime'):
                    continue
                field_eval = field.get('eval')
                if not field_eval or not any(date in field_eval for date in RELATIVE_DATES):
                    _logger.warning(
                        "Date field '%s' in model '%s' is hard coded (file: %s). ",
                        field_name,
                        model_name,
                        file_name,
                    )

    def _check_static_values_in_inputs(self, root, file_name):
        ALLOWED_INPUTS = {"resourceCapacity"}
        for tag in root.xpath("//input[@value] | //option[@value]"):
            value = tag.get("value")
            if not (value and value.isdigit()):
                continue
            if tag.get("t-att-value"):
                continue
            name = tag.get("name")
            if name in ALLOWED_INPUTS:
                continue

            line = getattr(tag, "sourceline", "?")
            _logger.warning(
                "Static value '%s' found in <%s name='%s'> in %s (line %s). "
                "Please use t-att-value=\"request.env.ref('module.record').id\" instead.",
                value,
                tag.tag,
                name or tag.get("id") or "",
                file_name,
                line,
            )

        for tag in root.xpath("//a[@href]"):
            href = tag.get("href")
            if tag.get("t-att-href") or tag.get("t-attf-href"):
                continue
            if href and (href.startswith(("tel:", "mailto:", "javascript:", "#", "http://", "https://"))):
                continue
            if href and re.search(r"-\d+$", href):
                line = getattr(tag, "sourceline", "?")
                _logger.warning(
                    "Static record link '%s' found in <a> in %s (line %s). "
                    "Please use t-att-href=\"request.env.ref('module.record').website_url\" instead.",
                    href,
                    file_name,
                    line,
                )
