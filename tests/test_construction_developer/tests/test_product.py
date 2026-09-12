from odoo import Command
from odoo.fields import Date

from .constructiondev_case import ConstructionDevCase


class ProductCostVendorListTestCase(ConstructionDevCase):
    def _confirm_po(self, qty, price):
        po = self.env['purchase.order'].create({
            'partner_id': self.vendor.id,
            'order_line': [Command.create({
                'product_id': self.simple_product.id,
                'name': self.simple_product.name,
                'product_qty': qty,
                'uom_id': self.simple_product.uom_id.id,
                'price_unit': price,
            })],
        })
        po.button_confirm()
        return po

    def _post_vendor_bill(self, qty, price):
        move = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': self.vendor.id,
            'invoice_date': Date.today(),
            'invoice_line_ids': [Command.create({
                'product_id': self.simple_product.id,
                'quantity': qty,
                'price_unit': price,
            })],
        })
        move.action_post()
        return move

    def _supplier_infos(self):
        return self.env['product.supplierinfo'].search([
            ('partner_id', '=', self.vendor.id),
            ('product_tmpl_id', '=', self.simple_product.product_tmpl_id.id),
        ])

    def test_confirm_po_creates_vendor_pricelist_and_updates_cost(self):
        """Tests 'automation_update_product_cost_and_vendor_list_from_purchase_order'"""
        self._confirm_po(10, 100)

        supplier_infos = self._supplier_infos()
        self.assertEqual(len(supplier_infos), 1, "A single vendor pricelist tier should have been created")
        self.assertEqual((supplier_infos.min_qty, supplier_infos.price), (10, 100))
        self.assertEqual(self.simple_product.standard_price, 100, "The product cost should be updated to the PO price")

    def test_confirm_po_updates_existing_tier_on_matching_price_or_qty(self):
        """Tests the two update branches of 'action_update_product_cost_and_vendor_list'"""
        self._confirm_po(10, 100)

        # Same price (100), different qty (20): matches on price -> should update the min_qty of the SAME tier
        self._confirm_po(20, 100)
        supplier_infos = self._supplier_infos()
        self.assertEqual(len(supplier_infos), 1, "Matching on price should update the existing tier instead of creating a new one")
        self.assertEqual((supplier_infos.min_qty, supplier_infos.price), (20, 100))

        # Same qty (20), different price (90): matches on qty -> should update the price of the SAME tier
        self._confirm_po(20, 90)
        supplier_infos = self._supplier_infos()
        self.assertEqual(len(supplier_infos), 1, "Matching on qty should update the existing tier instead of creating a new one")
        self.assertEqual((supplier_infos.min_qty, supplier_infos.price), (20, 90))
        self.assertEqual(self.simple_product.standard_price, 90)

    def test_confirm_po_cleans_up_dominated_tiers(self):
        """Tests the cleanup step at the end of 'action_update_product_cost_and_vendor_list'"""
        self._confirm_po(20, 100)  # tier A: 20 units at 100
        self._confirm_po(10, 150)  # tier B: 10 units at 150, no existing tier matches -> new tier

        # A new, better price at the same qty as tier B (10): matches tier B on qty -> updates its price in place,
        # and the cleanup then removes tier A since (20, 100) is now dominated (min_qty >= 10 and price >= 90)
        self._confirm_po(10, 90)

        supplier_infos = self._supplier_infos()
        self.assertEqual(len(supplier_infos), 1, "The dominated tier should have been cleaned up")
        self.assertEqual((supplier_infos.min_qty, supplier_infos.price), (10, 90))

    def test_vendor_bill_posted_updates_cost_and_vendor_list(self):
        """Tests 'automation_update_product_cost_and_vendor_list_from_vendor_bill'"""
        self._post_vendor_bill(5, 60)

        supplier_infos = self._supplier_infos()
        self.assertEqual(len(supplier_infos), 1)
        self.assertEqual((supplier_infos.min_qty, supplier_infos.price), (5, 60))
        self.assertEqual(self.simple_product.standard_price, 60)


class CostNatureTestCase(ConstructionDevCase):
    def test_cost_nature_inherited_from_parent_category(self):
        """Tests 'automation_update_cost_nature_on_write' inheriting a cost nature from the parent"""
        parent = self.env['product.category'].create({'name': 'Parent Category', 'x_cost_nature': 'material'})
        child = self.env['product.category'].create({'name': 'Child Category', 'parent_id': parent.id})
        self.assertEqual(child.x_cost_nature, 'material', "A child category without its own cost nature should inherit its parent's")

    def test_cost_nature_child_override_kept(self):
        """Tests 'automation_update_cost_nature_on_write' not overriding an explicit child value"""
        parent = self.env['product.category'].create({'name': 'Parent Category', 'x_cost_nature': 'material'})
        child = self.env['product.category'].create({'name': 'Child Category', 'parent_id': parent.id, 'x_cost_nature': 'labour'})
        self.assertEqual(child.x_cost_nature, 'labour', "A child category with its own cost nature should not be overridden by its parent's")

    def test_uom_matches_category_compute(self):
        """Tests 'field_product_template_x_uom_matches_category'"""
        material_categ = self.env['product.category'].create({'name': 'Material Category', 'x_cost_nature': 'material'})
        equipment_categ = self.env['product.category'].create({'name': 'Equipment Category', 'x_cost_nature': 'equipment'})
        unit = self.env.ref('uom.product_uom_unit')
        hour = self.env.ref('uom.product_uom_hour')

        material_product = self._create_product("Material product", categ_id=material_categ.id, uom_id=unit.id)
        self.assertTrue(material_product.product_tmpl_id.x_uom_matches_category, "Material products are not concerned by the UOM/hour check")

        equipment_product = self._create_product("Equipment product", categ_id=equipment_categ.id, uom_id=unit.id)
        self.assertFalse(equipment_product.product_tmpl_id.x_uom_matches_category, "An equipment product not measured in hours should not match its category")

        equipment_product.product_tmpl_id.uom_id = hour
        self.assertTrue(equipment_product.product_tmpl_id.x_uom_matches_category, "An equipment product measured in hours should match its category")
