# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime

from odoo import Command
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class ComputedFieldsTestCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Test Partner'})
        cls.product_attribute = cls.env['product.attribute'].create({
            'name': 'Guest Count',
            'x_captures_guests': True,
        })
        cls.value = cls.env['product.attribute.value'].create({
            'name': '2A1C',
            'attribute_id': cls.product_attribute.id,
            'x_adults': 2,
            'x_children': 1,
        })
        guest_product_template = cls.env['product.template'].create({
            'name': 'Guest Product',
            'type': 'service',
            'attribute_line_ids': [Command.create({
                'attribute_id': cls.product_attribute.id,
                'value_ids': [Command.link(cls.value.id)],
            })],
        })
        cls.guest_product_variant_id = guest_product_template.product_variant_id
        cls.product_template = cls.env['product.template'].create({
            'name': 'Test Room Offer',
            'type': 'service',
        })
        cls.resource = cls.env['resource.resource'].create({
            'name': 'Resource 1',
            'resource_type': 'material',
        })
        cls.role = cls.env['planning.role'].create({
            'name': 'Role',
            'x_is_a_room_offer': True
        })
        cls.project = cls.env['project.project'].create({
            'name': 'Housekeeping Project',
            'x_is_house_keeping_project': True,
        })
        cls.stage_to_clean = cls.env.ref('booking_engine.project_task_type_15')
        cls.stage_clean = cls.env.ref('booking_engine.project_task_type_17')
        cls.guests = cls.env['res.partner'].create([
            {'name': 'Guest 1'},
            {'name': 'Guest 2'},
        ])

    def test_x_identity_check_computation(self):
        self.assertEqual(self.partner.x_identity_check, 'na',
                         "Identity check should be 'na' when Nationality field is empty.")

        self.partner.write({'x_nationality': self.env.ref('base.be').id})
        self.assertEqual(self.partner.x_identity_check, 'invalid',
                         "Identity check should be 'invalid' when only Nationality is set, And Document Type, and Document Number are not set for customer.")

        self.partner.write({'x_document_type': 'Passport', 'x_document_number': 'A1234567'})
        self.assertEqual(self.partner.x_identity_check, 'ok',
                         "Identity check should be 'ok' when Nationality, Document Type, and Document Number are set.")

        self.partner.write({'x_document_number': False})
        self.assertEqual(self.partner.x_identity_check, 'invalid',
                         "Identity check should be 'invalid' when Document Type or Document Number is missing.")

    def _create_guest_product(self, adults=2, children=1):
        value = self.env['product.attribute.value'].create({
            'name': f'{adults}A{children}C',
            'attribute_id': self.product_attribute.id,
            'x_adults': adults,
            'x_children': children,
        })
        product_template = self.env['product.template'].create({
            'name': 'Test Room Offer',
            'type': 'service',
            'sale_ok': True,
        })
        self.role.write({'product_ids': [Command.link(product_template.id)]})
        product_template = self.env['product.template'].create({
            'name': 'Guest Product',
            'type': 'service',
            'sale_ok': True,
            'rent_ok': True,
            'planning_enabled': True,
            'planning_role_id': self.role.id,
            'x_is_a_room_offer': True,
            'x_has_city_tax': True,
            'attribute_line_ids': [Command.create({
                'attribute_id': self.product_attribute.id,
                'value_ids': [Command.link(value.id)],
            })],
        })
        return product_template.product_variant_id

    def _create_sale_order(self, partner, **kwargs):
        return self.env['sale.order'].with_context(in_rental_app=True).create({
            'partner_id': partner.id,
            'rental_start_date': datetime(2026, 2, 1, 0, 0),
            'rental_return_date': datetime(2026, 2, 2, 0, 0),
        })

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

        # Remove order lines
        order.order_line.unlink()

        product_template.write({'x_is_a_room_offer': False})

        self.env['sale.order.line'].create({
            'order_id': order.id,
            'product_id': product_template.product_variant_id.id,
            'product_uom_qty': 1,
        })
        self.assertFalse(order.x_order_involves_room,
                         "Order should not involve room when no room offer product is present in order line")

    def test_x_picked_up_computation(self):
        order = self._create_sale_order(self.partner)
        self.product_template.write({'rent_ok': True})
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
        order_line = self.env['sale.order.line'].create({
            'order_id': order.id,
            'product_id': self.guest_product_variant_id.id,
            'product_uom_qty': 1,
        })

        self.assertEqual(order_line.x_total_guests, 3, "Total guests should be the sum of adults plus children.")

    def test_x_nights_and_city_tax_computation(self):
        order = self._create_sale_order(self.partner)

        order_line = self.env['sale.order.line'].create({
            'order_id': order.id,
            'product_id': self.guest_product_variant_id.id,
            'product_uom_qty': 1,
        })

        order.action_confirm()
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
        product = self._create_guest_product(adults=2, children=1)
        order_line = self.env['sale.order.line'].with_context(in_rental_app=True).create({
            'order_id': order.id,
            'product_id': product.id,
            'product_uom_qty': 1,
        })
        order.action_confirm()
        city_tax = self.env['x_city_tax'].create({'x_sale_order_id': order.id})

        slot = order_line.planning_slot_ids[0]
        self.assertEqual(city_tax.x_slot_ids, slot,
                         "City tax slots should include only slots with city tax products")
        self.assertEqual(city_tax.x_total, slot.x_city_tax,
                         "Total city tax should sum the selected slots' city tax values")

    def test_x_sol_resource_ids_computation(self):
        order = self._create_sale_order(self.partner)
        guests_line = self.env['x_guests_line'].create({'x_sale_order_id': order.id})

        order_line = self.env['sale.order.line'].create({
            'order_id': order.id,
            'product_id': self.product_template.product_variant_id.id,
            'product_uom_qty': 1,
        })
        order.action_confirm()

        self.env['planning.slot'].create({
            'role_id': self.role.id,
            'resource_id': self.resource.id,
            'sale_line_id': order_line.id,
            'start_datetime': datetime(2026, 2, 5, 9, 0),
            'end_datetime': datetime(2026, 2, 6, 9, 0),
        })
        self.assertEqual(guests_line.x_sol_resource_ids.ids, self.resource.ids,
                         "Guest line resource ids should reflect sale order line resources")

    def test_x_guests_computation(self):
        order = self._create_sale_order(self.partner)

        guest_lines = self.env['x_guests_line'].create([
            {'x_sale_order_id': order.id, 'x_guest_partner_id': guest.id} for guest in self.guests
        ])

        # Validate both guests are linked
        self.assertEqual(order.x_guests, self.guests, "Guests should reflect all linked guest lines to the order.")

        # Remove one guest line
        guest_lines[0].unlink()

        self.assertEqual(order.x_guests, self.guests[1], "Guests should update correctly after removing a one guest line.")

    def test_x_occupant_ids_computation(self):
        order = self._create_sale_order(self.partner)
        order_line = self.env['sale.order.line'].create({
            'order_id': order.id,
            'product_id': self.product_template.product_variant_id.id,
            'product_uom_qty': 1,
        })
        order.action_confirm()
        order_line.qty_delivered = 1

        resource = self.env['resource.resource'].create({
            'name': 'Room 404',
            'resource_type': 'material',
            'role_ids': [Command.link(self.role.id)],
        })
        self.env['planning.slot'].create({
            'resource_id': resource.id,
            'sale_line_id': order_line.id,
            'start_datetime': datetime(2026, 2, 9, 10, 0),
            'end_datetime': datetime(2026, 2, 10, 10, 0),
        })

        self.env['x_guests_line'].create([
            {
                'x_sale_order_id': order.id,
                'x_guest_partner_id': guest.id,
                'x_room_resource_id': resource.id,
            }
            for guest in self.guests
        ])
        self.assertEqual(resource.x_occupant_ids, self.guests,
                         "Resource occupants should match guests assigned to the room")
        self.assertEqual(self.guests[0].x_ongoing_bookings, resource,
                         "Ongoing bookings should include resources where the partner is an occupant")

        order_line.qty_returned = 1
        # x_ongoing_bookings is store=False so use _invalidate_cache
        self.guests[0]._invalidate_cache(['x_ongoing_bookings'])
        self.assertFalse(resource.x_occupant_ids,
                         "Resource occupants should be empty when there is no ongoing booking")
        self.assertFalse(self.guests[0].x_ongoing_bookings,
                         "Ongoing bookings should be empty when there is no ongoing booking")

    def test_x_guests_count_computation(self):
        guest = self.env['res.partner'].create({'name': 'Guest Count'})
        order = self._create_sale_order(self.partner)
        self.assertEqual(guest.x_guests_count, 0,
                         "Guests count should be 0 when no guest lines exist for the partner.")

        self.env['x_guests_line'].create([
            {
                'x_sale_order_id': order.id,
                'x_guest_partner_id': guest.id,
            },
            {
                'x_sale_order_id': order.id,
                'x_guest_partner_id': guest.id,
            }
        ])
        # x_guests_count is store=False so use _invalidate_cache
        guest._invalidate_cache(['x_guests_count'])
        self.assertEqual(guest.x_guests_count, 2,
                         "Guests count should reflect the number of guest lines for the partner.")

        self.env['x_guests_line'].search([('x_guest_partner_id', '=', guest.id)], limit=1).unlink()
        self.assertEqual(guest.x_guests_count, 1,
                         "Guests count should update after removing a guest line.")

    def test_x_ongoing_task_id_computation(self):
        open_task = self.env['project.task'].create({
            'name': 'Open Task',
            'project_id': self.project.id,
            'x_resource_id': self.resource.id,
            'stage_id': self.stage_to_clean.id,
        })
        self.assertEqual(self.resource.x_ongoing_task_id, open_task,
                         "Ongoing task should be the open task linked to the resource")

        open_task.write({'state': '1_done', 'stage_id': self.stage_clean.id})
        self.assertFalse(self.resource.x_ongoing_task_id,
                         "Ongoing task should be empty when all tasks are closed")

    def test_x_is_in_stage_clean_computation(self):
        self.env['ir.config_parameter'].sudo().set_param('booking_engine.x_approvers_setting', '1')

        resource = self.env['resource.resource'].create({
            'name': 'Room 707',
            'resource_type': 'material',
        })
        task = self.env['project.task'].create({
            'name': 'Clean Task',
            'project_id': self.project.id,
            'x_resource_id': resource.id,
            'stage_id': self.stage_clean.id,
        })

        self.assertTrue(resource.x_is_in_stage_clean,
                        "Should be true when the ongoing task stage is clean")

        task.write({'stage_id': self.stage_to_clean.id})
        self.assertFalse(resource.x_is_in_stage_clean,
                         "Should be false when the ongoing task stage is not clean")

    def test_x_cleaning_color_computation(self):
        task = self.env['project.task'].create({
            'name': 'Cleaning Task',
            'project_id': self.project.id,
            'x_cleaning': 'checkout',
        })
        self.assertEqual(task.x_cleaning_color, 1,
                         "Cleaning color should be 1 for checkout cleaning type")

        task.write({'x_cleaning': 'stayover'})
        self.assertEqual(task.x_cleaning_color, 3,
                         "Cleaning color should be 3 for non-checkout cleaning type")

    def test_x_occupancy_color_computation(self):
        resource = self.env['resource.resource'].create({
            'name': 'Room 808',
            'resource_type': 'material',
            'x_occupancy': 'vacant',
        })
        self.assertEqual(resource.x_occupancy_color, 13,
                         "Occupancy color should be 13 for vacant occupancy")

        resource.write({'x_occupancy': 'occupied'})
        self.assertEqual(resource.x_occupancy_color, 3,
                         "Occupancy color should be 3 for non-vacant occupancy")
