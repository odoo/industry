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
        await this.env.services.action.doAction(actionXmlId, {
            additionalContext: {
                default_model: composer.thread.model,
                default_res_id: composer.thread.id,
                body: composer.composerHtml,
                attachment_ids: composer.attachments.map(a => a.id),
                partner_ids: composer.thread.suggestedRecipients.filter(r => r.partner_id).map(r => r.partner_id),
            },
        });

        // window.location.reload();
        // await composer.thread.fetchNewMessages();
        // await this.sendMessage();
        // this.state.active = false;
        // this.clear();
        // this.state.active = true;
        // this.ref.el?.focus();
    },
});
