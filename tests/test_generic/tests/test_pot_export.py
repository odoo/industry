import io

from odoo.tests import common, tagged
from odoo.tools.translate import trans_export

from .industry_case import IndustryCase


@tagged('post_install', '-at_install', '-standard', 'pot_export')
class PotExportTest(IndustryCase):
    @common.no_retry
    def test_export_industry_pot(self):
        """Export the source terms for every installed industry module and save them."""

        for module_name in self.installed_industries:
            module = self.env['ir.module.module'].search([('name', '=', module_name)], limit=1)
            with io.BytesIO() as buf:
                trans_export(False, [module_name], buf, 'po', self.env.cr)
                # TODO: From saas-18.4, check for empty POT files using return value
                common.save_test_file(
                    module.name, buf.getvalue(), prefix='i18n_', extension='pot',
                    document_type='Source Terms for %s' % module.name,
                    date_format='',
                )
