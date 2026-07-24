import { onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { SpreadsheetDashboardAction } from '@spreadsheet_dashboard/bundle/dashboard_action/dashboard_action';

class BookingEngineDashboardAction extends SpreadsheetDashboardAction {
    static template = "booking_engine.DashboardAction";

    setup() {
        super.setup();
        this.accommodationIds = ["spreadsheet_dashboard_2"]
        this.accommodationDashboardResIds = [];

        onWillStart(async () => {
            this.accommodationDashboardResIds = await Promise.all(
                this.accommodationIds.map(async (xmlId) => {
                    const [, resId] = await this.orm.call("ir.model.data", "check_object_reference", ["booking_engine", xmlId]);
                    return resId;
                })
            );
        });
    }

    getDashboardGroups() {
        const groups = this.loader.getDashboardGroups();
        groups.forEach(group => {
            group.dashboards = group.dashboards.filter(
                dashboard => this.accommodationDashboardResIds.includes(dashboard.data.id)
            );
        });
        return groups;
    }
}

registry.category("actions").add("booking_engine.dashboard_action", BookingEngineDashboardAction, { force: true });
