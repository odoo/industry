# Part of Odoo. See LICENSE file for full copyright and licensing details.
import ast
import os
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED


class IndustryUtils:
    def __init__(self, industry_path: str = './'):
        self.odoo_path = os.path.join(industry_path, '../odoo/addons/')
        self.enterprise_path = os.path.join(industry_path, '../enterprise/')
        self.industry_path = industry_path

    def get_zip(self, module_name: str):
        output = BytesIO()
        zf = ZipFile(output, "w", ZIP_DEFLATED)
        industry_modules = self.get_industry_dependencies(module_name)
        dirs = [self.industry_path + module for module in industry_modules]
        for dir in dirs:
            for dirname, _, files in os.walk(dir):
                zip_dirname = os.sep.join(dirname.split(os.sep)[1:])
                zf.write(dirname, zip_dirname)
                for filename in files:
                    zf.write(os.path.join(dirname, filename), os.path.join(zip_dirname, filename))
        zf.close()
        return output

    def get_manifest(self, industry: str):
        return self.industry_path + industry + '/__manifest__.py'

    def is_industry(self, module: str):
        return os.path.exists(self.get_manifest(module))

    def get_all_industries(self):
        return [name for name in os.listdir(self.industry_path) if self.is_industry(name)]

    def get_dependencies(self, module_name: str, full_standard_list: bool = False):
        industries = {module_name}
        other_dep = set()
        to_check = [module_name]
        while to_check:
            current_module = to_check.pop()
            manifest_file = self.get_manifest(current_module)
            if full_standard_list:
                if not os.path.exists(manifest_file):
                    manifest_file = os.path.join(self.enterprise_path, current_module, '__manifest__.py')
                if not os.path.exists(manifest_file):
                    manifest_file = os.path.join(self.odoo_path, current_module, '__manifest__.py')
                if not os.path.exists(manifest_file):
                    if current_module == 'base':
                        continue
                    raise Exception("manifest (%s) does not exist", manifest_file)
            with open(manifest_file, encoding="utf-8") as f:
                manifest = ast.literal_eval(f.read())
            for dep in manifest.get('depends'):
                if not self.is_industry(dep) and dep not in other_dep:
                    other_dep.add(dep)
                    if full_standard_list:
                        to_check.append(dep)
                elif dep not in industries:
                    to_check.append(dep)
                    industries.add(dep)
        return industries, other_dep

    def get_industry_dependencies(self, module_name: str):
        return self.get_dependencies(module_name)[0]

    def install_internal_dependencies(self, module_name: str, env):
        dependencies = self.get_dependencies(module_name)[1]
        modules = env['ir.module.module'].search([('name', 'in', dependencies)])
        return modules.button_immediate_install()

    def has_module_dependency(self, module_name: str, dependency_module_name: str):
        industries, other_dep = self.get_dependencies(module_name, full_standard_list=True)
        return dependency_module_name in (industries | other_dep)

    def get_industry_dependent_to_module(self, module):
        return [name for name in self.get_all_industries() if self.has_module_dependency(name, module)]
