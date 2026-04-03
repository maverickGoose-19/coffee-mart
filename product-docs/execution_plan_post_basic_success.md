# Post-MVP Execution Plan

This plan synthesizes the newly added research documents in `research/` and turns them into an execution roadmap for what happens after basic MVP success is reached.

## Source Synthesis

The six `.docx` research documents point to the same strategic pattern:

- stay B2B-first in the early company
- use a charge-on-order marketplace model
- keep the buyer as importer/consignee whenever possible
- avoid making India-to-consumer dropship the core business
- treat the lot ledger, document vault, and compliance pack as the moat
- begin EUDR-ready and traceability-ready data capture early
- add heavier operating models only after repeatable demand and low operational error rates

## Definition Of Basic Success

This roadmap starts only after the MVP has reached the following baseline:

- 10 to 20 verified suppliers onboarded
- 30 to 60 active lots listed
- 20 or more qualified buyer inquiries
- 5 to 10 sample requests completed
- 1 to 3 paid transactions or signed pilot orders
- at least 80 percent of active lots have minimum documentation completeness
- supplier export-readiness and sample-readiness are operationally visible in product

## Strategic Rule Set

These rules should hold through all phases unless there is a deliberate strategic change:

- the platform is a marketplace and workflow layer first, not an importer by default
- US buyers or their agents should remain responsible for importer-side obligations
- compliance ownership must be explicit on every cross-border shipment
- product expansion should follow operational proof, not ambition alone
- AI features should begin as explainable workflow support, not black-box automation

## AI Recommendation Layer

The research supports adding AI, but the first useful version should not be a generic chatbot. It should be an explainable recommendation layer tied to the lot ledger.

### What The Engine Should Recommend

- best-fit lots for a buyer based on sourcing preferences and commercial constraints
- similar lots when a preferred lot is unavailable
- suppliers likely to match a buyer's reliability, MOQ, and logistics needs
- lots with stronger export, sample, and compliance readiness

### Should Source Region Matter

Yes, but only as one feature. Region and source should influence recommendations because they correlate with:

- altitude and climate
- common varietals
- processing patterns
- expected cup profile
- logistics lead times
- buyer story and provenance preference

Source alone is not enough. The recommendation layer should combine source with:

- region
- altitude
- varietal
- process
- cup score and tasting notes
- moisture and QC fields
- certifications
- MOQ
- price band
- export readiness
- sample readiness
- compliance readiness
- historical buyer behavior

### Recommended Build Path

Stage 1: Rules and scoring

- use hard filters first: destination, MOQ, availability, export readiness, sample readiness
- rank remaining lots using weighted scoring
- show explanation such as: recommended because it matches Coorg origin, washed process, 200kg MOQ, and DHL sample shipping

Stage 2: Hybrid recommender

- combine content-based similarity with marketplace interaction data
- use saved lots, inquiries, sample requests, and conversions as signals
- support similar-lot recommendations and buyer-specific ranking

Stage 3: Learning-to-rank

- train on successful inquiry, sample, shipment, and deal outcomes
- optimize for conversion, not clicks alone
- include business constraints so high-risk or non-compliant lots do not get over-ranked

### AI Features To Add By Phase

- Phase 1: rules-based buyer-to-lot scoring with plain-English explanations
- Phase 2: document completeness scoring and supplier readiness scoring
- Phase 3: hybrid lot ranking using buyer behavior and deal outcomes
- Phase 4: quality and fulfillment risk flags
- Phase 5: EUDR-readiness scoring and EU buyer-specific recommendations

## Phase 1: Repeatable B2B Marketplace Engine

### Objective

Turn early proof into a repeatable sourcing engine for US buyers and Indian suppliers.

### Time Horizon

Months 0 to 3 after basic success.

### Primary Outcome

The company consistently converts supplier listings into shipped samples and paid B2B orders with low operational confusion.

### Product Work

- improve supplier onboarding with stricter approval workflows
- add readiness scoring for suppliers and lots
- make the buyer catalog feel trustworthy and easy to filter
- improve inquiry management and shipment milestone tracking
- generate compliance pack v1 from structured supplier and shipment data
- add buyer-facing status visibility for sample and order progress

### Operations Work

- standardize supplier activation checklist
- create first-shipment success playbook for every new supplier
- create document collection SOP for export docs and sample shipments
- define escalation paths when Prior Notice ownership is unclear
- build a lightweight QA checklist for sample and shipment quality issues

### GTM Work

- focus on a narrow buyer segment such as specialty roasters and import-savvy cafes
- target suppliers that already export or can operate through an export partner
- publish a clear message: verified Indian coffee sourcing with export and compliance visibility

### KPIs

- sample request to shipment conversion rate
- shipment to commercial deal conversion rate
- time from buyer inquiry to shipped sample
- percentage of lots with complete compliance pack data
- repeat inquiry rate from buyers

### Exit Criteria

- at least 5 repeat buyers or repeat buyer programs
- at least 5 suppliers who complete one successful shipment each
- dispute rate stays low and manageable
- compliance pack v1 is used in real buyer conversations

## Phase 2: Compliance And Traceability Moat

### Objective

Deepen the product from a useful marketplace into a defensible sourcing and compliance infrastructure layer.

### Time Horizon

Months 3 to 6 after basic success.

### Primary Outcome

The platform becomes meaningfully better than a spreadsheet broker because it stores traceability, documents, and lot-level readiness in a structured way.

### Product Work

- expand the lot ledger beyond basic listing fields
- add document vault and document type validation
- model traceability edges across supplier to lot, lot to shipment, and shipment to buyer
- introduce readiness tiers: Listed, Verified Docs, Export Ready, Traceability Ready
- begin geolocation and farm-map placeholder fields for future EU readiness
- add buyer download for compliance pack v2

