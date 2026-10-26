import { Component, onWillStart, t, useProps } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { rpc } from "@web/core/network/rpc";
import { EventScanView } from "@event/client_action/event_barcode";
import { EventRegistrationSummaryDialog } from "@event/client_action/event_registration_summary_dialog";

export class MuseumMemberCheckinDialog extends Component {
    static template = "museum.MuseumMemberCheckinDialog";
    static components = { Dialog };
    props = useProps({
        close: t.function(),
        member: t.object(),
    });
}

patch(EventScanView.prototype, {
    setup() {
        super.setup(...arguments);
        this._scanInProgress = false;
        this._museumMembersStation = null;

        onWillStart(async () => {
            this._museumMembersStation = await this._getMuseumMembersStation();
        });
    },

    async _getMuseumMembersStation() {
        try {
            const [data] = await this.orm.searchRead(
                "ir.model.data",
                [
                    ["module", "=", "museum"],
                    ["name", "=", "frontdesk_frontdesk_2"],
                    ["model", "=", "frontdesk.frontdesk"],
                ],
                ["res_id"],
                { limit: 1 }
            );

            if (!data) {
                return null;
            }

            const [station] = await this.orm.searchRead(
                "frontdesk.frontdesk",
                [["id", "=", data.res_id]],
                ["id", "access_token"],
                { limit: 1 }
            );

            return station || null;
        } catch {
            return null;
        }
    },

    async onBarcodeScanned(barcode, onNextScanTriggered = () => {}) {
        if (!barcode?.trim() || this._scanInProgress) return;

        this._scanInProgress = true;

        try {
            await this._doMuseumBarcodeScan(barcode, onNextScanTriggered);
        } finally {
            this._scanInProgress = false;
        }
    },

    async _doMuseumBarcodeScan(barcode, onNextScanTriggered) {
        const result = await this.orm.call("event.registration", "register_attendee", [], {
            barcode: barcode,
            event_id: this.eventId,
        });

        if (!result.error || result.error !== "invalid_ticket") {
            this.registrationId = result.id;
            this.closeLastDialog?.();
            this.closeLastDialog = this.dialog.add(EventRegistrationSummaryDialog, {
                playSound: (type) => this.playSound(type),
                doNextScan: onNextScanTriggered,
                registration: result,
            });
            return;
        }

        let museumEnabled = false;
        try {
            const [company] = await this.orm.searchRead("res.company", [], ["x_museum_frontdesk_event_checkin"], { limit: 1 });
            museumEnabled = company?.x_museum_frontdesk_event_checkin;
        } catch {}

        if (!museumEnabled) {
            this.playSound("error");
            this.notification.add(_t("Invalid ticket"), { type: "danger" });
            return;
        }

        const station = this._museumMembersStation;

        if (!station) {
            this.playSound("error");
            this.notification.add(
                _t("No Frontdesk Members station found. Please configure one in Frontdesk → Stations."),
                { type: "warning" }
            );
            return;
        }

        let memberData = null;
        try {
            memberData = await rpc(
                `/frontdesk/${station.id}/${station.access_token}/get_visitor_data`,
                { barcode }
            );
        } catch (error) {
            const serverMsg = error.data?.message || error.message || "";
            const isNotFound = serverMsg.includes("No partner corresponding to this barcode");
            const displayMsg = isNotFound
                ? _t("Invalid barcode.")
                : serverMsg || _t("Invalid barcode.");
            this.playSound("error");
            this.notification.add(displayMsg, { type: "danger" });
            return;
        }

        try {
            await rpc(
                `/frontdesk/${station.id}/${station.access_token}/prepare_visitor_data`,
                {
                    name: memberData.name,
                    phone: memberData.phone || false,
                    email: memberData.email || false,
                    company: memberData.company || false,
                }
            );
        } catch {}

        this.playSound("notify");
        this.closeLastDialog?.();
        this.closeLastDialog = this.dialog.add(MuseumMemberCheckinDialog, {
            member: memberData,
        });
    },
});
