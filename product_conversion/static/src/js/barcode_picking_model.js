/** @odoo-module **/

import BarcodePickingModel from "@stock_barcode/models/barcode_picking_model";
import { patch } from "@web/core/utils/patch";

patch(BarcodePickingModel.prototype, {

    get displayOnDemandConvertButton() {
        return (
            this.resModel === "stock.picking" &&
            !["incoming", "dropship"].includes(this.record.picking_type_code) &&
            !["draft", "cancel"].includes(this.record.state)
        );
    },

    async onDemandConvertProduct() {

        const ctx = {
            default_x_picking_id: this.record.id,
        };

        return this.action.doAction("product_conversion.action_convert_product_wizard", {
            additionalContext: ctx,
            onClose: () => this.trigger("refresh", { recordId: this.record.id }),
        });
    },
});