### Operations Work

- build audit trail for document uploads and approval steps
- define recall and incident response draft workflow
- create data completeness scorecard for each supplier
- create policy for suspending listings with missing critical documents

### GTM Work

- use compliance readiness as a sales differentiator
- segment suppliers into standard and premium verified tiers
- begin outreach to EU-interested buyers, but do not expand commercial motion too broadly yet

### KPIs

- percentage of suppliers with verified documentation
- percentage of lots with traceability completeness
- buyer usage rate of compliance pack downloads
- reduction in manual follow-up per deal
- supplier activation time

### Exit Criteria

- most active suppliers meet verified-doc readiness
- traceability links exist for the majority of active transactions
- buyers explicitly cite documentation and readiness as a reason to proceed

## Phase 3: Commercial Expansion And Workflow Automation

### Objective

Increase throughput without adding proportional operational chaos.

### Time Horizon

Months 6 to 9 after basic success.

### Primary Outcome

The business supports more suppliers, more buyers, and more orders with stronger process automation and clearer economics.

### Product Work

- add buyer accounts with saved searches and favorites
- add supplier performance scorecards
- add explainable lot ranking based on buyer constraints
- add pricing, MOQ, lead-time, and readiness filters at deeper granularity
- add reserve and payout workflow support if commercially needed
- create lightweight analytics for admin covering export-ready percentage, sample-ready percentage, inquiry funnel, and deal funnel

### Operations Work

- define reserve and payout policy
- create standard dispute handling workflow
- formalize logistics partner and broker handoff process
- build reporting cadence for supplier and buyer performance

### GTM Work

- widen from pilot buyers into a repeatable outbound motion
- add content and case studies around successful sample-to-deal journeys
- identify the strongest verticals for repeatable sales: roasters, cafes, importers, and distributors

### KPIs

- monthly GMV
- take-rate realization
- buyer retention
- repeat supplier utilization
- cost to serve per transaction
- dispute rate

### Exit Criteria

- clear proof that the business can grow without founder-only operations
- stable unit economics assumptions
- visible repeatability in supply and demand

## Phase 4: Controlled In-Market Fulfillment Pilot

### Objective

Test whether closer-to-buyer inventory or fulfillment improves trust, conversion, and quality control enough to justify operational complexity.

### Time Horizon

Months 9 to 12 after basic success.

### Primary Outcome

The company learns whether a small US in-market pilot or consignment model creates a step-change in reliability and margin.

### Product Work

- add support for consignment or in-market inventory status
- extend the shipment model for domestic fulfillment steps
- add intake QC and post-delivery issue tracking
- create inventory visibility for pilot SKUs or lots

### Operations Work

- choose a narrow pilot scope with one geography and a few suppliers
- define warehousing, 3PL, or partner fulfillment SOPs
- define title-transfer, consignee, and responsibility rules in contracts
- create QC checks at receiving and release

### GTM Work

- pitch faster fulfillment and higher confidence to selected buyers
- use this phase for learning, not broad rollout

### KPIs

- on-time delivery improvement
- quality complaint reduction
- conversion lift versus pure marketplace flow
- working-capital impact
- fulfillment error rate

### Exit Criteria

- evidence that in-market fulfillment creates real commercial value
- no major compliance confusion caused by the new model
- clear decision to scale, pause, or kill the pilot

## Phase 5: EU Readiness And Expansion

### Objective

Prepare the platform for stronger EU-facing trade and future compliance demand without overcommitting too early.

### Time Horizon

Months 12 to 18 after basic success.

### Primary Outcome

The company can credibly position itself as an EU-ready sourcing platform with strong traceability and geolocation capture foundations.

### Product Work

- mature geolocation capture for suppliers and plots
- build EUDR-readiness scoring and missing-data prompts
- expand compliance pack fields for EU buyer workflows
- add supplier chain and source metadata needed for due diligence

### Operations Work

- define EU buyer onboarding checklist
- document EORI, importer, and labeling responsibility assumptions for each commercial model
- create a policy library for EU trade support and exceptions

### GTM Work

- target EU buyers that value traceability and future-ready sourcing
- position the platform as a risk-reduction tool, not just a sourcing directory

### KPIs

- percentage of active suppliers with geolocation-ready data
- EU buyer pipeline growth
- percentage of lots with EU-oriented readiness scores
- share of deals where traceability readiness materially influences conversion

### Exit Criteria

- enough supplier-side data exists to support EU expansion without heroic manual work
- EU buyers see the platform as meaningfully differentiated on traceability and compliance

## Phase Gate Decision Framework

Before entering any next phase, ask:

1. Is the current model repeatable, or is the founder still manually stitching everything together?
2. Does the next phase improve margin, conversion, or defensibility enough to justify added complexity?
3. Will the next phase accidentally shift importer, consignee, or labeling responsibility onto the platform?
4. Do we have the data discipline to support the next layer, especially traceability and compliance?

If the answer to any of those is no, stay in the current phase longer.

## What Not To Do Too Early

- do not make B2C dropship from India the core operating model
- do not take title or importer responsibility casually
- do not expand into the EU before data capture discipline exists
- do not add AI features that cannot be explained operationally
- do not scale supplier acquisition faster than documentation and fulfillment quality allow

## Immediate Next Actions

To prepare for Phase 1 after MVP success, do these now:

1. Define the exact KPI dashboard that determines when MVP success has been reached.
2. Add readiness scoring logic into the product and admin model.
3. Create the first compliance pack template and shipment SOP.
4. Identify the first 10 target buyers for repeatable B2B motion.
5. Identify the first 5 suppliers that can become first-shipment case studies.
