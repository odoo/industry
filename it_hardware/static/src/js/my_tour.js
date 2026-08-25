/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("it_hardware_knowledge_tour", {
<<<<<<< 134aa9d5f4bd42e166983ed85585fa9085b8fc57
||||||| fd6aee8b29a784c76ef1aedb3a19cf87d9c1af70
    url: "/odoo",
    
=======
    
>>>>>>> 7da5a32870b611ac0bdd3dbf751a7d6466ea92c0
    steps: () => [
        {
            trigger: '.o_app[data-menu-xmlid="knowledge.knowledge_menu_root"]',
            content: _t("Get on track and explore our recommendations for your Odoo usage here!"),
            run: "click",
        },
    ],
});
