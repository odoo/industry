/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { RelationalModel } from "@web/model/relational_model/relational_model";

patch(RelationalModel.prototype, {   
    /**
     * Filter out non-remark stages when grouping by x_stage_id
     * @param {*} config 
     * @param {*} cache 
     * @returns 
     */ 
    async _webReadGroup(config, cache) {
        const result = await super._webReadGroup(config, cache);
        // filter out non-remark stages if grouping by x_stage_id
        // because multiple groupbys are possible, we need to check if x_stage_id is the current groupby
        if (config.groupBy.includes("x_stage_id") && result.groups.length > 0 && result.groups[0].x_stage_id) {
            // we need the x_is_remark_stage field value
            const stageIds = await (cache ? this.orm.cache(cache) : this.orm).search("project.task.type", [['x_is_remark_stage', '=', true]])
            // keep only the remark stages of the result groups
            result.groups = result.groups.filter((group) => stageIds.includes(group.x_stage_id[0]));
        }
        return result;
    }
});
