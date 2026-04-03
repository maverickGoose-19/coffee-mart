INSERT INTO buyers (
  id,
  company_name,
  contact_name,
  contact_email,
  buyer_type,
  destination_country,
  preferred_regions,
  preferred_varietals,
  preferred_processes,
  target_tasting_notes,
  preferred_certifications,
  min_moq_kg,
  max_moq_kg,
  max_price_per_kg,
  requires_samples,
  preferred_couriers,
  needs_us_compliance_support
)
VALUES
  (
    'buyer_001',
    'North Harbor Roasters',
    'Maya Chen',
    'maya@northharbor.example',
    'roaster',
    'US',
    ARRAY['Bababudangiri, Karnataka', 'Coorg, Karnataka'],
    ARRAY['Selection 795', 'SLN9'],
    ARRAY['Washed'],
    ARRAY['citrus', 'stone fruit', 'jaggery'],
    ARRAY['Organic'],
    120,
    400,
    14,
    TRUE,
    ARRAY['DHL'],
    TRUE
  ),
  (
    'buyer_002',
    'Pine Street Coffee',
    'Elena Brooks',
    'greenbuyer@pinestreet.example',
    'cafe',
    'US',
    ARRAY['Coorg, Karnataka'],
    ARRAY['Cauvery', 'Selection 9'],
    ARRAY['Natural'],
    ARRAY['berry', 'cacao', 'floral'],
    ARRAY['Rainforest Alliance'],
    80,
    250,
    15,
    TRUE,
    ARRAY['UPS'],
    TRUE
  )
ON CONFLICT (id) DO NOTHING;

INSERT INTO suppliers (
  id,
  company_name,
  contact_name,
  contact_email,
  region,
  website,
  altitude_meters,
  varietals,
  certifications,
  description,
  exports_internationally,
  export_partner_name,
  export_terms,
  min_export_order_kg,
  certificate_of_origin,
  phytosanitary_certificate,
  invoice_capability,
  can_ship_samples,
  sample_size_grams,
  sample_couriers,
  sample_shipping_paid_by,
  sample_prep_days,
  sample_shipping_days,
  sample_price,
  prior_notice_handler
)
VALUES
  (
    'supplier_001',
    'Ratnagiri Estate',
    'Anika Rao',
    'anika@ratnagiri.example',
    'Bababudangiri, Karnataka',
    'https://ratnagiri.example',
    1400,
    ARRAY['Selection 795', 'SLN9'],
    ARRAY['Organic'],
    'Specialty arabica estate producing washed and natural microlots.',
    TRUE,
    'Ratnagiri Export House',
    'FOB',
    240,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    200,
    ARRAY['DHL', 'FedEx'],
    'buyer',
    2,
    5,
    20,
    'supplier'
  ),
  (
    'supplier_002',
    'Bison Ridge Coffee Collective',
    'Rahul Menon',
    'rahul@bisonridge.example',
    'Coorg, Karnataka',
    'https://bisonridge.example',
    1250,
    ARRAY['Cauvery', 'Selection 9'],
    ARRAY['Rainforest Alliance'],
    'Producer collective focused on high-elevation lots and traceable contracts.',
    TRUE,
    'Coorg Mountain Exports',
    'EXW',
    300,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    250,
    ARRAY['UPS'],
    'supplier',
    3,
    6,
    0,
    'broker'
  )
ON CONFLICT (id) DO NOTHING;

INSERT INTO coffee_lots (
  id,
  supplier_id,
  lot_name,
  region,
  altitude_meters,
  varietals,
  process,
  harvest_year,
  quantity_kg,
  price_per_kg,
  cup_score,
  tasting_notes,
  export_ready,
  sample_ready,
  compliance_ready
)
VALUES
  (
    'lot_001',
    'supplier_001',
    'Ratnagiri Washed 24A',
    'Bababudangiri, Karnataka',
    1400,
    ARRAY['Selection 795', 'SLN9'],
    'Washed',
    2026,
    800,
    12.5,
    86.5,
    ARRAY['citrus', 'jaggery', 'stone fruit'],
    TRUE,
    TRUE,
    TRUE
  ),
  (
    'lot_002',
    'supplier_002',
    'Bison Ridge Natural Reserve',
    'Coorg, Karnataka',
    1250,
    ARRAY['Cauvery', 'Selection 9'],
    'Natural',
    2026,
    600,
    13.75,
    87.25,
    ARRAY['berry', 'cacao', 'floral'],
    TRUE,
    TRUE,
    TRUE
  )
ON CONFLICT (id) DO NOTHING;

INSERT INTO buyer_inquiries (
  id,
  buyer_id,
  supplier_id,
  lot_id,
  destination_country,
  requested_sample_grams,
  shipment_status,
  tracking_number,
  courier,
  prior_notice_required,
  prior_notice_filed,
  prior_notice_filed_by
)
VALUES
  (
    'inq_001',
    'buyer_001',
    'supplier_001',
    'lot_001',
    'US',
    200,
    'prior_notice_pending',
    NULL,
    'DHL',
    TRUE,
    FALSE,
    'supplier'
  ),
  (
    'inq_002',
    'buyer_002',
    'supplier_002',
    'lot_002',
    'US',
    250,
    'shipped',
    '7733445512',
    'UPS',
    TRUE,
    TRUE,
    'broker'
  )
ON CONFLICT (id) DO NOTHING;

INSERT INTO buyer_lot_interactions (
  id,
  buyer_id,
  lot_id,
  interaction_type,
  source_surface,
  occurred_at
)
VALUES
  (
    'interaction_001',
    'buyer_001',
    'lot_001',
    'recommendation_click',
    'recommended_catalog',
    '2026-03-16T09:15:00Z'
  ),
  (
    'interaction_002',
    'buyer_001',
    'lot_001',
    'sample_request',
    'lot_detail',
    '2026-03-16T09:25:00Z'
  ),
  (
    'interaction_003',
    'buyer_002',
    'lot_002',
    'view',
    'similar_lots',
    '2026-03-16T10:05:00Z'
  )
ON CONFLICT (id) DO NOTHING;

INSERT INTO lot_recommendation_snapshots (
  id,
  buyer_id,
  lot_id,
  model_version,
  source_region_fit,
  cup_profile_fit,
  commercial_fit,
  logistics_fit,
  compliance_fit,
  supplier_reliability_fit,
  recommendation_score,
  recommendation_reason
)
VALUES
  (
    'rec_001',
    'buyer_001',
    'lot_001',
    'rules-v1',
    0.95,
    0.92,
    0.86,
    0.90,
    1.00,
    0.82,
    0.91,
    'Matches your washed Karnataka preference, 120-400kg MOQ range, DHL sample preference, and compliance-ready workflow.'
  ),
  (
    'rec_002',
    'buyer_002',
    'lot_002',
    'rules-v1',
    0.98,
    0.94,
    0.89,
    0.88,
    0.96,
    0.80,
    0.91,
    'Matches your Coorg natural profile, berry-forward notes, UPS sample preference, and low-friction sample workflow.'
  )
ON CONFLICT (id) DO NOTHING;
