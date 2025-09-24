# Part of Odoo. See LICENSE file for full copyright and licensing details.

import os

from odoo.tests.common import TransactionCase

CATEGORIES = {'Services', 'Retail', 'Construction', 'Hospitality', 'Health and Fitness', 'Supply Chain'}


def get_industry_path():
    return os.path.abspath(__file__).split('tests/test_generic/')[0]


def get_modules():
    industry_path = get_industry_path()
    industries = [
        m for m in os.listdir(industry_path)
        if os.path.isdir(industry_path + m)
        and os.path.isdir(industry_path + m + '/data')
    ]
    return industries


class IndustryCase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        modules = cls.env['ir.module.module'].search(
            [('name', 'in', get_modules()), ('state', '=', 'installed')]
        )
        cls.installed_modules = modules.mapped('name')
        cls.installed_industries = modules.filtered(lambda m: m.category_id.name in CATEGORIES).mapped('name')
