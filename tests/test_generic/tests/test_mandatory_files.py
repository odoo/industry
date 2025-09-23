# Part of Odoo. See LICENSE file for full copyright and licensing details.

from difflib import unified_diff
import io
import logging
import os
from pathlib import Path
import re

from odoo import release
from odoo.tests import get_db_name, tagged
from odoo.tools.translate import trans_export

from .industry_case import IndustryCase, get_industry_path

_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install')
class FileTest(IndustryCase):

    def test_required_files(self):
        for module in self.installed_modules:
            required_files = {
                'icon': '/static/description/icon.png',
                'image': '/images/main.png',
                'index html file': '/static/description/index.html',
                'init': '/__init__.py',
                'pot file': f'/i18n/{module}.pot',
            }
            if module in self.installed_industries:
                required_files.update({
                    'icon': '/static/description/icon.png',
                    'image': '/images/main.png',
                    'tour': '/static/src/js/my_tour.js',
                })
            for f, path in required_files.items():
                if not os.path.isfile(get_industry_path() + module + path):
                    _logger.warning("Missing %s at %s", f, module + path)

            weblate_config = Path(get_industry_path() + '.weblate.json').read_text(encoding="utf-8")
            if not re.search(module, weblate_config):
                _logger.error("Missing module in .weblate.json")
                continue
            if release.version_info[3] != 'final':
                # skip test if master
                continue

            db_name = get_db_name()
            if not db_name.endswith('imported_with_demo'):
                return
            with io.BytesIO() as buf:
                trans_export(False, [module], buf, 'po', self.env.cr)
                new = buf.getvalue().decode("utf-8")
            old = Path(get_industry_path() + module + '/i18n/' + module + '.pot').read_text(encoding="utf-8")
            diff = list(unified_diff(old.split('\n'), new.split('\n')))
            if diff_str := '\n'.join(diff[16:]):
                _logger.warning("You forgot to export the pot file. Here is what changed:\n%s", diff_str)
