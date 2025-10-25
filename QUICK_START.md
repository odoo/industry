# MozinConceito Quick Start Guide

## Introduction

Welcome to MozinConceito! This guide will help you quickly identify which industry modules best fit your startup's materials, services, and products.

## Quick Module Selector

### Food & Beverage Services

| Your Business | Best Module | Alternative Modules |
|--------------|-------------|---------------------|
| Quick service restaurant | `fast_food` | `industry_restaurant` |
| Fine dining restaurant | `industry_restaurant` | `fast_food` |
| Food truck / Mobile food | `food_trucks` | `fast_food` |
| Food manufacturing | `food_distribution` | - |
| Catering services | `industry_restaurant` | `food_trucks` |

### Retail & E-commerce

| Your Business | Best Module | Alternative Modules |
|--------------|-------------|---------------------|
| Art gallery / Dealer | `gallery` | - |
| Farm supply store | `agriculture_shop` | - |
| General retail | `agriculture_shop` | `gallery` |
| Subscription box service | `members_club` | `3pl_logistic_company` |

### Services

| Your Business | Best Module | Alternative Modules |
|--------------|-------------|---------------------|
| Home repair / Maintenance | `handyman` | - |
| Membership organization | `members_club` | - |
| Online courses / Training | `elearning_platform` | - |
| Warehousing / Fulfillment | `3pl_logistic_company` | - |
| Field services | `handyman` | `food_trucks` |

## Getting Started in 5 Steps

### Step 1: Identify Your Primary Business Line

Ask yourself:
- What is my main revenue source?
- Who are my primary customers?
- What is my core service/product?

### Step 2: Select Your Module

Use the Quick Module Selector above to identify your primary module.

### Step 3: Set Up Development Environment

```bash
# Clone the repository
git clone https://github.com/greeklekissle/industry-mozin_conceito.git
cd industry-mozin_conceito

# Install your module with demo data
./run_industry.sh -n [your_module] -d
```

Examples:
```bash
# For a fast food restaurant
./run_industry.sh -n fast_food -d

# For a handyman service
./run_industry.sh -n handyman -d

# For an art gallery
./run_industry.sh -n gallery -d
```

### Step 4: Explore the Demo Data

