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
                manifest_data = self._load_manifest(module)
                self._validate_manifest(module, manifest_data)

    def _validate_manifest(self, module, manifest_data):
        # Check manifest keys and values
        for key, expected_value in MANDATORY_KEYS.items():
            value = manifest_data.get(key)
            expected_type = type(expected_value)
            self.assertIsInstance(value, expected_type, f"Wrong type for '{key}' in {module}, expected {expected_type}")
            if expected_value and key not in ['description']:
                self.assertEqual(value, expected_value, f"Incorrect value for '{key}' in {module}")

            if key == 'category':
                self.assertIn(value, CATEGORIES, f"Invalid category '{value}' in {module}")
            elif key in ['data', 'demo']:
                self.assertTrue(
                    all(val.startswith(f'{key}/') for val in value),
                    f"Files must be in '{key}/' directory for {module}"
                )
        # Validate files in folders
        for folder in ['data', 'demo']:
            self._test_files_in_manifest(module, manifest_data, folder)

        # Validate assets files
        self._validate_assets(module, manifest_data)

        # Check cloc_exclude files
        self._test_cloc_exclude_files(module, manifest_data)

        # Check dependencies
        self._test_dependencies(module, manifest_data)

    def _test_cloc_exclude_files(self, module, manifest_data):
        cloc_exclude_files = manifest_data.get('cloc_exclude', [])
        module_path = Path(get_industry_path() + module)
        for file in cloc_exclude_files:
            file_path = module_path / file
            self.assertTrue(file_path.exists(), f"File listed in cloc_exclude not found: {file}")

    def _validate_assets(self, module, manifest_data):
        assets = manifest_data.get('assets', {})
        module_path = Path(get_industry_path() + module)

        for asset_type, files in assets.items():
            self.assertIsInstance(files, list, f"Assets for {asset_type} must be a list in {module}")
            for file in files:
                # Check the file prefix
                self.assertTrue(
                    file.startswith(f'{module}/'),
                    f"All assets must start with '{module}/' in {module}"
                )
                # Check if the file exists
                file_path = module_path / file.replace(f"{module}/", "")
                self.assertTrue(
                    file_path.exists(),
                    f"Asset file not found: {file} in {module}"
                )
            
    def _test_files_in_manifest(self, module, manifest_data, folder_name):
        data_folder = Path(get_industry_path() + module) / folder_name
        if data_folder.exists():
            data_files_list = [
                str(file.relative_to(data_folder.parent)) 
                for file in data_folder.glob('*') if file.is_file()
            ]
            data_files = set(data_files_list)
            
            manifest_files_list = manifest_data.get(folder_name, [])
            manifest_files = set(manifest_files_list)

            # Check for duplicates in manifest_files_list
            duplicates_in_manifest = set(
                item for item in manifest_files_list 
                if manifest_files_list.count(item) > 1
            )

            self.assertFalse(
                duplicates_in_manifest,
                f"These files are duplicated in {folder_name} in the manifest: {', '.join(duplicates_in_manifest)}"
            )

            # Check for duplicates in data_files_list
            duplicates_in_data = set(
                item for item in data_files_list 
                if data_files_list.count(item) > 1
            )

            self.assertFalse(
                duplicates_in_data,
                f"These files are duplicated in {folder_name} in the data folder: {', '.join(duplicates_in_data)}"
            )

            self.assertFalse(
                data_files - manifest_files,
                f"Files in folder not listed in manifest {folder_name} for {module}: {', '.join(data_files - manifest_files)}"
            )
            self.assertFalse(
                manifest_files - data_files,
                f"Files listed in manifest {folder_name} not found in folder for {module}: {', '.join(manifest_files - data_files)}"
            )


    def _test_dependencies(self, module, manifest_data):
        dependencies = manifest_data.get('depends', [])
        self.assertTrue(
            dependencies,
            f"The 'depends' list in {module} must not be empty"
        )
        known_dependencies = self.env['ir.module.module'].search([('name', 'in', dependencies)]).mapped('name')
        unknown_dependencies = set(dependencies) - set(known_dependencies)
        self.assertFalse(
            unknown_dependencies,
            f"Unknown dependencies for {module}: {', '.join(unknown_dependencies)}"
        )
        theme_is_not_last = any(dep.startswith("theme_") for dep in dependencies) and not dependencies[-1].startswith("theme_")
        self.assertFalse(
            theme_is_not_last,
            f"Theme should be last dependency in manifest for {module}"
        )
        dependencies = [dep for dep in dependencies if not dep.startswith("theme_")]
        self.assertTrue(
            dependencies == sorted(dependencies),
            f"Dependencies not in alphabetical order for {module}"
        )