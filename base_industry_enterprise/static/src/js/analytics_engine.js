/** @odoo-module **/

/**
 * Mozin Conceito Analytics Engine
 * Advanced analytics and data processing
 */

/**
 * Analytics Engine
 * Process and analyze business data
 */
export class AnalyticsEngine {
    constructor() {
        this.dataStore = new Map();
        this.processors = new Map();
        this.registerDefaultProcessors();
    }

    /**
     * Register default data processors
     */
    registerDefaultProcessors() {
        this.registerProcessor('sum', (data, field) => {
            return data.reduce((sum, item) => sum + (parseFloat(item[field]) || 0), 0);
        });

        this.registerProcessor('average', (data, field) => {
            if (data.length === 0) return 0;
            const sum = this.process('sum', data, field);
            return sum / data.length;
        });

        this.registerProcessor('count', (data) => {
            return data.length;
        });

        this.registerProcessor('max', (data, field) => {
            return Math.max(...data.map(item => parseFloat(item[field]) || 0));
        });

        this.registerProcessor('min', (data, field) => {
            return Math.min(...data.map(item => parseFloat(item[field]) || 0));
        });

        this.registerProcessor('groupBy', (data, field) => {
            return data.reduce((groups, item) => {
                const key = item[field];
                if (!groups[key]) groups[key] = [];
                groups[key].push(item);
                return groups;
            }, {});
        });
    }

    /**
     * Register a custom data processor
     */
    registerProcessor(name, fn) {
        this.processors.set(name, fn);
    }

    /**
     * Process data using a registered processor
     */
    process(processorName, data, ...args) {
        const processor = this.processors.get(processorName);
        if (!processor) {
            throw new Error(`Processor '${processorName}' not found`);
        }
        return processor(data, ...args);
    }

    /**
     * Store dataset for later analysis
     */
    storeData(key, data) {
        this.dataStore.set(key, data);
    }

    /**
     * Retrieve stored dataset
     */
    getData(key) {
        return this.dataStore.get(key);
    }

    /**
     * Calculate growth rate between two periods
     */
    calculateGrowth(current, previous) {
        if (previous === 0) return 0;
        return ((current - previous) / previous) * 100;
    }

    /**
     * Calculate trend over time series data
     */
    calculateTrend(data, field) {
        if (data.length < 2) return 'neutral';
        
        const values = data.map(item => parseFloat(item[field]) || 0);
        const firstHalf = values.slice(0, Math.floor(values.length / 2));
        const secondHalf = values.slice(Math.floor(values.length / 2));
        
        const firstAvg = firstHalf.reduce((a, b) => a + b, 0) / firstHalf.length;
        const secondAvg = secondHalf.reduce((a, b) => a + b, 0) / secondHalf.length;
        
        if (secondAvg > firstAvg * 1.05) return 'up';
        if (secondAvg < firstAvg * 0.95) return 'down';
        return 'neutral';
    }

    /**
     * Calculate moving average
     */
    movingAverage(data, field, window = 3) {
        const values = data.map(item => parseFloat(item[field]) || 0);
        const result = [];
        
        for (let i = 0; i < values.length; i++) {
            const start = Math.max(0, i - window + 1);
            const end = i + 1;
            const subset = values.slice(start, end);
            const avg = subset.reduce((a, b) => a + b, 0) / subset.length;
            result.push(avg);
        }
        
        return result;
    }

    /**
     * Generate time series data
     */
    generateTimeSeries(startDate, endDate, interval = 'day') {
        const series = [];
        const current = new Date(startDate);
        const end = new Date(endDate);
        
        while (current <= end) {
            series.push(new Date(current));
            
            switch (interval) {
                case 'hour':
                    current.setHours(current.getHours() + 1);
                    break;
                case 'day':
                    current.setDate(current.getDate() + 1);
                    break;
                case 'week':
                    current.setDate(current.getDate() + 7);
                    break;
                case 'month':
                    current.setMonth(current.getMonth() + 1);
                    break;
                case 'year':
                    current.setFullYear(current.getFullYear() + 1);
                    break;
            }
        }
        
        return series;
    }

    /**
     * Calculate percentile
     */
    percentile(data, field, p) {
        const values = data.map(item => parseFloat(item[field]) || 0).sort((a, b) => a - b);
        const index = (p / 100) * (values.length - 1);
        const lower = Math.floor(index);
        const upper = Math.ceil(index);
        const weight = index % 1;
        
        if (lower === upper) return values[lower];
        return values[lower] * (1 - weight) + values[upper] * weight;
    }

    /**
     * Detect anomalies in data
     */
    detectAnomalies(data, field, threshold = 2) {
        const values = data.map(item => parseFloat(item[field]) || 0);
        const mean = values.reduce((a, b) => a + b, 0) / values.length;
        const variance = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length;
        const stdDev = Math.sqrt(variance);
        
        return data.filter((item, index) => {
            const value = parseFloat(item[field]) || 0;
            const zScore = Math.abs((value - mean) / stdDev);
            return zScore > threshold;
        });
    }
}

