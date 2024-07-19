import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { stepUtils } from "@web_tour/tour_service/tour_utils";

import { markup } from "@odoo/owl";

registry.category("web_tour.tours").add("knowledge_tour", {
  url: "/web",
  rainbowManMessage: _t("Congrats, best of luck catching such big fish! :)"),
  sequence: 0,
  steps: () => [
    stepUtils.showAppsMenuItem(),
    {
      trigger: '.o_app[data-menu-xmlid="knowledge.menu_point_root"]',
      content: markup(
        _t(
          "Ready to boost your sales? Let's have a look at your <b>Pipeline</b>."
        )
      ),
      position: "bottom",
      run: "click",
    },
  ],
});
