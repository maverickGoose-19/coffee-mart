# ☕ Coffee Marketplace — CLAUDE.md
# Working Instructions for AI-Assisted Development

This file tells Claude how to work in this repo. Read it at the start of every session.

---

## 1. Project Identity

**Name:** Indian Specialty Coffee B2B Sourcing Platform (internal codename: BeanAI / coffee-startup)
**Type:** B2B marketplace — Indian specialty coffee suppliers ↔ international buyers (roasters, cafes, importers)
**Stage:** MVP development — 5 flows live, 8 planned (see Linear project)

**Tech Stack:**
- Backend: FastAPI (Python 3.11+), in `product/web-app/server.py`
- Database: PostgreSQL via Supabase (connection via env vars)
- Frontend: React SPA, pre-built static in `product/web-app/static/` — source in `figma design/src/`
- Auth: Cookie-based sessions
- Tests: `tests/` directory, run with `pytest`
- Deployment: Render (current) → AWS/GCP (scaling target)

**Run locally:**
```bash
PYTHONPATH=. RELOAD=true .venv/bin/python product/web-app/server.py
```

**Health check:** `GET http://127.0.0.1:8000/health` → `{ok: true}`

---

## 2. Key Integrations

| Tool | Purpose | Where |
|------|---------|--------|
| **Linear** | All tickets, projects, milestones | Project: "Coffee Marketplace Platform" (MAV-*) |
| **Notion** | Specs, runbooks, admin capability map | https://notion.so/33bb22064438816db2dfe6aa2057f3f9 |
| **GitHub** | Source control, PRs, CI | Branch conventions below |
| **Render** | Live deployment (current) | render.yaml / Dockerfile |
| **AWS/GCP** | Scaling target (Phase 2+) | Infrastructure TBD |

---

## 3. Linear Workflow

**Project:** Coffee Marketplace Platform
**Team:** Maverick_den
**Milestones:** MVP (Apr 30) · Phase 1 (May 30)

### Ticket conventions
- Always reference the Linear ticket (e.g. `MAV-6`) in branch names, commits, and PRs
- Before starting work: move ticket to `In Progress`
- After PR is open: move ticket to `In Review`
- After merge: move ticket to `Done`

### Priority guide
| Label | Meaning | Branch target |
|-------|---------|--------------|
| P0 Urgent | Blocks MVP launch | `main` via short-lived feature branch |
| P1 High | MVP scope | `main` via feature branch |
| P2 Medium | Phase 1 | `develop` or `main` after MVP |

---

## 4. Branch Management

```
main          ← production-ready, deploys to Render automatically
develop       ← integration branch (optional, use for Phase 1+)
feature/*     ← all new work
hotfix/*      ← urgent production fixes only
```

### Branch naming
```
feature/MAV-6-shipment-state-machine
feature/MAV-5-profile-change-approval
hotfix/MAV-XXX-short-description
```

### PR rules
- PRs must reference Linear ticket: `Closes MAV-6` in description
- Must pass `pytest` before merge
- Squash merge preferred for clean history
- Never force-push to `main`

### Git commit format
```
feat(MAV-6): add shipment status state machine

- Implements PATCH /api/inquiries/{id}/shipment
- Adds ShipmentUpdateRequest Pydantic model
- Guards invalid transitions with 422 errors

Closes MAV-6
```

---

## 5. File & Code Map

```
product/web-app/
  server.py               ← FastAPI app, all routes registered here
  models.py               ← Pydantic request/response models
  notifications.py        ← Email notification helpers
  repositories/
    approvals.py          ← Profile change request DB logic
    marketplace.py        ← Lots, catalog DB logic
    inquiries.py          ← Inquiry / shipment DB logic
    users.py              ← User account DB logic
  services/
    approvals.py          ← ApprovalService business logic
    inquiries.py          ← Inquiry transition guards
  static/                 ← Pre-built React SPA (do not edit directly)

figma design/src/         ← React source (rebuild → copy app.js to static/)
tests/                    ← pytest test suite
data/                     ← Seed data (suppliers, lots, inquiries)
product-docs/             ← PRDs and flow specs
```

