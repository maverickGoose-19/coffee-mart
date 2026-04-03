# Wireframes

This product is a website, specifically a B2B web platform with three main user surfaces:

- supplier-facing onboarding
- buyer-facing discovery and inquiry flow
- admin-facing operations dashboard

Use the wireframes below as a Figma-ready brief for low-fidelity screens.

## Global Product Structure

Primary navigation:

- Logo
- Catalog
- Suppliers
- Inquiries
- Admin
- Sign In

Design direction:

- clean B2B marketplace layout
- trust-first UX, not flashy consumer ecommerce
- logistics and compliance information should be visibly embedded in the experience
- use cards, tables, badges, and timeline components

## Screen 1: Homepage / Landing Page

Purpose:

- explain the value proposition
- help buyers start browsing coffee
- help suppliers start onboarding

Layout:

1. Top navigation bar
2. Hero section
3. How it works section
4. Trust and logistics section
5. Featured suppliers or featured lots
6. Footer

Hero section content:

- headline: source Indian specialty coffee with export and sample visibility
- subheadline: discover verified suppliers, request samples, and track logistics and compliance for US imports
- primary CTA: Browse Coffee
- secondary CTA: Join as Supplier

How it works cards:

- Discover suppliers
- Request samples
- Track shipment and compliance

Trust section:

- Export-ready suppliers
- Sample shipping visibility
- Prior Notice responsibility tracking

## Screen 2: Supplier Onboarding

Purpose:

- collect supplier profile data
- capture export readiness
- capture sample logistics
- assign compliance responsibility

Layout:

1. Left side progress sidebar
2. Main form area
3. Sticky footer with Save Draft and Submit buttons

Progress steps:

- Basic Info
- Estate Info
- Export Readiness
- Sample Shipping
- Compliance Responsibility
- Review

Section A: Basic Info

Fields:

- company name
- contact name
- contact email
- contact phone
- region
- website

Section B: Estate Info

Fields:

- altitude
- varietals
- certifications
- estate description

Section C: Export Readiness

Fields:

- exports internationally toggle
- export partner name
- export terms dropdown: FOB, EXW
- minimum export order in kg
- documentation available checkboxes:
- certificate of origin
- phytosanitary certificate
- invoice capability

UI notes:

- show a status badge: Export Ready or Missing Info
- if incomplete, show inline warnings

Section D: Sample Shipping Capability

Fields:

- can ship samples toggle
- sample size in grams
- courier options multi-select: DHL, FedEx, UPS
- sample shipping paid by dropdown
- sample prep days
- sample shipping days
- sample price

UI notes:

- show a status badge: Sample Ready or Missing Info

Section E: Compliance Responsibility

Question:

- who handles FDA Prior Notice for US sample shipments?

Options:

- Supplier
- Buyer
- Freight Forwarder / Broker

UI notes:

- this should be visually emphasized with a warning/info callout
- note: required for US-bound food sample shipments

Review screen:

- summary cards for all sections
- red warning if approval-blocking fields are missing
- CTA: Submit for Approval

## Screen 3: Buyer Catalog

Purpose:

- help roasters and cafes browse discoverable coffee lots

Layout:

1. Top nav
2. Search and filter rail
3. Grid or list of lot cards

Filter rail:

- search by supplier or lot name
- region
- varietal
- certification
- export ready
- ships samples
- verified supplier

Lot card content:

- coffee lot name
- supplier name
- region
- process
- cup score
- tasting notes
- badges:
- Export Ready
- Sample Ready
- Verified Supplier
- CTA: View Details

## Screen 4: Coffee Detail Page

Purpose:

- give buyers confidence before requesting a sample

Layout:

1. Header with coffee title and supplier
2. Two-column body
3. Sticky inquiry/request sample card on the right

Left column sections:

- Overview
- Estate Story
- Coffee Specs
- Certifications
- Logistics

Overview block:

- lot name
- supplier name
- region
- process
- harvest year
- quantity available
- price indication

Coffee specs:

- altitude
- varietals
- cup score
- tasting notes

Logistics section:

- Export Ready: Yes/No
- Ships Samples: Yes/No
- Sample Size: 200g
- Courier: DHL / FedEx / UPS
- Sample Prep Time: 2 days
- Sample Shipping Time: 5 days
- Compliance: Supplier handles Prior Notice

Right-side inquiry card:

- request sample button
- selected sample size
- sample price
- shipping paid by
- short note: Prior Notice required for US shipments

## Screen 5: Sample Request Modal or Page

Purpose:

- capture a buyer inquiry with enough information to start logistics

Fields:

- buyer name
- company
- email
- destination country
- requested sample size
- message to supplier

System-generated hints:

- if destination country is US, show: Prior Notice required
- show who is responsible based on supplier profile

CTA:

- Submit Sample Request

## Screen 6: Buyer Inquiry Tracking

Purpose:

- show the lifecycle of a requested sample

Layout:

1. Inquiry header
2. Timeline component
3. Shipment and compliance detail cards

Timeline states:

- New
- Approved
- Sample Preparing
- Prior Notice Pending
- Shipped
- Delivered
- Closed

Shipment detail card:

- courier name
- tracking number
- ship date
- estimated arrival

Compliance detail card:

- Prior Notice required: Yes
- Prior Notice filed: Yes/No
- filed by: Supplier / Buyer / Broker

## Screen 7: Admin Dashboard

Purpose:

- manage supplier readiness and inquiry operations

Layout:

1. Top admin nav
2. Metrics row
3. Supplier readiness table
4. Inquiry pipeline section

Metrics row:

- % suppliers export-ready
- % suppliers sample-ready
- sample request to shipment conversion rate
- shipment to deal conversion rate

Supplier readiness table columns:

- Supplier
- Region
- Export Ready
- Sample Ready
- Compliance Ready
- Approval Status
- Action

Row actions:

- View
- Approve
- Request Changes

Inquiry pipeline board or table:

- New
- Approved
- Sample Preparing
- Prior Notice Pending
- Shipped
- Delivered
- Closed

Inquiry row fields:

- buyer
- supplier
- lot
- shipment status
- courier
- tracking number
- prior notice filed
- prior notice filed by

## Figma Build Notes

Recommended first frame list:

- Landing Page Desktop
- Supplier Onboarding Desktop
- Buyer Catalog Desktop
- Coffee Detail Desktop
- Sample Request Modal
- Buyer Inquiry Tracking Desktop
- Admin Dashboard Desktop

Recommended components:

- top nav
- sidebar progress stepper
- form field
- checkbox group
- badge
- card
- table
- status pill
- timeline step
- CTA button

Recommended annotations to include in Figma:

- approval-blocking fields in supplier onboarding
- derived fields for lot readiness
- Prior Notice warning for US shipments
- admin-only operational data visibility
