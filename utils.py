# Part of Odoo. See LICENSE file for full copyright and licensing details.
import os
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED


class IndustryUtils:
    def __init__(self, industry_path: str):
        self.industry_path = industry_path

    def get_zip(self, module_name: str):
        output = BytesIO()
        zf = ZipFile(output, "w", ZIP_DEFLATED)
        for dirname, _, files in os.walk(self.industry_path + module_name):
            zip_dirname = os.sep.join(dirname.split(os.sep)[1:])
            zf.write(dirname, zip_dirname)
            for filename in files:
                zf.write(os.path.join(dirname, filename), os.path.join(zip_dirname, filename))
        zf.close()
        return output
