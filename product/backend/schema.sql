CREATE TABLE buyers (
  id TEXT PRIMARY KEY,
  company_name TEXT NOT NULL,
  contact_name TEXT,
  contact_email TEXT NOT NULL,
  buyer_type TEXT NOT NULL,
  destination_country TEXT NOT NULL,
  preferred_regions TEXT[] DEFAULT ARRAY[]::TEXT[],
  preferred_varietals TEXT[] DEFAULT ARRAY[]::TEXT[],
  preferred_processes TEXT[] DEFAULT ARRAY[]::TEXT[],
  target_tasting_notes TEXT[] DEFAULT ARRAY[]::TEXT[],
  preferred_certifications TEXT[] DEFAULT ARRAY[]::TEXT[],
  min_moq_kg NUMERIC,
  max_moq_kg NUMERIC,
  max_price_per_kg NUMERIC,
  requires_samples BOOLEAN NOT NULL DEFAULT TRUE,
  preferred_couriers TEXT[] DEFAULT ARRAY[]::TEXT[],
  needs_us_compliance_support BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT buyers_type_check CHECK (
    buyer_type IN ('roaster', 'cafe', 'importer', 'distributor')
  )
);

CREATE TABLE suppliers (
  id TEXT PRIMARY KEY,
  company_name TEXT NOT NULL,
  contact_name TEXT,
  contact_email TEXT NOT NULL,
  contact_phone TEXT,
  region TEXT NOT NULL,
  website TEXT,
  altitude_meters NUMERIC,
  varietals TEXT[] DEFAULT ARRAY[]::TEXT[],
  certifications TEXT[] DEFAULT ARRAY[]::TEXT[],
  description TEXT,
  exports_internationally BOOLEAN NOT NULL DEFAULT FALSE,
  export_partner_name TEXT,
  export_terms TEXT,
  min_export_order_kg NUMERIC,
  certificate_of_origin BOOLEAN NOT NULL DEFAULT FALSE,
  phytosanitary_certificate BOOLEAN NOT NULL DEFAULT FALSE,
  invoice_capability BOOLEAN NOT NULL DEFAULT FALSE,
  can_ship_samples BOOLEAN NOT NULL DEFAULT FALSE,
  sample_size_grams NUMERIC,
  sample_couriers TEXT[] DEFAULT ARRAY[]::TEXT[],
  sample_shipping_paid_by TEXT,
  sample_shipping_days INTEGER,
  sample_prep_days INTEGER,
  sample_price NUMERIC,
  prior_notice_handler TEXT,
  approval_status TEXT NOT NULL DEFAULT 'pending',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT suppliers_export_terms_check CHECK (
    export_terms IS NULL OR export_terms IN ('FOB', 'EXW')
  ),
  CONSTRAINT suppliers_prior_notice_handler_check CHECK (
    prior_notice_handler IS NULL OR prior_notice_handler IN ('supplier', 'buyer', 'broker')
  )
);

