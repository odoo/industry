from odoo import Command
from odoo.fields import Datetime
from datetime import timedelta

from .constructiondev_case import ConstructionDevCase


class ConstructionDevMRPCase(ConstructionDevCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.so = cls.env['sale.order'].create({
            'partner_id': cls.partner_1.id,
            'order_line': [Command.create({
                'product_id': cls.bom_product_1.id,
                'product_uom_qty': 100,
                'x_bom_id': cls.bom_1.id,
            })],
        })
        cls.sol = cls.so.order_line[0]


class WBSDeadlinesAutomationsTestCase(ConstructionDevMRPCase):
    def test_default_planned_end_and_deadline_sync(self):
        """ Tests 'automation_default_planned_end' and 'automation_on_date_planned_end_write' """

        # Create a standard MO (no backorder sequence)
        mo = self.env['mrp.production'].create({
            'product_id': self.bom_product_1.id,
            'product_qty': 10,
            'uom_id': self.bom_product_1.uom_id.id,
            'bom_id': self.bom_1.id,
        })

        expected_planned_end = mo.date_start + timedelta(hours=1)
        self.assertEqual(
            mo.x_date_planned_end,
            expected_planned_end,
            "Non-backorder MO should default x_date_planned_end to start + 1 hour."
        )

        # Automation 2: Should immediately push that planned end date to the date_deadline
        self.assertEqual(
            mo.date_deadline,
            mo.x_date_planned_end,
            "The date_deadline should automatically sync to match x_date_planned_end upon creation."
        )

    def test_overwrite_deadline_prevention(self):
        """ Tests 'automation_overwrite_deadline' """
        mo = self.env['mrp.production'].create({
            'product_id': self.bom_product_1.id,
            'product_qty': 10,
            'uom_id': self.bom_product_1.uom_id.id,
            'bom_id': self.bom_1.id,
        })
        original_planned_end = mo.x_date_planned_end
        rogue_deadline = original_planned_end + timedelta(days=5)

        mo.write({'date_deadline': rogue_deadline})
        # The automation should catch the write and force it back to match x_date_planned_end
        self.assertEqual(
            mo.date_deadline,
            original_planned_end,
            "The automation should not allow date_deadline to be changed independently of x_date_planned_end."
        )

    def _create_and_backorder_mo(self, start_date, planned_end_date):
        """ Helper method to generate an MO with specific dates and force a backorder """
        parent_mo = self.env['mrp.production'].create({
            'product_id': self.bom_product_1.id,
            'product_qty': 100,
            'uom_id': self.bom_product_1.uom_id.id,
            'bom_id': self.bom_1.id,
            'sale_line_id': self.sol.id,
        })
        parent_mo.action_confirm()

        # Write the dates AFTER confirm, because action_confirm natively recalculates dates
        parent_mo.write({
            'date_start': start_date,
            'x_date_planned_end': planned_end_date,
        })

        # Partial production to trigger backorder
        parent_mo.qty_producing = 50
        action_dict = parent_mo.button_mark_done()

        wizard_context = action_dict.get('context', {})
        backorder_wizard = self.env['mrp.production.backorder'].with_context(**wizard_context).create({})
        backorder_wizard.action_backorder()

        child_mo = self.env['mrp.production'].search([
            ('production_group_id', '=', parent_mo.production_group_id.id),
            ('id', '!=', parent_mo.id)
        ], limit=1)

        return parent_mo, child_mo

    # for MOs:
    # MO --(backorder)-> MO1 + MO2
    # MO dates: D1 - D2
    # MO1 : D1 - now
    # MO2 : now - D2

    def test_backorder_scenario_1_past_mo(self):
        """ Scenario A: date_start < x_date_planned_end < now (MO is overdue) """
        now = Datetime.now()
        start_date = now - timedelta(days=10)
        planned_end_date = now - timedelta(days=5)

        parent, child = self._create_and_backorder_mo(start_date, planned_end_date)

        # PARENT MO1 CHECKS
        self.assertEqual(parent.date_start, start_date, "Parent hasn't kept its original start date")
        self.assertAlmostEqual(parent.x_date_planned_end, now, delta=timedelta(seconds=10), msg="Parent isn't closed now")

        # CHILD MO2 CHECKS
        self.assertAlmostEqual(child.date_start, now, delta=timedelta(seconds=10), msg="Child doesn't start now")

        # Exception: The child inherits D2 (5 days ago), but the automation must
        # push it to tomorrow (child.date_start + 1 day) because we need to see it in the WBS
        expected_child_end = child.date_start + timedelta(days=1)
        self.assertAlmostEqual(
            child.x_date_planned_end, expected_child_end, delta=timedelta(seconds=10),
            msg="Child's end date not pushed to tomorrow",
        )

    def test_backorder_scenario_2_current_mo(self):
        """ Scenario B: date_start < now < x_date_planned_end (MO is currently running) """
        now = Datetime.now()
        start_date = now - timedelta(days=2)
        planned_end_date = now + timedelta(days=3)

        parent, child = self._create_and_backorder_mo(start_date, planned_end_date)

        # PARENT MO1 CHECKS
        self.assertEqual(parent.date_start, start_date, "Parent hasn't kept its original start date")
        self.assertAlmostEqual(parent.x_date_planned_end, now, delta=timedelta(seconds=10), msg="Parent isn't closed now")

        # CHILD MO2 CHECKS
        self.assertAlmostEqual(child.date_start, now, delta=timedelta(seconds=10), msg="Child doesn't start now")
        self.assertEqual(child.x_date_planned_end, planned_end_date, msg="Valid future date not retained")

    def test_backorder_scenario_3_future_mo(self):
        """ Scenario C: now < date_start < x_date_planned_end (MO hasn't started yet) """
        now = Datetime.now()
        start_date = now + timedelta(days=5)
        planned_end_date = now + timedelta(days=10)

        parent, child = self._create_and_backorder_mo(start_date, planned_end_date)

        # PARENT MO1 CHECKS
        self.assertEqual(parent.date_start, start_date, "Parent hasn't kept its original start date")
        self.assertAlmostEqual(parent.x_date_planned_end, now, delta=timedelta(seconds=10), msg="Parent isn't closed now")

        # CHILD MO2 CHECKS
        self.assertAlmostEqual(child.date_start, now, delta=timedelta(seconds=10), msg="Child doesn't start now")
        self.assertEqual(child.x_date_planned_end, planned_end_date, msg="Valid future date not retained")


class SoConfirmLinkMrpTestCase(ConstructionDevMRPCase):
    def test_assign_so_bom_if_route_option_enabled(self):
        """Tests 'field_sale_order_line_x_bom_id'"""
        sol = self.env['sale.order.line'].create({
            'order_id': self.so_1.id,
            'product_id': self.bom_product_1.id,
        })
        self.assertEqual(sol.x_bom_id, self.bom_1, "The SOL should have a BOM when adding a product with a BOM and a route that allows preselection")

        self.env.ref('construction_developer.stock_route_on_site_consumption_bom')['x_allow_sol_preselect'] = False
        sol_2 = self.env['sale.order.line'].create({
            'order_id': self.so_1.id,
            'product_id': self.bom_product_1.id,
        })
        self.assertFalse(sol_2.x_bom_id, "The SOL should not have a BOM when adding a product with a BOM and no route allows preselection")

    def test_duplicate_bom_sets_name_and_link(self):
        """Tests 'action_duplicate_bom'"""
        sol = self.env['sale.order.line'].create({
            'order_id': self.so_1.id,
            'product_id': self.bom_product_1.id,
        })

        duplicated_bom = self.env.ref('construction_developer.action_duplicate_bom').with_context(bom=self.bom_1, bom_sol=sol).run()
        self.assertEqual(duplicated_bom.x_original_sol_id, sol, "The duplicate should be linked back to the SOL it was made for")
        self.assertEqual(sol.x_bom_id, duplicated_bom, "The SOL's BOM should be updated to the duplicate")
        self.assertEqual(
            duplicated_bom.code, f"{sol.x_reference} - {self.partner_1.name}",
            "The duplicated BOM should be named after the SOL reference and the partner, without a suffix since the original was the (unnamed) 'Template' BOM",
        )
        self.assertEqual(
            duplicated_bom.bom_line_ids.mapped('product_id'), self.bom_1.bom_line_ids.mapped('product_id'),
            "The duplicate should have the same components as the original",
        )

        # Duplicating a BOM that already has a custom (non-'Template') code should keep that code as a suffix
        duplicated_bom_2 = self.env.ref('construction_developer.action_duplicate_bom').with_context(bom=duplicated_bom, bom_sol=sol).run()
        self.assertEqual(
            duplicated_bom_2.code, f"{sol.x_reference} - {self.partner_1.name} - {duplicated_bom.code}",
            "Duplicating a non-template BOM should keep its code in the new name",
        )

    def test_mo_created_from_so_confirm_gets_worksite_location_and_bom(self):
        """Tests 'automation_on_mo_creation' and 'action_apply_locations_on_mo'"""
        project = self.env['project.project'].create({'name': 'Test Project'})
        so = self.env['sale.order'].create({
            'partner_id': self.partner_1.id,
            'project_id': project.id,
            'order_line': [Command.create({
                'product_id': self.bom_product_1.id,
                'product_uom_qty': 10,
            })],
        })
        sol = so.order_line[0]
        self.assertEqual(sol.x_bom_id, self.bom_1, "The SOL should have auto-selected the template BOM before confirmation")

        so.action_confirm()

        mo = self.env['mrp.production'].search([('sale_line_id', '=', sol.id)])
        self.assertTrue(mo, "Confirming the SO should have generated a Manufacturing Order")
        self.assertEqual(
            mo.location_src_id, self.partner_1.x_ws_location_id,
            "The MO should source from the customer's specific worksite location, not the generic Worksites parent",
        )
        self.assertEqual(mo.project_id, project, "The MO should be linked to the SO's project")
        self.assertNotEqual(mo.bom_id, self.bom_1, "The MO should use a duplicated BOM, not the shared template")
        self.assertEqual(mo.bom_id.x_original_sol_id, sol, "The duplicated BOM used on the MO should be linked back to the SOL")
        self.assertEqual(sol.x_bom_id, mo.bom_id, "The SOL's BOM should now point to the duplicate used on the MO")
        self.assertNotEqual(mo.state, 'draft', "The automation should have confirmed (and started) the MO")


class DeliveryProgressTestCase(ConstructionDevMRPCase):
    def _create_mo(self, product_qty):
        mo = self.env['mrp.production'].create({
            'product_id': self.bom_product_1.id,
            'product_qty': product_qty,
            'uom_id': self.bom_product_1.uom_id.id,
            'bom_id': self.bom_1.id,
            'sale_line_id': self.sol.id,
        })
        mo.action_confirm()
        return mo

    def test_increment_percent_and_quantity_sync(self):
        """Tests 'automation_update_progress_increment_percent_on_write' and 'automation_update_quantity_increment_on_write'"""
        mo = self._create_mo(100)

        mo.qty_producing = 25
        self.assertEqual(mo.x_increment_percent, 0.25, "Writing the quantity producing should update the increment percent")

        mo.x_increment_percent = 0.5
        self.assertEqual(mo.qty_producing, 50, "Writing the increment percent should update the quantity producing")

    def test_delivered_and_cumulated_progress(self):
        """Tests 'field_mrp_production_x_total_qty', 'x_delivered_qty', 'x_delivered_percent',
        'x_cumulated_qty' and 'x_cumulated_percent'"""
        mo_done = self._create_mo(60)
        mo_done.qty_producing = 60
        mo_done.button_mark_done()

        mo_in_progress = self._create_mo(40)
        mo_in_progress.qty_producing = 10

        self.assertEqual(mo_in_progress.x_total_qty, 100, "The total quantity should be the sum of both MOs of the SOL")
        self.assertEqual(mo_in_progress.x_delivered_qty, 60, "Only the done MO should count towards the delivered quantity")
        self.assertEqual(mo_in_progress.x_delivered_percent, 60.0)
        self.assertEqual(mo_in_progress.x_cumulated_qty, 70, "The cumulated quantity should add the in-progress MO's producing quantity")
        self.assertEqual(mo_in_progress.x_cumulated_percent, 70.0)
