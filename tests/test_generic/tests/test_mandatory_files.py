# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import os
from pathlib import Path
import re
import io

from odoo.tests import tagged
from odoo.tools.translate import trans_export

from .industry_case import IndustryCase, get_industry_path

_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install')
class FileTest(IndustryCase):

    def test_required_files(self):
        for module in self.installed_modules:
            needs_translation = False
            with io.BytesIO() as buffer:
                trans_export(False, [module], buffer, 'po', self.env)
                if f"module: {module}" in buffer.getvalue().decode("utf-8"):
                    needs_translation = True

            required_files = {
                'index html file': '/static/description/index.html',
                'init': '/__init__.py',
            }
            if module in self.installed_industries:
                required_files.update({
                    'icon': '/static/description/icon.png',
                    'icon-high': '/static/description/icon_hi.png',
                    'icon-svg': '/static/description/icon.svg',
                    'image': '/images/main.png',
                })
            for f, path in required_files.items():
                if not os.path.isfile(get_industry_path() + module + path):
                    _logger.warning("Missing %s at %s", f, module + path)

            weblate_config = Path(get_industry_path() + '.weblate.json').read_text(encoding="utf-8")
            if not (module_in_weblate := re.search(module, weblate_config)) and needs_translation:
                _logger.error("Missing module in .weblate.json")
                continue
            elif module_in_weblate and not needs_translation:
                _logger.warning("Remove module in .weblate.json")
                continue