### Auth pattern for all new endpoints
```python
user = current_user_from_request(request)
require_role(user, 'admin')   # or 'supplier', 'buyer'
```

### Demo credentials
| Role | Email | Password |
|------|-------|----------|
| Admin | admin@beanai.local | Admin123! |
| Buyer | buyer.demo@beanai.local | DemoBuyer123! |
| Supplier | supplier.demo@beanai.local | DemoSupplier123! |

---

## 6. Deployment — Render (Current)

**Live on Render** — auto-deploys from `main` branch on push.

Render config: `Dockerfile` + environment variables set in Render dashboard.

Required env vars:
- `DATABASE_URL` — Supabase PostgreSQL connection string
- `SECRET_KEY` — session signing key
- `RELOAD` — set `false` in production

### Deploy checklist before pushing to main
- [ ] `pytest` passes locally
- [ ] `GET /health` returns `{ok: true}` locally
- [ ] `GET /readyz` returns `{database: true, alertsConfigured: true}`
- [ ] No hardcoded secrets or local paths
- [ ] Linear ticket moved to `In Review` / PR open

---

## 7. Scaling Path — AWS / GCP (Phase 2+)

Target architecture (reference, not yet implemented):

```
                  ┌─────────────────────────────────┐
                  │  CloudFront / Cloud CDN           │  ← Static React SPA
                  └────────────┬────────────────────┘
                               │
                  ┌────────────▼────────────────────┐
                  │  ALB / Cloud Load Balancer        │
                  └────────────┬────────────────────┘
                               │
              ┌────────────────▼──────────────────────┐
              │  ECS Fargate / Cloud Run (FastAPI)     │  ← Auto-scaling containers
              └────────────────┬──────────────────────┘
                               │
              ┌────────────────▼──────────────────────┐
              │  RDS PostgreSQL / Cloud SQL            │  ← Managed DB (migrate from Supabase)
              └───────────────────────────────────────┘
```

**Migration steps (when ready):**
1. Containerize (Dockerfile already exists)
2. Push image to ECR / Artifact Registry
3. Deploy on ECS Fargate / Cloud Run
4. Migrate DB from Supabase → RDS / Cloud SQL with zero-downtime strategy
5. Set up CloudFront / CDN for static SPA
6. Configure secrets in AWS Secrets Manager / GCP Secret Manager
7. Add CI/CD via GitHub Actions → ECR → ECS

---

## 8. Notion Sync Rules

When completing a Linear ticket:
- If the Notion spec page exists, add a note: "✅ Implemented — [PR link] — [date]"
- If the flow is now live, update the Platform Flows Database status to `Live`

Key Notion pages:
- Platform Flows DB: https://www.notion.so/33bb220644388153aef0e51400574937
- New Flows Specs: https://www.notion.so/33bb22064438813f8eb9dcd7aeaed2d3
- Admin Capabilities: https://www.notion.so/33bb2206443881978b4fc4d517ca8135

---

## 9. Pointer Prompts — Copy & Use These

Below are ready-to-use prompts for common tasks. Copy, adapt, and run them.

---

### 🎫 Start a new ticket
```
Pick up Linear ticket MAV-[N]. Read the ticket description and acceptance criteria.
Create a feature branch `feature/MAV-[N]-[short-description]` and implement it.
Follow the implementation plan in the ticket. Run pytest when done.
Move the ticket to In Review when you open the PR.
```

---

### 🔀 Full ticket → PR → deploy flow
```
Implement Linear ticket MAV-[N] end to end:
1. Read the ticket from Linear
2. Create branch feature/MAV-[N]-[name]
3. Implement the endpoint(s) per the spec
4. Write or update tests in tests/
5. Run pytest — fix any failures
6. Check GET /health and GET /readyz pass
7. Commit with message: feat(MAV-[N]): [description]
8. Open PR targeting main with "Closes MAV-[N]" in body
9. Move Linear ticket to In Review
10. Update the Notion spec page to mark it as implemented
```

