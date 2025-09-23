# Part of Odoo. See LICENSE file for full copyright and licensing details.

import os

from odoo.tests.common import tagged

from .industry_case import IndustryCase, get_industry_path


@tagged('post_install', '-at_install')
class FileTest(IndustryCase):

    def test_required_files(self):
        for module in self.installed_modules:
            required_files = {
                'icon': '/static/description/icon.png',
                'image': '/images/main.png',
                'init': '/__init__.py',
            }
            for f, path in required_files.items():
                is_file = os.path.isfile(get_industry_path() + module + path)
                self.assertTrue(is_file, "Missing %s at %s" % (f, module + path))
