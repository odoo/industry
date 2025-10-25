/** @odoo-module **/

/**
 * Bakery Enterprise Dashboard
 * Modern dashboard with KPIs and analytics for bakery operations
 */

import { Component, useState, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

/**
 * Bakery Dashboard Component
 * Main dashboard view with KPIs, charts, and insights
 */
export class BakeryDashboard extends Component {
    static template = "bakery.Dashboard";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            loading: true,
            kpis: {
                dailySales: 0,
                orderCount: 0,
                averageOrderValue: 0,
                topProduct: '',
            },
            salesTrend: [],
            topProducts: [],
            recentOrders: [],
        });

        onMounted(() => {
            this.loadDashboardData();
        });
    }

    async loadDashboardData() {
        try {
            // Simulate loading dashboard data
            // In production, these would be actual ORM calls
            
            await this.loadKPIs();
            await this.loadSalesTrend();
            await this.loadTopProducts();
            await this.loadRecentOrders();
            
            this.state.loading = false;

            // Track dashboard view
            if (window.mcAnalyticsTracker) {
                window.mcAnalyticsTracker.track('bakery_dashboard_viewed', {
                    timestamp: new Date().toISOString(),
                });
            }
        } catch (error) {
            console.error('[BakeryDashboard] Error loading data:', error);
            this.state.loading = false;
        }
    }

    async loadKPIs() {
        // Simulated KPI data
        // In production, query actual sales data from the database
        this.state.kpis = {
            dailySales: 2847.50,
            dailySalesChange: 12.5,
            orderCount: 47,
            orderCountChange: 8.3,
            averageOrderValue: 60.59,
            averageOrderValueChange: -2.1,
            topProduct: 'Sourdough Bread',
        };
    }

    async loadSalesTrend() {
        // Simulated sales trend data for the last 7 days
        this.state.salesTrend = [
            { date: '2024-10-19', sales: 2345.00 },
            { date: '2024-10-20', sales: 2567.50 },
            { date: '2024-10-21', sales: 2123.75 },
            { date: '2024-10-22', sales: 2890.25 },
            { date: '2024-10-23', sales: 2654.00 },
            { date: '2024-10-24', sales: 2432.50 },
            { date: '2024-10-25', sales: 2847.50 },
        ];
    }

    async loadTopProducts() {
        // Simulated top products data
        this.state.topProducts = [
            { name: 'Sourdough Bread', sales: 45, revenue: 675.00 },
            { name: 'Croissants', sales: 38, revenue: 456.00 },
            { name: 'Baguette', sales: 32, revenue: 384.00 },
            { name: 'Cinnamon Rolls', sales: 28, revenue: 392.00 },
            { name: 'Multigrain Bread', sales: 25, revenue: 437.50 },
        ];
    }

    async loadRecentOrders() {
        // Simulated recent orders data
        this.state.recentOrders = [
            { 
                id: 'SO-0234',
                customer: 'Café Downtown',
                amount: 234.50,
                status: 'confirmed',
                date: '2024-10-25 14:23',
            },
            { 
                id: 'SO-0233',
                customer: 'Sarah Johnson',
                amount: 45.75,
                status: 'delivered',
                date: '2024-10-25 13:45',
            },
            { 
                id: 'SO-0232',
                customer: 'Restaurant Le Petit',
                amount: 567.00,
                status: 'in_progress',
                date: '2024-10-25 12:10',
            },
        ];
    }

    getStatusBadgeClass(status) {
        const classes = {
            'confirmed': 'mc-badge-info',
            'delivered': 'mc-badge-success',
            'in_progress': 'mc-badge-warning',
            'cancelled': 'mc-badge-error',
        };
        return `mc-badge ${classes[status] || 'mc-badge-info'}`;
    }

    getChangeClass(change) {
        return change >= 0 ? 'mc-kpi-change-positive' : 'mc-kpi-change-negative';
    }

    getChangeIcon(change) {
        return change >= 0 ? '↑' : '↓';
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
        }).format(amount);
    }

    formatPercentage(value) {
        return `${Math.abs(value).toFixed(1)}%`;
    }
}

// Register the dashboard component
registry.category("actions").add("bakery.dashboard", BakeryDashboard);

/**
 * Initialize Bakery Analytics
 */
export function initializeBakeryAnalytics() {
    // Set up bakery-specific analytics
    if (window.mcAnalyticsEngine) {
        // Register bakery-specific data processors
        window.mcAnalyticsEngine.registerProcessor('bakery_daily_revenue', (orders) => {
            return orders.reduce((sum, order) => {
                return sum + (parseFloat(order.amount_total) || 0);
            }, 0);
        });

        window.mcAnalyticsEngine.registerProcessor('bakery_popular_products', (orderLines) => {
            const products = {};
            orderLines.forEach(line => {
                const productId = line.product_id;
                if (!products[productId]) {
                    products[productId] = {
                        name: line.product_name,
                        quantity: 0,
                        revenue: 0,
                    };
                }
                products[productId].quantity += line.quantity;
                products[productId].revenue += line.price_total;
            });
            
            return Object.values(products)
                .sort((a, b) => b.revenue - a.revenue)
                .slice(0, 10);
        });
    }

    console.log('[Bakery] Analytics initialized');
}

// Auto-initialize
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeBakeryAnalytics);
} else {
    initializeBakeryAnalytics();
}

export default {
    BakeryDashboard,
    initializeBakeryAnalytics,
};
