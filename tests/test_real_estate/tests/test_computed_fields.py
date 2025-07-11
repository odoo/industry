# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields
from odoo.tests.common import TransactionCase
from odoo.tests import tagged, Form


@tagged('post_install', '-at_install')
class RealEstateComputedFieldsTestCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
