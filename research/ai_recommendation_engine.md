# AI Recommendation Engine

## Short Answer

Yes, this platform can support a recommendation engine.

The strongest version is not "recommend coffee just by where it was sourced." It is:

- source-aware
- buyer-aware
- compliance-aware
- logistics-aware

That makes it useful for a B2B sourcing platform instead of feeling like a consumer coffee quiz.

## What To Recommend

There are four recommendation problems in this product:

### 1. Buyer To Lot Recommendation

Recommend coffee lots to buyers based on:

- source region
- varietal
- process
- cup profile
- MOQ
- price range
- export readiness
- sample readiness
- courier and lead time
- compliance readiness

### 2. Similar Lot Recommendation

If a lot is sold out or unavailable, recommend substitutes with similar:

- region profile
- varietal family
- process
- tasting notes
- cup score
- commercial profile

### 3. Supplier Recommendation

Recommend suppliers to buyers based on:

- reliability
- documentation completeness
- shipping capability
- successful shipment history
- sample-to-deal conversion

### 4. Admin Recommendation

Recommend actions internally, such as:

- which suppliers need onboarding help
- which inquiries are most likely to convert
- which lots are missing critical compliance data

## Should Recommendations Use Source Region

Yes, source is valuable, but it should be one input among many.

Useful source-derived features include:

- region
- altitude band
- rainfall and growing conditions
- dominant species and varietals
- typical processing methods
- typical flavor tendencies
- distance to export routes and expected logistics complexity

For example:

- Coorg lots may skew toward certain varietals and logistics patterns
- Bababudangiri lots may carry different altitude and cup expectations
- Araku may matter for both story and buyer differentiation

## Best Engine Architecture

## Stage 1: Rules-Based Recommendation

Use this first because it works with low data volume.

Flow:

1. Filter out any non-eligible lots.
2. Score the remaining lots.
3. Sort by score.
4. Return the recommendation with reasons.

Hard filters:

- destination market supported
- export ready
- sample ready if buyer wants sample
- MOQ within buyer range
- required certifications present

Ranking features:

- source region match
- process match
- varietal match
- cup score
- tasting note overlap
- price fit
- lead-time fit
- supplier reliability
- compliance completeness

Output example:

- Recommended because it matches your preference for high-altitude Karnataka Arabica, washed processing, sample-ready shipping, and supplier-handled Prior Notice.

## Stage 2: Hybrid Recommendation

Once there is interaction data, combine content matching with behavior.

Signals:

- lot views
- saves
- inquiries
- sample requests
- quote requests
- shipments
- closed deals

Techniques:

- content-based similarity
- nearest-neighbor lot similarity
- buyer profile vectors
- supplier reliability weighting

This stage is likely the sweet spot for the first real production system.

## Stage 3: Learning-To-Rank

After enough transactions exist, train a ranking model to predict:

- probability of inquiry
- probability of shipped sample
- probability of deal conversion

Candidate models:

- gradient boosted trees
- pairwise ranking models
- learning-to-rank pipelines

This stage should remain explainable and policy-constrained so the engine does not over-rank risky or incomplete lots.

## Datasets Available Today

There are usable bootstrap datasets, but no obvious ready-made public dataset for "Indian specialty coffee buyer preference to deal outcome."

That means the long-term moat will come from proprietary platform data.

### A. Best External Datasets For Bootstrap

#### 1. Coffee Board Of India

Useful for:

- coffee regions
- region-level agronomic context
- exporter and market context
- production and export statistics
- periodic coffee databases

Useful fields to ingest:

- region
- altitude
- rainfall
- major varietals
- species mix
- production by district
- exporter directory references

#### 2. Coffee Quality Institute Derived Review Data

Useful for:

- cupping attributes
- region and country metadata
- varietal and process relationships
- early taste-profile modeling

Useful fields:

- country
- region
- altitude
- variety
- processing method
- aroma
- flavor
- aftertaste
- acidity
- body
- balance
- total cup points

#### 3. ICO Trade Statistics

Useful for:

- macro trade trends
- market pricing context
- export and import trend features
- demand-side market prioritization

Useful fields:

- production
- exports
- imports
- prices
- consumption

#### 4. FAOSTAT

Useful for:

- long-horizon production and trade context
- market sizing
- demand and supply trend baselines

#### 5. UN Comtrade

Useful for:

- HS-based coffee trade flows
- destination market analysis
- route and product-type demand patterns

#### 6. Visual QC Datasets

Useful for:

- bean defect classification
- future QA tooling

This is helpful later for quality workflows, but not required for the first recommender.

## Datasets You Should Create Internally

These will matter more than public data:

- buyer profile data
- inquiry outcomes
- sample request outcomes
- shipment outcomes
- deal conversion outcomes
- supplier response times
- supplier document completeness
- sample and logistics lead times
- dispute history
- buyer feedback on lots

## Recommended Data Model Additions

Add or standardize fields for:

- buyer preferred regions
- buyer preferred varietals
- buyer preferred process
- target cup profile tags
- acceptable MOQ range
- acceptable lead time
- preferred certifications
- sample requested
- sample converted
- shipment delivered
- deal closed
- buyer feedback score

## MVP Recommendation Engine Spec

Start with a scoring model like:

`recommendation_score =
source_fit +
cup_profile_fit +
commercial_fit +
logistics_fit +
compliance_fit +
supplier_reliability_fit`

Example weight ranges:

- source and cup profile: 35 percent
- commercial fit: 20 percent
- logistics fit: 20 percent
- compliance fit: 15 percent
- supplier reliability: 10 percent

## What I Would Build First

1. A rules-based lot recommender in the buyer catalog.
2. A "similar lots" block on each lot detail page.
3. An admin supplier-readiness score.
4. An inquiry conversion score for internal prioritization.

## Product Risk To Avoid

- do not market it as magical AI
- do not recommend non-compliant or incomplete lots
- do not use source alone as a proxy for quality
- do not train a complex model before you have enough platform outcomes
- do not optimize for clicks when the business cares about shipped samples and deals

## Practical Conclusion

Yes, you can create a recommendation engine.

The right first version is a source-aware, rules-based B2B recommender that uses origin as one feature inside a broader trade-fit model. Public datasets are enough to bootstrap feature design, but the real advantage will come from your own inquiry, shipment, and conversion data once the platform is live.
