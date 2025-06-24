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
                'pot file': f'/i18n/{module}.pot',
                'index html file': '/static/description/index.html',
            }
            if module in self.installed_industries:
                required_files.update({
                    'icon': '/static/description/icon.png',
                    'image': '/images/main.png',
                })
            for f, path in required_files.items():
                if not os.path.isfile(get_industry_path() + module + path):
                    _logger.warning("Missing %s at %s", f, module + path)

            tx_config = Path(get_industry_path() + '.tx/config').read_text(encoding="utf-8")
            if not re.search(module, tx_config):
                _logger.error("Missing module in .tx/config")
                continue
            if release.version_info[3] != 'final':
                # skip test if master
                continue
            odoo_version = release.serie
            if odoo_version.split('.')[1] != '0':
                odoo_version = odoo_version.replace('.', '-').split('~')[-1]
            else:
                odoo_version = odoo_version.split('.')[0]
            if not re.search(odoo_version + ':r:' + module, tx_config):
                _logger.warning("Wrong version in .tx/config")

            db_name = get_db_name()
            if not db_name.endswith('imported_with_demo'):
                return
            with io.BytesIO() as buf:
                trans_export(False, [module], buf, 'po', self.env)
                new = buf.getvalue().decode("utf-8")
            old = Path(get_industry_path() + module + '/i18n/' + module + '.pot').read_text(encoding="utf-8")
            diff = list(unified_diff(old.split('\n'), new.split('\n')))
            if diff_str := '\n'.join(diff[16:]):
                _logger.warning("You forgot to export the pot file. Here is what changed:\n%s", diff_str)
