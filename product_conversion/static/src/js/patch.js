/** @odoo-module **/

import BarcodePickingModel from "@stock_barcode/models/barcode_picking_model";
import BarcodeQuantModel from "@stock_barcode/models/barcode_quant_model";
import MainComponent from "@stock_barcode/components/main";
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

        return this.action.doAction("product_conversion.action_convert_product_wizard", {
            additionalContext: {
                default_x_picking_id: this.record.id,
            },
            onClose: () => this.trigger("refresh"),
        });
    },
});

patch(BarcodeQuantModel.prototype, {

    get displayOnDemandConvertButton() {
        return (
            this.resModel === "stock.quant" &&
            this.selectedLine
        );
    },

    async onDemandConvertProduct() {
        return this.action.doAction("product_conversion.action_stock_quant_convert_product", {
            additionalContext: {
                active_ids: [this.selectedLine.id],
                active_model: "stock.quant",
            },
            onClose: () => this.trigger("refresh"),
        });
    },
});

patch(MainComponent.prototype, {

    get displayOperationButtons() {
        return super.displayOperationButtons || this.env.model.displayOnDemandConvertButton;
    },
});
