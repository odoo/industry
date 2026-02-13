import { patch } from "@web/core/utils/patch";
import { ORM } from "@web/core/orm_service";
import { RelationalModel } from "@web/model/relational_model/relational_model";

// Display only project-specific remark stages when grouping by x_stage_id (either in search view or kanban stages)
patch(RelationalModel.prototype, { async _postprocessReadGroup(config, { groups, length }) {
    let { groups: res_groups } = await super._postprocessReadGroup(config, { groups, length });
    // because multiple nested groupbys are possible, we need to check if x_stage_id is the current groupby
    if (config.resModel == "x_remark" && groups.length > 0  && res_groups.length > 0 && (config.groupBy.includes("x_stage_id")) && groups[0].x_stage_id) {
        const stageIdsProjectsList = (await this.env.services.orm.searchRead("x_remark_stage", [], ['id', 'x_project_ids', 'x_sequence']));
        res_groups = res_groups.filter((group) => stageIdsProjectsList.some((stage) => stage.id === group.rawValue[0] && stage.x_project_ids.includes(config.context.default_x_project_id)))
                               .map((group) => { group.x_sequence = stageIdsProjectsList.find((stage) => stage.id === group.rawValue[0]).x_sequence; return group; }).sort((group_a, group_b) => group_a.x_sequence - group_b.x_sequence);}
    return { groups: res_groups, length: res_groups.length };}});

// Allow the user to drag and drop remark stages to reorder them like project stages, and save the new order in the x_sequence field
patch(ORM.prototype, { webResequence(model, ids, kwargs = {}) { return super.webResequence(model, ids, model === "x_remark_stage" ? { ...kwargs, 'specification': {'x_sequence': {}}, 'field_name': "x_sequence" } : kwargs); }});
