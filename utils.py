#!/usr/bin/env python
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import ast
import os
import shutil
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
from odoo.tools import file_open, file_open_temporary_directory


def get_zip(module_name, env):
    output = BytesIO()
    zf = ZipFile(output, "w", ZIP_DEFLATED)
    external_modules = get_external_dependencies('industry/' + module_name, env)
    dirs = ['industry/' + module_name] + ['industry/' + module for module in external_modules]
    for dir in dirs:
        for dirname, subdirs, files in os.walk(dir):
            zip_dirname = os.sep.join(dirname.split(os.sep)[1:])
            zf.write(dirname, zip_dirname)
            for filename in files:
                zf.write(os.path.join(dirname, filename), os.path.join(zip_dirname, filename))
    zf.close()
    return output


def get_external_dependencies(dir, env):
    manifest_file = dir + '/__manifest__.py'
    if not os.path.exists(manifest_file):
        raise FileNotFoundError(f"Manifest file not found: {manifest_file}")
    with file_open_temporary_directory(env) as temp_dir:
        temp_manifest_path = os.path.join(temp_dir, '__manifest__.py')
        shutil.copy(manifest_file, temp_manifest_path)
        with file_open(temp_manifest_path, env=env) as f:
            manifest = ast.literal_eval(f.read())
    dependencies = set(manifest.get('depends', ['base']))
    known_modules = env['ir.module.module'].search([]).mapped('name')
    return dependencies.difference(known_modules)
