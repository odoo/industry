/** @odoo-module **/

/**
 * Mozin Conceito Enterprise Core
 * Core JavaScript functionality for enterprise features
 */

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onMounted } from "@odoo/owl";

/**
 * Enterprise Theme Manager
 * Manages theme switching and customization
 */
export class ThemeManager {
    constructor() {
        this.currentTheme = this.getStoredTheme() || 'light';
        this.applyTheme(this.currentTheme);
    }

    getStoredTheme() {
        return localStorage.getItem('mc_theme');
    }

    setTheme(theme) {
        this.currentTheme = theme;
        localStorage.setItem('mc_theme', theme);
        this.applyTheme(theme);
        this.notifyThemeChange(theme);
    }

    applyTheme(theme) {
        const root = document.documentElement;
        if (theme === 'dark') {
            root.classList.add('mc-dark-mode');
        } else {
            root.classList.remove('mc-dark-mode');
        }
    }

    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
    }

    notifyThemeChange(theme) {
        const event = new CustomEvent('themeChange', { detail: { theme } });
        window.dispatchEvent(event);
    }
}

/**
 * Notification Manager
 * Enterprise-level notification system
 */
export class NotificationManager {
    constructor(notificationService) {
        this.service = notificationService;
    }

    success(message, options = {}) {
        this.service.add(message, {
            type: 'success',
            className: 'mc-notification mc-notification-success',
            ...options,
        });
    }

    error(message, options = {}) {
        this.service.add(message, {
            type: 'danger',
            className: 'mc-notification mc-notification-error',
            ...options,
        });
    }

    warning(message, options = {}) {
        this.service.add(message, {
            type: 'warning',
            className: 'mc-notification mc-notification-warning',
            ...options,
        });
    }

    info(message, options = {}) {
        this.service.add(message, {
            type: 'info',
            className: 'mc-notification mc-notification-info',
            ...options,
        });
    }
}

/**
 * Data Cache Manager
 * Client-side caching for improved performance
 */
export class CacheManager {
    constructor() {
        this.cache = new Map();
        this.ttl = 5 * 60 * 1000; // 5 minutes default TTL
    }

    set(key, value, ttl = this.ttl) {
        const expiry = Date.now() + ttl;
        this.cache.set(key, { value, expiry });
    }

    get(key) {
        const item = this.cache.get(key);
        if (!item) return null;

        if (Date.now() > item.expiry) {
            this.cache.delete(key);
            return null;
        }

        return item.value;
    }

    has(key) {
        return this.get(key) !== null;
    }

    clear() {
        this.cache.clear();
    }

    clearExpired() {
        const now = Date.now();
        for (const [key, item] of this.cache.entries()) {
            if (now > item.expiry) {
                this.cache.delete(key);
            }
        }
    }
}

/**
 * Analytics Tracker
 * Track user interactions and events
 */
export class AnalyticsTracker {
    constructor() {
        this.events = [];
        this.sessionId = this.generateSessionId();
    }

    generateSessionId() {
        return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    track(eventName, properties = {}) {
        const event = {
            name: eventName,
            properties,
            timestamp: new Date().toISOString(),
            sessionId: this.sessionId,
        };
        this.events.push(event);
        console.log('[Analytics]', event);
        
        // Could send to analytics service here
        this.sendToAnalytics(event);
    }

    sendToAnalytics(event) {
        // Placeholder for analytics service integration
        // This could send data to Google Analytics, Mixpanel, etc.
        if (window.gtag) {
            window.gtag('event', event.name, event.properties);
        }
    }

    getEvents() {
        return [...this.events];
    }

    clearEvents() {
        this.events = [];
    }
}

/**
 * Performance Monitor
 * Monitor application performance metrics
 */
export class PerformanceMonitor {
    constructor() {
        this.metrics = {
            pageLoads: [],
            apiCalls: [],
            interactions: [],
        };
    }

    recordPageLoad() {
        if (window.performance && window.performance.timing) {
            const perfData = window.performance.timing;
            const loadTime = perfData.loadEventEnd - perfData.navigationStart;
            
            this.metrics.pageLoads.push({
                timestamp: new Date().toISOString(),
                loadTime,
                domReady: perfData.domContentLoadedEventEnd - perfData.navigationStart,
            });
        }
    }

    recordApiCall(endpoint, duration, success) {
        this.metrics.apiCalls.push({
            endpoint,
            duration,
            success,
            timestamp: new Date().toISOString(),
        });
    }

    recordInteraction(action, duration) {
        this.metrics.interactions.push({
            action,
            duration,
            timestamp: new Date().toISOString(),
        });
    }

    getMetrics() {
        return { ...this.metrics };
    }

    getAverageLoadTime() {
        if (this.metrics.pageLoads.length === 0) return 0;
        const sum = this.metrics.pageLoads.reduce((acc, load) => acc + load.loadTime, 0);
        return sum / this.metrics.pageLoads.length;
    }
}

/**
 * Feature Flag Manager
 * Manage feature flags for gradual rollouts
 */
export class FeatureFlagManager {
    constructor() {
        this.flags = new Map();
        this.loadFlags();
    }

    loadFlags() {
        const storedFlags = localStorage.getItem('mc_feature_flags');
        if (storedFlags) {
            const flags = JSON.parse(storedFlags);
            Object.entries(flags).forEach(([key, value]) => {
                this.flags.set(key, value);
            });
        }
    }

    saveFlags() {
        const flagsObject = Object.fromEntries(this.flags);
        localStorage.setItem('mc_feature_flags', JSON.stringify(flagsObject));
    }

    isEnabled(flagName, defaultValue = false) {
        return this.flags.get(flagName) ?? defaultValue;
    }

    enable(flagName) {
        this.flags.set(flagName, true);
        this.saveFlags();
    }

    disable(flagName) {
        this.flags.set(flagName, false);
        this.saveFlags();
    }

    toggle(flagName) {
        const current = this.isEnabled(flagName);
        this.flags.set(flagName, !current);
        this.saveFlags();
    }
}

/**
 * Initialize Enterprise Core Services
 */
export function initializeEnterpriseCore() {
    // Initialize global managers
    window.mcThemeManager = new ThemeManager();
    window.mcCacheManager = new CacheManager();
    window.mcAnalyticsTracker = new AnalyticsTracker();
    window.mcPerformanceMonitor = new PerformanceMonitor();
    window.mcFeatureFlagManager = new FeatureFlagManager();

    // Record initial page load
    window.addEventListener('load', () => {
        window.mcPerformanceMonitor.recordPageLoad();
    });

    // Clear expired cache every 5 minutes
    setInterval(() => {
        window.mcCacheManager.clearExpired();
    }, 5 * 60 * 1000);

    console.log('[Mozin Conceito] Enterprise Core initialized');
}

// Auto-initialize when module loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeEnterpriseCore);
} else {
    initializeEnterpriseCore();
}

// Export all classes and functions
export default {
    ThemeManager,
    NotificationManager,
    CacheManager,
    AnalyticsTracker,
    PerformanceMonitor,
    FeatureFlagManager,
    initializeEnterpriseCore,
};
