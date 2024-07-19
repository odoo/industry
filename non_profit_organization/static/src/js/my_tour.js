/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("knowledge_tour", {
    url: "/odoo",
    sequence: 2,
    steps: () => [
        {
            trigger: '.o_app[data-menu-xmlid="knowledge.knowledge_menu_root"]',
            content: _t("Open Knowledge to find the onboarding guide."),
            position: "bottom",
            run: "click",
        },
    ],
});
