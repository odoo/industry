from .constructiondev_case import ConstructionDevCase


class BOMTemplateTestCase(ConstructionDevCase):
    def test_auto_assign_routes_on_product_when_bom_template(self):
        """Tests 'automation_set_product_routes_on_add_bom_write' and 'automation_set_product_routes_on_unlink_bom'"""
        prod = self._create_product("Product no BOM")
        self.assertEqual(sorted([
                self.env.ref('purchase_stock.route_warehouse0_buy').id,
                self.env.ref('construction_developer.stock_route_warehouse_on_site_delivery').id,
                self.env.ref('construction_developer.stock_route_on_site_consumption_goods').id,
            ]),
            sorted(prod.product_tmpl_id.route_ids.ids),
            "The product should have these three routes set by default",
        )

        bom = self._create_bom(prod.product_tmpl_id)
        self.assertEqual(
            [self.env.ref('construction_developer.stock_route_on_site_consumption_bom').id],
            prod.product_tmpl_id.route_ids.ids,
            "The product should have this route set when creating a BOM",
        )

        bom.unlink()
        self.assertEqual(sorted([
                self.env.ref('purchase_stock.route_warehouse0_buy').id,
                self.env.ref('construction_developer.stock_route_warehouse_on_site_delivery').id,
                self.env.ref('construction_developer.stock_route_on_site_consumption_goods').id,
            ]),
            sorted(prod.product_tmpl_id.route_ids.ids),
            "The product should have this three routes set by default",
        )

    def test_create_first_bom_sets_it_as_bom_template(self):
        """Tests 'automation_set_default_product_bom_on_bom_create'"""
        product_no_bom = self._create_product("Product no BOM")
        self.assertFalse(self.env['mrp.bom'].search([('product_tmpl_id', 'in', product_no_bom.product_tmpl_id.ids)], limit=1),
                        "No bom should exist yet for that product")

        bom = self._create_bom(product_no_bom.product_tmpl_id)
        self.assertTrue(bom.x_is_template,
                        "The first BOM created for a product should be set as a BOM template")
        self.assertEqual(product_no_bom.x_bom_template_id, bom,
                        "The product should have the BOM set as a template after creating it")

        bom_2 = self._create_bom(product_no_bom.product_tmpl_id)
        self.assertFalse(bom_2.x_is_template,
                        "The second BOM created for a product should not be set as a BOM template")
        self.assertNotEqual(product_no_bom.x_bom_template_id, bom_2,
                        "The product should still have the first BOM set as a template after creating a second one")

        self._run_action_on_ids('construction_developer.action_set_template_bom_on_product', bom_2)
        self.assertEqual(product_no_bom.x_bom_template_id, bom_2,
                        "The action should set the BOM as a template")

    def test_bom_template_code_reflects_is_template(self):
        """Tests 'automation_set_bom_template_code_on_x_is_template_write'.
        Note: 'x_is_template' only forces a write() (and so triggers this automation) when it
        becomes True; reading the field is what forces its (otherwise lazy) recompute, so this
        test checks 'x_is_template' before checking 'code' on each BOM."""
        product = self._create_product("Product no BOM")
        bom_1 = self._create_bom(product.product_tmpl_id)
        self.assertTrue(bom_1.x_is_template)
        self.assertEqual(bom_1.code, "Template", "The template BOM's code should be set to 'Template'")

        bom_2 = self._create_bom(product.product_tmpl_id)
        self.assertFalse(bom_2.x_is_template)
        self.assertNotEqual(bom_2.code, "Template", "A non-template BOM's code should not be 'Template'")

        self._run_action_on_ids('construction_developer.action_set_template_bom_on_product', bom_2)
        self.assertTrue(bom_2.x_is_template)
        self.assertEqual(bom_2.code, "Template", "The newly promoted template BOM's code should become 'Template'")
        self.assertFalse(bom_1.x_is_template)
        self.assertFalse(bom_1.code, "The old template's code should be cleared after losing its template status")

    def test_bom_available_compute(self):
        """Tests 'field_product_template_x_bom_available'"""
        product = self._create_product("Product no BOM")
        self.assertFalse(product.product_tmpl_id.x_bom_available, "A product without any BOM should not have a BOM available")

        bom = self._create_bom(product.product_tmpl_id)
        # x_bom_available has no 'depends', so its cached value isn't auto-invalidated by the BOM creation
        self.env.invalidate_all()
        self.assertTrue(product.product_tmpl_id.x_bom_available, "A product with a BOM should have a BOM available")

        bom.unlink()
        self.env.invalidate_all()
        self.assertFalse(product.product_tmpl_id.x_bom_available, "A product without any BOM anymore should not have a BOM available")

    def test_open_bom_action_duplicates_bom_and_reuses_existing_copy(self):
        """Tests 'action_open_bom' (the wand icon on the SOL) and 'action_duplicate_bom'"""
        sol = self.env['sale.order.line'].create({
            'order_id': self.so_1.id,
            'product_id': self.bom_product_1.id,
        })
        self.assertEqual(sol.x_bom_id, self.bom_1, "The SOL should have auto-selected the template BOM")

        action = self._run_action_on_ids('construction_developer.action_open_bom', sol)
        duplicated_bom = sol.x_bom_id
        self.assertNotEqual(duplicated_bom, self.bom_1, "Opening the BOM should duplicate it for this SOL")
        self.assertEqual(duplicated_bom.x_original_sol_id, sol, "The duplicate should be linked back to the SOL")
        self.assertEqual(action['res_id'], duplicated_bom.id, "The action should open the duplicated BOM")

        action_2 = self._run_action_on_ids('construction_developer.action_open_bom', sol)
        self.assertEqual(sol.x_bom_id, duplicated_bom, "Opening the BOM a second time should not create another copy")
        self.assertEqual(action_2['res_id'], duplicated_bom.id, "The action should reopen the same duplicated BOM")
