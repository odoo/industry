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
