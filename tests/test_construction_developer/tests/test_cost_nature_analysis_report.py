# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests import float_compare
from odoo.tests.common import TransactionCase


class TestCostNatureAnalysisReport(TransactionCase):

    def test_table_values_sale_order(self):
        sale_order = self.env.ref('construction_developer.sale_order_41', raise_if_not_found=False)
        # skip test if demo data is not loaded
        if not sale_order:
            return
        self._test_table_values_project_16({'active_ids': sale_order.ids})

    def test_table_values_project(self):
        project = self.env.ref('construction_developer.project_project_16', raise_if_not_found=False)
        # skip test if demo data is not loaded
        if not project:
            return
        self._test_table_values_project_16({'project_id': project.id})

    def _test_table_values_project_16(self, context):
        # call the query to populate SQL view
        server_action = self.env.ref('construction_developer.action_compute_cost_nature_analysis_report')
        server_action.with_context(context).run()

        # 24 SO lines:
        # Project Management (1)
        # WI1 (6)
        # WI2 (4)
        # WI3 (4)
        # WI4 (4)
        # WI5 (3)
        # WI6 (3)
        self.assertEqual(24, self.env['x_cost_nature_analysis_report'].search_count([]), "There should be 24 lines in the report model for S00003")
        # Equipment, Material, Labour
        self.assertEqual(3, len(self.env['x_cost_nature_analysis_report']._read_group([], groupby=['x_cost_nature']))
                        , "The number of cost natures in the cost nature report should be 3")
        # 16 unique WI products + project management
        self.assertEqual(17, len(self.env['x_cost_nature_analysis_report']._read_group([], groupby=['x_product_id']))
                        , "The number of products in the cost nature report should be 17")
        # 9 unique categories
        self.assertEqual(9, len(self.env['x_cost_nature_analysis_report']._read_group([], groupby=['x_category_id']))
                        , "The number of categories in the cost nature report should be 9")

        all_records = self.env['x_cost_nature_analysis_report'].search([])

        cost_shares_sums_to_100 = float_compare(sum(r.x_cost_share for r in all_records), 1, precision_digits=2) == 0
        margin_shares_sums_to_100 = float_compare(sum(r.x_margin_share for r in all_records), 1, precision_digits=2) == 0

        self.assertTrue(cost_shares_sums_to_100, "The cost shares should sum to 100%")
        self.assertTrue(margin_shares_sums_to_100, "The margin shares should sum to 100%")

        correct_margins = all(
                    float_compare(r.x_margin, r.x_total_price - r.x_total_cost, precision_digits=2) == 0
                and float_compare(r.x_margin_percent, r.x_margin / r.x_total_price, precision_digits=2) == 0
            for r in all_records)

        self.assertTrue(correct_margins, "The margins should be computed correctly")

        cost_sum = sum(r.x_total_cost for r in all_records)
        margin_sum = sum(r.x_margin for r in all_records)
        correct_shares = all(
                    float_compare(r.x_cost_share, r.x_total_cost / cost_sum, precision_digits=2) == 0
                and float_compare(r.x_margin_share, r.x_margin / margin_sum, precision_digits=2) == 0
            for r in all_records)

        self.assertTrue(correct_shares, "The shares should be computed correctly")
