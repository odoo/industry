# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo.addons.test_generic.tests.dashboard_case import DashboardCase

_logger = logging.getLogger(__name__)


class Test3plLogisticDashboard(DashboardCase):
    def test_excise_dashboard(self):
        dashboard = self.env.ref('3pl_logistic_company.spreadsheet_dashboard_15')
        for problem in self.check_dashboard(self.env, dashboard):
            _logger.warning(
                "Dashboard '%s' needs rework: %s",
                dashboard.name, problem,
            )
