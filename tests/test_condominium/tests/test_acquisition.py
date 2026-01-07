from odoo.tests import HttpCase, tagged, get_db_name


@tagged('post_install', '-at_install')
class TestUi(HttpCase):

    def test_condominium_acquisition(self):
        ir_module = self.env['ir.module.module'].search([('name', '=', 'condominium')])
        if not ir_module.demo:
            return
        self.start_tour("/odoo", 'Condominium_Acquisition', login="admin")
