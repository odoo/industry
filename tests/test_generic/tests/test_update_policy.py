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
    "ir.model",
    "ir.model.fields",
    "ir.model.fields.selection",
    "ir.module.module",
    "ir.ui.menu",
    "ir.ui.view",
    "knowledge.article",
    "portal.entry",
    "template",
}

EXCLUDED_FOLDERS = ('demo', 'images', 'i18n', 'static')


def iter_data_files(modules):
    industry_path = get_industry_path()
    for module in modules:
        module_path = os.path.join(industry_path, module)
        folders = [entry.name for entry in os.scandir(module_path) if entry.is_dir() and entry.name not in EXCLUDED_FOLDERS]
        for directory in sorted(folders):
            for file_path in sorted(glob.glob(os.path.join(module_path, directory, '**', '*.xml'), recursive=True)):
                yield module, os.path.relpath(file_path, industry_path), etree.parse(file_path).getroot()


class TestUpdatePolicy(IndustryCase):

    def test_update_policy(self):
        for module, file_name, root in iter_data_files(self.installed_modules):
            self._check_update_status(root, file_name)
            self._check_forcecreate(root, file_name, module)

    def _check_update_status(self, root, filename):
        for record in root.xpath("//record") + root.xpath("//function") + root.xpath("//template"):
            model = record.get('model') or record.tag
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

    def _check_forcecreate(self, root, file_name, module):
        for record in root.xpath("//record") + root.xpath("//template"):
            record_id = record.get('id')
            # external_xmlids of other modules only need a forcecreate
            if '.' in record_id and not record_id.startswith(module + '.'):
                if not record.get('forcecreate'):
                    _logger.warning(
                        "You should use forcecreate when using an external XML ID in %s: %s",
                        file_name,
                        record_id,
                    )
                continue
            model = record.get('model') or record.tag
            forcecreate = record.get('forcecreate')
            if model in MODELS_TO_UPDATE and forcecreate is not None:
                _logger.warning(
                    "Record %s should be created again when missing, 'forcecreate' attribute is useless in %s",
                    record_id,
                    file_name,
                )
            elif model not in MODELS_TO_UPDATE and forcecreate not in ('0', 'False'):
                _logger.warning(
                    "Record %s should not be created again once deleted, please set 'forcecreate=\"0\"' on it in %s",
                    record_id,
                    file_name,
                )
