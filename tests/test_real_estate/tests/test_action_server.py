# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests.common import TransactionCase
from odoo.tests import tagged
import logging
_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install')
class RealEstateAutomationsTestCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.region_value_1 = cls.env['product.attribute.value'].create({
            'name': 'Value 1',
            'attribute_id': cls.env.ref('real_estate.product_attribute_10').id,
        })
        cls.region_value_2 = cls.env['product.attribute.value'].create({
            'name': 'Value 2',
            'attribute_id': cls.env.ref('real_estate.product_attribute_10').id,
        })

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
        self.assertEqual(product.x_technical_partner_id.country_id, self.env.ref('base.us'),
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

    def test_on_ribbon_update(self):
        product = self.env['product.template'].create({
            'name': 'Test Property',
        })

        product.website_ribbon_id = self.env.ref('website_sale.sold_out_ribbon')
        self.assertTrue(product.x_ribbon_stage_is_accounted,
                        "The product ribbon should be marked as accounted when it is updated")
        self.assertTrue(product.x_last_notification_update,
                        "The last notification update should be set when the ribbon is updated")

    def test_on_price_update(self):
        product = self.env['product.template'].create({
            'name': 'Test Property',
        })
        product.website_ribbon_id = self.env.ref('website_sale.sold_out_ribbon')
        product.list_price = 100.0
        last_notification = product.x_last_notification_update
        product.list_price = 150.0
        self.assertGreater(product.x_last_notification_update, last_notification,
                           "The last notification update should be updated when the price changes")

    def test_commission_plan(self):
        seller = self.env['res.users'].create({'name': 'Seller', 'login': 'seller@example.com'})
        commission_plan_seller = self.env['sale.commission.plan.user'].create({
            'user_id': seller.id,
            'plan_id': self.env['sale.commission.plan'].search([('state', '=', 'approved')], limit=1).id
        })
        finder = self.env['res.users'].create({'name': 'Finder', 'login': 'finder@example.com'})
        self.env['sale.commission.plan.user'].create({
            'user_id': finder.id,
            'plan_id': self.env['sale.commission.plan'].search([('state', '=', 'approved')], limit=1).id
        })
        product = self.env['product.product'].create({
            'name': 'Test Property',
            'type': 'consu',
        })
        partner = self.env['res.partner'].create({'name': 'Customer'})
        sale_order = self.env['sale.order'].create({
            'partner_id': partner.id,
            'user_id': finder.id,
            'company_id': self.env.ref('base.main_company').id,
        })
        self.env['sale.order.line'].create({
            'order_id': sale_order.id,
            'product_id': product.id,
        })
        # Confirm the sale order
        sale_order.action_confirm()
        # Create the invoice
        invoice_wizard = self.env['sale.advance.payment.inv'].with_context(active_ids=sale_order.ids).create({'advance_payment_method': 'delivered'})
        invoice_wizard.create_invoices()
        invoice = sale_order.invoice_ids[0]
        # Set x_seller and post the invoice
        invoice.x_seller = seller.id
        invoice.action_post()

        # Check that a commission achievement was created
        achievement = self.env['sale.commission.achievement'].search([
            ('add_user_id', '=', commission_plan_seller.id),
        ])
        self.assertTrue(achievement, "A commission achievement should be created for the seller")

    def test_send_email_book_visit(self):
        product = self.env['product.template'].create({
            'name': 'Test Property',
            'categ_id': self.env.ref('real_estate.product_category_5').id
        })
        create_appointment = self.env['ir.actions.server'].browse(self.env.ref('real_estate.create_appointment_link_server_action').id)
        create_appointment.with_context(active_ids=product.id, active_model="product.template").run()

        # create a lead and trigger visit action
        lead = self.env['crm.lead'].create({
            'name': 'Test Lead',
            'partner_id': self.env['res.partner'].create({'name': 'Test Partner'}).id,
            'email_from': 'test@email.com',
            'x_interested_in_id': product.id,
        })
        visit = self.env['ir.actions.server'].browse(self.env.ref('real_estate.book_your_visit_server_action').id)
        visit.with_context(active_ids=lead.id, active_model="crm.lead").run()

        email = self.env['mail.mail'].search([('recipient_ids.id', '=', lead.partner_id.id)], limit=1)
        self.assertTrue(email, "An email should be sent to the lead's partner")

    def test_contact_side_matches(self):
        client = self.env['res.partner'].create({
            'name': 'Test Client',
            'email': 'client@test.com',
            'x_categories_ids': self.env.ref('real_estate.product_public_category_1'),
            'x_region_ids': self.region_value_1,
            'x_subscribe': True,
        })

        # Two matching properties
        property_1 = self.env['product.template'].create({
            'name': 'Property 1',
            'categ_id': self.env.ref('real_estate.product_category_5').id,
            'public_categ_ids': self.env.ref('real_estate.product_public_category_1'),
            'attribute_line_ids': [(0, 0, {
                'attribute_id': self.env.ref('real_estate.product_attribute_10').id,
                'value_ids': self.region_value_1,
            })],
        })
        property_2 = self.env['product.template'].create({
            'name': 'Property 2',
            'categ_id': self.env.ref('real_estate.product_category_5').id,
            'public_categ_ids': self.env.ref('real_estate.product_public_category_1'),
            'attribute_line_ids': [(0, 0, {
                'attribute_id': self.env.ref('real_estate.product_attribute_10').id,
                'value_ids': self.region_value_1,
            })],
        })
        # One non-matching property
        self.env['product.template'].create({
            'name': 'Property 3',
            'categ_id': self.env.ref('real_estate.product_category_5').id,
            'public_categ_ids': self.env.ref('real_estate.product_public_category_2'),
            'attribute_line_ids': [(0, 0, {
                'attribute_id': self.env.ref('real_estate.product_attribute_10').id,
                'value_ids': self.region_value_2,
            })],
        })

        # check the computed fields x_property_matches_contacts and x_x_contact_matches_properties_product_template_count
        self.assertEqual(client.x_x_contact_matches_properties_product_template_count, 2,
                         "The client should match 2 properties")
        self.assertEqual(client.x_property_matches_contacts[0].id, property_1.id,
                         "Property 1 should be matched with the client")
        self.assertEqual(client.x_property_matches_contacts[1].id, property_2.id,
                         "Property 2 should be matched with the client")

        # check for send_matches_from_contact_server_action
        send_matches_action = self.env['ir.actions.server'].browse(self.env.ref('real_estate.send_matches_from_contact_server_action').id)
        send_matches_action.with_context(active_id=client.id, active_model="res.partner").run()
        email = self.env['mail.mail'].search_count([('recipient_ids.id', '=', client.id)])
        self.assertEqual(email, 1, "One email should be sent to the client with matched properties")

        # check for notify_contacts_for_matches_server_action (also tests the x_to_notify_property_ids field)
        notify_action = self.env['ir.actions.server'].browse(self.env.ref('real_estate.notify_contacts_for_matches_server_action').id)
        notify_action.run()
        email_count = self.env['mail.mail'].search_count([('recipient_ids.id', '=', client.id)])
        self.assertEqual(email_count, 2, "One email should be sent to the client after notification by notify_contacts_for_matches action")

    def test_property_side_matches(self):
        property = self.env['product.template'].create({
            'name': 'Property',
            'categ_id': self.env.ref('real_estate.product_category_5').id,
            'public_categ_ids': self.env.ref('real_estate.product_public_category_1'),
            'attribute_line_ids': [(0, 0, {
                'attribute_id': self.env.ref('real_estate.product_attribute_10').id,
                'value_ids': self.region_value_1,
            })],
        })
        property.website_ribbon_id = self.env.ref('website_sale.new_ribbon')

        # Two matching users
        client_1 = self.env['res.partner'].create({
            'name': 'Fred',
            'email': 'fred@test.com',
            'x_categories_ids': self.env.ref('real_estate.product_public_category_1'),
            'x_region_ids': self.region_value_1,
        })
        client_2 = self.env['res.partner'].create({
            'name': 'Fred2',
            'email': 'fred2@test.com',
            'x_categories_ids': self.env.ref('real_estate.product_public_category_1'),
            'x_region_ids': self.region_value_1,
        })
        # One non-matching user
        self.env['res.partner'].create({
            'name': 'Fred3',
            'email': 'fred3@test.com',
            'x_categories_ids': self.env.ref('real_estate.product_public_category_1'),
            'x_region_ids': self.region_value_2,
        })

        # check the field x_contact_matches_properties
        self.assertEqual(property.x_contact_matches_properties[0].id, client_1.id,
                         "Client 1 should be matched with the property")
        self.assertEqual(property.x_contact_matches_properties[1].id, client_2.id,
                         "Client 2 should be matched with the property")

    def test_create_lead_from_match(self):
        property = self.env['product.template'].create({
            'name': 'Property 1',
            'categ_id': self.env.ref('real_estate.product_category_5').id,
            'public_categ_ids': self.env.ref('real_estate.product_public_category_1'),
            'attribute_line_ids': [(0, 0, {
                'attribute_id': self.env.ref('real_estate.product_attribute_10').id,
                'value_ids': self.region_value_1,
            })],
        })
        property.website_ribbon_id = self.env.ref('website_sale.new_ribbon')
        matching_client = self.env['res.partner'].create({
            'name': 'Fred',
            'email': 'fred@test.com',
            'x_categories_ids': self.env.ref('real_estate.product_public_category_1'),
            'x_region_ids': self.region_value_1,
        })

        create_lead_action = self.env['ir.actions.server'].browse(self.env.ref('real_estate.create_lead_from_match_server_action').id)
        create_lead_action.with_context(active_id=matching_client.id, active_model="res.partner", property_id=property.id).run()

        lead = self.env['crm.lead'].search([('partner_id', '=', matching_client.id)], limit=1)
        self.assertTrue(lead, "A lead should be created for the matching client")
        self.assertEqual(lead.x_interested_in_id.id, property.id,
                         "The lead should be linked to the matched property by the x_interested_in_id field")
        self.assertEqual(lead.partner_id.id, matching_client.id,
                         "The lead should be linked to the matching client")
