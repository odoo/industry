import { registry } from '@web/core/registry';

registry.category("web_tour.tours").add("Condominium_Acquisition", {
    url: "/odoo",
    steps: () => [
    {
        trigger: ".o_app[data-menu-xmlid='sale\\.sale_menu_root']",
        content: "Open the Sales app to create the quotation",
        run: "click"
    },
    {
        trigger: ".o_list_button_add",
        content: "Create a new quotation",
        tooltipPosition: "bottom",
        run: "click"
    },
    {
        trigger: ".o_field_widget[name='partner_id'] .o-autocomplete--input",
        content: "Create and edit a new condominium",
        run: "edit New condo",
    },
    {
        trigger: ".o-autocomplete--dropdown-item:contains('Create and edit') > a",
        run: "click"
    },
    {
        trigger: ".o_field_widget[name='vat'] .o-autocomplete--input",
        content: "Set a TIN for your company",
        run: "edit BE0477472701"
    },
    {
        trigger: ".o_field_widget[name='email'] .o_input",
        content: "Set the email address of the responsible",
        run: "edit john@sgsmg.com"
    },
    {
        trigger: "footer > .o_form_button_save",
        run: "click",
    },
    {
        trigger: ".o_field_widget[name='sale_order_template_id'] .o-autocomplete--input",
        content: "Select the right quotation template",
        run: "click"
    },
    {
        trigger: ".o-autocomplete--dropdown-item:nth-child(1) > a",
        run: "click"
    },
    {
        trigger: ".o_statusbar_buttons > button[name='action_confirm']",
        content: "If the quote is accepted, confirm it",
        run: "click"
    },
    {
        trigger: ".o_statusbar_buttons > button:contains('Create Invoice')",
        content: "Invoice the condominium",
        run: "click"
    },
    {
        trigger: ".o_technical_modal button[name='create_invoices']",
        run: "click"
    },
    {
        trigger: ".o_statusbar_buttons > button[name='action_post']",
        content: "Check the invoice and post it",
        run: "click"
    },
    {
        trigger: ".o_field_widget[name='partner_id'] .o_form_uri",
        content: "Open the customer to create the condominium setup",
        run: "click"
    },
    {
        trigger: ".o_statusbar_buttons > button:contains('Create Condominium')",
        content: "Convert it as condominium",
        expectUnloadPage: true,
        run: "click"
    },
    {
        trigger: ".o_switch_company_menu",
        content: "The condominium is created as a new company where you will be able to manage it",
        tooltipPosition: "bottom",
        run: "click"
    },
    ]
})
