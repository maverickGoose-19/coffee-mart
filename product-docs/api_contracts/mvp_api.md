# MVP API Contract

## Buyers

### `POST /api/buyers`

Creates a buyer profile and sourcing preference record.

```json
{
  "companyName": "North Harbor Roasters",
  "contactName": "Maya Chen",
  "contactEmail": "maya@northharbor.example",
  "buyerType": "roaster",
  "destinationCountry": "US",
  "preferredRegions": ["Coorg, Karnataka", "Bababudangiri, Karnataka"],
  "preferredVarietals": ["Selection 795", "SLN9"],
  "preferredProcesses": ["Washed"],
  "targetTastingNotes": ["citrus", "stone fruit", "chocolate"],
  "minMoqKg": 120,
  "maxMoqKg": 400,
  "maxPricePerKg": 14,
  "preferredCertifications": ["Organic"],
  "requiresSamples": true,
  "preferredCouriers": ["DHL"],
  "needsUsComplianceSupport": true
}
```

### `GET /api/buyers/:id/preferences`

Returns buyer sourcing preferences used by the recommendation engine.

## Suppliers

### `POST /api/suppliers`

Creates a supplier profile.

Required payload fields:

```json
{
  "companyName": "Blue Hills Estate",
  "contactEmail": "founder@example.com",
  "region": "Chikmagalur, Karnataka",
  "website": "https://example.com",
  "altitudeMeters": 1450,
  "varietals": ["SLN9", "Selection 795"],
  "certifications": ["Organic"],
  "description": "Washed and naturally processed arabica lots.",
  "exportsInternationally": true,
  "exportPartnerName": "Example Exports Pvt Ltd",
  "exportTerms": "FOB",
  "minExportOrderKg": 300,
  "documentationAvailable": {
    "certificateOfOrigin": true,
    "phytosanitaryCertificate": true,
    "invoiceCapability": true
  },
  "canShipSamples": true,
  "sampleSizeGrams": 200,
  "sampleCouriers": ["DHL", "FedEx"],
  "sampleShippingPaidBy": "buyer",
  "samplePrepDays": 2,
  "sampleShippingDays": 5,
  "samplePrice": 25,
  "priorNoticeHandler": "supplier"
}
```

### `GET /api/suppliers`

Supports filters:

- `region`
- `certification`
- `exportsInternationally`
- `canShipSamples`
- `exportReady`
- `sampleReady`

## Lots

### `POST /api/lots`

Creates a coffee lot listing tied to a supplier.

Derived fields returned in response:

- `exportReady`
- `sampleReady`
- `complianceReady`
- `recommendationEligible`

### `GET /api/lots/:id`

Returns cup profile, traceability details, logistics section, and similar-lot recommendations for buyers.

### `GET /api/lots/recommended`

Returns ranked lots for a buyer.

Supported params:

- `buyerId`
- `destinationCountry`
- `requiresSamples`
- `limit`

Response shape:

```json
{
  "buyerId": "buyer_001",
  "modelVersion": "rules-v1",
  "recommendations": [
    {
      "lotId": "lot_001",
      "score": 0.91,
      "reason": "Matches your washed Karnataka profile, 120-400kg MOQ band, DHL sample preference, and compliance-ready suppliers."
    }
  ]
}
```

### `GET /api/lots/:id/similar`

Returns substitute lots based on source, process, varietal, and commercial fit.

## Inquiries

### `POST /api/inquiries`

Creates a new sample request.

```json
{
  "buyerId": "buyer_001",
  "supplierId": "supplier_001",
  "lotId": "lot_001",
  "requestedSampleGrams": 200,
  "destinationCountry": "US"
}
```

Server defaults:

- `shipmentStatus = "new"`
- `priorNoticeRequired = true` when destination is `US`

### `PATCH /api/inquiries/:id/shipment`

Updates shipment and compliance state.

```json
{
  "shipmentStatus": "shipped",
  "courier": "DHL",
  "trackingNumber": "1234567890",
  "priorNoticeFiled": true,
  "priorNoticeFiledBy": "supplier"
}
```

## Recommendation Telemetry

### `POST /api/interactions`

Captures recommendation and discovery signals.

```json
{
  "buyerId": "buyer_001",
  "lotId": "lot_001",
  "interactionType": "view",
  "sourceSurface": "recommended_catalog"
}
```

## Admin

### `GET /api/admin/supplier-readiness`

Returns readiness table with:

- supplier name
- export ready flag
- sample ready flag
- compliance ready flag
- approval status

### `GET /api/admin/inquiries`

Returns inquiry pipeline with shipment status, courier, and Prior Notice ownership.

### `GET /api/admin/recommendations`

Returns recommendation telemetry and ranking outcomes, including:

- top recommended lots
- recommendation to inquiry conversion
- suppressed lots due to missing readiness
- buyer preference coverage gaps