Once the server starts (default: http://localhost:8069):
- Login with admin credentials
- Explore sample transactions
- Test workflows
- Review reports and dashboards

### Step 5: Map Your Materials and Services

Use the worksheets below to map your specific offerings.

---

## Module-Specific Quick Starts

### Fast Food - Quick Start

**Perfect for:** Quick service restaurants, cafes, food courts

**Initial Setup (30 minutes):**

1. **Configure POS**
   - Navigate to: Point of Sale → Configuration → Point of Sale
   - Click: Create
   - Set: Shop name, payment methods

2. **Set Up Menu**
   - Navigate to: Point of Sale → Products → Products
   - Import your menu items with prices
   - Organize into categories

3. **Add Employees**
   - Navigate to: Employees → Employees
   - Add staff members
   - Assign POS access rights

4. **Test Transaction**
   - Open POS session
   - Create test order
   - Process payment
   - Verify receipt

**Your Materials/Services Mapping:**

| Your Menu Item | Category | Price | Cost | Modifiers |
|----------------|----------|-------|------|-----------|
| Example: Burger | Main | $10 | $4 | Cheese, Bacon |
| | | | | |

---

### Members Club - Quick Start

**Perfect for:** Fitness clubs, professional associations, private clubs

**Initial Setup (45 minutes):**

1. **Create Membership Plans**
   - Navigate to: Subscriptions → Products
   - Define: Basic, Premium, VIP plans
   - Set: Pricing and duration

2. **Configure Benefits**
   - Define member grades
   - Map benefits to each grade
   - Set up renewal rules

3. **Set Up Events**
   - Navigate to: Events → Events
   - Create sample event
   - Configure ticketing

4. **Test Member Journey**
   - Create test member
   - Process subscription payment
   - Register for event
   - Verify emails sent

**Your Services Mapping:**

| Membership Type | Monthly Fee | Annual Fee | Benefits |
|----------------|-------------|------------|----------|
| Example: Gold | $99 | $999 | All access |
| | | | |

---

### Industry Restaurant - Quick Start

**Perfect for:** Fine dining, upscale restaurants, catering

**Initial Setup (60 minutes):**

1. **Configure Table Layout**
   - Navigate to: Point of Sale → Configuration → Restaurant
   - Set up: Floors and tables
   - Define: Table capacity

2. **Set Up Reservations**
   - Navigate to: Appointments → Configuration
   - Create: Dining appointment types
   - Set: Available time slots

3. **Configure Menu**
   - Create: Courses (appetizers, mains, desserts)
   - Add: Dishes with descriptions
   - Set: Pricing and preparation time

4. **Test Reservation Flow**
   - Book table via website
   - Confirm reservation
   - Process dining experience
   - Generate bill

**Your Menu Structure:**

| Course | Dish Name | Description | Price | Prep Time |
|--------|-----------|-------------|-------|-----------|
| Appetizer | | | | |
| Main | | | | |
| Dessert | | | | |

---

### Handyman - Quick Start

**Perfect for:** Home repair, maintenance, contracting services

**Initial Setup (45 minutes):**

1. **Define Service Catalog**
   - Navigate to: Sales → Products → Products
   - Create: Service items
   - Set: Hourly rates or fixed prices

2. **Configure Service Areas**
   - Set: Geographic territories
   - Define: Service zones
   - Configure: Travel time

3. **Set Up Technicians**
   - Add: Employee records
   - Assign: Skills and certifications
   - Configure: Availability

4. **Test Service Request**
   - Create: Lead from website
   - Convert: To project
   - Schedule: Technician
   - Complete: Timesheet
   - Generate: Invoice

**Your Services Catalog:**

| Service Type | Duration | Price | Required Skills |
|-------------|----------|-------|----------------|
| Plumbing | 2 hrs | $150 | Plumbing cert |
| | | | |

---

### Gallery - Quick Start

**Perfect for:** Art galleries, artist representation, art dealers

**Initial Setup (60 minutes):**

1. **Set Up Artists**
   - Navigate to: Contacts → Contacts
   - Create: Artist profiles
   - Configure: Commission rates

2. **Add Artwork Catalog**
   - Navigate to: Products → Products
   - Add: Artworks with images
   - Set: Pricing and variants
   - Mark: Consignment terms

3. **Configure Exhibitions**
   - Navigate to: Events → Events
   - Create: Exhibition
   - Set: Duration and location
   - Add: Featured artworks

4. **Test Sale Process**
   - Create: Sales order
   - Add: Artwork
   - Calculate: Commission
   - Generate: Consignment agreement
   - Process: Payment split

**Your Inventory Tracking:**

| Artwork | Artist | Medium | Size | Consignment/Owned | Price |
|---------|--------|--------|------|-------------------|-------|
| | | | | | |

---

### Food Trucks - Quick Start

**Perfect for:** Mobile food vendors, pop-up restaurants

**Initial Setup (45 minutes):**

1. **Configure Mobile POS**
   - Set up: Offline-capable POS
   - Configure: Payment terminals
   - Set: Menu availability

2. **Define Locations**
   - Add: Regular locations
   - Set: Operating hours per location
   - Configure: Location-based pricing

3. **Set Up Scheduling**
   - Navigate to: Planning
   - Create: Location schedule
   - Assign: Staff to locations
   - Plan: Route optimization

4. **Test Mobile Operation**
   - Start: POS session
   - Process: Orders offline
   - Sync: When online
   - Generate: Location reports

**Your Location Schedule:**

| Day | Location | Hours | Expected Volume |
|-----|----------|-------|----------------|
| Monday | | | |
| | | | |

---

### Food Distribution - Quick Start

**Perfect for:** Food manufacturers, wholesalers, distributors

**Initial Setup (90 minutes):**

1. **Configure Manufacturing**
   - Navigate to: Manufacturing → Products
   - Create: Bill of Materials
   - Define: Routing operations
   - Set up: Work centers

2. **Set Up Quality Control**
   - Define: Quality checkpoints
   - Create: Inspection worksheets
   - Configure: Pass/fail criteria

3. **Configure Expiry Tracking**
   - Enable: Lot/Serial numbers
   - Set: Expiry alert rules
   - Configure: FEFO removal strategy

4. **Test Production Flow**
   - Create: Manufacturing order
   - Process: Work orders
   - Perform: Quality checks
   - Complete: Production
   - Update: Inventory

**Your Products & BOMs:**

| Finished Product | Raw Materials | Quantity | Shelf Life |
|-----------------|---------------|----------|------------|
| | | | |

---

### eLearning Platform - Quick Start

**Perfect for:** Online course providers, training companies

**Initial Setup (60 minutes):**

1. **Create Course Structure**
   - Navigate to: Website → Courses
   - Create: Course categories
   - Define: Course paths

2. **Upload Content**
   - Add: Slides/presentations
   - Upload: Videos
   - Create: Quizzes
   - Design: Certificates

3. **Configure Commerce**
   - Set: Course pricing
   - Add: Subscription options
   - Configure: Payment gateway
   - Set up: Discount codes

4. **Test Student Journey**
   - Register: As student
   - Purchase: Course
   - Complete: Lessons
   - Pass: Certification
   - Download: Certificate

**Your Course Catalog:**

| Course Name | Duration | Level | Price | Certification |
|-------------|----------|-------|-------|---------------|
| | | | | |

---

### Agriculture Shop - Quick Start

**Perfect for:** Farm supply stores, garden centers

**Initial Setup (45 minutes):**

1. **Import Product Catalog**
   - Navigate to: Products → Products
   - Import: Inventory with expiry dates
   - Set up: Product categories
   - Configure: Seasonal tags

2. **Configure POS & Website**
   - Set up: Retail POS
   - Enable: Website shop
   - Configure: Loyalty program
   - Set: Seasonal promotions

3. **Set Up Suppliers**
   - Add: Supplier contacts
   - Configure: Purchase agreements
   - Set: Reorder points
   - Enable: Requisitions

4. **Test Full Cycle**
   - Create: Purchase order
   - Receive: Inventory
   - Sell: Via POS
   - Process: Customer loyalty
   - Generate: Reports

**Your Product Categories:**

| Category | Seasonal? | Expiry Tracking | Suppliers |
|----------|-----------|-----------------|-----------|
| Seeds | Yes | No | |
| Fertilizer | No | Yes | |
| | | | |

---

### 3PL Logistics Company - Quick Start

**Perfect for:** Warehouses, fulfillment centers, logistics providers

**Initial Setup (90 minutes):**

1. **Configure Warehouse**
   - Navigate to: Inventory → Configuration
   - Set up: Locations hierarchy
   - Define: Storage categories
   - Configure: Package types

2. **Set Up Billing Structure**
   - Create: Fee rate tables
   - Define: Storage fees
   - Set: Handling charges
   - Configure: Subscription plans

3. **Create Quality Processes**
   - Define: Inspection points
   - Create: Quality checks
   - Set: Acceptance criteria

4. **Configure Customer Portal**
   - Enable: Portal access
   - Set up: Custom dashboards
   - Configure: Inventory visibility
   - Enable: Document sharing

5. **Test End-to-End Flow**
   - Create: Customer account
   - Receive: Inventory
   - Perform: Quality check
   - Store: In locations
   - Process: Outbound order
   - Generate: Invoice

**Your Service Offerings:**

| Service Type | Unit | Rate | Minimum | SLA |
|-------------|------|------|---------|-----|
| Storage | per pallet/month | | | |
| Receiving | per pallet | | | |
| Picking | per order | | | |
| | | | | |

---

## Customization Quick Reference

### Adding Custom Fields

1. Enable Developer Mode: Settings → Activate Developer Mode
2. Navigate to your object (Products, Orders, etc.)
3. Use Web Studio: Click "Edit" in developer menu
4. Add fields and save

### Creating Reports

1. Navigate to: Settings → Technical → Reporting
2. Or use: Spreadsheet Dashboard feature
3. Define: Data sources and filters
4. Design: Layout and charts

### Email Templates

1. Navigate to: Settings → Technical → Email → Templates
2. Create: New template
3. Use: Dynamic fields with ${object.field}
4. Test: Send test email

### Automation Rules

1. Navigate to: Settings → Technical → Automation → Automated Actions
2. Define: Trigger (on create, update, etc.)
3. Set: Conditions
4. Configure: Actions (send email, create record, etc.)

---

## Common Customization Scenarios

### Scenario 1: Add Custom Discount Field to Products

```
Module: Any with products
Steps:
1. Go to: Products → Products
2. Developer Mode → Edit View → Web Studio
3. Add field: "Custom Discount" (percentage)
4. Save and test
```

### Scenario 2: Send Auto-Email When Order Confirmed

```
Module: Any with sales
Steps:
1. Go to: Settings → Technical → Automation
2. Create: New rule
3. Model: Sales Order
4. Trigger: On Status Change → To "Sale"
5. Action: Send Email → Select template
6. Save and test with order
```

### Scenario 3: Generate Custom Report

```
Module: Any
Steps:
1. Go to: Dashboards → Create Spreadsheet
2. Select: Data source (orders, products, etc.)
3. Add: Pivot tables and charts
4. Save: As dashboard
5. Schedule: Email delivery
```

---

## Troubleshooting Quick Fixes

### Problem: Can't Login
**Fix:** Reset admin password
```bash
python3 odoo/odoo-bin shell -d [database] -c [config]
# Then: env['res.users'].browse(2).write({'password': 'newpassword'})
```

### Problem: Module Won't Install
**Fix:** Check dependencies
```bash
# View module manifest
cat [module_name]/__manifest__.py
# Install missing dependencies first
```

### Problem: Slow Performance
**Fix:** Optimize database
```bash
# Connect to PostgreSQL
psql -d [database]
# Run: VACUUM ANALYZE;
```

### Problem: Email Not Sending
**Fix:** Check mail server configuration
```
Settings → Technical → Outgoing Mail Servers
- Verify SMTP settings
- Test connection
- Check credentials
```

---

## Next Steps

After completing your quick start:

1. **Read Full Documentation**
   - [MOZIN_CONCEITO.md](MOZIN_CONCEITO.md) - Complete module overview
   - [WORKFLOW.md](WORKFLOW.md) - Detailed development workflows

2. **Perform Full Audit**
   - Use audit checklists in WORKFLOW.md
   - Test all workflows thoroughly
   - Validate data integrity

3. **Customize for Your Needs**
   - Add custom fields
   - Create automation rules
   - Design custom reports
   - Configure integrations

4. **Train Your Team**
   - Create user guides
   - Record video tutorials
   - Hold training sessions
   - Set up support process

5. **Go Live**
   - Follow deployment checklist in WORKFLOW.md
   - Migrate production data
   - Monitor performance
   - Collect feedback

---

## Support Resources

### Documentation
- Main Documentation: [MOZIN_CONCEITO.md](MOZIN_CONCEITO.md)
- Workflow Guide: [WORKFLOW.md](WORKFLOW.md)
- Odoo Documentation: https://www.odoo.com/documentation/

### Community
- GitHub Issues: Report bugs and request features
- Odoo Forums: Community support
- Stack Overflow: Technical questions

### Getting Help

1. **Check Documentation First**
   - Search this guide
   - Review module-specific docs
   - Check Odoo official docs

2. **Search Existing Issues**
   - GitHub repository issues
   - Odoo community forums

3. **Create New Issue**
   - Describe problem clearly
   - Include steps to reproduce
   - Attach screenshots
   - Specify module and version

---

## Checklist for Your First Week

### Day 1: Setup
- [ ] Environment installed
- [ ] Module selected and running
- [ ] Demo data explored
- [ ] Initial mappings completed

### Day 2: Configuration
- [ ] Basic settings configured
- [ ] Users and permissions set
- [ ] Email templates reviewed
- [ ] Reports examined

### Day 3: Data
- [ ] Master data imported
- [ ] Data validation rules checked
- [ ] Sample transactions created
- [ ] Data integrity verified

### Day 4: Customization
- [ ] Custom fields added
- [ ] Views adjusted
- [ ] Automation rules created
- [ ] Reports customized

### Day 5: Testing
- [ ] Workflows tested end-to-end
- [ ] Edge cases identified
- [ ] Performance checked
- [ ] Security verified

---

*Keep this guide handy as you build your MozinConceito solution!*
