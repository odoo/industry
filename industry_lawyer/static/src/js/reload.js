import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";

patch(FormController.prototype, {
    async saveButtonClicked(params) {
        const record = this.model.root;
        const groupChanged = record?._changes?.group_ids;
        const res = await super.saveButtonClicked(params);
        if (this.props.resModel === "res.users" && groupChanged) {
            window.location.reload();
        }
        return res;
    },
});
