import glob
import os

from tests.test_generic.tests.features.behave_utils import (
    given,
    then,
)

from odoo.tests.common import TransactionCase

self = TransactionCase()  # dummy to prevent linting errors. Overwritten in the decorator by behave_utils


## Steps for the meta-test


@given('an industry module with a behave test folder')
def given_an_industry_module_with_a_behave_test_folder(context):
    # This step identifies which module we are currently testing.
    # If running in a loop, context.industry_name should be set.
    # For now, let's assume we are checking the one passed via the runner.
    self.assertTrue(hasattr(context, 'industry_name'), "Industry name not set in context")
    self.assertTrue(os.path.exists(context.industry_test_path), f"Test module path {context.industry_test_path} not found")
    self.assertTrue(os.path.isdir(os.path.join(context.industry_test_path, 'tests', 'features')), f"Features directory not found in {context.industry_test_path}")


@then('there should be at least one ".{ext}" file in "{subpath}" subdirectory')
def then_there_should_be_at_least_one_ext_file_in_subpath_subdirectory(context, ext, subpath):
    subdir_path = os.path.join(context.industry_test_path, 'tests', subpath)
    search_path = os.path.join(subdir_path, f"*.{ext}")
    features = glob.glob(search_path)
    self.assertTrue(len(features) > 0, f"No .{ext} files found in {subdir_path}")


@then('it should have a "{subpath}" subdirectory')
def then_it_should_have_a_subpath_subdirectory(context, subpath):
    full_path = os.path.join(context.industry_test_path, 'tests', subpath)
    self.assertTrue(os.path.isdir(full_path), f"Missing subdirectory: {subpath}")


@then('the file "{filename}" should exist in "{subpath}" subdirectory')
def then_the_file_filename_should_exist_in_subpath_subdirectory(context, filename, subpath):
    file_path = os.path.join(context.industry_test_path, 'tests', subpath, filename)
    self.assertTrue(os.path.isfile(file_path), f"Required file {filename} missing in {subpath}")
