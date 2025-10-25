/** @odoo-module **/

/**
 * Mozin Conceito Dashboard Widgets
 * Interactive dashboard components for analytics
 */

import { Component, useState, onMounted, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

/**
 * KPI Widget Component
 * Display key performance indicators with trend indicators
 */
export class KPIWidget extends Component {
    static template = "base_industry_enterprise.KPIWidget";
    static props = {
        title: String,
        value: [Number, String],
        change: { type: Number, optional: true },
        icon: { type: String, optional: true },
        variant: { type: String, optional: true }, // success, warning, error, info
    };

    get changeClass() {
        if (!this.props.change) return '';
        return this.props.change >= 0 ? 'mc-kpi-change-positive' : 'mc-kpi-change-negative';
    }

    get changeIcon() {
        if (!this.props.change) return '';
        return this.props.change >= 0 ? '↑' : '↓';
    }

    get cardClass() {
        const variant = this.props.variant || 'primary';
        return `mc-kpi-card mc-kpi-${variant}`;
    }
}

/**
 * Chart Widget Component
 * Base component for chart visualizations
 */
export class ChartWidget extends Component {
    static template = "base_industry_enterprise.ChartWidget";
    static props = {
        title: String,
        type: String, // line, bar, pie, doughnut
        data: Object,
        height: { type: Number, optional: true },
    };

    setup() {
        this.chartRef = useRef("chartCanvas");
        this.chart = null;

        onMounted(() => {
            this.renderChart();
        });
    }

    renderChart() {
        // Placeholder for chart rendering
        // In production, integrate with Chart.js or similar library
        const canvas = this.chartRef.el;
        if (!canvas) return;

        console.log('[ChartWidget] Rendering chart:', this.props.type, this.props.data);
        
        // Mock chart rendering
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = '#2C5AA0';
        ctx.fillRect(10, 10, canvas.width - 20, canvas.height - 20);
        ctx.fillStyle = '#ffffff';
        ctx.font = '16px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(`${this.props.type.toUpperCase()} CHART`, canvas.width / 2, canvas.height / 2);
    }

    willUnmount() {
        if (this.chart) {
            this.chart.destroy();
        }
    }
}

/**
 * Stats Card Component
 * Display statistical information with icons
 */
export class StatsCard extends Component {
    static template = "base_industry_enterprise.StatsCard";
    static props = {
        label: String,
        value: [Number, String],
        icon: { type: String, optional: true },
        trend: { type: String, optional: true }, // up, down, neutral
    };

    get iconClass() {
        return this.props.icon || 'fa-chart-line';
    }

    get trendClass() {
        const trend = this.props.trend || 'neutral';
        return `mc-stat-trend-${trend}`;
    }
}

/**
 * Progress Widget Component
 * Display progress bars with labels and percentages
 */
export class ProgressWidget extends Component {
    static template = "base_industry_enterprise.ProgressWidget";
    static props = {
        label: String,
        value: Number, // 0-100
        max: { type: Number, optional: true },
        variant: { type: String, optional: true }, // success, warning, error
    };

    get percentage() {
        const max = this.props.max || 100;
        return Math.min(100, (this.props.value / max) * 100);
    }

    get progressClass() {
        const variant = this.props.variant || 'primary';
        return `mc-progress-fill mc-progress-${variant}`;
    }
}

/**
 * Timeline Widget Component
 * Display events in a timeline format
 */
export class TimelineWidget extends Component {
    static template = "base_industry_enterprise.TimelineWidget";
    static props = {
        events: Array, // Array of {date, title, description}
    };
}

/**
 * Data Table Widget Component
 * Display tabular data with sorting and filtering
 */
export class DataTableWidget extends Component {
    static template = "base_industry_enterprise.DataTableWidget";
    static props = {
        columns: Array, // Array of {key, label}
        data: Array,
        sortable: { type: Boolean, optional: true },
        filterable: { type: Boolean, optional: true },
    };

    setup() {
        this.state = useState({
            sortColumn: null,
            sortDirection: 'asc',
            filterText: '',
        });
    }

    get filteredData() {
        let data = [...this.props.data];

        // Apply filter
        if (this.state.filterText) {
            const filter = this.state.filterText.toLowerCase();
            data = data.filter(row => {
                return Object.values(row).some(value => 
                    String(value).toLowerCase().includes(filter)
                );
            });
        }

        // Apply sort
        if (this.state.sortColumn) {
            data.sort((a, b) => {
                const aVal = a[this.state.sortColumn];
                const bVal = b[this.state.sortColumn];
                
                if (aVal < bVal) return this.state.sortDirection === 'asc' ? -1 : 1;
                if (aVal > bVal) return this.state.sortDirection === 'asc' ? 1 : -1;
                return 0;
            });
        }

        return data;
    }

    sortBy(columnKey) {
        if (this.state.sortColumn === columnKey) {
            this.state.sortDirection = this.state.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            this.state.sortColumn = columnKey;
            this.state.sortDirection = 'asc';
        }
    }

    onFilterChange(ev) {
        this.state.filterText = ev.target.value;
    }
}

/**
 * Alert Widget Component
 * Display alert messages with different severity levels
 */
export class AlertWidget extends Component {
    static template = "base_industry_enterprise.AlertWidget";
    static props = {
        type: String, // success, warning, error, info
        title: { type: String, optional: true },
        message: String,
        dismissible: { type: Boolean, optional: true },
    };

    setup() {
        this.state = useState({
            visible: true,
        });
    }

    dismiss() {
        this.state.visible = false;
    }

    get alertClass() {
        return `mc-alert mc-alert-${this.props.type}`;
    }

    get iconClass() {
        const icons = {
            success: 'fa-check-circle',
            warning: 'fa-exclamation-triangle',
            error: 'fa-times-circle',
            info: 'fa-info-circle',
        };
        return icons[this.props.type] || 'fa-info-circle';
    }
}

/**
 * Dashboard Grid Component
 * Responsive grid layout for dashboard widgets
 */
export class DashboardGrid extends Component {
    static template = "base_industry_enterprise.DashboardGrid";
    static props = {
        columns: { type: Number, optional: true },
        gap: { type: Number, optional: true },
        slots: Object,
    };

    get gridStyle() {
        const columns = this.props.columns || 3;
        const gap = this.props.gap || 24;
        return `
            display: grid;
            grid-template-columns: repeat(${columns}, 1fr);
            gap: ${gap}px;
        `;
    }
}

/**
 * Metric Card Component
 * Display a single metric with comparison
 */
export class MetricCard extends Component {
    static template = "base_industry_enterprise.MetricCard";
    static props = {
        title: String,
        value: [Number, String],
        previousValue: { type: [Number, String], optional: true },
        unit: { type: String, optional: true },
        format: { type: String, optional: true }, // number, currency, percentage
    };

    get formattedValue() {
        const value = this.props.value;
        const format = this.props.format || 'number';
        
        switch (format) {
            case 'currency':
                return new Intl.NumberFormat('en-US', {
                    style: 'currency',
                    currency: 'USD',
                }).format(value);
            case 'percentage':
                return `${value}%`;
            default:
                return new Intl.NumberFormat('en-US').format(value);
        }
    }

    get change() {
        if (!this.props.previousValue) return null;
        const current = parseFloat(this.props.value);
        const previous = parseFloat(this.props.previousValue);
        if (previous === 0) return null;
        return ((current - previous) / previous) * 100;
    }

    get changeClass() {
        if (!this.change) return '';
        return this.change >= 0 ? 'mc-metric-positive' : 'mc-metric-negative';
    }
}

// Register all components
registry.category("components").add("KPIWidget", KPIWidget);
registry.category("components").add("ChartWidget", ChartWidget);
registry.category("components").add("StatsCard", StatsCard);
registry.category("components").add("ProgressWidget", ProgressWidget);
registry.category("components").add("TimelineWidget", TimelineWidget);
registry.category("components").add("DataTableWidget", DataTableWidget);
registry.category("components").add("AlertWidget", AlertWidget);
registry.category("components").add("DashboardGrid", DashboardGrid);
registry.category("components").add("MetricCard", MetricCard);

export default {
    KPIWidget,
    ChartWidget,
    StatsCard,
    ProgressWidget,
    TimelineWidget,
    DataTableWidget,
    AlertWidget,
    DashboardGrid,
    MetricCard,
};
