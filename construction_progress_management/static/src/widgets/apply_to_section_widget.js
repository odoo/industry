import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { standardWidgetProps } from "@web/views/widgets/standard_widget_props";
import { _t } from "@web/core/l10n/translation";

export class ApplyToSectionWidget extends Component {
    static template = "construction_progress_management.ApplyToSectionButton";
    static props = {
        ...standardWidgetProps,
        record: Object,
    };

    setup() {
        this.actionService = useService("action");
        this.display_button = this.props.record.data.x_display_button;
        this.button_text = this.props.record.data.display_type == 'line_section' ? _t('Apply to section') : _t('Apply to subsection');
    }

    async applyToSection() {
        await this.props.record.save()  // might have pending changes not saved to the server
        this.actionService.doActionButton({
            type: "action",
            resId: this.props.record.data.id,
            name: "construction_progress_management.action_sol_update_section_progress",
            resModel: "sale.order.line",
        });
    }
}

export const applyToSectionWidget = {
    component: ApplyToSectionWidget,
};
registry.category("view_widgets").add("apply_to_section_widget", applyToSectionWidget);
