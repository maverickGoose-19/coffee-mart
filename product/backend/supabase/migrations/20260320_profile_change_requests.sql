CREATE TABLE IF NOT EXISTS profile_change_requests (
  id TEXT PRIMARY KEY,
  entity_type TEXT NOT NULL CHECK (entity_type IN ('buyer', 'supplier')),
  entity_id TEXT NOT NULL,
  requested_by_user_id TEXT NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
  current_snapshot JSONB NOT NULL,
  requested_snapshot JSONB NOT NULL,
  changed_fields TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  reviewed_at TIMESTAMPTZ,
  reviewed_by_user_id TEXT REFERENCES app_users(id)
);

CREATE INDEX IF NOT EXISTS idx_profile_change_requests_entity ON profile_change_requests(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_profile_change_requests_status ON profile_change_requests(status);
