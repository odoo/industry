/** @odoo-module **/

/**
 * Fitness Center Enterprise Features
 * Member analytics, class tracking, and equipment management
 */

import { registry } from "@web/core/registry";

/**
 * Initialize Fitness Analytics
 */
export function initializeFitnessAnalytics() {
    if (window.mcAnalyticsEngine) {
        // Register fitness-specific metrics
        window.mcAnalyticsEngine.registerProcessor('fitness_active_members', (subscriptions) => {
            return subscriptions.filter(sub => sub.stage_id === 'in_progress').length;
        });

        window.mcAnalyticsEngine.registerProcessor('fitness_class_attendance', (appointments) => {
            return appointments.reduce((sum, apt) => sum + (apt.attendee_count || 0), 0);
        });

        window.mcAnalyticsEngine.registerProcessor('fitness_equipment_status', (equipment) => {
            const status = { working: 0, maintenance: 0, broken: 0 };
            equipment.forEach(eq => {
                if (eq.maintenance_state === 'good') status.working++;
                else if (eq.maintenance_state === 'maintenance') status.maintenance++;
                else status.broken++;
            });
            return status;
        });

        window.mcAnalyticsEngine.registerProcessor('fitness_revenue_by_type', (orders) => {
            const revenue = {
                memberships: 0,
                classes: 0,
                merchandise: 0,
                supplements: 0,
            };
            
            orders.forEach(order => {
                const category = order.product_category || 'other';
                if (category.includes('membership')) revenue.memberships += order.amount_total;
                else if (category.includes('class')) revenue.classes += order.amount_total;
                else if (category.includes('merchandise')) revenue.merchandise += order.amount_total;
                else if (category.includes('supplement')) revenue.supplements += order.amount_total;
            });
            
            return revenue;
        });

        console.log('[Fitness] Analytics initialized');
    }

    // Track fitness-specific events
    if (window.mcAnalyticsTracker) {
        // Track member check-ins
        window.addEventListener('member_checkin', (event) => {
            window.mcAnalyticsTracker.track('member_checkin', {
                member_id: event.detail.member_id,
                timestamp: new Date().toISOString(),
            });
        });

        // Track class bookings
        window.addEventListener('class_booking', (event) => {
            window.mcAnalyticsTracker.track('class_booking', {
                class_id: event.detail.class_id,
                member_id: event.detail.member_id,
                timestamp: new Date().toISOString(),
            });
        });
    }
}

/**
 * Fitness Dashboard Helper
 */
export class FitnessDashboard {
    static getMembershipTrend(subscriptions, days = 30) {
        // Calculate membership growth trend
        const startDate = new Date();
        startDate.setDate(startDate.getDate() - days);
        
        const recent = subscriptions.filter(sub => 
            new Date(sub.start_date) >= startDate
        );
        
        return {
            newMembers: recent.length,
            growthRate: (recent.length / subscriptions.length) * 100,
        };
    }

    static getPopularClasses(appointments, limit = 5) {
        // Find most popular classes by attendance
        const classes = {};
        
        appointments.forEach(apt => {
            const className = apt.appointment_type_id.name;
            if (!classes[className]) {
                classes[className] = {
                    name: className,
                    bookings: 0,
                    attendance: 0,
                };
            }
            classes[className].bookings++;
            classes[className].attendance += apt.attendee_count || 0;
        });
        
        return Object.values(classes)
            .sort((a, b) => b.attendance - a.attendance)
            .slice(0, limit);
    }

    static getPeakHours(checkins) {
        // Analyze peak gym hours
        const hours = Array(24).fill(0);
        
        checkins.forEach(checkin => {
            const hour = new Date(checkin.timestamp).getHours();
            hours[hour]++;
        });
        
        return hours.map((count, hour) => ({
            hour: `${hour}:00`,
            count,
        }));
    }

    static getEquipmentAlerts(equipment) {
        // Get equipment needing attention
        return equipment.filter(eq => 
            eq.maintenance_state === 'maintenance' || 
            eq.maintenance_state === 'broken' ||
            (eq.maintenance_due_date && new Date(eq.maintenance_due_date) < new Date())
        );
    }
}

// Auto-initialize
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeFitnessAnalytics);
} else {
    initializeFitnessAnalytics();
}

export default {
    initializeFitnessAnalytics,
    FitnessDashboard,
};
