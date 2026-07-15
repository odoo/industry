import { patch } from "@web/core/utils/patch";
import { SaleOrderLineListRenderer } from '@sale/js/sale_order_line_field/sale_order_line_field';


// In the Sale Order form view, in the SOL list view
// Adds the Item number column to sections & subsections
patch(SaleOrderLineListRenderer.prototype, { getSectionAndNoteColumns(columns, record) {
    const res = super.getSectionAndNoteColumns(columns, record);
    const xCol = columns.find(c => c.name === 'x_item_number');
    
    if (xCol) res.splice(1, 0, xCol);

    return res.map(col => col.name === this.titleField ? { ...col, colspan: columns.length - res.length + 1 } : { ...col });}});
