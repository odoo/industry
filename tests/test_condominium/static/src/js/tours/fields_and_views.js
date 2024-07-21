import { registry } from '@web/core/registry';

registry.category("web_tour.tours").add("condominium_properties_and_units", {
    url: "/odoo",
    steps: () => [
    {
        "trigger": ".o_app[data-menu-xmlid='contacts\\.menu_contacts']",
        "run": "click"
    },
    {
        "trigger": ".o-dropdown-item[data-menu-xmlid='condominium\\.contacts_property_config_menu']",
        "run": "click"
    },
    {
        "trigger": ".o_facet_remove",
        "run": "click"
    },
    {
        "trigger": ".o-dropdown[data-menu-xmlid='contacts\\.res_partner_menu_config']",
        "run": "click"
    },
    {
        "trigger": ".o-dropdown-item[data-menu-xmlid='condominium\\.contacts_property_tags_config_menu']",
        "run": "click"
    },
    {
        "trigger": ".o_list_button_add",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='x_name'] > .o_input",
        "run": "edit Tag"
    },
    {
        "trigger": ".o-dropdown-item[data-menu-xmlid='condominium\\.contacts_property_config_menu']",
        "run": "click"
    },
    {
        "trigger": ".o_kanban_header input",
        "run": "edit New Condominium"
    },
    {
        "trigger": ".o_kanban_add",
        "run": "click"
    },
    {
        "trigger": ".o-kanban-button-new",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='x_name'] > .o_input",
        "run": "edit New Property"
    },
    {
        "trigger": ".o_field_widget[name='x_condominium_id'] .o-autocomplete--input",
        "run": "click "
    },
    {
        "trigger": ".o-autocomplete--dropdown-item:contains('My ') > a",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='x_partner_id'] .o-autocomplete--input",
        "run": "click"
    },
    {
        "trigger": ".o-autocomplete--dropdown-item:nth-child(3) > a",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='x_tenant_id'] .o-autocomplete--input",
        "run": "click"
    },
    {
        "trigger": ".o-autocomplete--dropdown-item:nth-child(3) > a",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='x_area'] > .o_input",
        "run": "edit 120"
    },
    {
        "trigger": ".o_field_many2many_selection .o-autocomplete--input",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='x_notes'] div[contenteditable='true']",
        "run": "editor Some notes"
    },
    {
        "trigger": ".o_back_button > a",
        "run": "click"
    },
    {
        "trigger": ".o_kanban_card_content",
        "run": "click"
    }
],
});
