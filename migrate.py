"""Run all migrations + seed in order against the Supabase DB."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# Load settings (reads product/backend/supabase/.env)
from product.backend.app.config import settings  # noqa: E402
import psycopg  # noqa: E402

MIGRATIONS = [
    ROOT / "product/backend/supabase/migrations/20260316_initial_schema.sql",
    ROOT / "product/backend/supabase/migrations/20260317_auth_and_live_inquiries.sql",
    ROOT / "product/backend/supabase/migrations/20260318_reviews_and_surveys.sql",
    ROOT / "product/backend/supabase/migrations/20260319_supplier_images.sql",
    ROOT / "product/backend/supabase/migrations/20260320_profile_change_requests.sql",
    ROOT / "product/backend/supabase/seed.sql",
]

db_url = settings.supabase_db_url
if "sslmode=" not in db_url:
    sep = "&" if "?" in db_url else "?"
    db_url = f"{db_url}{sep}sslmode=require"

print(f"Connecting to: {db_url.split('@')[-1]}")  # hide credentials

with psycopg.connect(db_url) as conn:
    conn.autocommit = True
    for path in MIGRATIONS:
        sql = path.read_text()
        print(f"  → {path.name} ...", end=" ", flush=True)
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
            print("OK")
        except Exception as e:
            print(f"FAILED\n    {e}")
            sys.exit(1)

print("\nAll migrations applied. You can now start the server.")
