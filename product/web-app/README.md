# Web App

This folder now contains the local website launcher and static frontend for a FastAPI-backed prototype that:

- serves the marketplace website locally
- reads data from Supabase
- submits supplier onboarding forms into the live `suppliers` table
- submits buyer onboarding forms into the live `buyers` table
- submits live sample requests into the live `buyer_inquiries` table
- supports role-based auth for buyers, suppliers, and admins
- computes recommendation scores dynamically from buyer preferences and lot readiness
- logs recommendation clicks and lot views into `buyer_lot_interactions`
- stores buyer recommendation-survey submissions for first-time recommendation onboarding
- supports supplier reviews and buyer reviews with star ratings
- shows role-gated buyer and supplier workspaces, with signup starting from the auth page
- exposes catalog, coffee detail, buyer preferences, inquiry tracking, and admin views

## Run Locally

```bash
cd coffee-startup
source .venv/bin/activate
python product/web-app/server.py
```

Default URL:

- `http://127.0.0.1:8000`

## Demo Sign-In

Local demo credentials:

- Admin: `admin@beanai.local` / `Admin123!`
- Seeded buyers: use seeded buyer emails with `DemoBuyer123!`
- Seeded suppliers: use seeded supplier emails with `DemoSupplier123!`

## Notes

- `server.py` is now a thin `uvicorn` launcher for the FastAPI app in `product/backend/app`
- the FastAPI app reads the database connection from `product/backend/supabase/.env`
- this avoids exposing a privileged database credential to the browser
- the Figma-exported code in `figma design/` remains as the visual reference bundle
- the UI palette was upgraded toward a more professional B2B visual system
