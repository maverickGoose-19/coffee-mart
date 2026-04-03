# Indian Specialty Coffee Sourcing Platform

This workspace is the operating system for a B2B sourcing startup focused on Indian specialty coffee.

The product is not just a marketplace. It combines:

- supplier discovery
- export readiness visibility
- sample logistics coordination
- FDA Prior Notice responsibility tracking for US-bound shipments
- an AI-assisted recommendation layer for buyers and operators

## Workspace Map

- `product/` application code, backend schema, and infrastructure
- `product-docs/` PRDs, user flows, and API contracts
- `research/` market, supply, logistics, compliance, and customer research
- `gtm/` outreach and go-to-market assets
- `operations/` process docs and deal execution
- `finance/` pricing and model placeholders
- `legal/` agreements and compliance notes
- `data/` seed records for suppliers, lots, and inquiries

## MVP Guardrails

The MVP is incomplete unless:

- suppliers capture export, sample, and compliance fields
- buyers can see shipping capability before requesting samples
- inquiries track sample shipment lifecycle
- admin can filter export-ready suppliers
- compliance responsibility is defined for every approved supplier
- recommendations never surface non-compliant or non-ready lots ahead of better-fit options

## Run

Local development:

```bash
cd coffee-startup
INSTALL_DEPS=true ./start.sh
```

Fast local restart without reinstalling dependencies:

```bash
cd coffee-startup
./start.sh
```

Production-style local run:

```bash
cd coffee-startup
make prod
```

Health checks:

- `GET /healthz`
- `GET /readyz`

## Production Notes

- The app is a FastAPI service that serves the static web UI and API from one process.
- Database migrations can be applied with `python migrate.py`.
- Alert emails support Resend first and SMTP second.
- The recommended deploy path is Docker with environment variables supplied at runtime.
- Session cookies should use `SECURE_COOKIES=true` in any HTTPS production environment.
- API docs can be disabled in production with `DOCS_ENABLED=false`.

Required environment variables:

- `SUPABASE_DB_URL`
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`
- `ALERT_EMAIL_TO`

Optional but recommended:

- `RESEND_API_KEY`
- `RESEND_FROM_EMAIL`
- `RESEND_REPLY_TO`
- `CORS_ORIGINS`
- `TRUSTED_HOSTS`
- `DOCS_ENABLED`