CREATE TABLE coffee_lots (
  id TEXT PRIMARY KEY,
  supplier_id TEXT NOT NULL REFERENCES suppliers(id),
  lot_name TEXT NOT NULL,
  region TEXT,
  altitude_meters NUMERIC,
  varietals TEXT[] DEFAULT ARRAY[]::TEXT[],
  process TEXT,
  harvest_year INTEGER,
  quantity_kg NUMERIC,
  price_per_kg NUMERIC,
  cup_score NUMERIC,
  tasting_notes TEXT[] DEFAULT ARRAY[]::TEXT[],
  export_ready BOOLEAN NOT NULL DEFAULT FALSE,
  sample_ready BOOLEAN NOT NULL DEFAULT FALSE,
  compliance_ready BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE buyer_inquiries (
  id TEXT PRIMARY KEY,
  buyer_id TEXT NOT NULL REFERENCES buyers(id),
  supplier_id TEXT NOT NULL REFERENCES suppliers(id),
  lot_id TEXT NOT NULL REFERENCES coffee_lots(id),
  destination_country TEXT NOT NULL,
  requested_sample_grams NUMERIC,
  shipment_status TEXT NOT NULL DEFAULT 'new',
  tracking_number TEXT,
  courier TEXT,
  prior_notice_required BOOLEAN NOT NULL DEFAULT FALSE,
  prior_notice_filed BOOLEAN NOT NULL DEFAULT FALSE,
  prior_notice_filed_by TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT buyer_inquiries_status_check CHECK (
    shipment_status IN (
      'new',
      'approved',
      'sample_preparing',
      'prior_notice_pending',
      'shipped',
      'delivered',
      'closed'
    )
  ),
  CONSTRAINT buyer_inquiries_prior_notice_filed_by_check CHECK (
    prior_notice_filed_by IS NULL OR prior_notice_filed_by IN ('supplier', 'buyer', 'broker')
  )
);

CREATE TABLE buyer_lot_interactions (
  id TEXT PRIMARY KEY,
  buyer_id TEXT NOT NULL REFERENCES buyers(id),
  lot_id TEXT NOT NULL REFERENCES coffee_lots(id),
  interaction_type TEXT NOT NULL,
  source_surface TEXT NOT NULL,
  occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT buyer_lot_interactions_type_check CHECK (
    interaction_type IN (
      'view',
      'save',
      'recommendation_click',
      'inquiry',
      'sample_request',
      'shipment_delivered',
      'deal_closed'
    )
  )
);

CREATE TABLE lot_recommendation_snapshots (
  id TEXT PRIMARY KEY,
  buyer_id TEXT NOT NULL REFERENCES buyers(id),
  lot_id TEXT NOT NULL REFERENCES coffee_lots(id),
  model_version TEXT NOT NULL,
  source_region_fit NUMERIC NOT NULL DEFAULT 0,
  cup_profile_fit NUMERIC NOT NULL DEFAULT 0,
  commercial_fit NUMERIC NOT NULL DEFAULT 0,
  logistics_fit NUMERIC NOT NULL DEFAULT 0,
  compliance_fit NUMERIC NOT NULL DEFAULT 0,
  supplier_reliability_fit NUMERIC NOT NULL DEFAULT 0,
  recommendation_score NUMERIC NOT NULL,
  recommendation_reason TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE VIEW supplier_readiness AS
SELECT
  s.id,
  s.company_name,
  (
    s.exports_internationally = TRUE
    AND s.export_terms IS NOT NULL
    AND s.min_export_order_kg IS NOT NULL
    AND s.certificate_of_origin = TRUE
    AND s.phytosanitary_certificate = TRUE
    AND s.invoice_capability = TRUE
  ) AS export_ready,
  (
    s.can_ship_samples = TRUE
    AND s.sample_size_grams IS NOT NULL
    AND CARDINALITY(s.sample_couriers) > 0
    AND s.sample_shipping_paid_by IS NOT NULL
    AND s.sample_shipping_days IS NOT NULL
    AND s.sample_prep_days IS NOT NULL
    AND s.sample_price IS NOT NULL
  ) AS sample_ready,
  (s.prior_notice_handler IS NOT NULL) AS compliance_ready,
  s.approval_status
FROM suppliers s;

CREATE VIEW recommendation_eligible_lots AS
SELECT
  l.id,
  l.lot_name,
  l.supplier_id,
  l.region,
  l.varietals,
  l.process,
  l.price_per_kg,
  l.quantity_kg,
  l.export_ready,
  l.sample_ready,
  l.compliance_ready,
  s.company_name AS supplier_name,
  s.sample_couriers,
  s.sample_shipping_days,
  s.sample_prep_days,
  s.prior_notice_handler
FROM coffee_lots l
JOIN suppliers s ON s.id = l.supplier_id
WHERE l.export_ready = TRUE
  AND l.compliance_ready = TRUE;
