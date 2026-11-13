# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta

from odoo import Command, fields
from odoo.tests import freeze_time, tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRentalContractRenew(TransactionCase):

    def _create_invoiced_rental(self):
        partner = self.env['res.partner'].create({'name': 'OPW 6390673 Tenant'})
        guarant = self.env['res.partner'].create({'name': 'OPW 6390673 Guarant'})
        building = self.env['x_buildings'].create({'x_name': 'OPW 6390673 Building'})
        prop = self.env['x_property'].create({
            'x_name': 'OPW 6390673 Property',
            'x_building': building.id,
            'x_type': self.env.ref('property_assets_distribution.x_properties_types_office').id,
        })
        with freeze_time('2026-01-15'):
            order = self.env['sale.order'].create({
                'partner_id': partner.id,
                'plan_id': self.env.ref('sale_subscription.subscription_plan_month').id,
                'require_payment': False,
                'start_date': fields.Date.to_date('2026-01-15'),
                'end_date': fields.Date.to_date('2026-07-14'),
                'x_property_id': prop.id,
                'x_guarant_partner_id': guarant.id,
                'order_line': [Command.create({
                    'product_id': self.env.ref('industry_real_estate.product_product_42').id,
                    'product_uom_qty': 1,
                    'price_unit': 1000,
                })],
            })
            order.action_confirm()
            order._create_recurring_invoice()
            self.assertNotEqual(
                order.start_date, order.next_invoice_date,
                "The first period must be invoiced before creating a renewal",
            )
        return order, prop, guarant

    def test_leasing_renewal_keeps_property(self):
        """Leasing Renew copies Property, stays on the rental form, and does not overlap tenants."""
        order, prop, guarant = self._create_invoiced_rental()
        rental_form_id = self.env.ref('industry_real_estate.rental_form_view').id

        with freeze_time('2026-02-15'):
            action = self.env.ref('industry_real_estate.action_open_leasing_so_form').with_context(
                active_id=order.id,
                active_ids=[order.id],
                active_model='sale.order',
                leasing_so_method='prepare_renewal_order',
            ).run()
            self.assertEqual(
                action.get('id'),
                self.env.ref('industry_real_estate.action_rental_contracts').id,
                "Leasing renew must keep the Rental Contracts action so the client does not fall back to /sale.order/<id>",
            )
            self.assertIn((rental_form_id, 'form'), action.get('views') or [])
            renewal = self.env['sale.order'].browse(action['res_id'])
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
