import { ProjectTaskStateSelection, projectTaskStateSelection } from "@project/components/project_task_state_selection/project_task_state_selection"
import { registry } from "@web/core/registry";

export class ProjectRemarkStateSelection extends ProjectTaskStateSelection { get isToggleMode() { return this.props.isToggleMode; }}

export const projectRemarkStateSelection = { ...projectTaskStateSelection, fieldDependencies: [{ name: "x_project_id", type: "many2one" }], component: ProjectRemarkStateSelection };

registry.category("fields").add("project_remark_state_selection", projectRemarkStateSelection);
