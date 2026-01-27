/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Composer } from "@mail/core/common/composer";
import { onWillStart } from "@odoo/owl";
import { user } from "@web/core/user";

patch(Composer.prototype, {
    setup() {
        super.setup();
        const composer = this.props.composer;
        const thread = composer?.thread;
        if (thread && ["sale.order", "account.move", "crm.lead"].includes(thread.model)) {
            this.state.isVisible = true;
        }
        onWillStart(async () => {
            this.state.isHighGroup = await user.hasGroup(
                "industry_lawyer.group_high"
            );
        });
    },
});
