from odoo import Command

from .constructiondev_case import ConstructionDevCase


class SolNumberingTestCase(ConstructionDevCase):
    def test_sol_numbering_sections_and_products(self):
        """Tests 'server_action_setup_sol_numbering' and 'field_sale_order_line_x_reference'"""
        so = self.env['sale.order'].create({
            'partner_id': self.partner_1.id,
            'order_line': [Command.create(vals) for vals in [
                {'display_type': 'line_section', 'name': 'Section A'},
                {'display_type': 'line_subsection', 'name': 'Subsection A.1'},
                {'product_id': self.simple_product.id, 'product_uom_qty': 1},
                {'product_id': self.simple_product.id, 'product_uom_qty': 1},
                {'display_type': 'line_subsection', 'name': 'Subsection A.2'},
                {'product_id': self.simple_product.id, 'product_uom_qty': 1},
                {'display_type': 'line_section', 'name': 'Section B'},
                {'display_type': 'line_subsection', 'name': 'Subsection B.1'},
                {'product_id': self.simple_product.id, 'product_uom_qty': 1},
            ]],
        })
        self.assertEqual(
            so.order_line.mapped('x_item_number'),
            ['1.', '1.1.', '1.1.1.', '1.1.2.', '1.2.', '1.2.1.', '2.', '2.1.', '2.1.1.'],
        )
        last_line = so.order_line[-1]
        self.assertEqual(
            last_line.x_reference, f"{so.name}.{last_line.x_item_number}",
            "The reference should combine the SO name and the line's item number",
        )

    def test_sol_numbering_updates_on_reorder(self):
        """Tests 'automation_update_sol_numbering_on_sol_change' (triggered by a sequence/parent_id change)"""
        so = self.env['sale.order'].create({
            'partner_id': self.partner_1.id,
            'order_line': [Command.create(vals) for vals in [
                {'product_id': self.simple_product.id, 'product_uom_qty': 1, 'sequence': 1},
                {'product_id': self.simple_product.id, 'product_uom_qty': 1, 'sequence': 2},
            ]],
        })
        first, second = so.order_line
        self.assertEqual((first.x_item_number, second.x_item_number), ('1.', '2.'))

        # Swap their order
        first.sequence, second.sequence = 2, 1
        self.assertEqual(
            (first.x_item_number, second.x_item_number), ('2.', '1.'),
            "Reordering the lines should renumber them to reflect their new positions",
        )

    def test_sol_numbering_updates_on_reorder_with_sections_and_subsections(self):
        """Tests 'automation_update_sol_numbering_on_sol_change' reordering multiple lines at the same time"""
        so = self.env['sale.order'].create({
            'partner_id': self.partner_1.id,
            'order_line': [Command.create(vals) for vals in [
                {'display_type': 'line_section', 'name': 'Section A', 'sequence': 1},
                {'display_type': 'line_subsection', 'name': 'Subsection A.1', 'sequence': 2},
                {'product_id': self.simple_product.id, 'product_uom_qty': 1, 'sequence': 3},
                {'display_type': 'line_subsection', 'name': 'Subsection A.2', 'sequence': 4},
                {'product_id': self.simple_product.id, 'product_uom_qty': 1, 'sequence': 5},
                {'display_type': 'line_section', 'name': 'Section B', 'sequence': 6},
                {'display_type': 'line_subsection', 'name': 'Subsection B.1', 'sequence': 7},
                {'product_id': self.simple_product.id, 'product_uom_qty': 1, 'sequence': 8},
            ]],
        })
        *_, subsection_a2, product_2, _, _, _ = so.order_line
        self.assertEqual(
            so.order_line.sorted('sequence').mapped('x_item_number'),
            ['1.', '1.1.', '1.1.1.', '1.2.', '1.2.1.', '2.', '2.1.', '2.1.1.'],
        )

        # Drag "Subsection A.2" (and its product) out of Section A, to the end of Section B
        subsection_a2.sequence = 9
        product_2.sequence = 10
        self.assertEqual(
            # 'order_line' is cached in its original creation order: re-sort by the new sequence values
            so.order_line.sorted('sequence').mapped('x_item_number'),
            ['1.', '1.1.', '1.1.1.', '2.', '2.1.', '2.1.1.', '2.2.', '2.2.1.'],
            "Section A should lose its second subsection, and Section B should gain it as a new, "
            "correctly-numbered second subsection, without disturbing what didn't move",
        )


class ContractTypeTestCase(ConstructionDevCase):
    def test_sol_contract_type_defaults_to_fixed_price(self):
        """Tests the ir.default on 'field_sale_order_line_sol_contract_type'"""
        sol = self.env['sale.order.line'].create({'order_id': self.so_1.id, 'product_id': self.simple_product.id})
        self.assertEqual(sol.x_sol_contract_type, 'fixed_price')

    def test_qty_delivered_state_compute(self):
        """Tests 'field_sale_order_line_qty_delivered_state'"""
        service_product = self._create_product("Manual Delivery Service", type='service', service_policy='delivered_manual')
        sol = self.env['sale.order.line'].create({
            'order_id': self.so_1.id,
            'product_id': service_product.id,
            'product_uom_qty': 10,
            'x_sol_contract_type': 'fixed_price',
        })
        self.assertFalse(sol.x_qty_delivered_state, "Not over-delivered yet: no state")

        sol.qty_delivered = 15
        self.assertEqual(sol.x_qty_delivered_state, 'danger', "Over-delivering a fixed price line should be a danger state")

        sol.x_sol_contract_type = 'open_book'
        self.assertEqual(sol.x_qty_delivered_state, 'warning', "Over-delivering an open book line should only be a warning state")

    def test_cumulated_percent_state_compute(self):
        """Tests 'field_mrp_production_x_cumulated_percent_state'"""
        so = self.env['sale.order'].create({
            'partner_id': self.partner_1.id,
            'order_line': [Command.create({
                'product_id': self.bom_product_1.id,
                'product_uom_qty': 10,
                'x_bom_id': self.bom_1.id,
                'x_sol_contract_type': 'fixed_price',
            })],
        })
        sol = so.order_line[0]
        mo = self.env['mrp.production'].create({
            'product_id': self.bom_product_1.id,
            'product_qty': 10,
            'uom_id': self.bom_product_1.uom_id.id,
            'bom_id': self.bom_1.id,
            'sale_line_id': sol.id,
        })
        mo.action_confirm()

        mo.x_increment_percent = 1.5
        self.assertEqual(mo.x_cumulated_percent_state, 'danger', "Being over 100% cumulated on a fixed price line should be a danger state")

        sol.x_sol_contract_type = 'open_book'
        self.assertEqual(mo.x_cumulated_percent_state, 'warning', "Being over 100% cumulated on an open book line should only be a warning state")

        mo.x_increment_percent = 0.5
        self.assertFalse(mo.x_cumulated_percent_state, "Being under 100% cumulated should have no state regardless of contract type")
