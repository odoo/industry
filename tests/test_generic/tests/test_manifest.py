# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ast import literal_eval
from pathlib import Path

from odoo.addons.test_lint.tests.test_manifests import ManifestLinter
from odoo.modules.module import module_manifest
from odoo.tests.common import tagged

from .industry_case import IndustryCase, get_industry_path

CATEGORIES = ('Services', 'Retail', 'Manufacturing', 'eCommerce', 'Public', 'NGO')

MANDATORY_KEYS = {
    'author': 'Odoo S.A.',
    'category': '',
    'data': [],
    'demo': [],
    'description': '',
    'depends': [],
    'images': ['images/main.png'],
    'license': 'OPL-1',
    'name': '',
    'version': '',
}


@tagged('post_install', '-at_install')
class ManifestTest(ManifestLinter, IndustryCase):

    def _load_manifest(self, module):
        manifest_file = module_manifest(get_industry_path() + module)
        return literal_eval(Path(manifest_file).read_text())

    def test_manifests(self):
        for module in self.installed_modules:
            with self.subTest(module=module):
                manifest_data = self._load_manifest(module)
                self._test_manifest_keys(module, manifest_data)
                self._test_manifest_values(module, manifest_data)
                self._test_files_in_manifest(module, manifest_data, 'data')
                self._test_files_in_manifest(module, manifest_data, 'demo')
                self._test_dependencies(module, manifest_data)

    def _test_manifest_keys(self, module, manifest_data):
        super()._test_manifest_keys(module, manifest_data)
        for key in MANDATORY_KEYS:
            self.assertIn(key, manifest_data, "Missing key %s in manifest" % key)

    def _test_manifest_values(self, module, manifest_data):
        for key in manifest_data:
            value = manifest_data[key]
            expected_value = MANDATORY_KEYS[key]
            expected_type = type(expected_value)
            self.assertEqual(
                type(value),
                expected_type,
                "Wrong type for manifest value %s in module %s, expected %s"
                % (key, module, expected_type),
            )
            if expected_value:
                self.assertEqual(
                    value,
                    expected_value,
                    "Wrong %s '%r' in manifest, it should be %s" % (key, value, expected_value),
                )
            if key == 'category':
                self.assertIn(
                    value,
                    CATEGORIES,
                    (
                        "Wrong category %s in manifest, it should be one of the following: %s"
                        % (
                            value,
                            ", ".join(cat for cat in CATEGORIES),
                        )
                    ),
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

    def _test_files_in_manifest(self, module, manifest_data, folder_name):
        data_folder = Path(get_industry_path() + module) / folder_name
        if data_folder.exists():
            # Get all files in the folder
            data_files = {
                str(file.relative_to(data_folder.parent))
                for file in data_folder.glob('*')
                if file.is_file()
            }
            # Get all files listed in the manifest for the folder
            manifest_list = manifest_data.get(folder_name, [])
            manifest_files = set(manifest_list)

            # Check for duplicates in the manifest
            duplicates_in_manifest = {
                item for item in manifest_list if manifest_list.count(item) > 1
            }
            self.assertFalse(
                duplicates_in_manifest,
                "These files are duplicated in %s in the manifest: %s"
                % (folder_name, ", ".join(duplicates_in_manifest)),
            )

            # Check that all files in the folder are listed in the manifest
            missing_in_manifest = data_files - manifest_files
            self.assertFalse(
                missing_in_manifest,
                "These files are not listed in %s in the manifest: %s"
                % (folder_name, ", ".join(f for f in missing_in_manifest)),
            )

            # Check that all files listed in the manifest exist in the folder
            missing_on_disk = [file for file in manifest_files if file not in data_files]
            self.assertFalse(
                missing_on_disk,
                "These files are listed in manifest %s but were not found on the disk: %s"
                % (folder_name, ", ".join(f for f in missing_on_disk)),
            )

    def _test_dependencies(self, module, manifest_data):
        dependencies = manifest_data.get('depends', [])
        known_dependencies = self.env['ir.module.module'].search([('name', 'in', dependencies)]).mapped('name')
        unknown_dependencies = set(dependencies) - set(known_dependencies)
        self.assertFalse(
            unknown_dependencies,
            "Unknown dependencies for %s: %s" % (module, ", ".join(unknown_dependencies))
        )
