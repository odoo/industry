# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ast import literal_eval
import logging
import os
from pathlib import Path

from odoo.addons.test_lint.tests.test_manifests import ManifestLinter
from odoo.modules.module import MANIFEST_NAMES, Manifest
from odoo.tests.common import tagged

from .industry_case import CATEGORIES, IndustryCase, get_industry_path

_logger = logging.getLogger(__name__)


MANDATORY_KEYS = {
    'author': 'Odoo S.A.',
    'category': '',
    'data': [],
    'depends': [],
    'license': 'OPL-1',
    'name': '',
    'version': '',
}

MANDATORY_KEYS_INDUSTRIES = {
    'cloc_exclude': [],
    'demo': [],
    'images': ['images/main.png'],
    'url': '',
    'website': '',
}


@tagged('-post_install', 'at_install')
class ManifestTest(ManifestLinter, IndustryCase):

    def _load_manifest(self, module):
        for manifest_name in MANIFEST_NAMES:
            candidate = os.path.join(get_industry_path() + module, manifest_name)
            if os.path.isfile(candidate):
                return literal_eval(Path(candidate).read_text())

    def test_manifests(self):
        for module in self.installed_modules:
            with self.subTest(module=module):
                self.module_path = Path(get_industry_path() + module)
                manifest_data = self._load_manifest(module)
                self._validate_manifest(module, manifest_data)

    def _validate_manifest(self, module, manifest_data):
        fake_Manifest = Manifest(path=get_industry_path() + 'test/test_generic', manifest_content=manifest_data)
        self._test_manifest_keys(fake_Manifest)
        self._test_manifest_values(fake_Manifest)
        self.assertNotIn('description', manifest_data, "Module description should be defined in /static/description/index.html, not in the manifest.")
        mandatory_keys = MANDATORY_KEYS.copy()
        if (is_industry := module in self.installed_industries):
            mandatory_keys.update(MANDATORY_KEYS_INDUSTRIES)
        for key, expected_value in mandatory_keys.items():
            value = manifest_data.get(key)
            self.assertIsNotNone(value, f"Missing '{key}' in manifest")
            expected_value = mandatory_keys[key]
            expected_type = type(expected_value)
            self.assertIsInstance(value, expected_type, f"Wrong type for '{key}', expected {expected_type}")
            if expected_value:
                self.assertEqual(value, expected_value, f"Wrong {key} '{value}' in manifest, it should be {expected_value}")
            if key in ['data', 'demo']:
                self.assertTrue(all(val.startswith(f'{key}/') for val in value), f"Files must be in '{key}/' directory")
            if is_industry:
                if key == 'category':
                    self.assertIn(value, CATEGORIES, f"Invalid category '{value}' not in {CATEGORIES}")
                elif key == 'url':
                    self.assertEqual(value, f"https://www.odoo.com/trial?industry&selected_app={module}", f"The url should link to the trial page: https://www.odoo.com/trial?industry&selected_app={module}")
                elif key == 'website':
                    self.assertTrue(
                        value.startswith("https://www.odoo.com/industries/") or value == "https://www.odoo.com/all-industries", "The url should link to the odoo.com page."
                    )
            elif key == 'category':
                self.assertNotIn(value, CATEGORIES, f"Module category '{value}' should not be an industry category: {CATEGORIES}")
        self._test_files_in_manifest(manifest_data, 'data')
        if manifest_data.get('demo'):
            self._test_files_in_manifest(manifest_data, 'demo')
        self._validate_assets(module, manifest_data)
        self._test_cloc_exclude_files(manifest_data)
        self._test_dependencies(manifest_data)

    def _test_cloc_exclude_files(self, manifest_data):
        for file in manifest_data.get('cloc_exclude', []):
            file_path = self.module_path / file
            self.assertTrue(file_path.exists(), f"File listed in cloc_exclude not found: {file}")

    def _validate_assets(self, module, manifest_data):
        for asset_type, files in manifest_data.get('assets', {}).items():
            self.assertIsInstance(files, list, f"Assets for {asset_type} must be a list")
            for file in files:
                self.assertTrue(file.startswith(f'{module}/'), f"All assets must start with '{module}/'")
                file_path = self.module_path / file.replace(f"{module}/", "")
                self.assertTrue(file_path.exists(), f"Asset file not found: {file}")

    def _test_files_in_manifest(self, manifest_data, folder_name):
        data_folder = self.module_path / folder_name
        self.assertTrue(data_folder.exists(), f"No folder {folder_name} found")

        data_files_list = [str(file.relative_to(data_folder.parent)) for file in data_folder.glob('*') if file.is_file()]
        data_files = set(data_files_list)

        manifest_files_list = manifest_data.get(folder_name, [])
        manifest_files = set(manifest_files_list)

        if (duplicates := {item for item in manifest_files_list if manifest_files_list.count(item) > 1}):
            _logger.warning("Duplicated in %s in the manifest: %s", folder_name, ', '.join(duplicates))
        if (duplicates := {item for item in data_files_list if data_files_list.count(item) > 1}):
            _logger.warning("Duplicated in %s folder: %s", folder_name, ', '.join(duplicates))

        if (not_listed := data_files - manifest_files):
            _logger.warning("Files not listed in manifest %s: %s", folder_name, ', '.join(not_listed))
        if (not_found := manifest_files - data_files):
            _logger.error("Files listed in manifest %s not found: %s", folder_name, ', '.join(not_found))

        website_xml = f"{folder_name}/website.xml"
        if website_xml in manifest_files_list:
            if manifest_files_list[-1] != website_xml:
                _logger.error(f"{website_xml} must be the last entry in the '{folder_name}' list of the manifest")

    def _test_dependencies(self, manifest_data):
        dependencies = manifest_data.get('depends', [])
        self.assertTrue(dependencies, "The 'depends' list must not be empty")
        if (duplicates := {item for item in dependencies if dependencies.count(item) > 1}):
            _logger.warning("These dependencies are duplicated in manifest: %s", ', '.join(duplicates))
        known_dependencies = self.env['ir.module.module'].search([('name', 'in', dependencies)]).mapped('name')
        if (unknown_dependencies := set(dependencies) - set(known_dependencies)):
            _logger.error("Unknown dependencies: %s", ', '.join(unknown_dependencies))
        if dependencies != sorted(dependencies):
            _logger.warning("Dependencies not in alphabetical order")
        if any(dependency.startswith("theme_") for dependency in dependencies):
            _logger.warning("Themes should not be in the dependencies.")
