# Supplier Onboarding Flow

## Objective

Collect enough commercial, logistics, and compliance data to approve only suppliers who can support real international sourcing workflows.

## Flow

1. Supplier creates profile and enters basic company information.
2. Supplier adds estate details and coffee background.
3. Supplier completes export readiness section.
4. Supplier completes sample shipping section.
5. Supplier assigns FDA Prior Notice responsibility for US sample shipments.
6. Platform validates required fields.
7. Admin reviews and either approves or requests changes.

## Validation Rules

- approval is blocked if export readiness is incomplete
- approval is blocked if sample shipping capability is incomplete
- approval is blocked if `prior_notice_handler` is missing
- if `can_ship_samples` is false, supplier cannot receive sample requests

## Admin Review Notes

Check that:

- export terms are realistic for the supplier profile
- documentation flags match stated export readiness
- sample lead times and couriers are credible
- compliance responsibility is clearly assigned
