# Part of Odoo. See LICENSE file for full copyright and licensing details.

import glob
import logging
import os

from lxml import etree

from .industry_case import IndustryCase, get_industry_path

_logger = logging.getLogger(__name__)

MODELS_TO_UPDATE = {
    "base.automation",
    "ir.access",
    "ir.actions.act_window",
    "ir.actions.report",
    "ir.actions.server",
    "ir.cron",
    "ir.embedded.actions",
    "ir.model",
    "ir.model.fields",
    "ir.model.fields.selection",
    "ir.module.module",
    "ir.ui.menu",
    "ir.ui.view",
    "knowledge.article",
    "portal.entry",
    "res.groups",
    "template",
    "theme.utils",
    "website.assets",
    "website.controller.page",
}

MODELS_TO_FORCECREATE = MODELS_TO_UPDATE.union({
    "ir.default",
    "report.paperformat",
    "spreadsheet.dashboard",
    "spreadsheet.dashboard.group"
})

# records referenced in a server action, an automation or a computed field:
# they must be created again when missing, TO BE REMOVED
FORCECREATE_EXCEPTIONS = {
    "agri_equipment_rental.stock_location_18",
    "architects.crm_stage_5",
    "booking_engine.project_task_type_17",
    "booking_engine.project_task_type_18",
    "construction_developer.stock_location_worksites",
    "corporate_gifts.project_project_1",
    "corporate_gifts.project_project_2",
    "corporate_gifts.project_task_type_4",
    "corporate_gifts.project_task_type_5",
    "corporate_gifts.project_task_type_6",
    "electronic_refurbishment.account_tax_2",
    "excise_management.excises_tax_group",
    "excise_management.no_excise_tax_purchase",
    "excise_management.no_excise_tax_sale",
    "garage_auto_repair.mail_template_task_appointment_booking",
    "garage_auto_repair.project_stage_1",
    "garage_auto_repair.project_task_type_4",
    "library.stock_route_4",
    "machine_tool_rental.stock_location_18",
    "property_assets_distribution.account_analytic_plan_2",
    "real_estate.sign_item_role_9",
    "real_estate.sign_item_role_10",
    "tattoo_shop.crm_stage_7",
    "vineyard.mrp_eco_stage_9",
}

EXCLUDED_FOLDERS = ("images", "i18n", "static")


def iter_xml_files(modules):
    industry_path = get_industry_path()
    for module in modules:
        module_path = os.path.join(industry_path, module)
        folders = [entry.name for entry in os.scandir(module_path) if entry.is_dir() and entry.name not in EXCLUDED_FOLDERS]
        for directory in sorted(folders):
            for file_path in sorted(glob.glob(os.path.join(module_path, directory, "**", "*.xml"), recursive=True)):
                yield module, os.path.relpath(file_path, industry_path), etree.parse(file_path).getroot()


class TestUpdatePolicy(IndustryCase):

    def test_update_policy(self):
        for module, file_name, root in iter_xml_files(self.installed_modules):
            is_demo = file_name.split(os.sep)[1] == "demo"
            if not is_demo:
                self._check_update_status(root, file_name)
            self._check_forcecreate(root, file_name, module, is_demo)

    def _check_update_status(self, root, filename):
        for record in root.xpath("//record") + root.xpath("//function") + root.xpath("//template"):
            model = record.get("model") or record.tag
            noupdate = False
            parent = record.getparent()
            data_tag = False
            while parent is not None:  # Find nearest parent with 'noupdate' attribute (data tag or odoo header tag)
                if "noupdate" in parent.attrib:
                    if data_tag:
                        _logger.warning(
                            "Avoid setting 'noupdate' around an already existing 'data' tag in %s",
                            filename,
                        )
                    noupdate = noupdate or parent.attrib["noupdate"].strip().lower() in ("1", "true")
                if parent.tag == "data":
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

    def _check_forcecreate(self, root, file_name, module, is_demo=False):
        # records in the 'features' folder are needed for the industry to work
        in_features = file_name.split(os.sep)[1] == "features"
        for record in root.xpath("//record | //template"):
            record_id = record.get("id")
            # external_xmlids of other modules only need a forcecreate
            if "." in record_id and not record_id.startswith(module + "."):
                if not record.get("forcecreate"):
                    _logger.warning(
                        "You should use forcecreate when using an external XML ID in %s: %s",
                        file_name,
                        record_id,
                    )
                continue
            if is_demo:  # only the previous check is relevant for demo data
                continue
            if (record_id if "." in record_id else f"{module}.{record_id}") in FORCECREATE_EXCEPTIONS:
                continue
            model = record.get("model") or record.tag
            forcecreate = record.get("forcecreate")
            should_forcecreate = in_features or model in MODELS_TO_FORCECREATE
            if should_forcecreate and forcecreate is not None:
                _logger.warning(
                    "Record %s should be created again when missing, 'forcecreate' attribute is useless in %s",
                    record_id,
                    file_name,
                )
            elif not should_forcecreate and (forcecreate or "").strip().lower() not in ("0", "false"):
                _logger.warning(
                    "Record %s should not be created again once deleted, please set 'forcecreate=\"0\"' on it in %s",
                    record_id,
                    file_name,
                )
