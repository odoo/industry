from odoo.tests import HttpCase


# could keep it when adding the demo data, but will be removed when refactoring the cost nature report anyway
class TestCostNatureAnalysisReportTour(HttpCase):
    def _test_cost_nature_tour(self):
        if not self.env['ir.module.module'].search_count([('demo', '=', True)], limit=1):
            return

        self.start_tour(
            '/odoo',
            'industry_construction_developer_cost_nature_analysis_report_tour',
            login='admin',
        )
