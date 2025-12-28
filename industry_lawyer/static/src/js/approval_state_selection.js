/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import {
    StateSelectionField,
    stateSelectionField,
} from "@web/views/fields/state_selection/state_selection_field";
// import { useCommand } from "@web/core/commands/command_hook";
import { CheckboxItem } from "@web/core/dropdown/checkbox_item";
import { formatSelection } from "@web/views/fields/formatters";
import { registry } from "@web/core/registry";
import { useState } from "@odoo/owl";
import { Dropdown } from "@web/core/dropdown/dropdown";

export class ApprovalStateSelection extends StateSelectionField {
    static template = "industry_lawyer.ApprovalStateSelection";

    // ✅ Only real OWL component
    static components = {
        Dropdown,
        CheckboxItem,
    };

    static props = {
        ...stateSelectionField.component.props,
        isToggleMode: { type: Boolean, optional: true },
        viewType: { type: String },
    };


    setup() {
        if (this.props.viewType != 'form') {
            super.setup();
        } 
        this.state = useState({
            isStateButtonHighlighted: false,
        });
        this.icons = {
            "01_in_progress": "o_status",
            "03_approved": "o_status o_status_green",
            "02_changes_requested": "fa fa-lg fa-exclamation-circle",
            "1_done": "fa fa-lg fa-check-circle",
            "1_canceled": "fa fa-lg fa-times-circle",
            "04_waiting_normal": "fa fa-lg fa-hourglass-o",
        };
        this.colorIcons = {
            "01_in_progress": "",
            "03_approved": "text-success",
            "02_changes_requested": "o_status_changes_requested",
            "1_done": "text-success",
            "1_canceled": "text-danger",
            "04_waiting_normal": "btn-outline-info",
        };
        this.colorButton = {
            "01_in_progress": "btn-outline-secondary",
            "03_approved": "btn-outline-success",
            "02_changes_requested": "btn-outline-warning",
            "1_done": "btn-outline-success",
            "1_canceled": "btn-outline-danger",
            "04_waiting_normal": "btn-outline-info",
        };
    }

    /* ---------- State helpers ---------- */

    get options() {
        const labels = new Map(super.options);
        const states = ["1_canceled", "1_done"];
        const currentState = this.props.record.data[this.props.name];
        if (currentState != "04_waiting_normal") {
            states.unshift("01_in_progress", "02_changes_requested", "03_approved");
        }
        return states.map((state) => [state, labels.get(state)]);
    }

    get availableOptions() {
        return this.options;
    }

    get label() {
        const waitOption = super.options.findLast(([state, _]) => state === "04_waiting_normal");
        const fullSelection = [...this.options, waitOption];
        return formatSelection(this.currentValue, {
            selection: fullSelection,
        });
    }

    stateIcon(value) {
        return this.icons[value] || "";
    }

    /**
     * @override
     */
    statusColor(value) {
        return this.colorIcons[value] || "";
    }

    get isToggleMode() {
        // Only allow toggle in list/kanban compact mode
        return this.props.isToggleMode &&
            this.isView(['list', 'kanban']) &&
            this.env.isSmall;
    }


    isView(viewNames) {
        return viewNames.includes(this.props.viewType);
    }

    async toggleState() {
        const toggleVal = this.currentValue == "1_done" ? "01_in_progress" : "1_done";
        await this.updateRecord(toggleVal);
    }

    getDropdownPosition() {
        if (this.isView(['activity', 'kanban', 'list', 'calendar']) || this.env.isSmall) {
            return '';
        }
        return 'bottom-end';
    }

    getTogglerClass(currentValue) {
        if (this.isView(['activity', 'kanban', 'list', 'calendar']) || this.env.isSmall) {
            return 'btn btn-link d-flex p-0';
        }
        return 'o_state_button btn rounded-pill ' + this.colorButton[currentValue];
    }

    async updateRecord(value) {
        const result = await super.updateRecord(value);
        this.state.isStateButtonHighlighted = false;
        if (result) {
            return result;
        }
    }

    /**
     * @param {MouseEvent} ev
     */
    onMouseEnterStateButton(ev) {
        if (!this.env.isSmall) {
            this.state.isStateButtonHighlighted = true;
        }
    }

    /**
     * @param {MouseEvent} ev
     */
    onMouseLeaveStateButton(ev) {
        this.state.isStateButtonHighlighted = false;
    }
}

/* ---------- Field registration ---------- */
export const approvalStateSelection = {
    ...stateSelectionField,
    component: ApprovalStateSelection,
    supportedOptions: [
        ...stateSelectionField.supportedOptions, {
            label: _t("Is toggle mode"),
            name: "is_toggle_mode",
            type: "boolean"
        }
    ],
    extractProps({ options, viewType }) {
        const props = stateSelectionField.extractProps(...arguments);
        props.isToggleMode = Boolean(options.is_toggle_mode);
        props.viewType = viewType;
        return props;
    },
}

registry.category("fields").add("approval_state_selection", approvalStateSelection);
