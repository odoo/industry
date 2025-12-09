import { _t } from "@web/core/l10n/translation";
import {
    stateSelectionField,
} from "@web/views/fields/state_selection/state_selection_field";
import { registry } from "@web/core/registry";
import { ProjectTaskStateSelection } from "@project/components/project_task_state_selection/project_task_state_selection"

export class ProjectRemarkStateSelection extends ProjectTaskStateSelection {
    get isToggleMode() {
        return this.props.isToggleMode;
    }
}

export const projectRemarkStateSelection = {
    ...stateSelectionField,
    component: ProjectRemarkStateSelection,
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

registry.category("fields").add("project_remark_state_selection", projectRemarkStateSelection);
