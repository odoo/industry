# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import os
from pathlib import Path
import re

from odoo.tests import tagged

from .industry_case import IndustryCase, get_industry_path

_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install')
class FileTest(IndustryCase):

    def test_required_files(self):
        for module in self.installed_modules:
            required_files = {
                'index html file': '/static/description/index.html',
                'init': '/__init__.py',
                'pot file': f'/i18n/{module}.pot',
            }
            if module in self.installed_industries:
                required_files.update({
                    'icon': '/static/description/icon.png',
                    'image': '/images/main.png',
                })
            for f, path in required_files.items():
                if not os.path.isfile(get_industry_path() + module + path):
                    _logger.warning("Missing %s at %s", f, module + path)

            weblate_config = Path(get_industry_path() + '.weblate.json').read_text(encoding="utf-8")
            if not re.search(module, weblate_config):
                _logger.error("Missing module in .weblate.json")
                continue
