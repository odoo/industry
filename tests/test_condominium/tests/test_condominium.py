from odoo.tests import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestUi(HttpCase):

    def test_fields_and_views(self):
        self.start_tour("/web", 'condominium_properties_and_units', login="admin")
