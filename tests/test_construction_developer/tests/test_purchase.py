from odoo import Command
from .constructiondev_case import ConstructionDevCase


class PurchaseDeliverySiteTestCase(ConstructionDevCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.on_site_picking_type = cls.env.ref('construction_developer.stock_picking_type_construction_vendor_on_site_delivery')
        cls.delivery_site = cls.env['stock.location'].create({
            'name': 'Test Worksite',
            'usage': 'internal',
            'location_id': cls.env.ref('construction_developer.stock_location_worksites').id,
        })

    def _create_po_line_vals(self, qty=5, price=10):
        return Command.create({
            'product_id': self.simple_product.id,
            'name': self.simple_product.name,
            'product_qty': qty,
            'uom_id': self.simple_product.uom_id.id,
            'price_unit': price,
        })

    def test_po_confirm_applies_delivery_site_to_receipt(self):
        """Tests 'automation_on_delivery_from_po_creation'"""
        po = self.env['purchase.order'].create({
            'partner_id': self.vendor.id,
            'picking_type_id': self.on_site_picking_type.id,
            'x_delivery_site_id': self.delivery_site.id,
            'order_line': [self._create_po_line_vals()],
        })
        self.assertNotEqual(
            self.delivery_site, self.on_site_picking_type.default_location_dest_id,
            "Sanity check: the chosen delivery site must differ from the picking type's default for this test to be meaningful",
        )

        po.button_confirm()

        self.assertTrue(po.picking_ids, "Confirming the PO should have generated a receipt")
        self.assertEqual(
            po.picking_ids.location_dest_id, self.delivery_site,
            "The receipt's destination should be the chosen delivery site, not the picking type's default",
        )

    def test_delivery_site_not_applied_when_destination_already_overridden(self):
        """Tests the guard in 'action_apply_locations_on_select_on_po_pickings' that leaves a destination
        alone once it no longer matches the picking type's default (see the comment on that automation
        explaining why it can't rely on trigger_field_ids)"""
        other_location = self.env.ref('stock.stock_location_stock')
        po = self.env['purchase.order'].create({
            'partner_id': self.vendor.id,
            'picking_type_id': self.on_site_picking_type.id,
            'x_delivery_site_id': self.delivery_site.id,
        })

        picking = self.env['stock.picking'].create({
            'partner_id': self.vendor.id,
            'picking_type_id': self.on_site_picking_type.id,
            'purchase_id': po.id,
            'location_id': self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id': other_location.id,
        })
        self.assertEqual(
            picking.location_dest_id, other_location,
            "A destination that was already set away from the picking type's default should be left untouched",
        )
