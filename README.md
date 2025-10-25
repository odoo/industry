[![Build Status](https://runbot.odoo.com/runbot/badge/flat/1/master.svg)](https://runbot.odoo.com/runbot)
[![Tech Doc](https://img.shields.io/badge/master-docs-875A7B.svg?style=flat&colorA=8F8F8F)](https://www.odoo.com/documentation/master)
[![Help](https://img.shields.io/badge/master-help-875A7B.svg?style=flat&colorA=8F8F8F)](https://www.odoo.com/forum/help-1)
[![Nightly Builds](https://img.shields.io/badge/master-nightly-875A7B.svg?style=flat&colorA=8F8F8F)](https://nightly.odoo.com/)

# MozinConceito - Industry-Specific Business Solutions

MozinConceito is a comprehensive ecosystem of industry-specific Odoo modules designed to provide complete business management solutions for startups and enterprises across multiple verticals.

## What is MozinConceito?

MozinConceito integrates 10 specialized industry modules that work together to provide a unified platform for managing diverse business operations. Whether you're running a food service business, a logistics company, or an e-learning platform, MozinConceito provides pre-configured, industry-tested solutions that you can deploy and customize for your specific needs.

## Core Industry Modules

### Hospitality & Food Services
- **[Fast Food](fast_food/)** - Quick service restaurant management with POS, online ordering, and kitchen display systems
- **[Fine Dining Restaurant](industry_restaurant/)** - Premium restaurant operations with reservations and table management
- **[Food Trucks](food_trucks/)** - Mobile food service management with location-based operations
- **[Members Club](members_club/)** - Membership management with subscriptions, events, and partner programs

### Services & Operations
- **[Handyman Services](handyman/)** - Field service management for maintenance and repair businesses
- **[eLearning Platform](elearning_platform/)** - Online education platform with course management and certification
- **[3PL Logistics Company](3pl_logistic_company/)** - Warehousing and fulfillment with quality control and subscriptions

### Retail & Distribution
- **[Gallery](gallery/)** - Art gallery management with commission tracking and consignment
- **[Agriculture Shop](agriculture_shop/)** - Agricultural retail with expiry tracking and inventory management
- **[Food Distribution](food_distribution/)** - Food manufacturing and distribution with quality control and MRP

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/greeklekissle/industry-mozin_conceito.git
cd industry-mozin_conceito

# Run a specific industry module with demo data
./run_industry.sh -n [module_name] -d
```

### Examples

```bash
# Start fast food module
./run_industry.sh -n fast_food -d

# Start handyman services module
./run_industry.sh -n handyman -d

# Start 3PL logistics module
./run_industry.sh -n 3pl_logistic_company -d
```

The server will start on http://localhost:8069 with demo data pre-loaded.

## Documentation

### 📚 Complete Documentation

**New to MozinConceito? Start with [INDEX.md](INDEX.md) - Your complete guide to all documentation!**

#### Core Documents
- **[INDEX.md](INDEX.md)** - 📖 Complete documentation index and navigation guide
- **[MOZIN_CONCEITO.md](MOZIN_CONCEITO.md)** - Comprehensive overview of all modules, features, and architecture
- **[WORKFLOW.md](WORKFLOW.md)** - Detailed development, audit, and deployment workflows
- **[QUICK_START.md](QUICK_START.md)** - Quick reference guide for getting started with each module
- **[MODULE_MATRIX.md](MODULE_MATRIX.md)** - Feature comparison matrix and decision support

### 🚀 Getting Started
1. Read [INDEX.md](INDEX.md) to navigate the documentation effectively
2. Use [QUICK_START.md](QUICK_START.md) to identify which module fits your business
3. Follow the module-specific quick start guide (30-90 minutes)
4. Use the audit checklists in [WORKFLOW.md](WORKFLOW.md) to validate your setup
5. Refer to [MOZIN_CONCEITO.md](MOZIN_CONCEITO.md) for detailed feature documentation

## Module Selection Guide

| Your Business Type | Recommended Module | Start Here |
|-------------------|-------------------|------------|
| Quick service restaurant | `fast_food` | [Fast Food Quick Start](QUICK_START.md#fast-food---quick-start) |
| Fine dining restaurant | `industry_restaurant` | [Restaurant Quick Start](QUICK_START.md#industry-restaurant---quick-start) |
| Food truck / Mobile food | `food_trucks` | [Food Trucks Quick Start](QUICK_START.md#food-trucks---quick-start) |
| Home repair services | `handyman` | [Handyman Quick Start](QUICK_START.md#handyman---quick-start) |
| Art gallery / Dealer | `gallery` | [Gallery Quick Start](QUICK_START.md#gallery---quick-start) |
| Farm supply store | `agriculture_shop` | [Agriculture Shop Quick Start](QUICK_START.md#agriculture-shop---quick-start) |
| Food manufacturing | `food_distribution` | [Food Distribution Quick Start](QUICK_START.md#food-distribution---quick-start) |
| Online courses | `elearning_platform` | [eLearning Quick Start](QUICK_START.md#elearning-platform---quick-start) |
| Membership organization | `members_club` | [Members Club Quick Start](QUICK_START.md#members-club---quick-start) |
| Warehousing / Fulfillment | `3pl_logistic_company` | [3PL Logistics Quick Start](QUICK_START.md#3pl-logistics-company---quick-start) |

## Key Features

### Integrated Workflows
All modules share common foundational features and integrate seamlessly:
- **Knowledge Base** - Internal documentation and training materials
- **CRM** - Customer relationship management
- **Sales** - Quote to cash processes
- **Inventory** - Stock management and tracking
- **Accounting** - Financial management and reporting
- **HR & Planning** - Employee management and scheduling

### Industry-Specific Capabilities
Each module includes specialized features for its industry:
- POS systems for retail and hospitality
- Field service management for service businesses
- Manufacturing and quality control for production
- Subscription and membership management
- Event and appointment scheduling
- Website and e-commerce integration

### Customization & Extensibility
- Web Studio for no-code customizations
- Custom fields and workflows
- Automated actions and rules
- Custom reports and dashboards
- API integrations

## Development Workflow

### Setting Up Development Environment

```bash
# Install module with demo data for development
./run_industry.sh -n [module_name] -d -i

# Run tests
./run_industry.sh -n [module_name] -t

# Reset database
./run_industry.sh -n [module_name] -h

# Enable debugging (Python debugpy on port 5678)
./run_industry.sh -n [module_name] -p
```

### Audit and Quality Assurance

Each module includes comprehensive audit checklists in [WORKFLOW.md](WORKFLOW.md):
- Configuration validation
- Data integrity checks
- Integration testing
- User acceptance criteria
- Security audit
- Performance benchmarks

### Deployment

Follow the deployment workflow in [WORKFLOW.md](WORKFLOW.md#deployment-process):
1. Pre-deployment checklist
2. Data migration
3. Configuration review
4. Testing and validation
5. Go-live procedures
6. Post-deployment monitoring

## Customization for Your Startup

MozinConceito modules are designed to be customized for your specific materials, services, and products:

1. **Map Your Offerings** - Use the worksheets in [QUICK_START.md](QUICK_START.md) to map your products/services to module features
2. **Configure Settings** - Adjust module settings to match your business processes
3. **Add Custom Fields** - Extend data models with your specific requirements
4. **Create Automation** - Define automated workflows for your operations
5. **Design Reports** - Build custom dashboards and reports for your KPIs

See [WORKFLOW.md](WORKFLOW.md#module-customization-guide) for detailed customization guidance.

## Support and Community

### Documentation & Resources
- [Complete Module Documentation](MOZIN_CONCEITO.md)
- [Development Workflows](WORKFLOW.md)
- [Quick Start Guides](QUICK_START.md)
- [Odoo Official Documentation](https://www.odoo.com/documentation/master)

### Getting Help
- **Issues**: Report bugs and request features via GitHub Issues
- **Discussions**: Ask questions and share knowledge in GitHub Discussions
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines

### Training & Learning
- Use the eLearning module to create internal training materials
- Explore demo data to understand workflows
- Review Knowledge articles within each module
- Follow the audit checklists to ensure proper implementation

## About Odoo

Odoo is a suite of web based open source business apps. The main Odoo Apps include an <a href="https://www.odoo.com/page/crm">Open Source CRM</a>,
<a href="https://www.odoo.com/app/website">Website Builder</a>,
<a href="https://www.odoo.com/app/ecommerce">eCommerce</a>,
<a href="https://www.odoo.com/app/inventory">Warehouse Management</a>,
<a href="https://www.odoo.com/app/project">Project Management</a>,
<a href="https://www.odoo.com/app/accounting">Billing &amp; Accounting</a>,
<a href="https://www.odoo.com/app/point-of-sale-shop">Point of Sale</a>,
<a href="https://www.odoo.com/app/employees">Human Resources</a>,
<a href="https://www.odoo.com/app/social-marketing">Marketing</a>,
<a href="https://www.odoo.com/app/manufacturing">Manufacturing</a>,
<a href="https://www.odoo.com/">and more</a>.

Odoo Apps can be used as stand-alone applications, but they also integrate seamlessly so you get
a full-featured <a href="https://www.odoo.com">Open Source ERP</a> when you install several Apps.

For a standard Odoo installation, please follow the <a href="https://www.odoo.com/documentation/master/administration/install/install.html">Setup instructions</a>
from the official documentation.

To learn Odoo, we recommend the <a href="https://www.odoo.com/slides">Odoo eLearning</a> platform, or <a href="https://www.odoo.com/page/scale-up-business-game">Scale-up</a>, the business game. Developers can start with <a href="https://www.odoo.com/documentation/master/developer/howtos.html">the developer tutorials</a>.

## License

This project is licensed under the Odoo Proprietary License v1.0 (OPL-1). See [LICENSE](LICENSE) file for details.

## Authors

**Original Odoo Modules**: Odoo S.A.  
**MozinConceito Integration & Documentation**: MozinConceito Team

---

*MozinConceito - Building integrated business solutions, one industry at a time.*
