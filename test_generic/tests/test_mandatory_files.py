# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.modules.module import get_module_icon, get_module_path
from odoo.tests.common import tagged
from odoo.tools.misc import file_path

from .industry_case import IndustryCase


@tagged('post_install', '-at_install')
class FileTest(IndustryCase):

    def test_icon_file(self):
        for module in self.installed_modules:
            path_icon = get_module_icon(module)
            base_path_icon = path_icon.split('/')[1]
            self.assertNotEqual(
                base_path_icon, 'base', "Missing icon at %s" % module + path_icon[5:]
            )

    def test_image_file(self):
        for module in self.installed_modules:
            is_image = True
            module_path = get_module_path(module)
            try:
                file_path(module_path + '/images/main.png')
            except FileNotFoundError:
                is_image = False
            self.assertTrue(is_image, "Missing image file at %s" % module + '/images/main.png')
