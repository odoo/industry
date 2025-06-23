import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("student_organization_knowledge_tour", {
    url: "/odoo",
    steps: () => [
        {
            trigger: '.o_app[data-menu-xmlid="knowledge.knowledge_menu_root"]',
            content: _t("Get on track and explore our recommendations for your Odoo usage here!"),
            run: "click",
        },
    ],
});
