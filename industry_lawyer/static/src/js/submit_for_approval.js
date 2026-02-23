/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Composer } from "@mail/core/common/composer";

patch(Composer.prototype, {

    async onClickSubmitForApproval(ev) {
        const composer = this.props.composer;
        const actionXmlId = ev.currentTarget.dataset.actionXmlid;
        if (!actionXmlId) {
            throw new Error("Submit approval server action XMLID not found");
        }
        await this.processMessage(async (value) => {
            const thread = this.thread ?? composer.targetThread;
            await this.env.services.action.doAction(actionXmlId, {
                additionalContext: {
                    default_model: thread?.model,
                    default_res_id: thread?.id,
                    body: value,
                    attachment_ids: composer.attachments.map((a) => a.id),
                    partner_ids: (thread?.suggestedRecipients || []).filter((r) => r.partner_id).map((r) => r.partner_id),
                },
            });
        });
    },
});
