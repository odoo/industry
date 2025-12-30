/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { RelationalModel } from "@web/model/relational_model/relational_model";

patch(RelationalModel.prototype, {
    async _webReadGroup(config, cache) { // Filter out non-remark stages when grouping by x_stage_id
        const result = await super._webReadGroup(config, cache);
        // filter out non-remark stages if grouping by x_stage_id
        // because multiple nested groupbys are possible, we need to check if x_stage_id is the current groupby
        if (config.resModel == "project.task" && result.groups.length > 0 && (config.groupBy.includes("x_stage_id") || config.groupBy.includes("stage_id"))) {
            const stageIdList = (await this.env.services.orm.searchRead("project.task.type", [['x_is_remark_stage', '=', true]], ['id'])).map(stage => stage.id);
            if (config.groupBy.includes("x_stage_id") && result.groups[0].x_stage_id) {
                result.groups = result.groups.filter((group) => stageIdList.includes(group.x_stage_id[0]));
            } else if (config.groupBy.includes("stage_id") && result.groups[0].stage_id) {
                result.groups = result.groups.filter((group) => !stageIdList.includes(group.stage_id[0]));
            }
            result.length = result.groups.length;
            await new Promise(resolve => setTimeout(resolve, 300));
        }
        return result;
    }
});