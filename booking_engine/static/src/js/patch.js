import { patch } from "@web/core/utils/patch";
import { GanttRenderer } from "@web_gantt/gantt_renderer";

// In the booking_engine.action_window_availability_occupancy Gantt chart, display the occupancy percentage in the pill
patch(GanttRenderer.prototype, { getDisplayName(pill) {
    if (this.env.config.actionXmlId == "booking_engine.action_window_availability_occupancy") {
        return (pill.record.x_occupancy !== undefined) ? Math.round((100 * pill.record.x_occupancy).toString()) + "%" : ""}
    if (this.env.config.actionXmlId == "booking_engine.action_window_availability_availability") {
        return pill.record.x_available.toString()}
    return super.getDisplayName(pill)}});
