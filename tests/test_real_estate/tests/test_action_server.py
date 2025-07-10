# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields
from odoo.tests.common import TransactionCase
from odoo.tests import tagged, Form
import logging
_logger = logging.getLogger(__name__)

@tagged('post_install', '-at_install')
class RealEstateAutomationsTestCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_create_technical_partner(self):
        product = self.env['product.template'].create({
            'name': 'Test Property',
        })
        product.write({
            'x_street': '123 Main St',
            'x_city': 'Springfield',
            'x_zip_code': '1234',
            'x_country': self.env.ref('base.us').id,
        })
        
        self.assertEqual(product.x_technical_partner_id.name, product.name,
                         "The technical partner should be created with the same name as the product")
        self.assertEqual(product.x_technical_partner_id.street, product.x_street,
                         "The technical partner should have the same street as the product")
        self.assertEqual(product.x_technical_partner_id.city, product.x_city,
                         "The technical partner should have the same city as the product")
        self.assertEqual(product.x_technical_partner_id.zip, "1234",
                         "The technical partner should have the same zip code as the product")
        self.assertEqual(product.x_technical_partner_id.country_id,  self.env.ref('base.us'),
                         "The technical partner should have the same country as the product")
    
    def test_publish_draft_product(self):
        product = self.env['product.template'].create({
            'name': 'Test Property',
            'website_ribbon_id': self.env.ref('website_sale.sale_ribbon').id
        })

        product.is_published = True     
        self.assertTrue(not product.is_published,
                        "The product should not be publishable when the ribbon is in draft state")
        
        product.website_ribbon_id = self.env.ref('website_sale.sold_out_ribbon')
        product.is_published = True
        self.assertTrue(product.is_published,
                        "The product should be publishable when the ribbon is not in draft state")
        
    def test_create_and_archive_appointment_types(self):
        product = self.env['product.template'].create({
            'name': 'Test Property',
        })
        
        create_appointment = self.env['ir.actions.server'].browse(self.env.ref('real_estate.create_appointment_link_server_action').id)
        create_appointment.with_context(active_ids=product.id, active_model="product.template").run()
        
        # Tests the 'create_appointment_link' server action
        appointment = product.x_appointment_ids
        self.assertTrue(appointment, "An appointment should be created for the product")
        self.assertTrue(appointment.active, "The appointment should be active initially")
        
        # Tests the 'archive_appointment_types' automation
        product.website_ribbon_id = self.env.ref('real_estate.product_ribbon_7')
        self.assertTrue(not appointment.active, 
                        "The appointment should be archived when the product ribbon is set to 'Sold'")
        

        
        
        