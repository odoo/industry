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
            this.state.isHighGroup = await user.hasGroup(
                "industry_lawyer.group_high"
            );

            const companyId = user.activeCompany.id;
            if (companyId) {
                const [company] = await this.env.services.orm.read("res.company", [companyId], ["x_approval_required"]);
                this.state.isApprovalOptional = company?.x_approval_required === "optional";
            }
        });
    },
});
