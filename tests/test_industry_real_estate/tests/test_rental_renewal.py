# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta

from odoo import Command, fields
from odoo.tests import freeze_time, tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRentalContractRenew(TransactionCase):

    def _create_invoiced_subscription(self, *, with_property=False):
        partner = self.env['res.partner'].create({'name': 'OPW 6390673 Tenant'})
        vals = {
            'partner_id': partner.id,
            'plan_id': self.env.ref('sale_subscription.subscription_plan_month').id,
            'require_payment': False,
            'start_date': fields.Date.to_date('2026-01-15'),
            'end_date': fields.Date.to_date('2026-07-14'),
            'order_line': [Command.create({
                'product_id': self.env.ref('industry_real_estate.product_product_42').id,
                'product_uom_qty': 1,
                'price_unit': 1000,
            })],
        }
        extra = {'partner': partner, 'prop': self.env['x_property'], 'guarant': self.env['res.partner']}
        if with_property:
            guarant = self.env['res.partner'].create({'name': 'OPW 6390673 Guarant'})
            building = self.env['x_buildings'].create({'x_name': 'OPW 6390673 Building'})
            prop = self.env['x_property'].create({
                'x_name': 'OPW 6390673 Property',
                'x_building': building.id,
                'x_type': self.env.ref('property_assets_distribution.x_properties_types_office').id,
            })
            vals['x_property_id'] = prop.id
            vals['x_guarant_partner_id'] = guarant.id
            extra['prop'] = prop
            extra['guarant'] = guarant

        with freeze_time('2026-01-15'):
            order = self.env['sale.order'].create(vals)
            order.action_confirm()
            order._create_recurring_invoice()
            self.assertNotEqual(
                order.start_date, order.next_invoice_date,
                "The first period must be invoiced before creating a renewal",
            )
        extra['order'] = order
        return extra

    def test_primary_form_keeps_customer_label(self):
        arch = self.env['sale.order'].get_view(
            self.env.ref('sale_subscription.sale_subscription_primary_form_view').id,
        )['arch']
        self.assertNotIn('x_property_id', arch)
        self.assertNotIn('Tenant', arch)

    def test_rental_form_shows_property_fields(self):
        arch = self.env['sale.order'].get_view(
            self.env.ref('industry_real_estate.rental_form_view').id,
        )['arch']
        self.assertIn('x_property_id', arch)
        self.assertIn('x_guarant_partner_id', arch)
        self.assertIn('Tenant', arch)

    def test_normal_subscription_renew_keeps_primary_form(self):
        order = self._create_invoiced_subscription()['order']
        primary_form_id = self.env.ref('sale_subscription.sale_subscription_primary_form_view').id
        rental_form_id = self.env.ref('industry_real_estate.rental_form_view').id

        with freeze_time('2026-02-15'):
            action = order.prepare_renewal_order()

        views = action.get('views') or []
        self.assertIn((primary_form_id, 'form'), views)
        self.assertNotIn((rental_form_id, 'form'), views)
        renewal = self.env['sale.order'].browse(action['res_id'])
        self.assertFalse(renewal.x_property_id)

    def test_renewal_keeps_property_and_closes_previous_tenant(self):
        """Renewing a rental contract copies Property and does not overlap tenants."""
        data = self._create_invoiced_subscription(with_property=True)
        order, prop, guarant = data['order'], data['prop'], data['guarant']

        first_tenant = self.env['x_stake_holder'].search([
            ('x_property_id', '=', prop.id),
            ('x_type', '=', 'tenant'),
        ])
        self.assertEqual(len(first_tenant), 1)

        with freeze_time('2026-02-15'):
            renewal = self.env['sale.order'].browse(order.prepare_renewal_order()['res_id'])
            self.assertEqual(
                renewal.x_property_id, prop,
                "Renewal quotation should keep the Property from the parent contract",
            )
            self.assertEqual(renewal.x_guarant_partner_id, guarant)
            renewal.action_confirm()

        tenants = self.env['x_stake_holder'].search([
            ('x_property_id', '=', prop.id),
            ('x_type', '=', 'tenant'),
        ], order='x_start_date')
        self.assertEqual(len(tenants), 2)
        self.assertEqual(tenants[0].x_end_date, renewal.start_date - timedelta(days=1))
        self.assertEqual(tenants[1].x_start_date, renewal.start_date)
        self.assertLess(tenants[0].x_end_date, tenants[1].x_start_date)

    def test_leasing_renew_opens_rental_form(self):
        data = self._create_invoiced_subscription(with_property=True)
        order, prop = data['order'], data['prop']
        rental_form_id = self.env.ref('industry_real_estate.rental_form_view').id

        with freeze_time('2026-02-15'):
            action = self.env.ref('industry_real_estate.action_open_leasing_so_form').with_context(
                active_id=order.id,
                active_ids=[order.id],
                active_model='sale.order',
                leasing_so_method='prepare_renewal_order',
            ).run()

        views = action.get('views') or []
        self.assertEqual(
            action.get('id'),
            self.env.ref('industry_real_estate.action_rental_contracts').id,
            "Leasing renew must keep the Rental Contracts action so the client does not fall back to /sale.order/<id>",
        )
        self.assertIn((rental_form_id, 'form'), views)
        renewal = self.env['sale.order'].browse(action['res_id'])
        self.assertEqual(
            renewal.x_property_id, prop,
            "Leasing renew action should keep the Property from the parent contract",
        )
