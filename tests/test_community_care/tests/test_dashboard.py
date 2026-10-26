# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo.addons.test_generic.tests.dashboard_case import DashboardCase

_logger = logging.getLogger(__name__)


class TestCommunityCareDashboard(DashboardCase):
    def test_excise_dashboard(self):
        dashboards = [
            self.env.ref('community_care.spreadsheet_dashboard_2'),
            self.env.ref('community_care.spreadsheet_dashboard_3'),
        ]
        for dashboard in dashboards:
            for problem in self.check_dashboard(self.env, dashboard):
                _logger.warning(
                    "Dashboard '%s' needs rework: %s",
                    dashboard.name, problem,
                )
