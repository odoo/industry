# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo.addons.test_generic.tests.dashboard_case import DashboardCase

_logger = logging.getLogger(__name__)


class TestMicroBreweryDashboard(DashboardCase):
    def test_excise_dashboard(self):
        dashboard = self.env.ref('spreadsheet_dashboard_sale.spreadsheet_dashboard_sales')
        for problem in self.check_dashboard(self.env, dashboard):
            _logger.warning(
                "Dashboard '%s' needs rework: %s",
                dashboard.name, problem,
            )
