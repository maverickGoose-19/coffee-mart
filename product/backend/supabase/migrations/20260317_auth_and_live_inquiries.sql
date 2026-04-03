CREATE TABLE IF NOT EXISTS app_users (
  id TEXT PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  display_name TEXT,
  role TEXT NOT NULL,
  password_hash TEXT NOT NULL,
  password_salt TEXT NOT NULL,
  supplier_id TEXT REFERENCES suppliers(id),
  buyer_id TEXT REFERENCES buyers(id),
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT app_users_role_check CHECK (
    role IN ('admin', 'supplier', 'buyer')
  )
);

CREATE TABLE IF NOT EXISTS app_sessions (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
  token_hash TEXT NOT NULL UNIQUE,
  expires_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE buyer_inquiries
  ADD COLUMN IF NOT EXISTS buyer_message TEXT;

ALTER TABLE buyer_inquiries
  ADD COLUMN IF NOT EXISTS source_surface TEXT;

CREATE INDEX IF NOT EXISTS idx_app_users_role ON app_users(role);
CREATE INDEX IF NOT EXISTS idx_app_users_supplier_id ON app_users(supplier_id);
CREATE INDEX IF NOT EXISTS idx_app_users_buyer_id ON app_users(buyer_id);
CREATE INDEX IF NOT EXISTS idx_app_sessions_user_id ON app_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_buyer_inquiries_buyer_id ON buyer_inquiries(buyer_id);
