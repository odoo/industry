# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ast import literal_eval
import logging
import os
from pathlib import Path

from odoo.addons.test_lint.tests.test_manifests import ManifestLinter
from odoo.modules.module import MANIFEST_NAMES, Manifest

from .industry_case import IndustryCase, get_industry_path

_logger = logging.getLogger(__name__)

CATEGORIES = {'Services', 'Retail', 'Construction', 'Hospitality', 'Health and Fitness', 'Supply Chain'}

HIDDEN_TECHNICAL_MODULE = {'base_industry_data'}

MANDATORY_KEYS = {
    'author': 'Odoo S.A.',
    'category': '',
    'data': [],
    'depends': [],
    'license': 'OEEL-1',
    'name': '',
}

MANDATORY_KEYS_INDUSTRIES = {
    'application': True,
    'cloc_exclude': [],
    'demo': [],
    'images': ['images/main.png'],
    'url': '',
    'website': '',
}


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
                if key == 'license' and not any(mod in manifest_data.get('depends', []) for mod in ['base_industry_data', 'knowledge', 'web_studio']):
                    expected_value = 'LGPL-3'
                self.assertEqual(value, expected_value, f"Wrong {key} '{value}' in manifest, it should be {expected_value}")
            if key == 'category':
                if module not in HIDDEN_TECHNICAL_MODULE:
                    self.assertIn(value, CATEGORIES, f"Invalid category '{value}' not in {CATEGORIES}")
                else:
                    self.assertNotIn(value, CATEGORIES, f"Module category '{value}' should not be an industry category: {CATEGORIES}")
            if is_industry:
                if key == 'url':
                    self.assertEqual(value, f"https://www.odoo.com/trial?industry&selected_app={module}", f"The url should link to the trial page: https://www.odoo.com/trial?industry&selected_app={module}")
                elif key == 'website':
                    self.assertTrue(
                        value.startswith("https://www.odoo.com/industries/") or value == "https://www.odoo.com/all-industries", "The url should link to the odoo.com page."
                    )
        self._test_files_in_manifest(manifest_data, 'data')
        if manifest_data.get('demo'):
            self._test_files_in_manifest(manifest_data, 'demo')
        self._test_no_orphaned_files(manifest_data)
        self._test_website_xml_order(manifest_data)
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

    def _test_files_in_manifest(self, manifest_data, manifest_key):
        manifest_files_list = manifest_data.get(manifest_key, [])
        manifest_files = set(manifest_files_list)

        if (duplicates := {item for item in manifest_files_list if manifest_files_list.count(item) > 1}):
            _logger.warning("Duplicated in %s in the manifest: %s", manifest_key, ', '.join(duplicates))

        # Check if the files listed in the manifest actually exist in the module
        if (not_found := {file_path for file_path in manifest_files if not (self.module_path / file_path).is_file()}):
            _logger.error("Files listed in manifest %s not found: %s", manifest_key, ', '.join(not_found))

    def _test_no_orphaned_files(self, manifest_data):
        listed_files = set()
        for key in ['data', 'demo']:
            listed_files.update(manifest_data.get(key, []))

        actual_files = set()
        for ext in ['*.xml', '*.csv']:
            for file in self.module_path.rglob(ext):
                if any(excluded in file.parts for excluded in ['static', 'tests', '__pycache__']):
                    continue
                actual_files.add(str(file.relative_to(self.module_path).as_posix()))

        if (unlisted := actual_files - listed_files):
            _logger.warning("Files found in module but not listed in manifest: %s", ', '.join(unlisted))

    def _test_website_xml_order(self, manifest_data):
        """Ensure website.xml is loaded last if a theme is loaded in the module."""
        theme_loaded = False

        # rglob('*website_*') finds any file containing 'website_' in its name, anywhere in the module
        for file_path in self.module_path.rglob('*website_*'):
            if file_path.is_file():
                try:
                    if 'button_choose_theme' in file_path.read_text(encoding='utf-8'):
                        theme_loaded = True
                        break
                except UnicodeDecodeError:
                    pass  # skip any binary/compiled files that might get caught in the glob

        if not theme_loaded:
            return

        # Enforce website.xml is the last entry in the manifest lists where it appears
        for manifest_key in ['data', 'demo']:
            manifest_files_list = manifest_data.get(manifest_key, [])
            website_xml_files = [f for f in manifest_files_list if f.endswith('website.xml')]

            if website_xml_files:
                if not manifest_files_list[-1].endswith('website.xml'):
                    _logger.error(
                        "A website.xml file must be the last entry in the '%s' list of the manifest because a theme is loaded.",
                        manifest_key,
                    )

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

    def _test_manifest_license(self, module, manifest, value):
        if "industry" in manifest.addons_path:
            return
        super()._test_manifest_license(module, manifest, value)
