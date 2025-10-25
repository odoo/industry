/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";

// Enhanced Bakery Tour using the Enterprise Tour Framework
registry.category("web_tour.tours").add("bakery_knowledge_tour", {
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

// Comprehensive Bakery Tour - Enterprise Edition
registry.category("web_tour.tours").add("bakery_enterprise_tour", {
    url: "/odoo",
    steps: () => [
        {
            trigger: 'body',
            content: `
                <div class="mc-tour-welcome mc-fade-in">
                    <h2 style="font-size: 2rem; font-weight: 700; margin-bottom: 1rem; color: #2C5AA0;">
                        🥖 Welcome to Bakery Enterprise!
                    </h2>
                    <p style="font-size: 1.125rem; line-height: 1.75; color: #616161; margin-bottom: 1.5rem;">
                        This comprehensive tour will guide you through all the features of your modern bakery management system.
                        Let's explore how to manage products, sales, inventory, and customers efficiently.
                    </p>
                    <div class="mc-alert mc-alert-info" style="text-align: left;">
                        <div class="mc-alert-icon">ℹ️</div>
                        <div class="mc-alert-content">
                            <div class="mc-alert-title">Tour Duration</div>
                            <div class="mc-alert-message">This tour takes approximately 5 minutes to complete</div>
                        </div>
                    </div>
                </div>
            `,
            position: "center",
            run: () => {},
        },
        {
            trigger: '.o_app[data-menu-xmlid="point_of_sale.menu_point_root"]',
            content: _t(`
                <div class="mc-tour-step">
                    <h3 style="font-weight: 600; margin-bottom: 0.5rem;">📱 Point of Sale System</h3>
                    <p>Your modern POS system for quick in-store sales. Handle walk-in customers, manage cash registers, and track daily sales with ease.</p>
                </div>
            `),
            position: "bottom",
            run: "click",
        },
        {
            trigger: '.o_app[data-menu-xmlid="sale.sale_menu_root"]',
            content: _t(`
                <div class="mc-tour-step">
                    <h3 style="font-weight: 600; margin-bottom: 0.5rem;">📋 Sales Orders</h3>
                    <p>Manage custom orders, corporate catering requests, and wholesale orders. Create quotes, track order status, and manage customer relationships.</p>
                </div>
            `),
            position: "bottom",
            run: "click",
        },
        {
            trigger: '.o_app[data-menu-xmlid="purchase.menu_purchase_root"]',
            content: _t(`
                <div class="mc-tour-step">
                    <h3 style="font-weight: 600; margin-bottom: 0.5rem;">🛒 Purchase Management</h3>
                    <p>Order raw materials from suppliers, manage vendor relationships, and track ingredient costs. Keep your inventory stocked with automated reordering.</p>
                </div>
            `),
            position: "bottom",
            run: "click",
        },
        {
            trigger: '.o_app[data-menu-xmlid="stock.menu_stock_root"]',
            content: _t(`
                <div class="mc-tour-step">
                    <h3 style="font-weight: 600; margin-bottom: 0.5rem;">📦 Inventory Control</h3>
                    <p>Track flour, sugar, butter, and all your ingredients. Monitor stock levels, set reorder points, and manage product expiration dates for food safety.</p>
                </div>
            `),
            position: "bottom",
            run: "click",
        },
        {
            trigger: '.o_app[data-menu-xmlid="website_sale.menu_catalog"]',
            content: _t(`
                <div class="mc-tour-step">
                    <h3 style="font-weight: 600; margin-bottom: 0.5rem;">🌐 Online Store</h3>
                    <p>Sell your baked goods online! Customers can order for pickup or delivery. Showcase your products with beautiful images and descriptions.</p>
                </div>
            `),
            position: "bottom",
            run: "click",
        },
        {
            trigger: '.o_app[data-menu-xmlid="hr.menu_hr_root"]',
            content: _t(`
                <div class="mc-tour-step">
                    <h3 style="font-weight: 600; margin-bottom: 0.5rem;">👥 Staff Management</h3>
                    <p>Manage your bakers, cashiers, and delivery staff. Track attendance, schedule shifts, and manage payroll for your bakery team.</p>
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
                        Tour Completed!
                    </h2>
                    <p style="font-size: 1.125rem; line-height: 1.75; color: #616161; margin-bottom: 1.5rem;">
                        You've successfully explored all the key features of your Bakery Enterprise system. 
                        You're now ready to start managing your bakery operations efficiently!
                    </p>
                    <div class="mc-card" style="text-align: left; max-width: 500px; margin: 1.5rem auto;">
                        <div class="mc-card-header">
                            <h3 style="font-weight: 600; margin: 0;">📚 Next Steps</h3>
                        </div>
                        <div class="mc-card-body">
                            <ul style="margin: 0; padding-left: 1.5rem; line-height: 1.75;">
                                <li>Set up your products and pricing</li>
                                <li>Configure your POS system</li>
                                <li>Add your suppliers</li>
                                <li>Create your team members</li>
                                <li>Customize your online store</li>
                            </ul>
                        </div>
                    </div>
                    <div class="mc-alert mc-alert-success" style="text-align: left; max-width: 500px; margin: 0 auto;">
                        <div class="mc-alert-icon">💡</div>
                        <div class="mc-alert-content">
                            <div class="mc-alert-title">Pro Tip</div>
                            <div class="mc-alert-message">Check the Knowledge app for detailed guides and best practices</div>
                        </div>
                    </div>
                </div>
            `,
            position: "center",
            run: () => {
                // Track tour completion
                if (window.mcTourManager) {
                    window.mcTourManager.completeTour('bakery_enterprise_tour');
                }
                if (window.mcAnalyticsTracker) {
                    window.mcAnalyticsTracker.track('bakery_tour_completed', {
                        duration: 'completed',
                        timestamp: new Date().toISOString(),
                    });
                }
            },
        },
    ],
});

