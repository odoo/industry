# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging, os
from odoo.modules.module import get_module_path
from odoo.tests.common import tagged

from .industry_case import IndustryCase

_logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 100 * 1024 * 1024  # in megabytes


@tagged('post_install', '-at_install')
class TestEnv(IndustryCase):

    def test_dummy(self):
        for module in self.installed_modules:
            self._check_files_in_path(module)

    def _check_files_in_path(self, module):
        path = get_module_path(module).rstrip('/')
        for root, dirs, files in os.walk(path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                ext = os.path.splitext(file_path)[1].lower()
                if ext != '.xml':
                    continue
                if os.path.getsize(file_path) > MAX_FILE_SIZE:
                    raise "Max file size exceeded"
                with open(file_path, 'rb') as f:
                    content = f.read().decode('utf8')
                self._check_xml(content, module, file_name)

    def _check_xml(self, s, module, file_name):
        s = s.strip()
        starts_with = "<?xml version='1.0' encoding='UTF-8'?>"
        first_line = s.split('\n')[0]
        if first_line != starts_with:
            _logger.warning(
                "XML files should begin with the following line: %s, but %s starts with %s",
                starts_with, file_name, first_line
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
