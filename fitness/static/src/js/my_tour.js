/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";

// Enhanced Fitness Tour using the Enterprise Tour Framework
registry.category("web_tour.tours").add("fitness_knowledge_tour", {
    url: "/odoo",
    
    steps: () => [
        {
            trigger: '.o_app[data-menu-xmlid="knowledge.knowledge_menu_root"]',
            content: _t("Get on track and explore our recommendations for your Odoo usage here!"),
            position: "bottom",
            run: "click",
        },
    ],
});

// Comprehensive Fitness Center Tour - Enterprise Edition
registry.category("web_tour.tours").add("fitness_enterprise_tour", {
    url: "/odoo",
    steps: () => [
        {
            trigger: 'body',
            content: `
                <div class="mc-tour-welcome mc-fade-in">
                    <h2 style="font-size: 2rem; font-weight: 700; margin-bottom: 1rem; color: #2C5AA0;">
                        💪 Welcome to Fitness Center Enterprise!
                    </h2>
                    <p style="font-size: 1.125rem; line-height: 1.75; color: #616161; margin-bottom: 1.5rem;">
                        Your complete solution for managing memberships, classes, equipment, and staff. 
                        Let's explore the powerful features that will transform your fitness center operations.
                    </p>
                    <div class="mc-alert mc-alert-success" style="text-align: left;">
                        <div class="mc-alert-icon">🎯</div>
                        <div class="mc-alert-content">
                            <div class="mc-alert-title">What You'll Learn</div>
                            <div class="mc-alert-message">Membership management, class scheduling, equipment tracking, and analytics</div>
                        </div>
                    </div>
                </div>
            `,
            position: "center",
            run: () => {},
        },
        {
            trigger: '.o_app[data-menu-xmlid="sale_subscription.menu_sale_subscription_root"]',
            content: _t(`
                <div class="mc-tour-step">
                    <h3 style="font-weight: 600; margin-bottom: 0.5rem;">🎫 Membership Management</h3>
                    <p>Manage all your gym memberships with automated renewals, flexible pricing plans, and member benefits tracking.</p>
                    <div class="mc-badge mc-badge-info" style="margin-top: 0.5rem;">Core Feature</div>
                </div>
            `),
            position: "bottom",
            run: "click",
        },
        {
            trigger: '.o_app[data-menu-xmlid="website_appointment.menu_appointment_root"]',
            content: _t(`
                <div class="mc-tour-step">
                    <h3 style="font-weight: 600; margin-bottom: 0.5rem;">📅 Class Scheduling</h3>
                    <p>Schedule fitness classes, personal training sessions, and group events. Members can book online through your website.</p>
                    <div class="mc-badge mc-badge-success" style="margin-top: 0.5rem;">Popular</div>
                </div>
            `),
            position: "bottom",
            run: "click",
        },
        {
            trigger: '.o_app[data-menu-xmlid="maintenance.menu_maintenance_title"]',
            content: _t(`
                <div class="mc-tour-step">
                    <h3 style="font-weight: 600; margin-bottom: 0.5rem;">🏋️ Equipment Tracking</h3>
                    <p>Monitor all your gym equipment, schedule maintenance, and track repair requests to keep everything in top condition.</p>
                </div>
            `),
            position: "bottom",
            run: "click",
        },
        {
            trigger: '.o_app[data-menu-xmlid="planning.planning_menu_root"]',
            content: _t(`
                <div class="mc-tour-step">
                    <h3 style="font-weight: 600; margin-bottom: 0.5rem;">👥 Staff Planning</h3>
                    <p>Create staff schedules, assign trainers to classes, and manage employee availability with visual planning tools.</p>
                </div>
            `),
            position: "bottom",
            run: "click",
        },
        {
            trigger: '.o_app[data-menu-xmlid="point_of_sale.menu_point_root"]',
            content: _t(`
                <div class="mc-tour-step">
                    <h3 style="font-weight: 600; margin-bottom: 0.5rem;">🛍️ Pro Shop & Supplements</h3>
                    <p>Sell merchandise, supplements, and day passes at the front desk with a fast, modern POS system.</p>
                </div>
            `),
            position: "bottom",
            run: "click",
        },
        {
            trigger: 'body',
            content: `
                <div class="mc-tour-complete mc-fade-in">
                    <div class="mc-tour-complete-icon">✓</div>
                    <h2 style="font-size: 2rem; font-weight: 700; margin-bottom: 1rem; color: #4caf50;">
                        You're All Set! 💪
                    </h2>
                    <p style="font-size: 1.125rem; line-height: 1.75; color: #616161; margin-bottom: 1.5rem;">
                        You've explored all the essential features of your Fitness Center Enterprise system.
                        Start building your member community today!
                    </p>
                    <div class="mc-kpi-grid" style="max-width: 600px; margin: 0 auto 1.5rem;">
                        <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%); border-radius: 12px; color: white;">
                            <div style="font-size: 2rem; font-weight: 700;">∞</div>
                            <div style="font-size: 0.875rem; opacity: 0.9;">Unlimited Members</div>
                        </div>
                        <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%); border-radius: 12px; color: white;">
                            <div style="font-size: 2rem; font-weight: 700;">24/7</div>
                            <div style="font-size: 0.875rem; opacity: 0.9;">Online Booking</div>
                        </div>
                        <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); border-radius: 12px; color: white;">
                            <div style="font-size: 2rem; font-weight: 700;">100%</div>
                            <div style="font-size: 0.875rem; opacity: 0.9;">Automated</div>
                        </div>
                    </div>
                </div>
            `,
            position: "center",
            run: () => {
                if (window.mcTourManager) {
                    window.mcTourManager.completeTour('fitness_enterprise_tour');
                }
                if (window.mcAnalyticsTracker) {
                    window.mcAnalyticsTracker.track('fitness_tour_completed', {
                        timestamp: new Date().toISOString(),
                    });
                }
            },
        },
    ],
});

