ALTER TABLE buyer_lot_interactions
  DROP CONSTRAINT IF EXISTS buyer_lot_interactions_type_check;

ALTER TABLE buyer_lot_interactions
  ADD CONSTRAINT buyer_lot_interactions_type_check CHECK (
    interaction_type IN (
      'view',
      'save',
      'recommendation_click',
      'inquiry',
      'sample_request',
      'shipment_delivered',
      'deal_closed',
      'lot_view',
      'similar_lot_click',
      'catalog_click',
      'survey_completed'
    )
  );

CREATE TABLE IF NOT EXISTS supplier_reviews (
  id TEXT PRIMARY KEY,
  supplier_id TEXT NOT NULL REFERENCES suppliers(id) ON DELETE CASCADE,
  reviewer_name TEXT NOT NULL,
  reviewer_role TEXT NOT NULL,
  reviewer_company TEXT,
  rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
  review_text TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS buyer_reviews (
  id TEXT PRIMARY KEY,
  buyer_id TEXT NOT NULL REFERENCES buyers(id) ON DELETE CASCADE,
  reviewer_name TEXT NOT NULL,
  reviewer_role TEXT NOT NULL,
  reviewer_company TEXT,
  rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
  review_text TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS buyer_recommendation_surveys (
  buyer_id TEXT PRIMARY KEY REFERENCES buyers(id) ON DELETE CASCADE,
  preferred_regions TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
  preferred_varietals TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
  preferred_processes TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
  target_tasting_notes TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
  preferred_couriers TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
  min_moq_kg NUMERIC,
  max_moq_kg NUMERIC,
  max_price_per_kg NUMERIC,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_supplier_reviews_supplier_id ON supplier_reviews(supplier_id);
CREATE INDEX IF NOT EXISTS idx_buyer_reviews_buyer_id ON buyer_reviews(buyer_id);

CREATE OR REPLACE VIEW supplier_review_summary AS
SELECT
  s.id AS supplier_id,
  COALESCE(ROUND(AVG(sr.rating)::numeric, 2), 0) AS average_rating,
  COUNT(sr.id)::integer AS review_count
FROM suppliers s
LEFT JOIN supplier_reviews sr ON sr.supplier_id = s.id
GROUP BY s.id;

CREATE OR REPLACE VIEW buyer_review_summary AS
SELECT
  b.id AS buyer_id,
  COALESCE(ROUND(AVG(br.rating)::numeric, 2), 0) AS average_rating,
  COUNT(br.id)::integer AS review_count
FROM buyers b
LEFT JOIN buyer_reviews br ON br.buyer_id = b.id
GROUP BY b.id;

INSERT INTO supplier_reviews (
  id, supplier_id, reviewer_name, reviewer_role, reviewer_company, rating, review_text
)
SELECT
  'sup_review_seed_001',
  'supplier_001',
  'Maya Chen',
  'buyer',
  'North Harbor Roasters',
  5,
  'Strong sample execution and clear Prior Notice ownership. Easy supplier to evaluate from the US.'
WHERE NOT EXISTS (SELECT 1 FROM supplier_reviews WHERE id = 'sup_review_seed_001');

INSERT INTO supplier_reviews (
  id, supplier_id, reviewer_name, reviewer_role, reviewer_company, rating, review_text
)
SELECT
  'sup_review_seed_002',
  'supplier_002',
  'Dev Kapoor',
  'buyer',
  'Harborline Imports',
  4,
  'Reliable export-ready communication and fast courier coordination for sample shipments.'
WHERE NOT EXISTS (SELECT 1 FROM supplier_reviews WHERE id = 'sup_review_seed_002');

INSERT INTO buyer_reviews (
  id, buyer_id, reviewer_name, reviewer_role, reviewer_company, rating, review_text
)
SELECT
  'buy_review_seed_001',
  'buyer_001',
  'Ratnagiri Estate',
  'supplier',
  'Ratnagiri Estate',
  5,
  'Responsive on sample feedback and very clear about evaluation criteria.'
WHERE NOT EXISTS (SELECT 1 FROM buyer_reviews WHERE id = 'buy_review_seed_001');

INSERT INTO buyer_reviews (
  id, buyer_id, reviewer_name, reviewer_role, reviewer_company, rating, review_text
)
SELECT
  'buy_review_seed_002',
  'harborline_imports_buy_f69b96',
  'Bison Ridge Coffee Collective',
  'supplier',
  'Bison Ridge Coffee Collective',
  4,
  'Commercial expectations were well defined and the team moved quickly after cupping.'
WHERE NOT EXISTS (SELECT 1 FROM buyer_reviews WHERE id = 'buy_review_seed_002');
