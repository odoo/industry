# -*- coding: utf-8 -*-
{
    'name': 'Learning Management Services',
    'version': '1.0',
    'category': 'Industry',
    'description': """
This module provides the infrastructure for delivering, managing, and tracking online courses.
They offer features such as course creation, student enrolment, assessments, progress tracking,
communication tools, certification and gamification.
""",
    'author': 'Odoo S.A.',
    'depends': [
        'account_followup',
        'appointment_crm',
        'base_vat',
        'knowledge',
        'project_enterprise',  
        'project_sms',
        'sale_crm',
        'sale_planning',
        'sale_project',
        'web_studio',
        'website_appointment',
        'website_crm',
        'website_sale_wishlist',
        'website_sale_loyalty',
        'website_sale_product_configurator',
        'website_sale_slides',
        'website_slides_forum',
        'website_slides_survey',
        'theme_clean',
    ],
    'data': [
        'data/res_config_settings.xml',
        'data/ir_attachment_pre.xml',
        'data/product_category.xml',
        'data/product_pricelist.xml',
        'data/product_product.xml',
        'data/loyalty_program.xml',
        'data/loyalty_rule.xml',
        'data/loyalty_reward.xml',
        'data/knowledge_cover.xml',
        'data/knowledge_article.xml',
        'data/knowledge_article_member.xml',
        'data/survey_survey.xml',
        'data/survey_question.xml',
        'data/survey_question_answer.xml',
        'data/slide_channel_tag.xml',
        'data/slide_tag.xml',
        'data/slide_channel.xml',
        'data/slide_slide.xml',
        'data/slide_question.xml',
        'data/slide_answer.xml',
        'data/appointment_type.xml',
    ],
    'demo': [
        'demo/website_view.xml',
        'demo/website.xml',
        'demo/res_partner.xml',
        'demo/sale_order.xml',
        'demo/sale_order_line.xml',
        'demo/sale_order_confirm.xml',
        'demo/loyalty_card.xml',
        'demo/website_menu.xml',
        'demo/website_theme_apply.xml',
        'demo/website_ir_attachment.xml',
        'demo/forum_forum.xml',
        'demo/forum_post.xml',
    ],
    'application': False,
    'license': 'OPL-1',
}