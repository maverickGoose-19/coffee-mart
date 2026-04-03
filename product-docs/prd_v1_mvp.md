# PRD v1: MVP

## Product Summary

Build a B2B marketplace that helps US roasters and cafes source Indian specialty coffee from verified suppliers. The first release must make sourcing trustable by exposing export readiness, sample shipping capability, FDA Prior Notice ownership, and explainable lot recommendations that respect logistics and compliance constraints.

## Users

- Suppliers: estates, exporters, producer groups, and processors in India
- Buyers: roasters, cafes, importers, and green coffee programs
- Admins: internal operators managing onboarding, inquiries, and compliance visibility

## Core Problem

Coffee discovery alone is not enough for cross-border trade. Buyers need to know whether a supplier can export, whether a sample can actually be shipped, and who will file FDA Prior Notice for US-bound food shipments.

## MVP Scope

### 1. Supplier Onboarding

Suppliers submit:

- basic company and contact information
- estate details including altitude, varietals, certifications, and story
- export readiness details
- sample shipping capability
- compliance responsibility for FDA Prior Notice

Required export fields:

- `exports_internationally`
- `export_partner_name`
- `export_terms`
- `min_export_order_kg`
- `documentation_available.certificate_of_origin`
- `documentation_available.phytosanitary_certificate`
- `documentation_available.invoice_capability`

Required sample fields:

- `can_ship_samples`
- `sample_size_grams`
- `courier_options`
- `sample_shipping_paid_by`
- `sample_prep_days`
- `sample_shipping_days`
- `sample_price`

Required compliance field:

- `prior_notice_handler` with one of `supplier`, `buyer`, `broker`

Approval rule:

- a supplier cannot be approved without complete export, sample, and compliance data

### 2. Coffee Lot Listings

Each listing includes green coffee attributes plus operational readiness signals:

- `export_ready` derived from export section completeness
- `sample_ready` derived from sample shipping completeness
- `compliance_ready` derived from presence of `prior_notice_handler`

### 3. Buyer Experience

Buyers can:

- browse a searchable catalog
- filter by region, varietal, certifications, export readiness, and sample readiness
- receive explainable lot recommendations based on sourcing preferences and commercial fit
- view logistics details before requesting a sample

Buyer preference profile should support:

- preferred regions
- preferred varietals
- preferred processes
- target tasting notes
- MOQ range
- target price range
- preferred certifications
- sample requirement
- destination market

Detail page logistics block:

- Export Ready
- Ships Samples
- Sample Size
- Courier
- Sample Prep Time
- Sample Shipping Time
- Compliance Responsibility

Recommendation blocks:

- Recommended for you in catalog
- Similar lots on lot detail page
- Why this matches your profile explanation

### 4. Inquiry and Sample Workflow

Workflow:

1. Buyer requests a sample.
2. Platform logs inquiry and notifies supplier.
3. Supplier approves and prepares sample.
4. Prior Notice responsibility is confirmed and tracked.
5. Shipment is created and tracking is added.
6. Buyer receives sample.
7. Opportunity progresses to closed or converted deal.

Statuses:

- `new`
- `approved`
- `sample_preparing`
- `prior_notice_pending`
- `shipped`
- `delivered`
- `closed`

### 5. Admin Dashboard

Admin views:

- supplier readiness table
- inquiry pipeline with shipment and compliance states
- export-ready percentage
- sample-ready percentage
- recommendation performance and buyer intent signals

Supplier readiness columns:

- Supplier
- Export Ready
- Sample Ready
- Compliance
- Status

Recommendation insights:

- most viewed lots
- most saved lots
- inquiry likelihood score
- lots suppressed because of readiness or compliance gaps

### 6. Compliance Tracking

The system must support:

- `prior_notice_required` set to `true` for US-bound sample shipments
- `prior_notice_filed`
- `prior_notice_filed_by`
- `shipment_tracking_number`
- `courier_name`

### 7. Recommendation Engine

The MVP recommendation layer should be rules-based and explainable.

Hard filters:

- destination compatibility
- export readiness
- sample readiness when samples are required
- MOQ fit
- required certifications

Ranking inputs:

- source region fit
- varietal fit
- process fit
- cup profile fit
- price fit
- logistics fit
- compliance fit
- supplier reliability fit

The system should never over-rank a lot with incomplete export, sample, or compliance readiness over a lower-risk lot that otherwise fits the buyer profile.

## Non-Goals For MVP

- payment processing
- live freight rate marketplace
- customs brokerage automation
- ERP integration
- automated Prior Notice filing with FDA

## Success Metrics

- percentage of suppliers marked export-ready
- percentage of suppliers marked sample-ready
- sample request to shipment conversion
- shipment to deal conversion
- recommendation click-through to inquiry rate
- recommendation-driven sample request conversion

## Release Principle

This MVP should create trust in international sourcing before optimizing transaction volume.
