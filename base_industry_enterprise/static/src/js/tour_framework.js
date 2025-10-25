/** @odoo-module **/

/**
 * Mozin Conceito Enhanced Tour Framework
 * Modern, interactive guided tours for enterprise applications
 */

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";

/**
 * Enhanced Tour Builder
 * Create sophisticated, multi-step tours with branching logic
 */
export class EnhancedTourBuilder {
    constructor(tourName, options = {}) {
        this.tourName = tourName;
        this.options = {
            url: "/odoo",
            fadeIn: true,
            showBullets: true,
            showProgress: true,
            ...options,
        };
        this.steps = [];
        this.conditions = new Map();
    }

    /**
     * Add a step to the tour
     */
    addStep(stepConfig) {
        const step = {
            trigger: stepConfig.trigger,
            content: stepConfig.content,
            position: stepConfig.position || "bottom",
            run: stepConfig.run || "click",
            tooltipPosition: stepConfig.tooltipPosition || "bottom",
            ...stepConfig,
        };

        // Add step metadata
        step.id = `step_${this.steps.length}`;
        step.index = this.steps.length;

        this.steps.push(step);
        return this;
    }

    /**
     * Add a welcome step
     */
    addWelcomeStep(title, description) {
        return this.addStep({
            trigger: 'body',
            content: `<div class="mc-tour-welcome">
                <h2>${title}</h2>
                <p>${description}</p>
            </div>`,
            position: "center",
            run: () => {},
        });
    }

    /**
     * Add an app navigation step
     */
    addAppStep(appXmlId, description) {
        return this.addStep({
            trigger: `.o_app[data-menu-xmlid="${appXmlId}"]`,
            content: description,
            position: "bottom",
            run: "click",
        });
    }

    /**
     * Add a form field step
     */
    addFieldStep(fieldName, description) {
        return this.addStep({
            trigger: `input[name="${fieldName}"], .o_field_widget[name="${fieldName}"]`,
            content: description,
            position: "right",
        });
    }

    /**
     * Add a button click step
     */
    addButtonStep(buttonText, description) {
        return this.addStep({
            trigger: `button:contains("${buttonText}")`,
            content: description,
            position: "bottom",
            run: "click",
        });
    }

    /**
     * Add a completion step
     */
    addCompletionStep(message) {
        return this.addStep({
            trigger: 'body',
            content: `<div class="mc-tour-complete">
                <div class="mc-tour-complete-icon">✓</div>
                <h2>Congratulations!</h2>
                <p>${message}</p>
            </div>`,
            position: "center",
            run: () => {},
        });
    }

    /**
     * Add conditional logic to a step
     */
    addCondition(stepIndex, condition) {
        this.conditions.set(stepIndex, condition);
        return this;
    }

    /**
     * Build and register the tour
     */
    build() {
        const tourConfig = {
            url: this.options.url,
            steps: () => this.steps.map((step, index) => {
                // Apply conditions if any
                const condition = this.conditions.get(index);
                if (condition && !condition()) {
                    return null;
                }
                return step;
            }).filter(step => step !== null),
        };

        // Register tour
        registry.category("web_tour.tours").add(this.tourName, tourConfig);
        console.log(`[TourBuilder] Registered tour: ${this.tourName}`);
        
        return tourConfig;
    }
}

/**
 * Interactive Tour Manager
 * Manage tour state, progress, and user preferences
 */
export class TourManager {
    constructor() {
        this.tours = new Map();
        this.completedTours = this.loadCompletedTours();
        this.tourProgress = new Map();
    }

    /**
     * Load completed tours from storage
     */
    loadCompletedTours() {
        const stored = localStorage.getItem('mc_completed_tours');
        return stored ? new Set(JSON.parse(stored)) : new Set();
    }

    /**
     * Save completed tours to storage
     */
    saveCompletedTours() {
        localStorage.setItem('mc_completed_tours', 
            JSON.stringify([...this.completedTours]));
    }

    /**
     * Register a tour
     */
    registerTour(name, tour) {
        this.tours.set(name, tour);
    }

