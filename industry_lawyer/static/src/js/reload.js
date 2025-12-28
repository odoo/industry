import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";

patch(FormController.prototype, {
    async saveButtonClicked(params) {
        const res = await super.saveButtonClicked(params);

        if (this.props.resModel === "res.users") {
            window.location.reload();
        }

        return res;
    },
});
