import { CustomMediaDialog } from "@html_editor/fields/x2many_field/custom_media_dialog";
import { X2ManyImageField, x2ManyImageField } from "@html_editor/fields/x2many_field/x2many_image_field";
import { patch } from "@web/core/utils/patch";

patch(X2ManyImageField.prototype, {  // Patching the instance
    onFileRemove() {  // parentField not defined in our case, so we handle x_remark_image specifically
        if (this.props.record.resModel === "x_remark_image") {
            this.props.record._parentRecord.data["x_remark_image_ids"].delete(this.props.record);
        } else { super.onFileRemove(); }},
    onFileEdit(ev) {  // Overwriting to handle x_remark_image model specifically to hide video tab
        if (this.props.record.resModel === "x_remark_image") {
            console.log("found props:", this.props);
            this.dialog.add(CustomMediaDialog, { visibleTabs: ["IMAGES"], activeTab: "IMAGES",
                save: (el) => {},
                imageSave: this.onImageSave.bind(this), videoSave: this.onVideoSave.bind(this)});
        } else { super.onFileEdit(...arguments); }},
    async onImageSave(attachment) { // Copy original logic, only change the field 'name' to 'x_name'
        if (this.props.record.resModel === "x_remark_image") {
            const attachmentRecord = await this.orm.searchRead("ir.attachment", [["id", "=", attachment[0].id]], ["id", "datas", "name"], {});
            if (!attachmentRecord[0].datas) {
                return this.notification.add(`Cannot add URL type attachment "${attachmentRecord[0].name}". Please try to reupload this image.`, {type: "warning",}); }
            await this.props.record.update({[this.props.name]: attachmentRecord[0].datas, x_name: attachmentRecord[0].name,});
        } else { super.onImageSave(...arguments); }}});
