import { KanbanController } from "@web/views/kanban/kanban_controller";
import { patch } from "@web/core/utils/patch";
import { RelationalModel } from "@web/model/relational_model/relational_model";
import { ProjectTaskKanbanDynamicGroupList } from "@project/views/project_task_kanban/project_task_kanban_model";

// Opens the remark form view when clicking on a remark kanban card instead of the default task view
patch(KanbanController.prototype, {
    async openRecord(record, { newWindow } = {}) { // Opens the remark form view when clicking on a remark kanban card instead of the default kanban behavior.
        if (record.data.x_is_remark) {
            return this.actionService.doAction("construction_remarks.action_x_remark_form_view", { additionalContext: { active_id: record.resId }, props: { resId: record.resId }});}
        return super.openRecord(record, { newWindow }); }});

// Override isGroupedByStage to include x_stage_id to be able to quick create stages
patch(ProjectTaskKanbanDynamicGroupList.prototype, { get isGroupedByStage() { return !!this.groupByField && ["stage_id", "x_stage_id"].includes(this.groupByField.name); }});

// Filter out non-remark stages when grouping by x_stage_id (either in search view or kanban stages)
patch(RelationalModel.prototype, {
    async _postprocessReadGroup(config, { groups, length }) {
        let { groups: res_groups, length: res_length } = await super._postprocessReadGroup(config, { groups, length });
        // filter out non-remark stages if grouping by x_stage_id
        // because multiple nested groupbys are possible, we need to check if x_stage_id is the current groupby
        if (config.resModel == "project.task" && groups.length > 0  && res_groups.length > 0 && (config.groupBy.includes("x_stage_id") || config.groupBy.includes("stage_id"))) {
            const stageIdsProjectsList = (await this.env.services.orm.searchRead("project.task.type", [['x_is_remark_stage', '=', true]], ['id', 'project_ids']));
            if (config.groupBy.includes("x_stage_id") && groups[0].x_stage_id) {
                res_groups = res_groups.filter((group) => stageIdsProjectsList.some((stage) => stage.id === group.value && stage.project_ids.includes(config.context.default_project_id)));
            } else if (config.groupBy.includes("stage_id") && groups[0].stage_id) {
                res_groups = res_groups.filter((group) => !stageIdsProjectsList.some((stage) => stage.id === group.value));}
            res_length = res_groups.length;}
        return { groups: res_groups, length: res_length };}});
