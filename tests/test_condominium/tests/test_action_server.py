# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class CondominiumActionServerTestCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env["res.company"].create({
            "name": "Test Condominium SA",
            "country_id": cls.env.ref("base.be").id,
        })
        cls.env["account.chart.template"].try_loading("generic_coa", cls.company, install_demo=False)
        cls.owner_1 = cls.env["res.partner"].create({"name": "Alice Owner"})
        cls.owner_2 = cls.env["res.partner"].create({"name": "Bob Owner"})
        cls.building = cls.env["x_buildings"].create({"x_name": "Building A", "x_company_id": cls.company.id})
        cls.property_1 = cls._make_property("Apt 101", 70.0, cls.owner_1)
        cls.property_2 = cls._make_property("Apt 102", 30.0, cls.owner_2)
        cls.analytic_1 = cls._make_analytic("Analytic Apt 101", cls.owner_1, cls.property_1)
        cls.analytic_2 = cls._make_analytic("Analytic Apt 102", cls.owner_2, cls.property_2)
        cls.owner_line_1 = cls._make_owner_line(cls.property_1, cls.owner_1, cls.analytic_1, datetime.date(2026, 1, 1))
        cls.owner_line_2 = cls._make_owner_line(cls.property_2, cls.owner_2, cls.analytic_2, datetime.date(2026, 1, 1))
        cls.analytic_1.x_owner_line = cls.owner_line_1.id
        cls.analytic_2.x_owner_line = cls.owner_line_2.id
        cls.product = cls.env["product.product"].create({"name": "Maintenance Service", "type": "service"})
        cls.distribution_key = cls._make_distribution_key(
            "Standard Distribution Key",
            ratio_ids=[
                Command.create({"x_owner": cls.owner_1.id, "x_property_ratios": cls.property_1.id, "x_ratio": 60.0}),
                Command.create({"x_owner": cls.owner_2.id, "x_property_ratios": cls.property_2.id, "x_ratio": 40.0}),
            ],
        )
        cls.meter = cls.env["x_meters"].create({"x_name": "Water Meter"})
        cls.event = cls.env["calendar.event"].create({
            "name": "General Assembly",
            "x_condominium": cls.company.id,
        })
        cls.motion = cls.env["x_motion"].create({
            "x_name": "Elevator Repair",
            "x_calendar_event_id": cls.event.id,
        })
        cls.action_split_so = cls.env.ref("condominium.ir_act_server_split_per_property")
        cls.action_distribute_costs = cls.env.ref("condominium.ir_actions_server_distribute_costs")
        cls.action_compute_meter = cls.env.ref("condominium.action_server_set_usage_meter_reading")
        cls.action_split_analytic = cls.env.ref("condominium.split_analytic_item_action")
        cls.analytic_plan_col = cls.env.ref("condominium.account_analytic_plan_2")._column_name()
        cls.action_populate_distribution_key = cls.env.ref("condominium.action_populate_distribution_key")
        cls.action_compute_ratios = cls.env.ref("condominium.action_compute_distribution_key_ratios")
        cls.action_update_voter_line = cls.env.ref("condominium.action_update_voter_line_for_motion")
        cls.action_confirm_split = cls.env.ref("condominium.confirm_analytic_account_item_split_action")

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    @classmethod
    def _make_property(cls, name, area, owner):
        return cls.env["x_property"].create({
            "x_name": name,
            "x_building": cls.building.id,
            "x_company_id": cls.company.id,
            "x_area": area,
            "x_current_owner": owner.id if owner else False,
        })

    @classmethod
    def _make_analytic(cls, name, owner, prop):
        return cls.env["account.analytic.account"].create({
            "name": name,
            "partner_id": owner.id,
            "x_property": prop.id,
        })

    @classmethod
    def _make_owner_line(cls, prop, owner, analytic, start_date, end_date=False):
        return cls.env["x_property_owner"].create({
            "x_property_id": prop.id,
            "x_owner": owner.id,
            "x_start_date": start_date,
            "x_end_date": end_date,
            "x_account": analytic.id,
        })

    @classmethod
    def _make_distribution_key(cls, name, based_on="Shares", ratio_ids=None, meter=None):
        vals = {
            "x_name": name,
            "x_company_id": cls.company.id,
        }
        if based_on:
            vals["x_based_on"] = based_on
        if ratio_ids is not None:
            vals["x_ratio_ids"] = ratio_ids
        if meter:
            vals["x_meter"] = meter.id
        return cls.env["x_distribution_key"].create(vals)

    def _make_bill(self, distribution_key, price_unit, name="Service", period_start=None, period_end=None):
        vals = {
            "move_type": "in_invoice",
            "partner_id": self.owner_1.id,
            "company_id": self.company.id,
            "x_distribution_key": distribution_key.id,
            "invoice_line_ids": [
                Command.create({"product_id": self.product.id, "name": name, "price_unit": price_unit}),
            ],
        }
        if period_start:
            vals["x_period_start"] = period_start
        if period_end:
            vals["x_period_end"] = period_end
        return self.env["account.move"].create(vals)

    def _make_reading(self, prop, date, quantity):
        return self.env["x_meter_reading"].create({
            "x_meter_id": self.meter.id,
            "x_property": prop.id,
            "x_date": date,
            "x_quantity": quantity,
        })

    def _make_analytic_line(self, name, amount, analytic_account=None):
        analytic = analytic_account or self.analytic_1
        return self.env["account.analytic.line"].create({
            "name": name,
            "amount": amount,
            self.analytic_plan_col: analytic.id,
        })

    def _run_action(self, action, records):
        return action.with_context(
            active_id=records[:1].id,
            active_ids=records.ids,
            active_model=records._name,
        ).run()

    # -------------------------------------------------------------------------
    # Server Action: Condominium: Split SO per Property
    # -------------------------------------------------------------------------

    def test_split_so_per_owner(self):
        so = self.env["sale.order"].create({
            "partner_id": self.owner_1.id,
            "company_id": self.company.id,
        })
        with self.assertRaises(UserError):
            self._run_action(self.action_split_so, so)

        master_so = self.env["sale.order"].create({
            "partner_id": self.owner_1.id,
            "company_id": self.company.id,
            "x_distribution_key": self.distribution_key.id,
            "order_line": [
                Command.create({"product_id": self.product.id, "name": "Common Area Roof Maintenance", "price_unit": 1000.0}),
            ],
        })
        self._run_action(self.action_split_so, master_so)

        self.assertEqual(master_so.state, "cancel", "Original master SO must be cancelled.")
        child_sos = self.env["sale.order"].search([("x_source_sales_order", "=", master_so.id)])
        self.assertEqual(
            len(child_sos),
            len(self.distribution_key.x_ratio_ids.mapped("x_owner")),
            "One child Sales Order should be created per owner in the distribution key.",
        )
        alice_so = child_sos.filtered(lambda s: s.partner_id == self.owner_1)
        bob_so = child_sos.filtered(lambda s: s.partner_id == self.owner_2)
        self.assertEqual(alice_so.order_line.price_unit, 600.0, "Owner 1 pays 60% of original price.")
        self.assertEqual(bob_so.order_line.price_unit, 400.0, "Owner 2 pays 40% of original price.")
        self.assertEqual(sum(child_sos.mapped("amount_untaxed")), 1000.0, "Sum of child SOs must equal original amount.")
        self.assertEqual(alice_so.order_line.analytic_distribution, {str(self.analytic_1.id): 100}, "Alice SO line must distribute 100% to analytic_1.")
        self.assertEqual(bob_so.order_line.analytic_distribution, {str(self.analytic_2.id): 100}, "Bob SO line must distribute 100% to analytic_2.")

    # -------------------------------------------------------------------------
    # Server Action: Condominium: Distribute Costs
    # -------------------------------------------------------------------------

    def test_distribute_costs_shares(self):
        bill = self._make_bill(self.distribution_key, 5000.0, "Elevator Maintenance")
        self._run_action(self.action_distribute_costs, bill)
        self.assertEqual(
            bill.invoice_line_ids.analytic_distribution,
            {str(self.analytic_1.id): 60.0, str(self.analytic_2.id): 40.0},
            "Costs should be distributed 60/40 according to distribution key shares.",
        )

    def test_distribute_costs_shares_with_overlapping_period(self):
        self.owner_line_2.write({"x_end_date": datetime.date(2026, 1, 10)})
        owner_3 = self.env["res.partner"].create({"name": "Charlie Owner"})
        analytic_3 = self._make_analytic("Analytic Apt 102 (New Owner)", owner_3, self.property_2)
        owner_line_3 = self._make_owner_line(self.property_2, owner_3, analytic_3, datetime.date(2026, 1, 11))
        analytic_3.x_owner_line = owner_line_3.id

        bill = self._make_bill(
            self.distribution_key,
            2000.0,
            "Heating Fuel",
            period_start=datetime.date(2026, 1, 1),
            period_end=datetime.date(2026, 1, 20),
        )
        self._run_action(self.action_distribute_costs, bill)
        self.assertEqual(
            bill.invoice_line_ids.analytic_distribution,
            {str(self.analytic_1.id): 60.0, str(self.analytic_2.id): 20.0, str(analytic_3.id): 20.0},
            "Costs should be prorated across consecutive ownership periods.",
        )

    def test_distribute_costs_meter_readings(self):
        meter_distribution_key = self._make_distribution_key(
            "Water Meter Key",
            based_on="Meter Readings",
            meter=self.meter,
        )
        self._make_reading(self.property_1, datetime.date(2026, 1, 1), 100.0)
        self._make_reading(self.property_1, datetime.date(2026, 1, 31), 180.0)
        self._make_reading(self.property_2, datetime.date(2026, 1, 1), 200.0)
        self._make_reading(self.property_2, datetime.date(2026, 1, 31), 220.0)
        bill = self._make_bill(
            meter_distribution_key,
            1000.0,
            "Water Consumption Bill",
            period_start=datetime.date(2026, 1, 1),
            period_end=datetime.date(2026, 1, 31),
        )
        self._run_action(self.action_distribute_costs, bill)
        self.assertEqual(
            bill.invoice_line_ids.analytic_distribution,
            {str(self.analytic_1.id): 80.0, str(self.analytic_2.id): 20.0},
            "Costs should be distributed based on meter consumption ratio (80/20).",
        )

    # -------------------------------------------------------------------------
    # Server Action: Condominium: Compute Meter Reading Consumption
    # -------------------------------------------------------------------------

    def test_compute_meter_usage(self):
        first_reading = self._make_reading(self.property_1, datetime.date(2026, 1, 1), 100.0)
        second_reading = self._make_reading(self.property_1, datetime.date(2026, 2, 1), 150.0)
        latest_reading = self._make_reading(self.property_1, datetime.date(2026, 3, 1), 220.0)
        # Property 2 has only a single reading with no prior initial reading
        property_2_reading = self._make_reading(self.property_2, datetime.date(2026, 1, 1), 200.0)

        self._run_action(self.action_compute_meter, latest_reading)
        self._run_action(self.action_compute_meter, property_2_reading)

        self.assertEqual(first_reading.x_usage, 0.0, "First meter reading usage should be 0.")
        self.assertEqual(second_reading.x_usage, 50.0, "Second meter reading usage should be delta from first (150 - 100).")
        self.assertEqual(latest_reading.x_usage, 70.0, "Latest meter reading usage should be delta from second (220 - 150).")
        self.assertEqual(property_2_reading.x_usage, 0.0, "Property with no prior initial reading should have usage 0.0.")

    # -------------------------------------------------------------------------
    # Server Action: Condominium: Split Analytic Item
    # -------------------------------------------------------------------------

    def test_split_analytic_item(self):
        """Split analytic line into wizard with 2 half amounts, or raise on zero."""
        # 1. Zero amount raises
        zero_line = self._make_analytic_line("Zero Line", 0.0)
        with self.assertRaises(UserError):
            self._run_action(self.action_split_analytic, zero_line)

        # 2. Valid split creates wizard with 2 lines
        line = self._make_analytic_line("Roof Maintenance", 1000.0)
        result = self._run_action(self.action_split_analytic, line)
        self.assertEqual(result["res_model"], "x_split_analytic_items_wizard", "Action must open the split analytic items wizard.")
        wizard = self.env["x_split_analytic_items_wizard"].browse(result["res_id"])
        self.assertEqual(wizard.x_total, 1000.0, "Wizard total must equal original line amount.")
        self.assertEqual(len(wizard.x_line_ids), 2, "Wizard should contain exactly 2 split lines.")
        self.assertEqual(wizard.x_line_ids.mapped("x_amount"), [500.0, 500.0], "Each line must have half the original amount.")
        for split_line in wizard.x_line_ids:
            self.assertEqual(split_line.x_analytic_account_id, self.analytic_1, "Each split line must retain analytic account.")
            self.assertEqual(split_line.x_analytic_line_id, line, "Each split line must reference original line.")

    # -------------------------------------------------------------------------
    # Server Action: Condominium: Confirm Account Analytic Line Split
    # -------------------------------------------------------------------------

    def test_confirm_analytic_split(self):
        """Confirm split validates 100% share sum, zeroes original, and creates note."""
        analytic_line = self._make_analytic_line("Roof Maintenance", 1000.0)

        # 1. Shares not summing to 100 raises UserError
        bad_wizard = self.env["x_split_analytic_items_wizard"].create({
            "x_total": 1000.0,
            "x_line_ids": [
                Command.create({"x_analytic_line_id": analytic_line.id, "x_analytic_account_id": self.analytic_1.id, "x_amount": 600.0}),
                Command.create({"x_analytic_line_id": analytic_line.id, "x_analytic_account_id": self.analytic_2.id, "x_amount": 300.0}),
            ],
        })
        with self.assertRaises(UserError):
            self._run_action(self.action_confirm_split, bad_wizard)

        # 2. Valid split confirms, zeroes original, writes notes
        wizard = self.env["x_split_analytic_items_wizard"].create({
            "x_total": 1000.0,
            "x_line_ids": [
                Command.create({"x_analytic_line_id": analytic_line.id, "x_analytic_account_id": self.analytic_1.id, "x_amount": 600.0}),
                Command.create({"x_analytic_line_id": analytic_line.id, "x_analytic_account_id": self.analytic_2.id, "x_amount": 400.0}),
            ],
        })
        existing_line_ids = self.env["account.analytic.line"].search([]).ids
        self._run_action(self.action_confirm_split, wizard)

        self.assertEqual(analytic_line.amount, 0.0, "Original line amount should be zeroed after split.")
        self.assertTrue(analytic_line.x_notes, "Original line should have explanatory note.")
        split_lines = self.env["account.analytic.line"].search([
            ("id", "not in", existing_line_ids),
            ("amount", "!=", 0.0),
        ])
        self.assertEqual(len(split_lines), 2, "Two new non-zero split lines should be created.")
        self.assertCountEqual(split_lines.mapped("amount"), [600.0, 400.0], "Split amounts must match wizard line amounts.")
        self.assertTrue(all(split_line.x_notes for split_line in split_lines), "Each split line should have split notes.")

    # -------------------------------------------------------------------------
    # Server Action: Condominium: Populate Distribution Key
    # -------------------------------------------------------------------------

    def test_populate_distribution_key(self):
        key = self._make_distribution_key("Key to Populate")
        self._run_action(self.action_populate_distribution_key, key)
        self.assertEqual(len(key.x_ratio_ids), 2, "Distribution key should populate ratios for all properties in company.")
        property_1_ratio = key.x_ratio_ids.filtered(lambda r: r.x_property_ratios == self.property_1)
        property_2_ratio = key.x_ratio_ids.filtered(lambda r: r.x_property_ratios == self.property_2)
        self.assertEqual(property_1_ratio.x_ratio, 70.0, "Property 1 ratio should be 70% proportional to area (70/100).")
        self.assertEqual(property_2_ratio.x_ratio, 30.0, "Property 2 ratio should be 30% proportional to area (30/100).")

        # Re-running is idempotent
        self._run_action(self.action_populate_distribution_key, key)
        self.assertEqual(len(key.x_ratio_ids), 2, "Re-populating distribution key should be idempotent.")

    # -------------------------------------------------------------------------
    # Server Action: Condominium: Compute Distribution Key Ratios
    # -------------------------------------------------------------------------

    def test_compute_distribution_key_ratios(self):
        # 1. Zero total area raises UserError
        zero_key = self._make_distribution_key("Zero Area Key")
        with self.assertRaises(UserError):
            self._run_action(self.action_compute_ratios, zero_key)

        # 2. Computes percentage based on x_area
        key = self._make_distribution_key(
            "Area Key",
            ratio_ids=[
                Command.create({"x_property_ratios": self.property_1.id}),
                Command.create({"x_property_ratios": self.property_2.id}),
            ],
        )
        self._run_action(self.action_compute_ratios, key)
        ratio_1 = key.x_ratio_ids.filtered(lambda r: r.x_property_ratios == self.property_1)
        ratio_2 = key.x_ratio_ids.filtered(lambda r: r.x_property_ratios == self.property_2)
        self.assertEqual(ratio_1.x_ratio, 70.0, "Ratio 1 must be 70% based on total area 100.")
        self.assertEqual(ratio_2.x_ratio, 30.0, "Ratio 2 must be 30% based on total area 100.")

    # -------------------------------------------------------------------------
    # Server Action: Condominium: Create Task from Motion
    # -------------------------------------------------------------------------

    def test_create_task_from_motion(self):
        project = self.env["project.project"].create({
            "name": "Condo Project",
            "partner_id": self.company.partner_id.id,
        })
        result = self._run_action(self.env.ref("condominium.action_create_task_from_motion"), self.motion)
        self.assertEqual(result["res_model"], "project.task", "Action should open a new project.task.")
        self.assertEqual(result["context"]["default_project_id"], project.id, "Default project should match company partner project.")
        self.assertEqual(result["context"]["default_name"], "Elevator Repair", "Default task name should match motion name.")
        self.assertEqual(result["context"]["default_partner_id"], self.company.partner_id.id, "Default customer should match company partner.")
        self.assertEqual(result["context"]["default_user_ids"], [self.env.user.id], "Default assigned user should be current user.")

    # -------------------------------------------------------------------------
    # Server Action: Condominium: Update Voter Line for Motion
    # -------------------------------------------------------------------------

    def test_update_voter_line_for_motion(self):
        attendee = self.env["calendar.attendee"].create({
            "event_id": self.event.id,
            "partner_id": self.owner_1.id,
            "x_attending": True,
        })

        # 1. Attending -> voter line is created
        self._run_action(self.action_update_voter_line, attendee)
        self.assertEqual(len(self.motion.x_attendee_vote_ids), 1, "Voter line should be created when attendee is attending.")
        self.assertEqual(self.motion.x_attendee_vote_ids.x_attendee_id, self.owner_1, "Voter attendee should match the attendee partner.")

        # 2. Not attending or delegating -> voter line is removed
        attendee.write({"x_attending": False, "x_delegating": False})
        self._run_action(self.action_update_voter_line, attendee)
        self.assertEqual(len(self.motion.x_attendee_vote_ids), 0, "Voter line should be removed when attendee is neither attending nor delegating.")

    # -------------------------------------------------------------------------
    # Server Action: Condominium: Set Votes All In Favor / All Against
    # -------------------------------------------------------------------------

    def test_set_votes_all_favor_and_against(self):
        vote_1 = self.env["x_motion_vote"].create({
            "x_motion_id": self.motion.id,
            "x_attendee_id": self.owner_1.id,
            "x_vote": "Abstention",
        })
        vote_2 = self.env["x_motion_vote"].create({
            "x_motion_id": self.motion.id,
            "x_attendee_id": self.owner_2.id,
            "x_vote": "Abstention",
        })

        # 1. Set all in favor
        self._run_action(self.env.ref("condominium.action_set_votes_as_all_favor"), self.motion)
        self.assertEqual(vote_1.x_vote, "In Favor", "Vote 1 should be set to 'In Favor'.")
        self.assertEqual(vote_2.x_vote, "In Favor", "Vote 2 should be set to 'In Favor'.")

        # 2. Set all against
        self._run_action(self.env.ref("condominium.action_set_votes_as_all_against"), self.motion)
        self.assertEqual(vote_1.x_vote, "Against", "Vote 1 should be set to 'Against'.")
        self.assertEqual(vote_2.x_vote, "Against", "Vote 2 should be set to 'Against'.")

    # -------------------------------------------------------------------------
    # Server Action: Condominium: Populate Voters
    # -------------------------------------------------------------------------

    def test_populate_voters_for_motion(self):
        self.env["calendar.attendee"].create({
            "event_id": self.event.id,
            "partner_id": self.owner_1.id,
            "x_attending": True,
        })
        self.env["calendar.attendee"].create({
            "event_id": self.event.id,
            "partner_id": self.owner_2.id,
            "x_attending": False,
            "x_delegating": False,
        })
        self._run_action(self.env.ref("condominium.action_populate_voters"), self.motion)
        self.assertEqual(len(self.motion.x_attendee_vote_ids), 1, "Only attending attendee should be populated as voter.")
        self.assertEqual(self.motion.x_attendee_vote_ids.x_attendee_id, self.owner_1, "Voter partner should match attending owner.")

    # -------------------------------------------------------------------------
    # Server Action: Condominium: Create Condominium Company
    # -------------------------------------------------------------------------

    def test_create_condominium_action(self):
        action = self.env.ref("condominium.ir_action_create_condominium")
        partner_no_country = self.env["res.partner"].create({"name": "Condo Without Country"})
        result_warning = self._run_action(action, partner_no_country)
        self.assertEqual(result_warning.get("tag"), "display_notification", "Should return display_notification when country is missing.")

        partner_with_country = self.env["res.partner"].create({
            "name": "Condo With Country",
            "country_id": self.env.ref("base.be").id,
        })
        result_reload = self._run_action(action, partner_with_country)
        self.assertEqual(result_reload.get("tag"), "reload", "Should return client reload action on successful creation.")
        created_company = self.env["res.company"].search([("partner_id", "=", partner_with_country.id)], limit=1)
        self.assertTrue(created_company, "New res.company should be created with partner_id set.")

    # -------------------------------------------------------------------------
    # Server Action: Condominium: Archive Related Accounts
    # -------------------------------------------------------------------------

    def test_archive_related_accounts(self):
        prop = self._make_property("Prop To Archive", 50.0, self.owner_1)
        analytic = self._make_analytic("Analytic To Archive", self.owner_1, prop)
        owner_line = self._make_owner_line(prop, self.owner_1, analytic, datetime.date(2026, 1, 1))
        analytic.x_owner_line = owner_line.id
        self.assertTrue(analytic.active, "Analytic account should initially be active.")

        self._run_action(self.env.ref("condominium.action_archive_related_accounts"), prop)
        self.assertFalse(analytic.active, "Analytic account should be archived after running action.")
