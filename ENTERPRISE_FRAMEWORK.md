# Mozin Conceito Enterprise Framework

## Overview

The Mozin Conceito Enterprise Framework is a comprehensive, modern design system and feature set that transforms industry-specific Odoo modules into enterprise-grade applications. This framework provides a consistent, accessible, and performant foundation for over 100 industry modules.

## 🎯 Key Features

### Modern Design System
- **CSS Variables & Design Tokens**: Consistent theming across all modules
- **Responsive Grid System**: Mobile-first, adaptive layouts
- **Typography Scale**: Professional font sizing and spacing
- **Color Palette**: Primary, secondary, accent, and semantic colors
- **Dark Mode Support**: Automatic theme switching based on user preferences
- **Elevation & Shadows**: Depth hierarchy for better UI organization

### Component Library
- **Buttons**: Primary, secondary, outline variants
- **Cards**: Content containers with headers, bodies, and footers
- **Badges**: Status indicators and labels
- **Alerts**: Success, warning, error, and info messages
- **Modals**: Dialog boxes with backdrop
- **Tabs**: Content organization
- **Dropdowns**: Navigation and selection menus
- **Forms**: Input fields, textareas, checkboxes, radio buttons
- **Tables**: Data display with sorting and filtering
- **Pagination**: Navigation for large datasets
- **Tooltips**: Contextual help
- **Breadcrumbs**: Navigation hierarchy
- **Avatars**: User representations
- **Loading Spinners**: Activity indicators

### Dashboard Widgets
- **KPI Cards**: Key performance indicators with trend indicators
- **Chart Widgets**: Line, bar, pie, and doughnut charts
- **Stats Cards**: Statistical displays with icons
- **Progress Bars**: Visual progress indicators
- **Timeline**: Event sequences
- **Data Tables**: Interactive tabular data
- **Metric Cards**: Comparative metrics

### Analytics Engine
- **Data Processing**: Aggregation, grouping, filtering
- **Trend Analysis**: Moving averages, growth rates
- **Forecasting**: Linear regression, exponential smoothing
- **Anomaly Detection**: Statistical outlier identification
- **Report Generation**: Customizable reports
- **Export**: CSV and JSON export capabilities

### Enhanced Tour Framework
- **Interactive Tours**: Step-by-step guidance
- **Branching Logic**: Conditional tour paths
- **Progress Tracking**: Tour completion monitoring
- **Tour Templates**: Pre-built tour patterns
- **Visual Design**: Modern, engaging tour UI

### Performance Optimizations
- **Client-side Caching**: Reduced server requests
- **Lazy Loading**: On-demand resource loading
- **Performance Monitoring**: Metrics tracking
- **Code Splitting**: Modular loading

### Enterprise Features
- **Theme Manager**: Dynamic theme switching
- **Feature Flags**: Gradual feature rollouts
- **Analytics Tracker**: Event and interaction tracking
- **Notification System**: Enterprise-level notifications
- **Accessibility**: WCAG 2.1 AAA compliance

## 📁 Architecture

```
base_industry_enterprise/
├── __init__.py
├── __manifest__.py
├── static/
│   ├── description/
│   │   └── index.html          # Module description
│   └── src/
│       ├── js/
│       │   ├── enterprise_core.js      # Core functionality
│       │   ├── dashboard_widgets.js     # Dashboard components
│       │   ├── analytics_engine.js      # Analytics tools
│       │   └── tour_framework.js        # Enhanced tours
│       └── scss/
│           ├── enterprise_theme.scss    # Base theme
│           ├── dashboard.scss           # Dashboard styles
│           ├── components.scss          # UI components
│           └── frontend_enterprise.scss # Frontend styles
```

## 🚀 Getting Started

### Installation

1. **Install the base module**:
   ```bash
   # Navigate to your Odoo addons directory
   cd /path/to/odoo/addons
   
   # The module is already present in the industry-mozin_conceito repository
   ```

2. **Update your module list**:
   - Go to Apps → Update Apps List
   - Search for "Industry Enterprise Base"
   - Click Install

### Using in Your Industry Module

1. **Add dependency** in your `__manifest__.py`:
   ```python
   'depends': [
       'base_industry_enterprise',
       # ... other dependencies
   ],
   ```

2. **Include assets** in your `__manifest__.py`:
   ```python
   'assets': {
       'web.assets_backend': [
           'your_module/static/src/scss/your_styles.scss',
           'your_module/static/src/js/your_script.js',
       ],
   },
   ```

3. **Import base styles** in your SCSS file:
   ```scss
   @import '../../../base_industry_enterprise/static/src/scss/enterprise_theme.scss';
   @import '../../../base_industry_enterprise/static/src/scss/dashboard.scss';
   ```

## 🎨 Design System Usage

### Color Variables
```css
/* Primary Colors */
--mc-primary: #2C5AA0;
--mc-primary-dark: #1e3d6e;
--mc-primary-light: #4a7bc8;

/* Use in your styles */
.my-button {
    background-color: var(--mc-primary);
    color: var(--mc-text-inverse);
}
```

