# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime

from odoo import Command
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class ComputedFieldsTestCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.country = cls.env.ref('base.be')
        cls.partner = cls.env['res.partner'].create({'name': 'Test Partner'})
        cls.product_template = cls.env['product.template'].create({
            'name': 'Test Room Offer',
            'type': 'service',
        })
        cls.role = cls.env['planning.role'].create({'name': 'Room Role'})


    def test_x_identity_check_computation(self):
        self.assertEqual(self.partner.x_identity_check, 'na',
                         "Identity check should be 'na' when Nationality field is empty.")

        self.partner.write({'x_nationality': self.country.id})
        self.assertEqual(self.partner.x_identity_check, 'invalid',
                         "Identity check should be 'invalid' when only Nationality is set, And Document Type, and Document Number are not set for customer.")

        self.partner.write({
            'x_document_type': 'Passport',
            'x_document_number': 'A1234567',
        })
        self.assertEqual(self.partner.x_identity_check, 'ok',
                         "Identity check should be 'ok' when Nationality, Document Type, and Document Number are set.")

        self.partner.write({'x_document_number': False})
        self.assertEqual(self.partner.x_identity_check, 'invalid',
                         "Identity check should be 'invalid' when Document Type or Document Number is missing.")

    # need to write this guest_product in class 
    def _create_guest_product(self, adults=2, children=1):
        attribute = self.env['product.attribute'].create({
            'name': 'Guest Count',
            'x_captures_guests': True,
        })
        value = self.env['product.attribute.value'].create({
            'name': f'{adults}A{children}C',
            'attribute_id': attribute.id,
            'x_adults': adults,
            'x_children': children,
        })
        product_template = self.env['product.template'].create({
            'name': 'Guest Product',
            'type': 'service',
            'attribute_line_ids': [Command.create({
                'attribute_id': attribute.id,
                'value_ids': [Command.link(value.id)],
            })],
        })
        return product_template.product_variant_id

    def _create_sale_order(self, partner, in_rental_app=False, **kwargs):
        vals = {
            'partner_id': partner.id,
        }
        if in_rental_app:
            vals.update({
                'rental_start_date': datetime(2026, 2, 1, 0, 0),
                'rental_return_date': datetime(2026, 2, 2, 0, 0),
            })
        vals.update(kwargs)
        return self.env['sale.order'].with_context(in_rental_app=in_rental_app).create(vals)

    def test_x_order_involves_room_computation(self):
        order = self._create_sale_order(self.partner)
        product_template = self.env['product.template'].create({
            'name': 'Test Room Offer',
            'type': 'service',
            'x_is_a_room_offer': True,
        })

        self.env['sale.order.line'].create({
            'order_id': order.id,
            'product_id': product_template.product_variant_id.id,
            'product_uom_qty': 1,
        })

        self.assertTrue(order.x_order_involves_room,
                        "Order should involve room when a room offer product is present in order line")

        # Remove all order lines
        order.order_line.unlink()

        product_template.write({'x_is_a_room_offer': False,})

        self.env['sale.order.line'].create({
            'order_id': order.id,
            'product_id': product_template.product_variant_id.id,
            'product_uom_qty': 1,
        })
        self.assertFalse(order.x_order_involves_room,
                         "Order should not involve room when no room offer product is present in order line")
        self.product_template.write({'x_is_a_room_offer': True,})

    def test_x_picked_up_computation(self):
        order = self._create_sale_order(self.partner, in_rental_app=True)

        self.product_template.write({'rent_ok': True,})
        order_line = self.env['sale.order.line'].with_context(in_rental_app=True).create({
            'order_id': order.id,
            'product_id': self.product_template.product_variant_id.id,
            'product_uom_qty': 2,
        })
        order.action_confirm()

        self.assertFalse(order.x_picked_up,
                         "Order should not be picked up when delivered quantity is below ordered quantity")

        order_line.qty_delivered = 2
        self.assertTrue(order.x_picked_up,
                        "Order should be picked up when delivered quantity meets ordered quantity")

    def test_x_total_guests_computation(self):
        order = self._create_sale_order(self.partner)
        product = self._create_guest_product(adults=2, children=1)
        order_line = self.env['sale.order.line'].create({
            'order_id': order.id,
            'product_id': product.id,
            'product_uom_qty': 1,
        })

        self.assertEqual(order_line.x_total_guests, 3, "Total guests should be the sum of adults and children.")

    def test_x_nights_and_city_tax_computation(self):
        order = self._create_sale_order(self.partner)
        product = self._create_guest_product(adults=2, children=0)

        order_line = self.env['sale.order.line'].create({
            'order_id': order.id,
            'product_id': product.id,
            'product_uom_qty': 1,
        })

        start = datetime(2026, 2, 1, 14, 0)
        end = datetime(2026, 2, 3, 10, 0)
        slot = self.env['planning.slot'].create({
            'role_id': self.role.id,
            'sale_line_id': order_line.id,
            'start_datetime': start,
            'end_datetime': end,
        })

        expected_nights = int(((end - start).total_seconds() + 86399) // 86400)
        self.assertEqual(slot.x_nights, expected_nights, "Nights should be computed according to start/end datetimes")
        self.assertEqual(slot.x_city_tax, expected_nights * order_line.x_total_guests,
                         "City tax should be nights multiplied by total guests.")

    def test_city_tax_slot_ids_and_total_computation(self):
        order = self._create_sale_order(self.partner)
        product = self._create_guest_product(adults=1, children=1)
        tax_role = self.env['planning.role'].create({
            'name': 'Tax Role',
        })
        product.write({
            'x_is_a_room_offer': True, 
            'x_has_city_tax': True, 
            'planning_enabled': True, 
            'planning_role_id': tax_role.id,
        })
        order_line = self.env['sale.order.line'].create({
            'order_id': order.id,
            'product_id': product.id,
            'product_uom_qty': 1,
        })

        order.action_confirm()

        city_tax = self.env['x_city_tax'].create({'x_sale_order_id': order.id})
        self.assertEqual(city_tax.x_slot_ids, order_line.planning_slot_ids,
                         "City tax slots should include only slots with city tax products")

        # need to rd for city_tax.x_total
        self.assertEqual(city_tax.x_total, order_line.planning_slot_ids.x_city_tax,
                         "Total city tax should sum the selected slots' city tax values")

    # def test_x_sol_resource_ids_computation(self):
    #     partner = self.env['res.partner'].create({'name': 'Resource Partner'})
    #     order = self._create_sale_order(partner)
    #     product_template = self.env['product.template'].create({
    #         'name': 'Resource Product',
    #         'type': 'service',
    #     })
    #     line = self.env['sale.order.line'].create({
    #         'order_id': order.id,
    #         'product_id': product_template.product_variant_id.id,
    #         'product_uom_qty': 1,
    #     })
    #     role = self.env['planning.role'].create({'name': 'Resource Role'})
    #     resource = self.env['resource.resource'].create({
    #         'name': 'Resource 1',
    #         'resource_type': 'material',
    #     })
    #     self.env['planning.slot'].create({
    #         'role_id': role.id,
    #         'resource_id': resource.id,
    #         'sale_line_id': line.id,
    #         'start_datetime': datetime(2026, 2, 5, 9, 0),
    #         'end_datetime': datetime(2026, 2, 6, 9, 0),
    #     })
    #     guests_line = self.env['x_guests_line'].create({
    #         'x_sale_order_id': order.id,
    #     })

    #     self.assertEqual(guests_line.x_sol_resource_ids, resource,
    #                      "Guest line resource ids should reflect sale order line resources")



    def test_x_sol_resource_ids_computation(self):
        order = self._create_sale_order(self.partner)
        guests_line = self.env['x_guests_line'].create({
            'x_sale_order_id': order.id,
        })
        resource = self.env['resource.resource'].create({
            'name': 'Room 101',
            'resource_type': 'material',
        })
        tax_role1 = self.env['planning.role'].create({
            'name': 'Tax Role',
            'resource_ids': [Command.link(resource.id)],
        })
        product_template = self.env['product.template'].create({
            'name': 'Test Room Offer',
            'type': 'service',
            'planning_enabled': True,
            'planning_role_id': tax_role1.id,
            'x_is_a_room_offer': True, 
            'x_has_city_tax': True, 
        })

        order_line = self.env['sale.order.line'].create({
            'order_id': order.id,
            'product_id': product_template.id,
            'product_uom_qty': 1,
        })

        order.action_confirm()

        new_role = self.env['planning.role'].create({'name': 'Resource Role'})
        new_resource = self.env['resource.resource'].create({
            'name': 'Resource 1',
            'resource_type': 'material',
        })

        self.env['planning.slot'].create({
            'role_id': new_role.id,
            'resource_id': new_resource.id,
            'sale_line_id': order_line.id,
            'start_datetime': datetime(2026, 2, 5, 9, 0),
            'end_datetime': datetime(2026, 2, 6, 9, 0),
        })


        self.assertEqual(guests_line.x_sol_resource_ids, new_resource,
                         "Guest line resource ids should reflect sale order line resources")

    def test_x_guests_computation(self):
        guest_1 = self.env['res.partner'].create({'name': 'Guest 1'})
        guest_2 = self.env['res.partner'].create({'name': 'Guest 2'})
        order = self._create_sale_order(self.partner)

        guests_line = self.env['x_guests_line'].create({
            'x_sale_order_id': order.id,
            'x_guest_partner_id': guest_1.id,
        })
        self.env['x_guests_line'].create({
            'x_sale_order_id': order.id,
            'x_guest_partner_id': guest_2.id,
        })

        self.assertEqual(order.x_guests, guest_1 + guest_2,
                         "Order guests should match the guest lines")

        guests_line.unlink()
        self.assertEqual(order.x_guests, guest_2,
                         "Order guests should update when guest lines change")

    # def test_x_occupant_ids_computation(self):
    #     guest_1 = self.env['res.partner'].create({'name': 'Occupant 1'})
    #     guest_2 = self.env['res.partner'].create({'name': 'Occupant 2'})
    #     order = self._create_sale_order(self.partner)

    #     order_line = self.env['sale.order.line'].create({
    #         'order_id': order.id,
    #         'product_id': self.product_template.product_variant_id.id,
    #         'product_uom_qty': 1,
    #         'qty_delivered': 1,
    #         'qty_returned': 0,
    #     })
    #     resource = self.env['resource.resource'].create({
    #         'name': 'Room 404',
    #         'resource_type': 'material',
    #     })
    #     self.env['planning.slot'].create({
    #         'resource_id': resource.id,
    #         'sale_line_id': order_line.id,
    #         'start_datetime': datetime(2026, 2, 9, 10, 0),
    #         'end_datetime': datetime(2026, 2, 10, 10, 0),
    #     })

    #     self.env['x_guests_line'].create({
    #         'x_sale_order_id': order.id,
    #         'x_guest_partner_id': guest_1.id,
    #         'x_room_resource_id': resource.id,
    #     })
    #     self.env['x_guests_line'].create({
    #         'x_sale_order_id': order.id,
    #         'x_guest_partner_id': guest_2.id,
    #         'x_room_resource_id': resource.id,
    #     })

    #     self.assertEqual(resource.x_occupant_ids, guest_1 + guest_2,
    #                      "Resource occupants should match guests assigned to the room")

    #     order_line.qty_returned = 1
    #     self.assertFalse(resource.x_occupant_ids,
    #                      "Resource occupants should be empty when there is no ongoing booking")
