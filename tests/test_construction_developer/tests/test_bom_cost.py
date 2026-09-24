from .constructiondev_case import ConstructionDevCase


class BOMCostTestCase(ConstructionDevCase):
    def _mk_sol_50_margin(self, so, prod):
        return self.env['sale.order.line'].create({
            'order_id': so.id,
            'product_id': prod.id,
            'purchase_price': 20,
            'margin_percent': 0.5,
            'price_unit': 40,
        })

    def test_sol_bom_cost_update_on_bom_select(self):
        """Tests 'automation_sol_price_and_cost_on_x_bom_id_write', relying on the
        'field_sale_order_line_x_bom_id' auto-select compute (and the BOM-template
        routing) to set x_bom_id on the SOL"""
        sol = self._mk_sol_50_margin(self.so_1, self.bom_product_1)
        self.assertEqual(sol.x_bom_id, self.bom_1, "The SOL should have a BOM")
        self.assertEqual(
            (sol.purchase_price, sol.margin_percent, sol.price_unit),
            (150, 0.5, 300),
            "The values on the SOL should be set based on the computed BOM price when there is a BOM on the line",
        )

        self.bom_1.unlink()
        sol = self._mk_sol_50_margin(self.so_1, self.bom_product_1)
        self.assertFalse(sol.x_bom_id, "The SOL should not have a BOM")
        self.assertEqual(
            (sol.purchase_price, sol.margin_percent, sol.price_unit),
            (20, 0.5, 40),
            "The values on the SOL should not be set based on the computed BOM price when there is no BOM on the line",
        )

    def test_sol_bom_cost_product_change_registered(self):
        """Tests 'action_view_sale_order_line_bom_list' and 'field_mrp_bom_x_bom_cost'"""
        sol = self._mk_sol_50_margin(self.so_1, self.bom_product_1)
        self.assertEqual(sol.x_bom_id, self.bom_1, "The SOL should have a BOM")
        self.assertEqual(
            (sol.purchase_price, sol.margin_percent, sol.price_unit),
            (150, 0.5, 300),
            "The values on the SOL should be set based on the computed BOM price when there is a BOM on the line",
        )
        # simulate the click of the button to open the window (computes the booleans)
        self._run_action_on_ids('construction_developer.action_view_sale_order_line_bom_list', self.so_1)
        self.assertFalse(
            sol.x_different_bom_cost,
            "The price of the BOM should be the same at SOL creation",
        )

        self.bom_comp_2.write({'standard_price': 100000})
        # Force the ORM to drop cached values so the compute method for x_bom_cost triggers again
        self.env.invalidate_all()
        # simulate the click of the button to open the window (computes the booleans)
        self._run_action_on_ids('construction_developer.action_view_sale_order_line_bom_list', self.so_1)
        self.assertTrue(
            sol.x_different_bom_cost,
            "The price of the SOL being different than the BOM's computed price should trigger the difference",
        )

        self._run_action_on_ids('construction_developer.action_update_sol_cost_price_margin_on_x_bom_id_write', sol)
        self.env.invalidate_all()
        # simulate the click of the button to open the window (computes the booleans)
        self._run_action_on_ids('construction_developer.action_view_sale_order_line_bom_list', self.so_1)
        self.assertFalse(
            sol.x_different_bom_cost,
            "After applying the price from the BOM on the SOL it should be the same",
        )

    def test_apply_to_selected_updates_multiple_sols(self):
        """Tests 'action_update_sol_cost_price_margin_on_x_bom_id_write' called on more than one SOL at once,
        like the 'Apply to Selected' button does from the list view"""
        bom_product_2 = self._create_product("Test Product with a BOM 2", standard_price=20)
        bom_2 = self._create_bom(bom_product_2.product_tmpl_id)
        self.env['mrp.bom.line'].create({'bom_id': bom_2.id, 'product_id': self.bom_comp_1.id})

        sol_1 = self._mk_sol_50_margin(self.so_1, self.bom_product_1)
        sol_2 = self._mk_sol_50_margin(self.so_1, bom_product_2)
        self.assertEqual(sol_1.x_bom_id, self.bom_1)
        self.assertEqual(sol_2.x_bom_id, bom_2)

        self.bom_comp_1.write({'standard_price': 1000})
        self.env.invalidate_all()

        self._run_action_on_ids('construction_developer.action_update_sol_cost_price_margin_on_x_bom_id_write', sol_1 + sol_2)
        self.assertEqual(sol_1.purchase_price, self.bom_1.x_bom_cost, "sol_1 should be updated by the multi-record action")
        self.assertEqual(sol_2.purchase_price, bom_2.x_bom_cost, "sol_2 should be updated by the multi-record action")

    def test_any_sol_bom_compute(self):
        """Tests 'field_sale_order_x_any_sol_bom'"""
        so = self.env['sale.order'].create({'partner_id': self.partner_1.id})
        self.assertFalse(so.x_any_sol_bom, "A new SO with no lines should not have any SOL with a BOM")

        no_bom_product = self._create_product("No BOM product")
        self.env['sale.order.line'].create({'order_id': so.id, 'product_id': no_bom_product.id})
        self.assertFalse(so.x_any_sol_bom, "A SO with only a SOL without a BOM should not have any SOL with a BOM")

        self.env['sale.order.line'].create({'order_id': so.id, 'product_id': self.bom_product_1.id})
        self.assertTrue(so.x_any_sol_bom, "A SO with a SOL that has a BOM should have x_any_sol_bom set")
