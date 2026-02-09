import { patch } from "@web/core/utils/patch";
import { Composer } from "@mail/core/common/composer";

patch(Composer.prototype, {
    async setup() {
        await super.setup(...arguments);
        const composer = this.props.composer;
        const thread = composer?.thread;

        if (!(thread && thread.suggestedRecipients?.length && ["sale.order", "account.move", "crm.lead"].includes(thread.model))) {
            return;
        }
        const orm = this.env.services.orm;
        // Get current record
        const [record] = await orm.searchRead(thread.model, [["id", "=", thread.id]], ["partner_id"]);
        // Get claimant partners from customer
        const claimantLines = await orm.searchRead("x_claimants_line", [["x_claimant_parent_id", "=", record.partner_id]], ["x_claimant_id"]);
        
        const claimantPartnerIds = claimantLines.map(line => line.x_claimant_id?.[0]);

        const partners = await orm.searchRead("res.partner", [["id", "in", claimantPartnerIds]], ["name", "email"]);

        
        // Inject recipients
        thread.additionalRecipients ??= [];
        const existingIds = new Set(thread.additionalRecipients.map((r) => r.partner_id));

        for (const { id, name, email } of partners) {
            if (existingIds.has(id)) {
                continue;
            }

            thread.additionalRecipients.push({
                partner_id: id,
                name: name,
                email:  email,
            });
        }
    },
});
