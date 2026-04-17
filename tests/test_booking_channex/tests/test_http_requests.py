# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json

from odoo.tests import tagged
from odoo.tests.common import HttpCase, MockHTTPClient


@tagged("post_install", "-at_install")
class BookingChannexHTTPRequestsTestCase(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.company.x_channex_api_key = "MyTestAPIKey"

    def test_receive_new_booking(self):
        payload_receive_booking = {
            'timestamp': '2026-03-03T09:36:35.024296Z',
            'event': 'booking_new',
            'user_id': None,
            'payload': {
                'currency': 'EUR',
                'amount': '88.00',
                'channel_id': None,
                'property_id': '38149695-d95b-4c80-a7c3-34ce96efc7ba',
                'booking_id': 'e868f16e-b474-4b95-af12-5b114133e670',
                'arrival_date': '2026-03-04',
                'booking_revision_id': '074cd7f9-df51-4fc6-a8f4-7658573a235d',
                'live_feed_event_id': 'f2baf04e-7d63-4b29-80fd-f180f66b1b2c',
                'count_of_rooms': 1,
                'booking_unique_id': 'BDC-00001',
                'count_of_nights': 1,
                'customer_name': 'Demo Marc',
                'ota_code': '00001'
            },
            'property_id': '38149695-d95b-4c80-a7c3-34ce96efc7ba'
        }
        booking_ack_answer = {"meta": {"message": "Success"}}
        get_booking_answer = {
            "data": {
                "attributes": {
                    "id": "e868f16e-b474-4b95-af12-5b114133e670",
                    "meta": {},
                    "status": "cancelled",
                    "services": [],
                    "currency": "EUR",
                    "amount": "88.00",
                    "agent": None,
                    "unique_id": "BDC-00001",
                    "inserted_at": "2026-03-03T09:36:34.926048",
                    "ota_name": "BookingCom",
                    "channel_id": None,
                    "property_id": "38149695-d95b-4c80-a7c3-34ce96efc7ba",
                    "booking_id": "e868f16e-b474-4b95-af12-5b114133e670",
                    "arrival_date": "2026-03-04",
                    "arrival_hour": "15:00",
                    "customer": {
                        "meta": None,
                        "name": "Demo",
                        "state": None,
                        "zip": "1000",
                        "address": "Rue de Marc",
                        "country": "BE",
                        "city": "Bruxelles",
                        "language": None,
                        "mail": "marc.demo@odootest.test",
                        "phone": None,
                        "surname": "Marc"
                    },
                    "departure_date": "2026-03-05",
                    "deposits": [],
                    "notes": None,
                    "ota_commission": "0.00",
                    "ota_reservation_code": "00001",
                    "payment_collect": "ota",
                    "payment_type": "credit_card",
                    "rooms": [
                        {
                            "meta": None,
                            "taxes": [],
                            "services": [],
                            "amount": "88.00",
                            "days": {
                                "2026-03-04": "88.00"
                            },
                            "ota_commission": None,
                            "guests": [],
                            "occupancy": {
                                "children": 0,
                                "adults": 1,
                                "ages": [],
                                "infants": 0
                            },
                            "rate_plan_id": "abd55f84-a02c-4593-8109-1d13b178105d",
                            "room_type_id": "28ff9c15-c4a1-4334-a259-146557838b5e",
                            "booking_room_id": "f9101f02-ab78-4afb-9841-50b23035fe81",
                            "checkout_date": "2026-03-05",
                            "checkin_date": "2026-03-04",
                            "is_cancelled": False,
                            "ota_unique_id": None
                        }
                    ],
                    "occupancy": {
                        "children": 0,
                        "adults": 1,
                        "ages": [],
                        "infants": 0
                    },
                    "guarantee": None,
                    "secondary_ota": None,
                    "acknowledge_status": "pending",
                    "has_unacked_revisions": False,
                    "raw_message": "{\"meta\":{},\"status\":\"cancelled\",\"services\":[],\"currency\":\"EUR\",\"amount\":8800,\"ota_name\":\"BookingCom\",\"property_id\":\"38149695-d95b-4c80-a7c3-34ce96efc7ba\",\"arrival_date\":\"2026-03-04\",\"arrival_hour\":\"15:00:00\",\"customer\":{\"meta\":null,\"name\":\"Demo\",\"state\":null,\"zip\":\"1000\",\"address\":\"Rue de Marc\",\"country\":\"BE\",\"city\":\"Bruxelles\",\"language\":null,\"mail\":\"marc.demo@odootest.test\",\"phone\":null,\"surname\":\"Marc\"},\"departure_date\":\"2026-03-05\",\"deposits\":[],\"notes\":null,\"ota_commission\":0,\"ota_reservation_code\":\"00001\",\"payment_collect\":\"ota\",\"payment_type\":\"credit_card\",\"rooms\":[{\"meta\":null,\"taxes\":[],\"services\":[],\"amount\":8800,\"days\":{\"2026-03-04\":8800},\"guests\":[],\"occupancy\":{\"children\":0,\"adults\":1,\"ages\":[],\"infants\":0},\"rate_plan_id\":\"abd55f84-a02c-4593-8109-1d13b178105d\",\"room_type_id\":\"28ff9c15-c4a1-4334-a259-146557838b5e\"}]}",
                    "revision_id": "4ba0eeed-0cb0-4e54-971e-b00fbee0504f",
                    "is_crs_revision": False
                },
                "id": "e868f16e-b474-4b95-af12-5b114133e670",
                "type": "booking"
            }
        }
        room = self.env['product.product'].create({
            'name': 'Test Room'
        })
        self.env['x_channex_mapping'].create({
            'x_model_type': 'room_type',
            'x_remote_id': '28ff9c15-c4a1-4334-a259-146557838b5e',
            'x_local_id': room.id,
        })
        self.env['sale.order'].create({  # Needed for the webhook to find something to operate on
            'partner_id': self.env['res.partner'].create({'name': 'Test Partner 1'}).id,
        })
        with (
            MockHTTPClient(url="https://staging.channex.io/api/v1/booking_revisions/074cd7f9-df51-4fc6-a8f4-7658573a235d/ack", return_json=booking_ack_answer, return_status=200),
            MockHTTPClient(url="https://staging.channex.io/api/v1/bookings/e868f16e-b474-4b95-af12-5b114133e670", return_json=get_booking_answer, return_status=200),
        ):
            self.url_open(
                self.env.ref("booking_channex.webhook_get_booking_create_change_or_delete").url,
                data=json.dumps(payload_receive_booking),
                headers={'Content-Type': 'application/json'}
            )
            self.assertTrue(self.env['sale.order.line'].search_count([('product_id', '=', room.id)]), 'The sale order has not been created when webhook received the payload.')

    def test_product_create_on_channex(self):
        create_room_type_answer = {"data": {"type": "room_type", "id": "994d1375-dbbd-4072-8724-b2ab32ce781b", "attributes": {
            "id": "994d1375-dbbd-4072-8724-b2ab32ce781b", "title": "Standard Room",
            "occ_adults": 3, "occ_children": 0, "occ_infants": 0, "default_occupancy": 2, "count_of_rooms": 20, "room_kind": "room", "capacity": None,
            "content": {"description": "Some Room Type Description Text", "photos": []}
            },
            "relationships": {"facilities": {"data": []}, "property": {"data": {"type": "property", "id": "716305c4-561a-4561-a187-7f5b8aeb5920"}}}
        }}
        with (MockHTTPClient(url="https://staging.channex.io/api/v1/room_types", return_json=create_room_type_answer, return_status=200)):  # as request_response
            new_room = self.env["product.template"].create({
                'name': 'Test room',
                'type': 'service',
                'list_price': 90.0,
            })
            self.env["x_channex_mapping"].search([
                ("x_model_type", "=", "room_type"),
                ("x_local_id", "=", new_room.id),
            ], limit=1)
            # Is failing right now as it is not yet implemented; should be here again when non-ari updates arrives
            # self.assertEqual(request_response.calls, 0, "Creating a room type in odoo did not send any requests to channex")
            # self.assertTrue(room_mapping.x_remote_id, "Creating a room did not create a mapping entry in odoo")
            # self.assertEqual(room_mapping.x_remote_id, "994d1375-dbbd-4072-8724-b2ab32ce781b", "Creating a room did not put the correct remote id in the mapping")
