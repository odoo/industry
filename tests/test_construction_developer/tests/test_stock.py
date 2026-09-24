from odoo import Command

from .constructiondev_case import ConstructionDevCase


class DeliverySourceFromSOTestCase(ConstructionDevCase):
    def test_delivery_picking_source_set_from_so_worksite(self):
        """Tests 'automation_on_picking_creation' (so_confirm_link_stock.xml)"""
        goods_picking_type = self.env.ref('construction_developer.stock_picking_type_on_site_consumption_goods')
        self.partner_1.x_ws_location_id = self.env['stock.location'].create({
            'name': 'Test Worksite',
            'usage': 'internal',
            'location_id': self.env.ref('construction_developer.stock_location_worksites').id,
        })
        so = self.env['sale.order'].create({'partner_id': self.partner_1.id})

        picking = self.env['stock.picking'].create({
            'partner_id': self.partner_1.id,
            'picking_type_id': goods_picking_type.id,
            'sale_id': so.id,
            'location_dest_id': self.env.ref('stock.stock_location_customers').id,
        })
        self.assertEqual(
            picking.location_id, self.partner_1.x_ws_location_id,
            "The delivery's source should be the customer's specific worksite location, not the picking type's generic default",
        )

    def test_delivery_picking_source_untouched_without_so(self):
        """Tests the filter_domain guard of 'automation_on_picking_creation': a picking with no linked SO
        should keep its default source location"""
        goods_picking_type = self.env.ref('construction_developer.stock_picking_type_on_site_consumption_goods')
        self.partner_1.x_ws_location_id = self.env['stock.location'].create({
            'name': 'Test Worksite',
            'usage': 'internal',
            'location_id': self.env.ref('construction_developer.stock_location_worksites').id,
        })

        picking = self.env['stock.picking'].create({
            'partner_id': self.partner_1.id,
            'picking_type_id': goods_picking_type.id,
            'location_dest_id': self.env.ref('stock.stock_location_customers').id,
        })
        self.assertEqual(
            picking.location_id, goods_picking_type.default_location_src_id,
            "Without a linked SO, the picking should keep the picking type's default source location",
        )


class WorksiteLocationCreationTestCase(ConstructionDevCase):
    def test_so_confirm_creates_worksite_location_with_bom_sol(self):
        """Tests 'automation_create_delivery_location_on_so_confirm' (so_worksite_loc/bridge_so_bom_cost_updates.xml)
        actually creates the worksite location when the SO has a SOL with a BOM.

        NB: writes 'state' directly instead of calling 'action_confirm()' to keep this test focused on the
        location-creation automation, without also triggering the MO/procurement chain."""
        so = self.env['sale.order'].create({
            'partner_id': self.partner_1.id,
            'order_line': [Command.create({
                'product_id': self.bom_product_1.id,
                'product_uom_qty': 1,
                'x_bom_id': self.bom_1.id,
            })],
        })
        self.assertTrue(so.x_any_sol_bom, "Sanity check: this SO has a line with a BOM")
        self.assertEqual(so.partner_shipping_id, self.partner_1, "Sanity check: no separate delivery address")
        self.assertFalse(self.partner_1.x_ws_location_id)

        so.write({'state': 'sale'})

        location = self.partner_1.x_ws_location_id
        self.assertTrue(location, "A worksite location should have been created for the partner")
        self.assertEqual(
            location.location_id, self.env.ref('construction_developer.stock_location_worksites'),
            "The worksite location should be created under the Worksites parent location",
        )
        self.assertEqual(location.name, self.partner_1.name, "The worksite location should be named after the partner")
        self.assertEqual(location.usage, 'internal')
        self.assertTrue(location.replenish_location, "The worksite location should be replenishable")

    def test_so_confirm_does_not_create_worksite_location_without_any_bom_sol(self):
        """Tests 'automation_create_delivery_location_on_so_confirm' (so_worksite_loc/bridge_so_bom_cost_updates.xml)
        in isolation: it only fires when 'x_any_sol_bom' is True. A SO containing only non-BOM ('goods' route)
        products never gets a worksite location created on confirm.

        NB: writes 'state' directly instead of calling 'action_confirm()', since the latter also launches
        the procurement/delivery chain, which crashes for such a SO - see the test below."""
        no_bom_product = self._create_product("No BOM product")
        so = self.env['sale.order'].create({
            'partner_id': self.partner_1.id,
            'order_line': [Command.create({'product_id': no_bom_product.id, 'product_uom_qty': 1})],
        })
        self.assertFalse(so.x_any_sol_bom, "Sanity check: no line on this SO has a BOM")

        so.write({'state': 'sale'})
        self.assertFalse(
            self.partner_1.x_ws_location_id,
            "No worksite location should have been created since no SOL has a BOM",
        )

    def test_goods_delivery_source_untouched_without_worksite_location(self):
        """'automation_create_delivery_location_on_so_confirm' (above) only creates 'partner.x_ws_location_id'
        when 'x_any_sol_bom' is True, so a SO containing only non-BOM ('goods' route) products never gets
        one. 'automation_on_picking_creation' (so_confirm_link_stock.xml) must therefore not try to apply
        a worksite location in that case - it used to unconditionally force the delivery's required
        'location_id' to False (since x_ws_location_id was empty), which the database rejected and blew up
        'action_confirm()' entirely for such a SO. Its filter_domain now also requires
        'sale_id.partner_shipping_id.x_ws_location_id' to be set before touching the picking."""
        goods_picking_type = self.env.ref('construction_developer.stock_picking_type_on_site_consumption_goods')
        so = self.env['sale.order'].create({'partner_id': self.partner_1.id})
        self.assertFalse(self.partner_1.x_ws_location_id, "Sanity check: no worksite location exists for this partner")

        picking = self.env['stock.picking'].create({
            'partner_id': self.partner_1.id,
            'picking_type_id': goods_picking_type.id,
            'sale_id': so.id,
            'location_dest_id': self.env.ref('stock.stock_location_customers').id,
        })
        self.assertEqual(
            picking.location_id, goods_picking_type.default_location_src_id,
            "Without a worksite location to apply, the picking should keep the picking type's default source",
        )
