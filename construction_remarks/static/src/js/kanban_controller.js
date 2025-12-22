/** @odoo-module **/

import { KanbanController } from "@web/views/kanban/kanban_controller";
import { patch } from "@web/core/utils/patch";

patch(KanbanController.prototype, {
    /**
     * Opens the remark form view when clicking on a remark kanban card instead of the
     * default kanban behavior.
     * @override
     * @param {*} record 
     * @param {*} param1 
     * @returns 
     */
    async openRecord(record, { newWindow } = {}) {
        if (record.data.x_is_remark) {
            await this.actionService.doAction("construction_remarks.action_x_remark_form_view", {
                additionalContext: {
                    active_id: record.resId,
                },
                props: {
                    resId: record.resId,
                },
            });
            return;
        }
        return super.openRecord(record, { newWindow });
    }
});
