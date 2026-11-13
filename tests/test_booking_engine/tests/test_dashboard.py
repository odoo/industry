# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo.addons.test_generic.tests.dashboard_case import DashboardCase

_logger = logging.getLogger(__name__)


class TestBookingEngineDashboard(DashboardCase):
    def test_excise_dashboard(self):
        dashboard = self.env.ref('booking_engine.spreadsheet_dashboard_1')
        for problem in self.check_dashboard(self.env, dashboard):
            _logger.warning(
                "Dashboard '%s' needs rework: %s",
                dashboard.name, problem,
            )
