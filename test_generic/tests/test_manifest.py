# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.addons.test_lint.tests.test_manifests import ManifestLinter
from odoo.tests.common import tagged

from .industry_case import IndustryCase

CATEGORIES = ('Services', 'Retail', 'Manufacturing', 'eCommerce', 'Public', 'NGO')

MANDATORY_KEYS = {
    'category': '',
    'data': [],
    'demo': [],
    'description': '',
    'depends': [],
    'images': [],
    'license': '',
    'name': '',
    'version': '',
}


@tagged('post_install', '-at_install')
class ManifestTest(ManifestLinter, IndustryCase):

    def test_manifests(self):
        for module in self.installed_modules:
            with self.subTest(module=module):
                manifest_data = self._load_manifest(module)
                self._test_manifest_keys(module, manifest_data)
                self._test_manifest_values(module, manifest_data)

    def _test_manifest_keys(self, module, manifest_data):
        res = super()._test_manifest_keys(module, manifest_data)
        for key in MANDATORY_KEYS:
            self.assertIn(key, manifest_data, "Missing key %s in manifest" % key)

    def _test_manifest_values(self, module, manifest_data):
        res = super()._test_manifest_values(module, manifest_data)
        for key in manifest_data:
            value = manifest_data[key]
            expected_type = type(MANDATORY_KEYS[key])
            self.assertEqual(
                type(value),
                expected_type,
                "Wrong type for manifest value %s in module %s, expected %s" % (
                    key, module, expected_type
                )
            )
            if key == 'category':
                self.assertIn(
                    value, CATEGORIES, (
                        "Wrong category %s in manifest, it should be one of the following: %s" % (
                            value, ", ".join(cat for cat in CATEGORIES),
                        )
                    )
                )
            elif key == 'images':
                self.assertEqual(
                    value,
                    ['images/main.png'],
                    "Wrong images %r in manifest, it should be ['images/main.png']" % value
                )
            elif key == 'license':
                self.assertEqual(
                    value, 'OPL-1', "Wrong license %r in manifes, it should be 'OPL-1'" % value
                )
            elif key == 'data':
                self.assertTrue(
                    all(len(val.split('/')) == 2 and val.split('/')[0] == 'data' for val in value),
                    "all data files should be in 'data/' subfolder",
                )
            elif key == 'demo':
                self.assertTrue(
                    all(len(val.split('/')) == 2 and val.split('/')[0] == 'demo' for val in value),
                    "all demo files should be in 'demo/' subfolder",
                )
        return res
