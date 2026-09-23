# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import Command
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class CondominiumComputedFieldsTestCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env["res.company"].create({
            "name": "CF Test Condominium",
            "country_id": cls.env.ref("base.be").id,
        })
        cls.owner_1, cls.owner_2, cls.owner_3 = cls.env["res.partner"].create([
            {"name": "Alice Owner"},
            {"name": "Bob Owner"},
            {"name": "Carol Owner"},
        ])
        cls.vendor = cls.env["res.partner"].create({
            "name": "Maintenance Vendor",
            "x_vendor_condominiums": [Command.link(cls.company.partner_id.id)],
        })
        cls.property_1 = cls._make_property("Apt 101", 60.0, cls.owner_1)
        cls.property_2 = cls._make_property("Apt 102", 30.0, cls.owner_2)
        cls.property_3 = cls._make_property("Apt 103", 10.0, cls.owner_3)
        cls.distribution_key = cls.env["x_distribution_key"].create({
            "x_name": "CF Voting Key",
            "x_company_id": cls.company.id,
            "x_ratio_ids": [
                Command.create({"x_owner": cls.owner_1.id, "x_property_ratios": cls.property_1.id, "x_ratio": 60.0}),
                Command.create({"x_owner": cls.owner_2.id, "x_property_ratios": cls.property_2.id, "x_ratio": 30.0}),
                Command.create({"x_owner": cls.owner_3.id, "x_property_ratios": cls.property_3.id, "x_ratio": 10.0}),
            ],
        })
        cls.event = cls.env["calendar.event"].create({
            "name": "General Meeting",
            "start": "2026-06-01 10:00:00",
            "stop": "2026-06-01 12:00:00",
            "x_condominium": cls.company.id,
            "x_voting_key_id": cls.distribution_key.id,
        })
        cls.attendee_1, cls.attendee_2, cls.attendee_3 = cls.env["calendar.attendee"].create([
            {"event_id": cls.event.id, "partner_id": cls.owner_1.id, "x_attending": True},
            {"event_id": cls.event.id, "partner_id": cls.owner_2.id, "x_attending": True},
            {"event_id": cls.event.id, "partner_id": cls.owner_3.id, "x_attending": False},
        ])
        cls.vote_criteria_majority = cls.env["x_vote_criteria"].create({
            "x_name": "Simple Majority",
            "x_acceptation_threshold": 0.5,
        })
        cls.vote_criteria_supermajority = cls.env["x_vote_criteria"].create({
            "x_name": "Super Majority",
            "x_acceptation_threshold": 0.75,
        })
        cls.parent_so = cls.env["sale.order"].create({
            "partner_id": cls.owner_1.id,
            "company_id": cls.company.id,
        })

    # Helpers

    @classmethod
    def _make_property(cls, name, area, owner):
        return cls.env["x_property"].create({
            "x_name": name,
            "x_company_id": cls.company.id,
            "x_area": area,
            "x_current_owner": owner.id if owner else False,
        })

    def _make_motion(self, vote_criteria=None, vote_map=None):
        motion = self.env["x_motion"].create({
            "x_name": "Test Motion",
            "x_calendar_event_id": self.event.id,
            "x_vote_criteria": vote_criteria.id if vote_criteria else False,
        })
        for partner, vote in (vote_map or {}).items():
            vote_line = motion.x_attendee_vote_ids.filtered(lambda v, p=partner: v.x_attendee_id == p)
            if vote_line:
                vote_line.x_vote = vote
            else:
                self.env["x_motion_vote"].create({
                    "x_motion_id": motion.id,
                    "x_attendee_id": partner.id,
                    "x_vote": vote,
                })
        return motion

    # Model: calendar.attendee (x_ratio)

    def test_attendee_ratio_matches_distribution_key(self):
        """x_ratio mirrors the owner's share in the event's distribution key."""
        self.assertEqual(self.attendee_1.x_ratio, 60.0, "Attendee 1 ratio should match its 60% key share")
        self.assertEqual(self.attendee_2.x_ratio, 30.0, "Attendee 2 ratio should match its 30% key share")
        self.assertEqual(self.attendee_3.x_ratio, 10.0, "Attendee 3 ratio should match its 10% key share")

    def test_attendee_ratio_zero_without_voting_key(self):
        """x_ratio must be 0 when the event has no voting key assigned."""
        event_no_key = self.env["calendar.event"].create({
            "name": "Meeting No Key",
            "start": "2026-07-01 10:00:00",
            "stop": "2026-07-01 12:00:00",
        })
        attendee = self.env["calendar.attendee"].create({
            "event_id": event_no_key.id,
            "partner_id": self.owner_1.id,
        })
        self.assertEqual(attendee.x_ratio, 0.0, "Attendee ratio should be 0.0 without voting key")

    # Model: calendar.event (x_attending_owners, x_attending_ratio)

    def test_attending_owners_count(self):
        """x_attending_owners counts attendees where x_attending or x_delegating is True."""
        self.assertEqual(self.event.x_attending_owners, 2, "Only attending or delegating owners should be counted")

    def test_attending_owners_count_includes_delegating(self):
        """x_attending_owners includes delegating attendees alongside attending ones."""
        event = self.env["calendar.event"].create({
            "name": "Delegating Meeting",
            "start": "2026-08-01 10:00:00",
            "stop": "2026-08-01 12:00:00",
        })
        self.env["calendar.attendee"].create([
            {"event_id": event.id, "partner_id": self.owner_1.id, "x_attending": True},
            {"event_id": event.id, "partner_id": self.owner_2.id, "x_delegating": True},
            {"event_id": event.id, "partner_id": self.owner_3.id, "x_attending": False},
        ])
        self.assertEqual(event.x_attending_owners, 2, "Both attending and delegating owners must be counted")

    def test_attending_ratio_computed_correctly(self):
        """x_attending_ratio = (60 + 30) / 100 = 0.9 (Carol absent, her 10 not counted)."""
        self.assertEqual(
            self.event.x_attending_ratio, 0.9,
            "Attending ratio should be sum of attending ratios over total distribution ratio",
        )

    def test_attending_ratio_zero_when_no_attending_owners(self):
        """x_attending_ratio must be 0 when nobody is attending or delegating."""
        event = self.env["calendar.event"].create({
            "name": "Empty Meeting",
            "start": "2026-09-01 10:00:00",
            "stop": "2026-09-01 12:00:00",
            "x_condominium": self.company.id,
            "x_voting_key_id": self.distribution_key.id,
        })
        self.env["calendar.attendee"].create({
            "event_id": event.id,
            "partner_id": self.owner_1.id,
            "x_attending": False,
        })
        self.assertEqual(event.x_attending_ratio, 0.0, "Attending ratio must be 0.0 when no one attends")

    # Model: x_motion (x_in_favor, x_against, x_abstention, x_outcome)

    def test_motion_vote_ratios(self):
        """Vote ratios normalize each vote by the total key ratio and attending ratio."""
        motion = self._make_motion(vote_map={self.owner_1: "In Favor", self.owner_2: "Against"})
        self.assertAlmostEqual(
            motion.x_in_favor, 60.0 / 100.0 / 0.9, places=4,
            msg="In Favor ratio should reflect Alice's 60% share over 0.9 attending ratio",
        )
        self.assertAlmostEqual(
            motion.x_against, 30.0 / 100.0 / 0.9, places=4,
            msg="Against ratio should reflect Bob's 30% share over 0.9 attending ratio",
        )

        abstention_motion = self._make_motion(vote_map={self.owner_1: "In Favor", self.owner_2: "Abstention"})
        self.assertAlmostEqual(
            abstention_motion.x_abstention, 30.0 / 100.0 / 0.9, places=4,
            msg="Abstention ratio should reflect Bob's 30% share over 0.9 attending ratio",
        )

    def test_motion_outcome_thresholds(self):
        """Outcome evaluates to Approved if x_in_favor >= threshold, else Rejected."""
        votes = {self.owner_1: "In Favor", self.owner_2: "Against"}

        motion_approved = self._make_motion(self.vote_criteria_majority, votes)
        self.assertEqual(
            motion_approved.x_outcome, "Approved",
            "Motion should be Approved when in_favor meets the (66.7%) >= 50% threshold",
        )

        motion_rejected = self._make_motion(self.vote_criteria_supermajority, votes)
        self.assertEqual(
            motion_rejected.x_outcome, "Rejected",
            "Motion should be Rejected when in_favor (66.7%) < 75% threshold",
        )

    def test_motion_outcome_falsy_conditions(self):
        """Outcome is False when no votes are cast or no criteria is assigned."""
        self.assertFalse(
            self._make_motion(vote_criteria=self.vote_criteria_majority).x_outcome,
            "Outcome must be False when no votes are cast",
        )
        self.assertFalse(
            self._make_motion(vote_map={self.owner_1: "In Favor"}).x_outcome,
            "Outcome must be False without voting criteria",
        )

    def test_motion_votes_recomputed_on_vote_change(self):
        """Modifying an attendee vote recomputes x_in_favor and flips x_outcome."""
        motion = self._make_motion(
            self.vote_criteria_majority,
            {self.owner_1: "Against", self.owner_2: "Against"},
        )
        self.assertEqual(motion.x_outcome, "Rejected", "Outcome should initially be Rejected when all votes are Against")

        motion.x_attendee_vote_ids.filtered(lambda v: v.x_attendee_id == self.owner_1).write({"x_vote": "In Favor"})
        self.assertEqual(motion.x_outcome, "Approved", "Outcome should flip to Approved after voter changes vote to In Favor")

    # Model: x_account_analytic_split_line & x_split_analytic_items_wizard

    def test_analytic_split_line_share_computed(self):
        """x_share = (x_amount / wizard.x_total) * 100 for each split line."""
        wizard = self.env["x_split_analytic_items_wizard"].create({
            "x_total": 500.0,
            "x_line_ids": [Command.create({"x_amount": a}) for a in (250.0, 150.0, 100.0)],
        })
        shares = wizard.x_line_ids.mapped("x_share")
        self.assertEqual(shares[0], 50.0, "First line share should be 50% (250/500)")
        self.assertEqual(shares[1], 30.0, "Second line share should be 30% (150/500)")
        self.assertEqual(shares[2], 20.0, "Third line share should be 20% (100/500)")

    def test_analytic_split_share_total(self):
        """x_share_total sums up all split line shares to 100%."""
        wizard = self.env["x_split_analytic_items_wizard"].create(
            {
                "x_total": 600.0,
                "x_line_ids": [Command.create({"x_amount": a}) for a in (250.0, 250.0, 100.0)],
            }
        )
        self.assertEqual(wizard.x_share_total, 100.0, "Total shares must sum to 100%")

    def test_analytic_split_share_zero_when_total_is_zero(self):
        """x_share must safely evaluate to 0 when x_total is 0 without ZeroDivisionError."""
        wizard = self.env["x_split_analytic_items_wizard"].create({
            "x_total": 0.0,
            "x_line_ids": [Command.create({"x_amount": 50.0})],
        })
        self.assertEqual(wizard.x_line_ids[0].x_share, 0.0, "Share must be 0.0 when wizard total is 0")

    def test_analytic_split_share_recomputed_on_amount_change(self):
        """x_share recomputes dynamically when line x_amount is modified."""
        wizard = self.env["x_split_analytic_items_wizard"].create({
            "x_total": 200.0,
            "x_line_ids": [Command.create({"x_amount": a}) for a in (100.0, 100.0)],
        })
        line = wizard.x_line_ids[0]
        self.assertEqual(line.x_share, 50.0, "Initial share should be 50% (100/200)")
        line.x_amount = 150.0
        self.assertEqual(line.x_share, 75.0, "Updated share should recompute to 75% (150/200)")

    # Model: res.partner
    # (x_x_condominium_x_property_count, x_x_current_owner_x_property_count,
    #  x_vendor_companies, x_companies)

    def test_partner_condominium_property_count(self):
        """x_x_condominium_x_property_count counts properties belonging to this condominium."""
        self.assertEqual(
            self.company.partner_id.x_x_condominium_x_property_count, 3,
            "Condominium partner should count all 3 linked properties",
        )

    def test_partner_current_owner_property_count(self):
        """x_x_current_owner_x_property_count counts properties currently owned by the partner."""
        self.assertEqual(self.owner_1.x_x_current_owner_x_property_count, 1, "Owner 1 should have exactly 1 property")
        self.assertEqual(self.owner_2.x_x_current_owner_x_property_count, 1, "Owner 2 should have exactly 1 property")

    def test_partner_vendor_companies(self):
        """x_vendor_companies maps vendor's condominium partners to their associated companies."""
        self.assertEqual(self.vendor.x_vendor_companies, self.company, "Vendor companies should match condominium company")

    def test_partner_owner_companies(self):
        """x_companies resolves condominium companies for properties owned by this partner."""
        self.assertEqual(
            self.owner_1.x_companies, self.company,
            "Owner companies should match condominium company of owned properties",
        )

    # Model: sale.order (x_company_partner_id, x_x_source_sales_order_sale_order_count)

    def test_sale_order_company_partner_flag(self):
        """x_company_partner_id is True only when SO customer is the company's own partner."""
        so_internal = self.env["sale.order"].create({
            "partner_id": self.company.partner_id.id,
            "company_id": self.company.id,
        })
        self.assertTrue(
            so_internal.x_company_partner_id,
            "SO should have x_company_partner_id=True when customer is company partner",
        )
        self.assertFalse(
            self.parent_so.x_company_partner_id,
            "SO should have x_company_partner_id=False when customer is external owner",
        )

    def test_source_sale_order_child_count(self):
        """x_x_source_sales_order_sale_order_count counts child SOs linked via x_source_sales_order."""
        self.assertEqual(self.parent_so.x_x_source_sales_order_sale_order_count, 0, "Initial child SO count should be 0")
        self.env["sale.order"].create([
            {"partner_id": self.owner_1.id, "company_id": self.company.id, "x_source_sales_order": self.parent_so.id},
            {"partner_id": self.owner_1.id, "company_id": self.company.id, "x_source_sales_order": self.parent_so.id},
        ])
        self.parent_so.invalidate_recordset(["x_x_source_sales_order_sale_order_count"])
        self.assertEqual(self.parent_so.x_x_source_sales_order_sale_order_count, 2, "Child SO count should update to 2")
