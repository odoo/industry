/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Composer } from "@mail/core/common/composer";
import { onWillStart } from "@odoo/owl";
import { user } from "@web/core/user";

patch(Composer.prototype, {
    setup() {
        super.setup();

        onWillStart(async () => {
            this.state.isHighGroup = await user.hasGroup(
                "industry_lawyer.group_high"
            );
        });
    },
});