---

### 🌿 Branch hygiene
```
Show me all open feature branches. For each one, tell me:
- Which Linear ticket it maps to
- Whether the ticket is still In Progress or already Done
- Whether it has an open PR or not
Then help me clean up any stale branches.
```

---

### 🚀 Deploy to Render
```
Run the pre-deploy checklist for the coffee-startup project:
- Run pytest and show results
- Hit GET /health and GET /readyz locally
- Check for any hardcoded secrets or TODO comments near new endpoints
- Confirm Dockerfile builds cleanly
- Push to main and confirm Render deployment succeeds
```

---

### 📋 Sync Linear ↔ Notion after a deploy
```
I just merged and deployed MAV-[N].
1. Move the Linear ticket MAV-[N] to Done
2. Find the corresponding Notion spec page and mark it as implemented (add ✅ Implemented with today's date)
3. Update the Platform Flows Database status for this flow from Planned → Live
```

---

### 🔍 Plan next sprint from Linear backlog
```
Look at the Coffee Marketplace Platform project in Linear.
List all tickets that are:
- In the MVP milestone
- Status: Todo or Backlog
- Not blocked

For each, show the priority, effort estimate, and any blocking dependencies.
Suggest the best 3-5 tickets to work on this sprint, starting with P0s.
```

---

### 🧪 Write tests for a new endpoint
```
Write pytest tests for the endpoint implemented in MAV-[N].
Cover:
- Happy path (200/201/204)
- Auth failures (401 unauthenticated, 403 wrong role)
- Not found (404)
- Conflict or invalid input (409 / 422)
- Ownership violations (supplier accessing another's resource)
Use the existing test patterns in tests/ as reference.
```

---

### 🐛 Debug a broken endpoint
```
The endpoint [METHOD] /api/[path] is returning [status code] when it should return [expected].
Steps to reproduce: [curl command or request body]
Read the relevant service and repository file, identify the bug, fix it, and add a regression test.
```

---

### 📊 Update Notion flow status after work
```
I completed work on the following flows today: [list]
For each one:
1. Find the relevant entry in the Notion Platform Flows Database
2. Update its Status to the correct value (Live / In Progress / Partial)
3. Add any relevant notes about what was built
```

---

### ☁️ Prepare for AWS/GCP migration
```
Review the current Dockerfile and server.py for AWS/GCP readiness.
Check for:
- Hardcoded localhost references
- Non-environment-variable secrets
- Missing health check endpoint compatibility
- Any Render-specific config that needs to be abstracted
Then produce a migration checklist and GitHub Actions CI/CD workflow draft.
```

---

### 📝 Write a runbook for a completed flow
```
Write a detailed runbook for the [flow name] flow (MAV-[N]).
Include:
- Overview and actors
- Step-by-step API call sequence (with curl examples)
- Expected responses at each step
- Error scenarios and how to handle them
Save it to product-docs/ and create a corresponding Notion page under Existing Flows — Detailed Runbooks.
```

---

## 10. Rules Claude Should Always Follow

1. **Never hard-delete data** — use soft deletes (`archived = true`, `is_active = false`)
2. **Never hard-code secrets** — all credentials via environment variables
3. **Never push directly to main** — always via PR (except emergency hotfixes)
4. **Always run pytest before opening a PR** — do not open a PR with failing tests
5. **Always update Linear ticket status** as work progresses
6. **Role guards on every new endpoint** — `require_role(user, role)` pattern
7. **Immutable fields** — never overwrite `companyName`, `contactEmail`, `region`, `buyerType` even if in a snapshot
8. **Partial updates** — PATCH endpoints only update fields that are explicitly provided
9. **Render auto-deploys from main** — only push to main when the build is production-ready
10. **Keep Notion in sync** — update flow status and spec pages after completing work