    /**
     * Mark tour as completed
     */
    completeTour(tourName) {
        this.completedTours.add(tourName);
        this.saveCompletedTours();
        
        // Track completion
        if (window.mcAnalyticsTracker) {
            window.mcAnalyticsTracker.track('tour_completed', {
                tourName,
                timestamp: new Date().toISOString(),
            });
        }
    }

    /**
     * Check if tour is completed
     */
    isTourCompleted(tourName) {
        return this.completedTours.has(tourName);
    }

    /**
     * Reset tour progress
     */
    resetTour(tourName) {
        this.completedTours.delete(tourName);
        this.tourProgress.delete(tourName);
        this.saveCompletedTours();
    }

    /**
     * Reset all tours
     */
    resetAllTours() {
        this.completedTours.clear();
        this.tourProgress.clear();
        this.saveCompletedTours();
    }

    /**
     * Get tour completion percentage
     */
    getCompletionPercentage() {
        const total = this.tours.size;
        const completed = this.completedTours.size;
        return total > 0 ? (completed / total) * 100 : 0;
    }

    /**
     * Get available tours
     */
    getAvailableTours() {
        return Array.from(this.tours.keys());
    }

    /**
     * Get recommended next tour
     */
    getRecommendedTour() {
        const available = this.getAvailableTours();
        const incomplete = available.filter(name => !this.isTourCompleted(name));
        return incomplete.length > 0 ? incomplete[0] : null;
    }
}

/**
 * Tour Templates
 * Pre-built tour templates for common scenarios
 */
export class TourTemplates {
    /**
     * Create a basic app introduction tour
     */
    static createAppIntroTour(appName, appXmlId, features = []) {
        const builder = new EnhancedTourBuilder(`${appName.toLowerCase()}_intro_tour`);
        
        builder.addWelcomeStep(
            _t(`Welcome to ${appName}!`),
            _t(`This tour will guide you through the key features of ${appName}.`)
        );

        builder.addAppStep(
            appXmlId,
            _t(`Click here to open the ${appName} application.`)
        );

        features.forEach((feature, index) => {
            builder.addStep({
                trigger: feature.trigger,
                content: feature.content,
                position: feature.position || "bottom",
            });
        });

        builder.addCompletionStep(
            _t(`You've completed the ${appName} introduction tour!`)
        );

        return builder.build();
    }

    /**
     * Create a form creation tour
     */
    static createFormTour(modelName, fields = []) {
        const builder = new EnhancedTourBuilder(`${modelName}_form_tour`);
        
        builder.addWelcomeStep(
            _t("Create a New Record"),
            _t(`Let's create a new ${modelName} record together.`)
        );

        builder.addButtonStep(
            "Create",
            _t("Click the Create button to start.")
        );

        fields.forEach(field => {
            builder.addFieldStep(
                field.name,
                field.description || _t(`Fill in the ${field.name} field.`)
            );
        });

        builder.addButtonStep(
            "Save",
            _t("Save your new record.")
        );

        builder.addCompletionStep(
            _t("Great job! You've created a new record.")
        );

        return builder.build();
    }

    /**
     * Create a dashboard tour
     */
    static createDashboardTour(dashboardName, kpis = []) {
        const builder = new EnhancedTourBuilder(`${dashboardName}_dashboard_tour`);
        
        builder.addWelcomeStep(
            _t("Dashboard Overview"),
            _t(`Explore the ${dashboardName} dashboard and key metrics.`)
        );

        kpis.forEach(kpi => {
            builder.addStep({
                trigger: kpi.selector,
                content: kpi.description,
                position: "bottom",
            });
        });

        builder.addCompletionStep(
            _t("You now know how to use the dashboard!")
        );

        return builder.build();
    }
}

/**
 * Initialize Enhanced Tour Framework
 */
export function initializeTourFramework() {
    window.mcTourManager = new TourManager();
    window.mcTourBuilder = EnhancedTourBuilder;
    window.mcTourTemplates = TourTemplates;
    
    console.log('[Mozin Conceito] Enhanced Tour Framework initialized');
}

// Auto-initialize
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeTourFramework);
} else {
    initializeTourFramework();
}

export default {
    EnhancedTourBuilder,
    TourManager,
    TourTemplates,
    initializeTourFramework,
};
