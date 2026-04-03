# Sample Request Flow

## Primary Use Case

A US buyer requests a coffee sample from an Indian supplier and the platform tracks both shipment logistics and FDA Prior Notice responsibility.

## Workflow

1. Buyer receives a recommendation or browses the catalog.
2. Buyer opens a coffee detail page and confirms the lot is sample-ready.
3. Buyer reviews the recommendation explanation and logistics section.
4. Buyer submits a sample request.
5. Platform creates an inquiry record with `shipment_status = new`.
6. Supplier reviews and approves the request.
7. Inquiry moves to `approved`.
8. Supplier prepares the sample and the inquiry moves to `sample_preparing`.
9. Prior Notice responsibility is confirmed and filing progress is tracked with `prior_notice_pending`.
10. Supplier or logistics partner ships the sample.
11. Tracking number and courier are saved.
12. Inquiry moves to `shipped`.
13. Buyer confirms receipt and the inquiry moves to `delivered`.
14. Opportunity is closed or converted into a commercial deal.

## Operational Notes

- for US-bound shipments, `prior_notice_required` is always true
- the platform does not need to file Prior Notice in MVP, but must clearly record who owns it
- tracking information should be visible to buyer and admin
- recommendation events should be logged so the team can measure recommendation-to-inquiry conversion
