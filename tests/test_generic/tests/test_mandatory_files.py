# Part of Odoo. See LICENSE file for full copyright and licensing details.

import os
from pathlib import Path
import re

from odoo import release
from odoo.tests.common import tagged

from .industry_case import IndustryCase, get_industry_path


@tagged('post_install', '-at_install')
class FileTest(IndustryCase):

    def test_required_files(self):
        for module in self.installed_modules:
            required_files = {
                'icon': '/static/description/icon.png',
                'image': '/images/main.png',
                'pot file': f'/i18n/{module}.pot',
            }
            for f, path in required_files.items():
                is_file = os.path.isfile(get_industry_path() + module + path)
                self.assertTrue(is_file, "Missing %s at %s" % (f, module + path))

            tx_config = Path(get_industry_path() + '.tx/config').read_text(encoding="utf-8")
            self.assertTrue(re.search(module, tx_config), "Missing module in .tx/config")
            if release.version_info[3] != 'final':
                # skip test if master
                continue
            odoo_version = release.serie
            if odoo_version.split('.')[1] != '0':
                odoo_version = odoo_version.replace('.', '-').split('~')[-1]
            else:
                odoo_version = odoo_version.split('.')[0]
            self.assertTrue(
                re.search(odoo_version + ':r:' + module, tx_config), "Wrong version in .tx/config"
            )
