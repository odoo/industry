import { SaleOrderLineListRenderer } from "@sale/js/sale_order_line_field/sale_order_line_field";
import { getSectionRecords } from "@account/components/section_and_note_fields_backend/section_and_note_fields_backend";
import { patch } from "@web/core/utils/patch";
import { x2ManyCommands } from "@web/core/orm_service";

patch(SaleOrderLineListRenderer.prototype, {
    async toggleIsOptional(record) {
        const setOptional = !record.data.is_optional;
        const commands = [x2ManyCommands.update(record.resId || record._virtualId, { is_optional: setOptional })];
        for (const r of getSectionRecords(this.props.list, record)) {
            const changes = !r.data.display_type
                ? (setOptional ? { price_subtotal: 0, price_total: 0, price_unit: 0.0 } : {})
                : (this.isSubSection?.(r) && setOptional ? { collapse_composition: false, collapse_prices: false } : {});
            if (Object.keys(changes).length) {
                commands.push(x2ManyCommands.update(r.resId || r._virtualId, changes));
            }
        }
        await this.props.list.applyCommands(commands, { sort: true });
    },
    async _handleQuantityAdjustment() {},
});