/**
 * Report Generator
 * Generate analytical reports from data
 */
export class ReportGenerator {
    constructor(analyticsEngine) {
        this.analytics = analyticsEngine;
        this.templates = new Map();
    }

    /**
     * Register report template
     */
    registerTemplate(name, template) {
        this.templates.set(name, template);
    }

    /**
     * Generate report from template
     */
    generate(templateName, data, options = {}) {
        const template = this.templates.get(templateName);
        if (!template) {
            throw new Error(`Report template '${templateName}' not found`);
        }
        
        return template(data, this.analytics, options);
    }

    /**
     * Generate summary report
     */
    generateSummary(data, fields) {
        const summary = {};
        
        fields.forEach(field => {
            summary[field] = {
                count: data.length,
                sum: this.analytics.process('sum', data, field),
                average: this.analytics.process('average', data, field),
                min: this.analytics.process('min', data, field),
                max: this.analytics.process('max', data, field),
            };
        });
        
        return summary;
    }

    /**
     * Generate comparison report
     */
    generateComparison(currentData, previousData, field) {
        const currentSum = this.analytics.process('sum', currentData, field);
        const previousSum = this.analytics.process('sum', previousData, field);
        const growth = this.analytics.calculateGrowth(currentSum, previousSum);
        
        return {
            current: {
                total: currentSum,
                average: this.analytics.process('average', currentData, field),
                count: currentData.length,
            },
            previous: {
                total: previousSum,
                average: this.analytics.process('average', previousData, field),
                count: previousData.length,
            },
            comparison: {
                growth: growth,
                trend: growth > 0 ? 'up' : growth < 0 ? 'down' : 'neutral',
            },
        };
    }

    /**
     * Export report to CSV
     */
    exportToCSV(data, filename = 'report.csv') {
        if (data.length === 0) return;
        
        const headers = Object.keys(data[0]);
        const csvContent = [
            headers.join(','),
            ...data.map(row => 
                headers.map(header => 
                    JSON.stringify(row[header] ?? '')
                ).join(',')
            )
        ].join('\n');
        
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.click();
        URL.revokeObjectURL(url);
    }

    /**
     * Export report to JSON
     */
    exportToJSON(data, filename = 'report.json') {
        const jsonContent = JSON.stringify(data, null, 2);
        const blob = new Blob([jsonContent], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.click();
        URL.revokeObjectURL(url);
    }
}

/**
 * Forecasting Engine
 * Predict future trends based on historical data
 */
export class ForecastingEngine {
    /**
     * Simple linear regression forecast
     */
    linearForecast(data, field, periods = 1) {
        const values = data.map(item => parseFloat(item[field]) || 0);
        const n = values.length;
        
        // Calculate linear regression
        const xMean = (n - 1) / 2;
        const yMean = values.reduce((a, b) => a + b, 0) / n;
        
        let numerator = 0;
        let denominator = 0;
        
        for (let i = 0; i < n; i++) {
            numerator += (i - xMean) * (values[i] - yMean);
            denominator += Math.pow(i - xMean, 2);
        }
        
        const slope = numerator / denominator;
        const intercept = yMean - slope * xMean;
        
        // Generate forecast
        const forecast = [];
        for (let i = 0; i < periods; i++) {
            const x = n + i;
            const y = slope * x + intercept;
            forecast.push(Math.max(0, y)); // Ensure non-negative
        }
        
        return forecast;
    }

    /**
     * Moving average forecast
     */
    movingAverageForecast(data, field, window = 3, periods = 1) {
        const values = data.map(item => parseFloat(item[field]) || 0);
        const lastValues = values.slice(-window);
        const average = lastValues.reduce((a, b) => a + b, 0) / lastValues.length;
        
        return Array(periods).fill(average);
    }

    /**
     * Exponential smoothing forecast
     */
    exponentialSmoothingForecast(data, field, alpha = 0.3, periods = 1) {
        const values = data.map(item => parseFloat(item[field]) || 0);
        let smoothed = values[0];
        
        for (let i = 1; i < values.length; i++) {
            smoothed = alpha * values[i] + (1 - alpha) * smoothed;
        }
        
        return Array(periods).fill(smoothed);
    }
}

// Initialize analytics engine
export function initializeAnalytics() {
    window.mcAnalyticsEngine = new AnalyticsEngine();
    window.mcReportGenerator = new ReportGenerator(window.mcAnalyticsEngine);
    window.mcForecastingEngine = new ForecastingEngine();
    
    console.log('[Mozin Conceito] Analytics Engine initialized');
}

// Auto-initialize
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeAnalytics);
} else {
    initializeAnalytics();
}

export default {
    AnalyticsEngine,
    ReportGenerator,
    ForecastingEngine,
    initializeAnalytics,
};
