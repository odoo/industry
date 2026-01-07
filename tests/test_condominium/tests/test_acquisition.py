from odoo.tests import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestUi(HttpCase):

    def test_condominium_acquisition(self):
        if not self.env['ir.module.module'].search_count([('demo', '=', True)], limit=1):
            return
        self.start_tour("/odoo", 'Condominium_Acquisition', login="admin")
