/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Composer } from "@mail/core/common/composer";

patch(Composer.prototype, {
    async sendMessageSubmitForApproval() {
        await this.processMessage(async (value) => {
            await this._sendMessage(
                value,
                this.postData,
                {
                    ...this.extraData,
                    context: {
                        ...(this.extraData.context || {}),
                        default_x_submit_for_approval: true,
                    },
                }
            );
        });
    },
});

