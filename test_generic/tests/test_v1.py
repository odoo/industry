# Part of Odoo. See LICENSE file for full copyright and licensing details.

import os
from odoo.addons.test_lint.tests.test_manifests import ManifestLinter
from odoo.tests.common import tagged, TransactionCase

CATEGORIES = ('Services', 'Retail', 'Manufacturing', 'eCommerce', 'Public', 'NGO')

def get_modules():
    industry_path = os.path.abspath(__file__).split('test_generic/')[0]
    industries = [
        m for m in os.listdir(industry_path)
        if os.path.isdir(industry_path + m)
        and os.path.isfile(industry_path + m + '/__manifest__.py')
    ]
    industries.remove('test_generic')
    return industries


@tagged('post_install', '-at_install')
class BasicTest(ManifestLinter, TransactionCase):

    def test_manifests(self):
        installed_modules = self.env['ir.module.module'].search(
            [('name', 'in', get_modules()), ('state', '=', 'installed')]
        ).mapped('name')
        for module in installed_modules:
            with self.subTest(module=module):
                manifest_data = self._load_manifest(module)
                self._test_manifest_keys(module, manifest_data)
                self._test_manifest_values(module, manifest_data)

    def _test_manifest_values(self, module, manifest_data):
        res = super()._test_manifest_values(module, manifest_data)
        for key in manifest_data:
            value = manifest_data[key]
            if key == 'category':
                self.assertIn(
                    value, CATEGORIES, (
                        "Wrong category %s, it should be one of the following: %s" % (
                            value,
                            ", ".join(cat for cat in CATEGORIES),
                        )
                    )
                )
        return res
