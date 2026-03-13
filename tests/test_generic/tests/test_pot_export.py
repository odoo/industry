import io
from pathlib import Path

from odoo.tests import common, tagged
from odoo.tools import config
from odoo.tools.translate import trans_export

from .industry_case import IndustryCase


@tagged('post_install', '-at_install', '-standard', 'pot_export')
class PotExportTest(IndustryCase):
    @common.no_retry
    def test_export_industry_pot(self):
        """Export the source terms for every installed industry module and save them."""
        industry = self.env['ir.config_parameter'].sudo().get_param('test_industry.industry_module')
        if industry:
            industries = [industry]
        else:
            industries = self.installed_industries

        for module_name in industries:
            with io.BytesIO() as buf:
                trans_export(False, [module_name], buf, 'po', self.env.cr)
                # TODO: From saas-18.4, check for empty POT files using return value
                dir = Path(config['screenshots'])
                dir.mkdir(parents=True, exist_ok=True)
                with (dir / f'i18n__{module_name}.pot').open('wb') as f:
                    f.write(buf.getvalue())
