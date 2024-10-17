# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ast import literal_eval
from pathlib import Path

from odoo.addons.test_lint.tests.test_manifests import ManifestLinter
from odoo.modules.module import module_manifest
from odoo.tests.common import tagged

from .industry_case import IndustryCase, get_industry_path

CATEGORIES = ('Services', 'Retail', 'Construction', 'Hospitality', 'Health and Fitness', 'Supply Chain')

MANDATORY_KEYS = {
    'assets': {},
    'author': 'Odoo S.A.',
    'category': '',
    'cloc_exclude': [],
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
                self.module_path = Path(get_industry_path() + module)
                manifest_data = self._load_manifest(module)
                self._validate_manifest(module, manifest_data)

    def _validate_manifest(self, module, manifest_data):
        self._test_manifest_keys(module, manifest_data)
        for key, expected_value in MANDATORY_KEYS.items():
            value = manifest_data.get(key)
            self.assertIsNotNone(value, "Missing '{key}' in manifest")
            expected_value = MANDATORY_KEYS[key]
            expected_type = type(expected_value)
            self.assertIsInstance(value, expected_type, f"Wrong type for '{key}', expected {expected_type}")
            if expected_value:
                self.assertEqual(value, expected_value, f"Wrong {key} '{value}' in manifest, it should be {expected_value}")
            if key == 'category':
                self.assertIn(value, CATEGORIES, f"Invalid category '{value}' not in {CATEGORIES}")
            elif key in ['data', 'demo']:
                self.assertTrue(all(val.startswith(f'{key}/') for val in value), f"Files must be in '{key}/' directory")
        for folder in ['data', 'demo']:
            self._test_files_in_manifest(manifest_data, folder)
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

        duplicates = {item for item in manifest_files_list if manifest_files_list.count(item) > 1}
        self.assertFalse(duplicates, f"Duplicated in {folder_name} in the manifest: {', '.join(duplicates)}")
        duplicates = {item for item in data_files_list if data_files_list.count(item) > 1}
        self.assertFalse(duplicates, f"Duplicated in {folder_name} folder: {', '.join(duplicates)}")

        not_listed = data_files - manifest_files
        self.assertFalse(not_listed, f"Files not listed in manifest {folder_name}: {', '.join(not_listed)}")
        not_found = manifest_files - data_files
        self.assertFalse(not_found, f"Files listed in manifest {folder_name} not found: {', '.join(not_found)}")

    def _test_dependencies(self, manifest_data):
        dependencies = manifest_data.get('depends', [])
        self.assertTrue(dependencies, "The 'depends' list must not be empty")
        duplicates = {item for item in dependencies if dependencies.count(item) > 1}
        self.assertFalse(duplicates, f"These dependencies are duplicated in manifest: {', '.join(duplicates)}")
        known_dependencies = self.env['ir.module.module'].search([('name', 'in', dependencies)]).mapped('name')
        unknown_dependencies = set(dependencies) - set(known_dependencies)
        self.assertFalse(unknown_dependencies, f"Unknown dependencies: {', '.join(unknown_dependencies)}")
        theme_is_not_last = any(dep.startswith("theme_") for dep in dependencies) and not dependencies[-1].startswith("theme_")
        self.assertFalse(theme_is_not_last, "Theme should be last dependency in manifest")
        dependencies = [dep for dep in dependencies if not dep.startswith("theme_")]
        self.assertTrue(dependencies == sorted(dependencies), "Dependencies not in alphabetical order")
