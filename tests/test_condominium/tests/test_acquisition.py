from odoo.tests import HttpCase, tagged, get_db_name


@tagged('post_install', '-at_install')
class TestUi(HttpCase):

    def test_condominium_acquisition(self):
        db_name = get_db_name()
        if db_name.endswith('imported_no_demo'):
            return
        self.start_tour("/odoo", 'Condominium_Acquisition', login="admin")
