# Part of Odoo. See LICENSE file for full copyright and licensing details.

import functools
import glob
import logging
import os
import re
from collections import defaultdict

from lxml import etree
from odoo.modules.module import Manifest

from .industry_case import IndustryCase, get_industry_path, get_modules

_logger = logging.getLogger(__name__)

MODELS_TO_UPDATE = {
    "base.automation",
    "ir.actions.act_window",
    "ir.actions.report",
    "ir.actions.server",
    "ir.cron",
    "ir.embedded.actions",
    "ir.model",
    "ir.access",
    "ir.model.fields",
    "ir.model.fields.selection",
    "ir.module.module",
    "ir.ui.menu",
    "ir.ui.view",
    "knowledge.article",
    "portal.entry",
    "template",
    "theme.utils",
    "website.assets",
    "website.controller.page",
}
SERVER_ACTION_MODELS = {
    "ir.actions.server",
    "ir.cron",
}
TRUE_VALUES = ('1', 'True', 'true')
# env.ref('module.xml_id')
XML_ID_REF_RE = re.compile(r"""env\.ref\(\s*['"]([a-z0-9_]+\.[a-zA-Z0-9_]+)['"]""")
# ref('xml_id') in XML evals
EVAL_REF_RE = re.compile(r"""\bref\(\s*['"]([\w.]+)['"]""")

WARNINGS = {
    'noupdate_set': (
        "%s should be updated on module upgrade (%s), "
        "please remove the 'noupdate=\"1\"' attribute tied to it in %s."
    ),
    'forcecreate_unset': (
        "%s should be restored when missing (%s), "
        "please set 'forcecreate=\"1\"' on it in %s."
    ),
    'noupdate_unset': (
        "%s should not be updated on module upgrade (%s), "
        "please add 'noupdate=\"1\"' in the header of %s, or in a data tag around it."
    ),
    'forcecreate_set': (
        "%s should not be created again once the user deleted it (%s), "
        "please set 'forcecreate=\"0\"' on it in %s."
    ),
}


def iter_data_files(modules):
    industry_path = get_industry_path()
    for module in modules:
        for directory in ('data', 'demo'):
            for file_path in sorted(glob.glob(os.path.join(industry_path, module, directory, '**', '*.xml'), recursive=True)):
                yield module, directory, os.path.relpath(file_path, industry_path), etree.parse(file_path).getroot()


def get_noupdate(node):
    # the closest noupdate attribute applies
    noupdate = next((parent.get('noupdate') for parent in node.iterancestors() if 'noupdate' in parent.attrib), None)
    return noupdate in TRUE_VALUES


def get_full_xml_id(xml_id, module):
    return xml_id if '.' in xml_id else f'{module}.{xml_id}'


def get_eval_xml_ids(node, module):
    return {
        get_full_xml_id(xml_id, module)
        for element in [node, *node.iter('value')]
        for attr in ('eval', 'search')
        for xml_id in EVAL_REF_RE.findall(element.get(attr) or '')
    }


@functools.cache
def get_data_xml_ids(module):
    manifest = Manifest.for_addon(module, display_warning=False)
    xml_ids = set()
    for file_name in manifest.get('data', []) if manifest else []:
        file_path = os.path.join(manifest.path, file_name)
        if file_name.endswith('.xml') and os.path.isfile(file_path):
            nodes = etree.parse(file_path).iter('record', 'template', 'menuitem')
            xml_ids.update(get_full_xml_id(node.get('id'), module) for node in nodes if node.get('id'))
    return xml_ids


class TestUpdatePolicy(IndustryCase):

    def test_update_policy(self):
        referenced_xml_ids, deleted_xml_ids = self._get_server_actions_references()
        for module, directory, file_name, root in iter_data_files(self.installed_modules):
            self._check_update_policy(root, file_name, module, directory, referenced_xml_ids, deleted_xml_ids)

    def _get_server_actions_references(self):
        deleted_xml_ids = {'data': set(), 'demo': set()}
        actions = []
        for module, directory, _file_name, root in iter_data_files(get_modules()):
            for function in root.xpath("//function[@name='unlink']"):
                # records of other modules are only deleted if this one is installed
                xml_ids = {xml_id for xml_id in get_eval_xml_ids(function, module) if xml_id.startswith(module + '.')}
                deleted_xml_ids['demo'] |= xml_ids
                if directory == 'data':
                    deleted_xml_ids['data'] |= xml_ids
            for record in root.iter('record'):
                if record.get('model') in SERVER_ACTION_MODELS:
                    code = ' '.join(record.xpath("field[@name='code']/text()"))
                    actions.append((get_full_xml_id(record.get('id', ''), module), directory, XML_ID_REF_RE.findall(code)))
        # an action deleted on install never runs again, as it can't come back on upgrade
        referenced_xml_ids = {
            xml_id
            for action_xml_id, directory, xml_ids in actions if action_xml_id not in deleted_xml_ids[directory]
            for xml_id in xml_ids
        }
        return referenced_xml_ids, deleted_xml_ids

    def _check_update_policy(self, root, file_name, module, directory, referenced_xml_ids, deleted_xml_ids):
        issues = defaultdict(lambda: defaultdict(list))
        for node in root.xpath("//record | //template | //function"):
            model = node.get('model') or node.tag
            record_id = node.get('id')  # functions have none, so only records and templates have a forcecreate
            xml_id = record_id and get_full_xml_id(record_id, module)
            is_defined_here = bool(xml_id) and xml_id.startswith(module + '.')
            is_referenced = is_defined_here and xml_id in referenced_xml_ids
            # what the module deletes on install, and the functions running on it, must not come back on upgrade
            targets = get_eval_xml_ids(node, module) if node.tag == 'function' else {xml_id} if xml_id else set()
            is_deleted = bool(targets) and targets <= deleted_xml_ids[directory]
            noupdate = get_noupdate(node)

            label = record_id or f'<{node.tag} model="{model}"/>'
            forcecreate = node.get('forcecreate')
            if is_referenced or (model in MODELS_TO_UPDATE and not is_deleted):
                reason = "referenced by a server action" if is_referenced else f"model {model}"
                if noupdate:
                    issues['noupdate_set'][reason].append(label)
                if record_id and forcecreate not in TRUE_VALUES:
                    issues['forcecreate_unset'][reason].append(label)
            else:
                reason = "deleted during install" if is_deleted else f"model {model}"
                if not noupdate:
                    issues['noupdate_unset'][reason].append(label)
                # forcecreate="1" is what creates another module's record when that module doesn't define it
                if record_id and forcecreate in (None, *TRUE_VALUES) and (
                    is_defined_here or xml_id in get_data_xml_ids(xml_id.split('.', 1)[0])
                ):
                    issues['forcecreate_set'][reason].append(label)

        if root.xpath("//*[@noupdate]//data[.//record | .//template | .//function]"):
            _logger.warning("Avoid setting 'noupdate' around an already existing 'data' tag in %s", file_name)
        for kind, model in sorted(issues.items()):
            for reason, records in sorted(model.items()):
                _logger.warning(WARNINGS[kind], ', '.join(records), reason, file_name)
