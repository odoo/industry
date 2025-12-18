import io

from odoo.tests import common, tagged
from odoo.tools.translate import trans_export

from .industry_case import IndustryCase


@tagged('-standard', 'pot_export')
class PotExportTest(IndustryCase):
    @common.no_retry
    def test_export_industry_pot(self):
        """Export the source terms for every installed industry module and save them."""

        for module_name in self.installed_industries:
            module = self.env['ir.module.module'].search([('name', '=', module_name)], limit=1)
            with io.BytesIO() as buf:
                if not trans_export(False, [module_name], buf, 'po', self.env.cr):
                    # No terms to translate, so skip saving the file.
                    continue
                common.save_test_file(
                    module.name, buf.getvalue(), prefix='i18n_', extension='pot',
                    document_type='Source Terms for %s' % module.name,
                    date_format='',
                )
