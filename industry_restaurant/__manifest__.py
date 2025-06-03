{
    'name': 'Fine Dining Restaurant',
    'version': '3.0',
    'category': 'Hospitality',
    'description': """
Odoo for Restaurant
======================================================

This industry package is designed to streamline and enhance the management of your restaurant operations. It provides a seamless integration of all necessary modules (POS, Inventory, Accounting, Reporting, ...) to optimize restaurant workflows and improve customer satisfaction.

Basics
  * Use the Point of Sale at the desk for your sales. You can also download the Odoo Mobile App on any phone to take orders.
  * The Kitchen Display will ensure a great follow-up of every order in your bar and kitchen.
  * Let your customer book a table anytime with the Appointment App.
  * Use the Project App to never miss a reordering or a cleaning task.
  * Use the Planning App to schedule and share your shifts with your employees.
  * Use the Purchase App to reorder your products.
  * Use the Inventory App to manage your stock and receive products.
  * Get visibility and share your menu with a great Website.
  * Use the Attendances App to record employee's time spent working.
Customisations
  * User defined settings save time at product attribute definition.
""",
    'depends': [
        'account_followup',
        'contacts',
        'hr',
        'hr_attendance',
        'knowledge',
        'planning',
        'pos_enterprise',
        'pos_loyalty',
        'pos_online_payment_self_order',
        'pos_restaurant_appointment',
        'project',
        'purchase_stock',
        'website_appointment',
    ],
    'data': [
        'data/resource_calendar_data.xml',
        'data/res_config_settings.xml',
        'data/appointment_type.xml',
        'data/ir_attachment_pre.xml',
        'data/ir_default_data.xml',
        'data/product_category.xml',
        'data/product_pricelist.xml',
        'data/uom_uom.xml',
        'data/product_product.xml',
        'data/project_task_type.xml',
        'data/project_project.xml',
        'data/knowledge_cover.xml',
        'data/knowledge_article.xml',
        'data/knowledge_article_favorite.xml',
        'data/mail_message.xml',
        'data/knowledge_tour.xml',
    ],
    'demo': [
        'demo/pos_payment_method.xml',
        'demo/payment_provider_demo_post.xml',
        'demo/res_partner.xml',
        'demo/hr_employee.xml',
        'demo/product_supplierinfo.xml',
        'demo/planning_role.xml',
        'demo/planning_slot_templates.xml',
        'demo/pos_config.xml',
        'demo/product_product.xml',
        'demo/stock_quant.xml',
        'demo/stock_warehouse_orderpoint.xml',
        'demo/appointment_type.xml',
        'demo/kitchen_display.xml',
        'demo/purchase_order.xml',
        'demo/purchase_order_line.xml',
        'demo/purchase_order_post.xml',
        'demo/planning_slot.xml',
        'demo/project_task.xml',
        'demo/website_attachment.xml',
        'demo/website_view.xml',
        'demo/website_page.xml',
        'demo/website_menu.xml',
        'demo/website_theme_apply.xml',
        'demo/pos_orders.xml',
        'demo/pos_order_lines.xml',
    ],
    'license': 'OPL-1',
    'assets': {
        'web.assets_backend': [
            'industry_restaurant/static/src/js/my_tour.js',
        ]
    },
    'author': 'Odoo S.A.',
    "cloc_exclude": [
        "data/knowledge_article.xml",
        "demo/website_view.xml",
        "static/src/js/my_tour.js",
    ],
    'images': ['images/main.png'],
}
