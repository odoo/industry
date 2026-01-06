import { patch } from "@web/core/utils/patch";
import { Composer } from "@mail/core/common/composer";

patch(Composer.prototype, {
    async setup() {
        await super.setup(...arguments);
        const composer = this.props.composer;
        const thread = composer?.thread;
        if (!thread || !["sale.order", "account.move", "crm.lead"].includes(thread.model)) {
            return;
        }

        const orm = this.env.services.orm;

        // Get sale order
        const [order] = await orm.searchRead(thread.model, [["id", "=", thread.id]], ["partner_id"]);
        debugger;
        // Get claimant partners from customer
        const claimantLines = await orm.searchRead("x_claimants_line", [["x_claimants_id", "=", order.partner_id]], ["x_claimants"]);
        
        const claimantPartnerIds = claimantLines.map(line => line.x_claimants?.[0]).filter(Boolean);

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
