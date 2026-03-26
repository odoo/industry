/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Composer } from "@mail/core/common/composer";
import { onWillStart } from "@odoo/owl";
import { user } from "@web/core/user";

patch(Composer.prototype, {
    setup() {
        super.setup();
        this.state.isHighGroup = false;
        this.state.isApprovalOptional = false;
        this.state.isDisplayApproval = false;

        const thread = this.props.composer?.thread;

        if (thread && ["sale.order", "account.move", "crm.lead"].includes(thread.model)) {
            this.state.isDisplayApproval = true;
        }
        onWillStart(async () => {
            debugger;
            const approvalGroupsCount = await this.env.services.orm.searchCount(
                "res.groups",
                [
                    ["user_ids", "in", user.userId],
                    ["x_approval_groups", "=", true],
                    ["implied_by_ids", "=", false],
                ]
            );
            this.state.isHighGroup = approvalGroupsCount > 0;

            const companyId = user.activeCompany.id;
            if (companyId) {
                const [company] = await this.env.services.orm.read("res.company", [companyId], ["x_approval_required"]);
                this.state.isApprovalOptional = company.x_approval_required === "mendatory";
            }
        });
    },
});
