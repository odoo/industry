# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo.addons.test_generic.tests.dashboard_case import DashboardCase

_logger = logging.getLogger(__name__)


class TestConstructionDeveloperDashboard(DashboardCase):
    def test_excise_dashboard(self):
        dashboards = [
            self.env.ref('construction_developer.spreadsheet_dashboard_cost_nature'),
            self.env.ref('construction_developer.spreadsheet_dashboard_progress_report'),
        ]
        for dashboard in dashboards:
            for problem in self.check_dashboard(self.env, dashboard):
                _logger.warning(
                    "Dashboard '%s' needs rework: %s",
                    dashboard.name, problem,
                )
