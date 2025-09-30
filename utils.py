# Part of Odoo. See LICENSE file for full copyright and licensing details.
import ast
import os
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED


def get_zip(module_name, env):
    output = BytesIO()
    zf = ZipFile(output, "w", ZIP_DEFLATED)
    external_modules = get_external_dependencies('industry/' + module_name, env)
    dirs = ['industry/' + module_name] + ['industry/' + module for module in external_modules]
    for dir in dirs:
        for dirname, _, files in os.walk(dir):
            zip_dirname = os.sep.join(dirname.split(os.sep)[1:])
            zf.write(dirname, zip_dirname)
            for filename in files:
                zf.write(os.path.join(dirname, filename), os.path.join(zip_dirname, filename))
    zf.close()
    return output


def get_dependencies(dir):
    manifest_file = dir + '/__manifest__.py'
    if not os.path.exists(manifest_file):
        raise FileNotFoundError(f"Manifest file not found: {manifest_file}")
    with open(manifest_file, encoding="utf-8") as f:
        manifest = ast.literal_eval(f.read())
    return set(manifest.get('depends', ['base']))


def get_external_dependencies(dir, env):
    dependencies = get_dependencies(dir)
    known_modules = env['ir.module.module'].search([]).mapped('name')
    return dependencies.difference(known_modules)


def install_internal_dependencies(dir, env):
    dependencies = get_dependencies(dir)
    modules = env['ir.module.module'].search([('name', 'in', dependencies)])
    return modules.button_immediate_install()
