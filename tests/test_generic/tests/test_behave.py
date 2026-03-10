import logging
import os
import sys
from datetime import datetime

from behave.configuration import Configuration
from behave.runner import Runner, load_step_modules

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from .industry_case import CATEGORIES, get_industry_path, get_modules

_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install')
class BehaveTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        modules = cls.env['ir.module.module'].search(
            [('name', 'in', get_modules()), ('state', '=', 'installed')],
        )
        cls.installed_modules = modules.mapped('name')
        cls.installed_industries = modules.filtered(lambda m: m.category_id.name in CATEGORIES).mapped('name')

        # ./features
        cls.generic_features_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'features'))
        # Putting it in the tests of the industry folder
        cls.reports_dir = os.path.join(get_industry_path(), 'tests', 'test_execution_reports')
        os.makedirs(cls.reports_dir, exist_ok=True)

    def test_run_gherkin(self):
        # Dynamically get the absolute path to 'industry/'
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
        self.assertTrue(repo_root.endswith('/industry'), f"Expected repo root to end with '/industry', got {repo_root}")

        # Add the industry repo to the path in which behave/python will
        # look for modules to solve the import nightmare
        # Behave forbids/does not support relative imports,
        # So we need to treat the tests/ addon as a python module
        if repo_root not in sys.path:
            sys.path.insert(0, repo_root)
        # actually run the tests
        for module in self.installed_modules:
            self.test_module_path = os.path.join(get_industry_path(), "tests", "test_" + module)
            self.feature_dir = os.path.join(self.test_module_path, 'tests', 'features')
            self._test_run_gherkin(module)

    def _make_report_path(self, module):
        timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        return os.path.join(self.reports_dir, f"Test_Report_{module}_{timestamp}.html")

    def _setup_runner_config(self, module):
        # Store Odoo's current working directory
        original_cwd = os.getcwd()

        # Shift the working directory so Behave finds the .ini file
        try:
            os.chdir(self.generic_features_dir)

            # Instantiate Configuration (Behave will natively load behave.ini here)
            config = Configuration(
                paths=[self.generic_features_dir, self.feature_dir],  # Gather all steps
                outfiles=[None, self._make_report_path(module)],  # Terminal + html file
            )
        finally:
            # IMMEDIATELY shift back to Odoo's root so we don't break the ORM/filestore
            os.chdir(original_cwd)

        config.format = ['pretty', 'html-pretty']
        config.userdata['industry_name'] = module
        config.userdata['industry_test_path'] = self.test_module_path
        config.userdata['self'] = self
        config.userdata['_logger'] = _logger

        return Runner(config)

    def _test_run_gherkin(self, module):
        if not os.path.isdir(self.feature_dir):
            _logger.info("No features directory found for module %s at %s, skipping Behave tests.", module, self.feature_dir)
            return

        runner = self._setup_runner_config(module)

        step_folders = [
            os.path.join(self.generic_features_dir, 'steps'),
            os.path.join(self.feature_dir, 'steps'),
        ]
        existing_step_folders = [p for p in step_folders if os.path.isdir(p)]
        load_step_modules(existing_step_folders)

        runner.run()

        # Better here or in environment.py? Looks better here
        for feature in runner.features:
            for scenario in feature.scenarios:
                if scenario.status.name in ['failed', 'error']:
                    for scenarioo in (hasattr(scenario, 'scenarios') and scenario.scenarios) or [scenario]:
                        if scenarioo.status.name in ['failed', 'error']:
                            # do not fail the whole test suite, but report all failed scenarios
                            with self.subTest(module=module, feature=feature.name, scenario=scenarioo.name):
                                for step in scenarioo.steps:
                                    self.assertNotIn(step.status.name, ['failed', 'error', 'undefined'], f"""
Behave test failed in module '{module}' for feature '{feature.name}' in scenario '{scenario.name}'.
Step: '{step.keyword} {step.name}'
{step.error_message or f"Step '{step.keyword} {step.name}' is not implemented"}""")
