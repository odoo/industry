/** @odoo-module **/

import { browser } from "@web/core/browser/browser";
import { patch } from "@web/core/utils/patch";
import { ListRenderer } from "@web/views/list/list_renderer";

patch(ListRenderer.prototype, {
    computeOptionalActiveFields() {
        const defaults = this.env.searchModel?.context?.show_optional_columns;
        if (!Array.isArray(defaults)) {
            return super.computeOptionalActiveFields();
        }
        const initKey = `${this.keyOptionalFields}_${defaults.slice().sort()}_initialized`;
        if (browser.localStorage.getItem(initKey)) {
            return super.computeOptionalActiveFields();
        }
        const activeFields = {};
        const storedFields = new Set(
            browser.localStorage.getItem(this.keyOptionalFields)?.split(",") || []
        );
        for (const column of this.allColumns) {
            if (column.type !== "field" || !column.optional) {
                continue;
            }
            const fieldName = column.name.replace(/^article_properties\./, "");
            const isVisible =
                defaults.includes(column.name) ||
                defaults.includes(fieldName) ||
                column.optional === "show" ||
                storedFields.has(column.name);
            activeFields[column.name] = isVisible;
            if (isVisible) {
                storedFields.add(column.name);
            }
        }
        browser.localStorage.setItem(this.keyOptionalFields, [...storedFields]);
        browser.localStorage.setItem(initKey, "true");
        return activeFields;
    },
});
