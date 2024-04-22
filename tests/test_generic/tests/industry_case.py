# Part of Odoo. See LICENSE file for full copyright and licensing details.

import os

from odoo.tests.common import TransactionCase


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

    def setUp(cls):
        super().setUp()
        cls.installed_modules = cls.env['ir.module.module'].search(
            [('name', 'in', get_modules()), ('state', '=', 'installed')]
        ).mapped('name')
