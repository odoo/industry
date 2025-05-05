{
  'name': 'Food Trucks',
  'version': '1.0',
  'category': 'Hospitality',
  'author': 'Odoo S.A.',
  'depends': [
      'industry_fsm_sale',
      'knowledge',
      'planning',
      'pos_restaurant',
      'sale_crm',
  ],
  'data': [
      'data/crm_tag.xml',
      'data/pos_payment_method.xml',
      'data/uom_uom.xml',
      'data/product_product.xml',
      'data/restaurant_floor.xml',
      'data/restaurant_table.xml',
      'data/knowledge_article.xml',
      'data/knowledge_article_favorite.xml',
      'data/mail_message.xml',
      'data/knowledge_tour.xml',
      'data/res_config_settings.xml',
  ],
  'demo': [
      'demo/pos_config.xml',
      'demo/res_partner.xml',
      'demo/crm_lead.xml',
      'demo/hr_department.xml',
      'demo/hr_employee.xml',
      'demo/pos_order.xml',
      'demo/pos_order_line.xml',
      'demo/sale_order.xml',
      'demo/sale_order_line.xml',
      'demo/sale_order_confirm.xml',
      'demo/project_task.xml',
  ],
  'assets': {
      'web.assets_backend': [
          'food_trucks/static/src/js/my_tour.js',
      ]
  },
  "cloc_exclude": [
      "data/knowledge_article.xml",
      "static/src/js/my_tour.js",
  ],
  'images': ['images/main.png'],
  'license': 'OPL-1'
}
