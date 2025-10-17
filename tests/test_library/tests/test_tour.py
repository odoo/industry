from odoo.tests import HttpCase, tagged


@tagged('post_install', '-at_install')
class LibraryTourTestCase(HttpCase):
    def test_return_tour(self):
        # skip test if demo data is not loaded
        if self.env['sale.order'].search_count([]) == 0:
            return

        self.start_tour(
            '/odoo',
            'industry_library_tour',
            login='admin',
        )
