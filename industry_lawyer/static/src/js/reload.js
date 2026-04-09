import { user } from "@web/core/user";
import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";

patch(FormController.prototype, {
   async saveButtonClicked(params) {
       const record = this.model.root;
       const isUser = this.props.resModel === "res.users";
       const groupChanged = isUser && !!record?._changes?.group_ids;
       const isCurrentUser = isUser && record?.resId === user.userId;
       const res = await super.saveButtonClicked(params);
       if (isCurrentUser && groupChanged) {
           window.location.reload();
       }
       return res;
   },
});