### Spacing Scale
```css
/* Spacing utilities */
--mc-space-1: 0.25rem;  /* 4px */
--mc-space-2: 0.5rem;   /* 8px */
--mc-space-4: 1rem;     /* 16px */
--mc-space-6: 1.5rem;   /* 24px */
```

### Typography
```html
<h1 class="mc-heading-1">Main Heading</h1>
<h2 class="mc-heading-2">Subheading</h2>
<p class="mc-text-body">Body text</p>
```

### Buttons
```html
<button class="mc-btn mc-btn-primary">Primary Action</button>
<button class="mc-btn mc-btn-secondary">Secondary Action</button>
<button class="mc-btn mc-btn-outline">Outlined Button</button>
```

### Cards
```html
<div class="mc-card">
    <div class="mc-card-header">
        <h3>Card Title</h3>
    </div>
    <div class="mc-card-body">
        <p>Card content goes here</p>
    </div>
    <div class="mc-card-footer">
        <button class="mc-btn mc-btn-primary">Action</button>
    </div>
</div>
```

## 📊 Dashboard Example

```javascript
// Using dashboard widgets
import { KPIWidget, ChartWidget } from '@base_industry_enterprise/dashboard_widgets';

// Create a KPI widget
<KPIWidget 
    title="Daily Sales"
    value={2847.50}
    change={12.5}
    icon="💰"
    variant="success"
/>

// Create a chart widget
<ChartWidget 
    title="Sales Trend"
    type="line"
    data={salesData}
/>
```

## 🧪 Analytics Usage

```javascript
// Using the analytics engine
const analytics = window.mcAnalyticsEngine;

// Calculate sum
const totalSales = analytics.process('sum', salesData, 'amount');

// Calculate average
const avgOrder = analytics.process('average', orders, 'total');

// Detect anomalies
const outliers = analytics.detectAnomalies(data, 'value', 2);

// Generate forecast
const forecast = window.mcForecastingEngine.linearForecast(data, 'sales', 7);
```

## 🎯 Tour Framework

```javascript
import { EnhancedTourBuilder } from '@base_industry_enterprise/tour_framework';

// Create a custom tour
const tour = new EnhancedTourBuilder('my_feature_tour');

tour.addWelcomeStep(
    'Welcome to Feature X',
    'This tour will guide you through the key features'
);

tour.addAppStep(
    'my_module.my_app_menu',
    'Click here to open the application'
);

tour.addCompletionStep(
    'You\'ve completed the tour!'
);

tour.build();
```

## 🔧 Performance Features

```javascript
// Use caching
window.mcCacheManager.set('my_data', data, 60000); // 60 seconds TTL
const cachedData = window.mcCacheManager.get('my_data');

// Track analytics
window.mcAnalyticsTracker.track('feature_used', {
    feature: 'export',
    format: 'csv',
});

// Check feature flags
if (window.mcFeatureFlagManager.isEnabled('new_dashboard')) {
    // Show new dashboard
}
```

## 📱 Responsive Design

The framework is mobile-first and includes responsive breakpoints:

- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

All components automatically adapt to screen size.

## ♿ Accessibility

The framework follows WCAG 2.1 Level AAA guidelines:

- Semantic HTML
- Keyboard navigation support
- Screen reader compatibility
- Focus indicators
- Sufficient color contrast
- Skip links
- ARIA labels and roles

## 🎨 Customization

### Override Theme Colors

```css
:root {
    /* Override primary color */
    --mc-primary: #your-color;
    --mc-primary-dark: #your-dark-color;
    --mc-primary-light: #your-light-color;
}
```

### Custom Components

```scss
// Extend base components
.my-custom-card {
    @extend .mc-card;
    border-left: 4px solid var(--my-brand-color);
}
```

## 📚 Examples

See the following modules for implementation examples:

- **Bakery** (`bakery/`): Complete dashboard, enhanced tours, custom styling
- **Fitness** (`fitness/`): Member analytics, class scheduling, equipment tracking
- **Restaurant** (`industry_restaurant/`): Order management, table tracking
- **Hotel** (`hotel/`): Booking engine, room management

## 🤝 Contributing

To add enterprise features to a new industry module:

1. Add `base_industry_enterprise` to dependencies
2. Create module-specific SCSS file importing base styles
3. Create module-specific JavaScript for analytics
4. Enhance tours using the tour framework
5. Update module description with modern design

## 📝 Best Practices

1. **Always use design tokens**: Use CSS variables instead of hard-coded values
2. **Maintain consistency**: Follow the established component patterns
3. **Test accessibility**: Ensure keyboard navigation and screen reader support
4. **Optimize performance**: Use caching and lazy loading where appropriate
5. **Document custom features**: Add clear comments for module-specific code
6. **Use semantic HTML**: Proper heading hierarchy and ARIA labels
7. **Mobile-first**: Design for mobile, enhance for desktop

## 🔗 Resources

- [Odoo Documentation](https://www.odoo.com/documentation)
- [WCAG Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [CSS Variables Reference](https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties)

## 📄 License

OPL-1 (Odoo Proprietary License)

## 👥 Authors

- Mozin Conceito Team
- Odoo S.A.

---

**Version**: 2.0  
**Last Updated**: October 2024
