from unittest.mock import patch

from odoo.tests import HttpCase


class TestUi(HttpCase):

    def test_condominium_acquisition(self):
        if not self.env['ir.module.module'].search_count([('demo', '=', True)], limit=1):
            return

        def autocomplete_by_vat(*args, **kwargs):
            return []

        with patch('odoo.addons.partner_autocomplete.models.res_partner.ResPartner.autocomplete_by_vat', new=autocomplete_by_vat):
            self.start_tour("/odoo", 'Condominium_Acquisition', login="admin")
