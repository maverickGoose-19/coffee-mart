const state = {
  bootstrap: null,
  lotDetail: null,
};

const app = document.getElementById("app");

function formatPercent(value) {
  return `${Math.round(Number(value || 0))}%`;
}

function safeJoin(items) {
  return (items || []).length ? items.join(", ") : "Not set";
}

function csvValue(items) {
  return (items || []).length ? items.join(", ") : "";
}

function parseCsv(value) {
  return String(value || "")
    .split(",")
    .map((entry) => entry.trim())
    .filter(Boolean);
}

const REGION_ESTATE_IMAGES = {
  "Bababudangiri, Karnataka": "https://images.unsplash.com/photo-1447933601403-0c6688de566e?auto=format&fit=crop&w=1200&q=80",
  "Coorg, Karnataka": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=1200&q=80",
  "Chikmagalur, Karnataka": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=1200&q=80",
  "Wayanad, Kerala": "https://images.unsplash.com/photo-1461988091159-192b6df7054f?auto=format&fit=crop&w=1200&q=80",
  "Araku Valley, Andhra Pradesh": "https://images.unsplash.com/photo-1442512595331-e89e73853f31?auto=format&fit=crop&w=1200&q=80",
};

const DEFAULT_COFFEE_IMAGE = "https://images.unsplash.com/photo-1494314671902-399b18174975?auto=format&fit=crop&w=1200&q=80";
const HOME_GALLERY_IMAGES = [
  "https://images.unsplash.com/photo-1511920170033-f8396924c348?auto=format&fit=crop&w=1200&q=80",
  "https://images.unsplash.com/photo-1442512595331-e89e73853f31?auto=format&fit=crop&w=1200&q=80",
  "https://images.unsplash.com/photo-1459755486867-b55449bb39ff?auto=format&fit=crop&w=1200&q=80",
  "https://images.unsplash.com/photo-1447933601403-0c6688de566e?auto=format&fit=crop&w=1200&q=80",
];

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function estateImageFor(entity) {
  return entity?.estate_image_url || entity?.estateImageUrl || entity?.gallery_image_urls?.[0] || REGION_ESTATE_IMAGES[entity?.region] || DEFAULT_COFFEE_IMAGE;
}

function coffeeImageFor(entity) {
  return entity?.coffee_image_url || entity?.coffeeImageUrl || entity?.gallery_image_urls?.[1] || entity?.galleryImageUrls?.[1] || entity?.gallery_image_urls?.[0] || entity?.galleryImageUrls?.[0] || DEFAULT_COFFEE_IMAGE;
}

function mediaFrame(url, alt, className = "media-frame") {
  return `<div class="${className}"><img src="${escapeHtml(url)}" alt="${escapeHtml(alt)}" loading="lazy" /></div>`;
}

async function refreshBootstrap() {
  try {
    const response = await fetch("/api/bootstrap");
    if (!response.ok) throw new Error(`Bootstrap HTTP ${response.status}`);
    state.bootstrap = await response.json();
  } catch (error) {
    console.error("[bootstrap] failed to refresh:", error);
  }
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const result = await response.json();
  return { response, result };
}

async function patchJson(url, payload) {
  const response = await fetch(url, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const result = await response.json();
  return { response, result };
}

async function trackInteraction(lotId, interactionType, sourceSurface) {
  if (!lotId || !interactionType) return;
  try {
    await postJson("/api/interactions", {
      lotId,
      interactionType,
      sourceSurface,
    });
  } catch (_error) {
    // Ignore telemetry failures in the UI; they should never block the product flow.
  }
}

function currentUser() {
  return state.bootstrap?.currentUser || null;
}

function currentParams() {
  return new URLSearchParams(window.location.search);
}

function renderStars(rating, reviewCount = 0) {
  const rounded = Math.round(Number(rating || 0));
  const stars = Array.from({ length: 5 }, (_, index) => (
    index < rounded ? "★" : "☆"
  )).join("");
  return `
    <div class="star-row">
      <span class="stars">${stars}</span>
      <span>${Number(rating || 0).toFixed(1)}${reviewCount ? ` · ${reviewCount} review${reviewCount === 1 ? "" : "s"}` : ""}</span>
    </div>
  `;
}

function renderReviewCards(reviews, emptyText) {
  if (!reviews?.length) {
    return `<p class="lead">${emptyText}</p>`;
  }
  return `
    <div class="review-stack">
      ${reviews.map((review) => `
        <div class="review-card">
          <div class="review-card-head">
            <strong>${review.reviewer_name}</strong>
            <span>${"★".repeat(review.rating)}${"☆".repeat(5 - review.rating)}</span>
          </div>
          <p class="lead">${review.review_text || "No written review provided."}</p>
          <div class="review-meta">${review.reviewer_role}${review.reviewer_company ? ` · ${review.reviewer_company}` : ""}</div>
        </div>
      `).join("")}
    </div>
  `;
}

function renderChangeRequestList(requests, emptyText, showAdminActions = false) {
  if (!requests?.length) {
    return `<p class="lead">${emptyText}</p>`;
  }
  return `
    <div class="review-stack">
      ${requests.map((request) => {
        const status = request.status;
        const isPending = status === "pending";
        const adminBtns = showAdminActions && isPending ? `
          <div style="margin-top:8px;display:flex;gap:8px;">
            <button class="button admin-change-request-btn" style="font-size:12px;padding:4px 12px;background:#16a34a;border-color:#16a34a"
              data-request-id="${request.id}" data-decision="approved">✓ Approve</button>
            <button class="button-secondary admin-change-request-btn" style="font-size:12px;padding:4px 12px;color:#dc2626;border-color:#dc2626"
              data-request-id="${request.id}" data-decision="rejected">✗ Deny</button>
          </div>` : "";
        return `
          <div class="review-card" id="chgreq-${request.id}">
            <div class="review-card-head">
              <strong>${request.entity_type || request.entityType} update</strong>
              <span class="badge ${status === "approved" ? "" : status === "rejected" ? "warn" : "muted"}">${status}</span>
            </div>
            <p class="lead">Changed fields: ${(request.changed_fields || request.changedFields || []).join(", ")}</p>
            <div class="review-meta">Request ${request.id}</div>
            ${adminBtns}
          </div>
        `;
      }).join("")}
    </div>
  `;
}

function canAccessBuyerWorkspace() {
  const user = currentUser();
  return user?.role === "buyer" || currentParams().get("signup") === "buyer";
}

function canAccessSupplierWorkspace() {
  const user = currentUser();
  return user?.role === "supplier" || currentParams().get("signup") === "supplier";
}

function workspacePathForUser(user = currentUser()) {
  if (!user) return "/auth";
  if (user.role === "admin") return "/admin";
  if (user.role === "buyer") return "/buyer-preferences";
  if (user.role === "supplier") return "/supplier-onboarding";
  return "/catalog";
}

function nav(pathname) {
  const user = currentUser();
  const links = [
    { href: "/", label: "Home" },
    { href: "/catalog", label: "Catalog" },
  ];
  if (user?.role === "buyer") {
    links.push({ href: "/buyer-preferences", label: "Buyer Workspace" });
  }
  if (user?.role === "supplier") {
    links.push({ href: "/supplier-onboarding", label: "Supplier Workspace" });
  }
  if (user) {
    links.push({ href: "/inquiries", label: "Inquiries" });
  }
  if (user?.role === "admin") {
    links.push({ href: "/admin", label: "Admin" });
  }
  return `
    <header class="nav">
      <div class="nav-inner">
        <a class="brand" href="/">Indian Coffee Ledger</a>
        <nav class="nav-links">
          ${links.map((link) => `
            <a class="${pathname === link.href ? "active" : ""}" href="${link.href}">${link.label}</a>
          `).join("")}
        </nav>
        <div class="nav-auth">
          ${
            user
              ? `<div class="auth-chip">
                  <strong>${user.display_name || user.email}</strong>
                  <span>${user.role}</span>
                </div>
                <button class="button-ghost" id="nav-signout">Sign Out</button>`
              : `<a class="button-ghost" href="/auth">Sign In / Sign Up</a>`
          }
        </div>
      </div>
    </header>
  `;
}

function footer() {
  return `
    <footer class="footer">
      <div class="footer-inner">
        Built from the Figma handoff and upgraded into a live Supabase-backed prototype with recommendation-aware sourcing flows.
      </div>
    </footer>
  `;
}

function lotCard(lot, reason) {
  const notes = (lot.tasting_notes || []).join(", ");
  return `
    <article class="card">
      ${mediaFrame(coffeeImageFor(lot), `${lot.lot_name} coffee lot`, "card-media")}
      <div class="badge-row">
        ${lot.export_ready ? '<span class="badge">Export Ready</span>' : ""}
        ${lot.sample_ready ? '<span class="badge">Sample Ready</span>' : '<span class="badge warn">Sample Gap</span>'}
        ${lot.compliance_ready ? '<span class="badge">Compliance Ready</span>' : '<span class="badge warn">Compliance Gap</span>'}
      </div>
      <h3>${lot.lot_name}</h3>
      <p><strong>${lot.supplier_name}</strong> · ${lot.region || "Region pending"}</p>
      ${renderStars(lot.supplier_average_rating, lot.supplier_review_count)}
      <p>${lot.process || "Process pending"} · Cup score ${lot.cup_score || "TBD"} · $${lot.price_per_kg || "TBD"}/kg</p>
      <p class="lead">${notes || "Tasting notes pending"}</p>
      ${reason ? `<div class="callout"><strong>Why it matches</strong><br>${reason}</div>` : ""}
      <div class="actions">
        <a class="button" href="/coffee/${lot.id}">View Detail</a>
      </div>
    </article>
  `;
}

function homeTeaserCard(lot, user) {
  if (user) {
    return lotCard(lot);
  }
  return `
    <article class="card teaser-card">
      ${mediaFrame(coffeeImageFor(lot), `${lot.lot_name} teaser`, "card-media")}
      <div class="badge-row">
        ${lot.export_ready ? '<span class="badge">Export Ready</span>' : ""}
        ${lot.sample_ready ? '<span class="badge">Sample Ready</span>' : '<span class="badge warn">Sample Gap</span>'}
      </div>
      <h3>${lot.lot_name}</h3>
      <p><strong>${lot.region || "Indian origin"}</strong></p>
      <p class="lead">Log in to view supplier identity, pricing, process details, sample logistics, and contact workflow.</p>
      <div class="actions">
        <a class="button-secondary" href="/auth">Log In To See More</a>
      </div>
    </article>
  `;
}

function bindGlobalActions() {
  const signout = document.getElementById("nav-signout");
  if (signout) {
    signout.addEventListener("click", async () => {
      await fetch("/api/auth/signout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
      await refreshBootstrap();
      window.location.href = "/";
    });
  }

  document.querySelectorAll("[data-track-type][data-lot-id]").forEach((element) => {
    if (element.dataset.trackingBound === "true") return;
    element.dataset.trackingBound = "true";
    element.addEventListener("click", () => {
      trackInteraction(
        element.dataset.lotId,
        element.dataset.trackType,
        element.dataset.sourceSurface || ""
      );
    });
  });

  bindSurveyModal();
}

function ensureSurveyModal() {
  const user = currentUser();
  if (!user || user.role !== "buyer" || !state.bootstrap?.surveyRequired) return;
  if (sessionStorage.getItem(`survey-dismissed:${user.id}`) === "true") return;
  if (document.getElementById("survey-modal")) return;
  document.body.insertAdjacentHTML("beforeend", `
    <div class="modal-backdrop" id="survey-modal">
      <div class="modal-card">
        <div class="section-head">
          <div>
            <h2>Recommendation Survey</h2>
            <p class="lead">Start with default recommendations, then unlock more relevant matches by telling us what this buyer actually wants to source.</p>
          </div>
        </div>
        <div id="survey-error" class="error-banner hidden"></div>
        <form id="survey-form" class="form-grid">
          <div class="form-grid two">
            <label>Preferred Regions<input class="input" name="preferredRegions" placeholder="Coorg, Karnataka" /></label>
            <label>Preferred Varietals<input class="input" name="preferredVarietals" placeholder="Selection 795, SLN9" /></label>
            <label>Preferred Processes<input class="input" name="preferredProcesses" placeholder="Washed, Natural" /></label>
            <label>Target Tasting Notes<input class="input" name="targetTastingNotes" placeholder="citrus, berry, cacao" /></label>
            <label>Preferred Couriers<input class="input" name="preferredCouriers" placeholder="DHL, UPS" /></label>
            <label>Max Price Per Kg<input class="input" name="maxPricePerKg" type="number" step="0.01" /></label>
            <label>Minimum MOQ (kg)<input class="input" name="minMoqKg" type="number" /></label>
            <label>Maximum MOQ (kg)<input class="input" name="maxMoqKg" type="number" /></label>
          </div>
          <div class="actions">
            <button class="button" type="submit">Save Survey</button>
            <button class="button-secondary" type="button" id="survey-later">Later</button>
          </div>
        </form>
      </div>
    </div>
  `);
}

function bindSurveyModal() {
  ensureSurveyModal();
  const modal = document.getElementById("survey-modal");
  if (!modal) return;
  const later = document.getElementById("survey-later");
  if (later && later.dataset.bound !== "true") {
    later.dataset.bound = "true";
    later.addEventListener("click", () => {
      const user = currentUser();
      if (user) {
        sessionStorage.setItem(`survey-dismissed:${user.id}`, "true");
      }
      modal.remove();
    });
  }
  const form = document.getElementById("survey-form");
  if (form && form.dataset.bound !== "true") {
    form.dataset.bound = "true";
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const error = document.getElementById("survey-error");
      error.classList.add("hidden");
      const formData = new FormData(form);
      const { response, result } = await postJson("/api/recommendation-survey", {
        preferredRegions: parseCsv(formData.get("preferredRegions")),
        preferredVarietals: parseCsv(formData.get("preferredVarietals")),
        preferredProcesses: parseCsv(formData.get("preferredProcesses")),
        targetTastingNotes: parseCsv(formData.get("targetTastingNotes")),
        preferredCouriers: parseCsv(formData.get("preferredCouriers")),
        minMoqKg: formData.get("minMoqKg") ? Number(formData.get("minMoqKg")) : null,
        maxMoqKg: formData.get("maxMoqKg") ? Number(formData.get("maxMoqKg")) : null,
        maxPricePerKg: formData.get("maxPricePerKg") ? Number(formData.get("maxPricePerKg")) : null,
      });
      if (!response.ok) {
        error.textContent = result.error || "Could not save survey.";
        error.classList.remove("hidden");
        return;
      }
      const user = currentUser();
      if (user) {
        sessionStorage.removeItem(`survey-dismissed:${user.id}`);
      }
      await refreshBootstrap();
      modal.remove();
      router();
    });
  }
}

function renderHome(pathname) {
  const lots = state.bootstrap.lots.slice(0, 3);
  const recs = state.bootstrap.recommendations.slice(0, 2);
  const contextBuyer = state.bootstrap.recommendationContextBuyer;
  const recommendationMode = state.bootstrap.recommendationMode;
  const user = currentUser();
  const examples = [
    {
      title: "Seattle roaster sample flow",
      copy: "Buyer filters for washed Karnataka coffees, requests a sample, and sees who handles Prior Notice before the box ships.",
      image: coffeeImageFor(recs[0] || lots[0] || {}),
    },
    {
      title: "Importer shortlist by readiness",
      copy: "Catalog results stay grounded in export, sample, and compliance status so low-friction lots surface first.",
      image: estateImageFor(recs[0] || lots[0] || { region: "Coorg, Karnataka" }),
    },
    {
      title: "Supplier story with visuals",
      copy: "Estates can add their own photos, agronomy details, and export capabilities to build trust before the first call.",
      image: HOME_GALLERY_IMAGES[2],
    },
  ];
  app.innerHTML = `
    <div class="shell">
      ${nav(pathname)}
      <main>
        <section class="hero section">
          <div class="hero-card section">
            <div class="hero-copy">
              <span class="eyebrow">Trust + Logistics + Recommendations</span>
              <h1>Source Indian specialty coffee with export visibility and recommendation support.</h1>
              <p>Discover verified suppliers, request samples, track Prior Notice responsibility, and surface the best-fit lots for each buyer based on origin, process, commercial fit, and readiness.</p>
              <div class="actions">
                <a class="button" href="/catalog">Browse Coffee</a>
                ${user ? `<a class="button-secondary" href="${workspacePathForUser(user)}">Open Workspace</a>` : `<a class="button-secondary" href="/auth">Sign In / Sign Up</a>`}
              </div>
              <div class="hero-stat-row">
                <div class="hero-stat">
                  <strong>${state.bootstrap.metrics?.supplier_count || 0}</strong>
                  <span>Suppliers in platform</span>
                </div>
                <div class="hero-stat">
                  <strong>${state.bootstrap.metrics?.buyer_count || 0}</strong>
                  <span>Buyers profiled</span>
                </div>
                <div class="hero-stat">
                  <strong>${recommendationMode === "personalized" ? "Personalized" : "Default"}</strong>
                  <span>Recommendation mode</span>
                </div>
              </div>
            </div>
            <div class="hero-visual-stack">
              <div class="hero-media-grid">
                ${mediaFrame(recs[0] ? estateImageFor(recs[0]) : estateImageFor({ region: "Coorg, Karnataka" }), "Indian coffee estate", "hero-media")}
                ${mediaFrame(recs[0] ? coffeeImageFor(recs[0]) : DEFAULT_COFFEE_IMAGE, "Coffee cherries and green coffee", "hero-media")}
              </div>
              <div class="mini-gallery">
                ${HOME_GALLERY_IMAGES.slice(0, 3).map((image, index) => mediaFrame(image, `Coffee sourcing gallery ${index + 1}`, "mini-gallery-card")).join("")}
              </div>
              <div class="trust-stack">
                <div class="trust-item">
                <strong>Export and sample readiness embedded</strong>
                Buyers see real shipping capability before they request samples.
                </div>
                <div class="trust-item">
                <strong>Compliance tracked per shipment</strong>
                Prior Notice ownership is explicit for every US-bound sample flow.
                </div>
                <div class="trust-item">
                <strong>Explainable recommendations</strong>
                Recommendations are sourced-aware, logistics-aware, and compliance-aware.
                </div>
              </div>
            </div>
          </div>
        </section>
        <section class="section roomy-section">
          <div class="section-head">
            <div>
              <h2>Real sourcing examples</h2>
              <p>The homepage should show what the platform actually helps people do, not just describe the product in abstract terms.</p>
            </div>
          </div>
          <div class="story-grid">
            ${examples.map((example) => `
              <article class="story-card">
                ${mediaFrame(example.image, example.title, "story-media")}
                <div class="story-content">
                  <span class="eyebrow subtle">Example</span>
                  <h3>${example.title}</h3>
                  <p class="lead">${example.copy}</p>
                </div>
              </article>
            `).join("")}
          </div>
        </section>
        <section class="section">
          <div class="section-head">
            <div>
              <h2>Recommended right now</h2>
              <p>${recommendationMode === "personalized" && contextBuyer ? `These are personalized recommendations for ${contextBuyer.company_name}, based on survey preferences, lot attributes, and readiness rules.` : "These are default recommendations for first-time or anonymous users, ranked by readiness, quality, and supplier trust signals."}</p>
            </div>
          </div>
          <div class="recommendation-rail section">
            ${recs.map((rec) => `
              <div class="recommendation-card">
                ${mediaFrame(coffeeImageFor(rec), `${rec.lot_name} recommendation`, "recommendation-media")}
                <div class="recommendation-score">Fit score ${Math.round(rec.recommendation_score * 100)}%</div>
                <h3>${rec.lot_name}</h3>
                <p><strong>${rec.region}</strong>${user ? ` · ${rec.supplier_name}` : ""}</p>
                <p>${user ? `${rec.process} · Cup score ${rec.cup_score}` : "Sign in to view process, supplier, and logistics details."}</p>
                <p class="lead">${user ? rec.recommendation_reason : "Default homepage recommendations stay visible, but deeper supplier and lot detail is gated behind login."}</p>
                <a class="button-ghost" href="${user ? `/coffee/${rec.lot_id}` : `/auth`}" data-lot-id="${user ? rec.lot_id : ""}" data-track-type="${user ? "recommendation_click" : ""}" data-source-surface="home_recommendation">${user ? "Open lot" : "Log In To See More"}</a>
              </div>
            `).join("")}
          </div>
        </section>
        <section class="section roomy-section">
          <div class="section-head">
            <div>
              <h2>Featured lots</h2>
              <p>Use these as concrete examples of how the marketplace combines agronomy, commercial fit, and export readiness into one buyer-facing surface.</p>
            </div>
          </div>
          <div class="grid-3">
            ${lots.map((lot) => homeTeaserCard(lot, user)).join("")}
          </div>
        </section>
        <section class="section">
          <div class="panel home-bottom-panel">
            <div class="section-head">
              <div>
                <h2>Why this feels lower risk</h2>
                <p>Good B2B sourcing products reduce ambiguity before the sample ever leaves origin. That is the real value layer here.</p>
              </div>
            </div>
            <div class="grid-3">
              <div class="card soft-card">
                ${mediaFrame(HOME_GALLERY_IMAGES[1], "Coffee export and sample workflow", "story-media compact")}
                <h3>Clear logistics</h3>
                <p class="lead">Prep time, courier choice, shipping ownership, and sample size are all visible before the buyer commits.</p>
              </div>
              <div class="card soft-card">
                ${mediaFrame(HOME_GALLERY_IMAGES[0], "Coffee quality and recommendations", "story-media compact")}
                <h3>Explainable matching</h3>
                <p class="lead">Recommendations are tied back to region, process, notes, readiness, and commercial constraints instead of black-box suggestions.</p>
              </div>
              <div class="card soft-card">
                ${mediaFrame(HOME_GALLERY_IMAGES[3], "Estate storytelling and supplier trust", "story-media compact")}
                <h3>Supplier trust signals</h3>
                <p class="lead">Supplier photos, reviews, certifications, and readiness fields make first contact feel much more credible.</p>
              </div>
            </div>
          </div>
        </section>
      </main>
      ${footer()}
    </div>
  `;
  bindGlobalActions();
}

function renderAuthPage(pathname, flashMessage = "") {
  const user = currentUser();
  app.innerHTML = `
    <div class="shell">
      ${nav(pathname)}
      <main class="section">
        <div class="section-head">
          <div>
            <h1 class="page-title">Sign In or Start Signup</h1>
            <p class="lead">Buyers and suppliers can start signup here, then complete their role-specific onboarding. Admin access is sign-in only.</p>
          </div>
        </div>
        <div class="detail-layout">
          <section class="panel">
            ${flashMessage ? `<div class="success-banner">${flashMessage}</div>` : ""}
            ${user ? `
              <div class="callout">
                <strong>Signed in as ${user.display_name || user.email}</strong><br>
                Role: ${user.role}
              </div>
              <div class="actions">
                <a class="button" href="${workspacePathForUser(user)}">Go to your workspace</a>
              </div>
            ` : `
              <div id="auth-error" class="error-banner hidden"></div>
              <form id="signin-form" class="form-grid">
                <label>Email or Demo Username<input class="input" name="email" type="text" required /></label>
                <label>Password<input class="input" name="password" type="password" required /></label>
                <div class="actions">
                  <button class="button" type="submit">Sign In</button>
                </div>
              </form>
              <div class="section-head" style="margin-top:24px;">
                <div>
                  <h3>Start Signup</h3>
                  <p class="lead">Choose the role you want to create. Admin signup is intentionally disabled.</p>
                </div>
              </div>
              <div class="grid-3">
                <div class="card">
                  <h3>Buyer</h3>
                  <p class="lead">Create a buyer account, then complete your sourcing profile and recommendation survey.</p>
                  <a class="button" href="/buyer-preferences?signup=buyer">Sign Up as Buyer</a>
                </div>
                <div class="card">
                  <h3>Supplier</h3>
                  <p class="lead">Create a supplier account, then complete export, sample, and compliance onboarding.</p>
                  <a class="button" href="/supplier-onboarding?signup=supplier">Sign Up as Supplier</a>
                </div>
              </div>
            `}
          </section>
          <aside class="panel sticky">
            <h3>Local Demo Credentials</h3>
            <div class="kpi"><span>Admin email</span><strong>admin@beanai.local</strong></div>
            <div class="kpi"><span>Admin username</span><strong>admin</strong></div>
            <div class="kpi"><span>Admin password</span><strong>Admin123!</strong></div>
            <div class="kpi"><span>Buyer email</span><strong>buyer.demo@beanai.local</strong></div>
            <div class="kpi"><span>Buyer username</span><strong>buyer-demo</strong></div>
            <div class="kpi"><span>Buyer password</span><strong>DemoBuyer123!</strong></div>
            <div class="kpi"><span>Supplier email</span><strong>supplier.demo@beanai.local</strong></div>
            <div class="kpi"><span>Supplier username</span><strong>supplier-demo</strong></div>
            <div class="kpi"><span>Supplier password</span><strong>DemoSupplier123!</strong></div>
            <div class="callout" style="margin-top:18px;">
              Sign-in is email-based in the real product, but the local demo also accepts the three short usernames above for convenience.
            </div>
          </aside>
        </div>
      </main>
      ${footer()}
    </div>
  `;

  bindGlobalActions();
  const form = document.getElementById("signin-form");
  if (form) {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const error = document.getElementById("auth-error");
      error.classList.add("hidden");
      const formData = new FormData(form);
      const response = await fetch("/api/auth/signin", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: formData.get("email"),
          password: formData.get("password"),
        }),
      });
      const result = await response.json();
      if (!response.ok) {
        error.textContent = result.error || "Could not sign in.";
        error.classList.remove("hidden");
        return;
      }
      await refreshBootstrap();
      window.location.href = workspacePathForUser(state.bootstrap.currentUser);
    });
  }
}

function renderAccessGate(pathname, title, description) {
  app.innerHTML = `
    <div class="shell">
      ${nav(pathname)}
      <main class="section">
        <div class="panel">
          <h1 class="page-title">${title}</h1>
          <p class="lead">${description}</p>
          <div class="actions">
            <a class="button" href="/auth">Go to Auth</a>
          </div>
        </div>
      </main>
      ${footer()}
    </div>
  `;
  bindGlobalActions();
}

function renderBuyerPreferences(pathname, flashMessage = "") {
  const user = currentUser();
  const signupMode = currentParams().get("signup") === "buyer";
  if (!signupMode && user?.role !== "buyer") {
    return renderAccessGate(pathname, "Buyer Workspace", "Sign in as a buyer to manage buyer onboarding, see buyer reviews, and unlock personalized recommendations.");
  }
  const buyer = state.bootstrap.buyerProfile || state.bootstrap.recommendationContextBuyer;
  const matching = state.bootstrap.recommendations || [];
  const reviews = state.bootstrap.buyerReviews || [];
  const changeRequests = state.bootstrap.profileChangeRequests || [];
  const surveyRequired = state.bootstrap.surveyRequired;
  const recommendationMode = state.bootstrap.recommendationMode;
  const isEditing = user?.role === "buyer" && !signupMode;
  app.innerHTML = `
    <div class="shell">
      ${nav(pathname)}
      <main class="section">
        <div class="section-head">
          <div>
            <h1 class="page-title">${signupMode ? "Buyer Signup" : "Buyer Workspace"}</h1>
            <p class="lead">${signupMode ? "Create a buyer account first. After signup, the buyer will see default recommendations and get a survey popup to unlock more personalized matches." : "Buyer onboarding is now role-gated. This workspace shows the buyer profile, buyer reviews, and recommendation status."}</p>
          </div>
        </div>
        <div class="detail-layout">
          <section>
            <div id="buyer-success" class="success-banner ${flashMessage ? "" : "hidden"}">${flashMessage}</div>
            <div id="buyer-error" class="error-banner hidden"></div>
            <form id="buyer-form">
              ${onboardingSection("Buyer Identity", "Capture the organization and destination market so the platform can apply the right logistics and compliance assumptions. Company name, contact email, and buyer type are locked after onboarding and cannot be self-edited later.", `
                <div class="form-grid two">
                  <label>Company Name<input class="input" name="companyName" value="${buyer?.company_name || ""}" ${isEditing ? "readonly" : ""} required /></label>
                  <label>Contact Name<input class="input" name="contactName" value="${buyer?.contact_name || ""}" /></label>
                  <label>Contact Email<input class="input" name="contactEmail" type="email" value="${buyer?.contact_email || user?.email || ""}" ${isEditing ? "readonly" : ""} required /></label>
                  <label>Buyer Type<select class="select" name="buyerType" ${isEditing ? "disabled" : ""} required><option value="">Select type</option><option value="roaster" ${buyer?.buyer_type === "roaster" ? "selected" : ""}>Roaster</option><option value="cafe" ${buyer?.buyer_type === "cafe" ? "selected" : ""}>Cafe</option><option value="importer" ${buyer?.buyer_type === "importer" ? "selected" : ""}>Importer</option><option value="distributor" ${buyer?.buyer_type === "distributor" ? "selected" : ""}>Distributor</option></select></label>
                  <label>Destination Country<select class="select" name="destinationCountry" required><option value="">Select destination</option><option value="US" ${buyer?.destination_country === "US" ? "selected" : ""}>United States</option><option value="EU" ${buyer?.destination_country === "EU" ? "selected" : ""}>European Union</option></select></label>
                  <label><input type="checkbox" name="needsUsComplianceSupport" ${buyer?.needs_us_compliance_support ? "checked" : ""} /> Needs compliance support guidance</label>
                </div>
                ${isEditing ? '<div class="callout" style="margin-top:14px;"><strong>Approval workflow</strong><br>Editable buyer changes are sent for approval before they touch the live buyer record.</div>' : ""}
              `)}
              ${onboardingSection("Preference Baseline", "These fields are saved on the buyer record, while the popup survey is what unlocks the larger personalized recommendation set.", `
                <div class="form-grid two">
                  <label>Preferred Regions<input class="input" name="preferredRegions" value="${csvValue(buyer?.preferred_regions).replaceAll('"', "&quot;")}" placeholder="Coorg, Karnataka, Bababudangiri, Karnataka" /></label>
                  <label>Preferred Varietals<input class="input" name="preferredVarietals" value="${csvValue(buyer?.preferred_varietals).replaceAll('"', "&quot;")}" placeholder="Selection 795, SLN9" /></label>
                  <label>Preferred Processes<input class="input" name="preferredProcesses" value="${csvValue(buyer?.preferred_processes).replaceAll('"', "&quot;")}" placeholder="Washed, Natural" /></label>
                  <label>Target Tasting Notes<input class="input" name="targetTastingNotes" value="${csvValue(buyer?.target_tasting_notes).replaceAll('"', "&quot;")}" placeholder="citrus, stone fruit, cacao" /></label>
                  <label>Preferred Certifications<input class="input" name="preferredCertifications" value="${csvValue(buyer?.preferred_certifications).replaceAll('"', "&quot;")}" placeholder="Organic, Rainforest Alliance" /></label>
                  <label>Preferred Couriers<input class="input" name="preferredCouriers" value="${csvValue(buyer?.preferred_couriers).replaceAll('"', "&quot;")}" placeholder="DHL, UPS" /></label>
                  <label>Minimum MOQ (kg)<input class="input" name="minMoqKg" type="number" value="${buyer?.min_moq_kg || ""}" /></label>
                  <label>Maximum MOQ (kg)<input class="input" name="maxMoqKg" type="number" value="${buyer?.max_moq_kg || ""}" /></label>
                  <label>Maximum Price Per Kg<input class="input" name="maxPricePerKg" type="number" step="0.01" value="${buyer?.max_price_per_kg || ""}" /></label>
                  <label><input type="checkbox" name="requiresSamples" ${buyer?.requires_samples !== false ? "checked" : ""} /> Requires samples before purchasing</label>
                </div>
              `)}
              ${signupMode ? onboardingSection("Account Access", "Create a linked buyer account so this organization can sign in, get default recommendations immediately, and submit the survey popup to unlock more.", `
                <div class="form-grid two">
                  <label>Password<input class="input" name="password" type="password" required /></label>
                  <label>Confirm Password<input class="input" name="confirmPassword" type="password" required /></label>
                </div>
              `) : ""}
              <div class="actions">
                <button class="button" type="submit">${signupMode ? "Create Buyer" : "Submit Buyer Change Request"}</button>
                <a class="button-secondary" href="/catalog">View Catalog</a>
                ${user?.role === "buyer" && surveyRequired ? '<button class="button-secondary" type="button" id="open-survey-manual">Open Recommendation Survey</button>' : ""}
              </div>
            </form>
            ${user && user.role === "buyer" ? `
              <div class="panel" style="margin-top:18px;">
                <h3>Buyer Reputation</h3>
                ${renderStars(buyer?.average_rating, buyer?.review_count)}
                <p class="lead">${surveyRequired ? "This buyer is still using default recommendations. Complete the survey popup to unlock more personalized matches." : "This buyer has completed the recommendation survey and now gets the full personalized recommendation set."}</p>
              </div>
            ` : ""}
            <div class="panel" style="margin-top:18px;">
              <h3>Buyer Reviews</h3>
              ${renderReviewCards(reviews, "No buyer reviews yet. Supplier-side reviews will appear here once counterparties start leaving feedback.")}
            </div>
            ${isEditing ? `
              <div class="panel" style="margin-top:18px;">
                <h3>Pending Buyer Change Requests</h3>
                ${renderChangeRequestList(changeRequests, "No buyer change requests submitted yet.")}
              </div>
            ` : ""}
          </section>
          <aside class="panel sticky">
            <h3>Recommendation Status</h3>
            <div class="callout">
              <strong>${recommendationMode === "personalized" ? "Personalized mode" : "Default mode"}</strong><br>
              ${recommendationMode === "personalized" ? "Recommendations are now using the buyer survey plus profile data." : "The buyer is seeing default, trust-first recommendations until the survey is completed."}
            </div>
            ${buyer ? `
              <div class="panel" style="margin-top:18px; padding:0; border:none; box-shadow:none; background:transparent;">
                <h3>Current Recommendation Preview</h3>
              ${matching.map((rec) => `
                  <div class="recommendation-card" style="margin-bottom:12px;">
                    ${mediaFrame(coffeeImageFor(rec), `${rec.lot_name} preview`, "recommendation-media")}
                    <div class="recommendation-score">Fit score ${Math.round(rec.recommendation_score * 100)}%</div>
                    <strong>${rec.lot_name}</strong>
                    <p>${rec.recommendation_reason}</p>
                  </div>
                `).join("") || '<p class="lead">No live recommendations yet for this buyer.</p>'}
              </div>
            ` : ""}
          </aside>
        </div>
      </main>
      ${footer()}
    </div>
  `;
  bindGlobalActions();

  const openSurvey = document.getElementById("open-survey-manual");
  if (openSurvey) {
    openSurvey.addEventListener("click", () => {
      sessionStorage.removeItem(`survey-dismissed:${currentUser().id}`);
      const existing = document.getElementById("survey-modal");
      if (existing) existing.remove();
      bindSurveyModal();
    });
  }

  const form = document.getElementById("buyer-form");
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const success = document.getElementById("buyer-success");
    const error = document.getElementById("buyer-error");
    success.classList.add("hidden");
    error.classList.add("hidden");

    const formData = new FormData(form);
    if (signupMode && formData.get("password") !== formData.get("confirmPassword")) {
      error.textContent = "Passwords do not match.";
      error.classList.remove("hidden");
      return;
    }
    const payload = {
      id: buyer?.id || undefined,
      companyName: isEditing ? buyer?.company_name : formData.get("companyName"),
      contactName: formData.get("contactName"),
      contactEmail: isEditing ? buyer?.contact_email : formData.get("contactEmail"),
      buyerType: isEditing ? buyer?.buyer_type : formData.get("buyerType"),
      destinationCountry: formData.get("destinationCountry"),
      preferredRegions: parseCsv(formData.get("preferredRegions")),
      preferredVarietals: parseCsv(formData.get("preferredVarietals")),
      preferredProcesses: parseCsv(formData.get("preferredProcesses")),
      targetTastingNotes: parseCsv(formData.get("targetTastingNotes")),
      preferredCertifications: parseCsv(formData.get("preferredCertifications")),
      minMoqKg: formData.get("minMoqKg") ? Number(formData.get("minMoqKg")) : null,
      maxMoqKg: formData.get("maxMoqKg") ? Number(formData.get("maxMoqKg")) : null,
      maxPricePerKg: formData.get("maxPricePerKg") ? Number(formData.get("maxPricePerKg")) : null,
      requiresSamples: formData.get("requiresSamples") === "on",
      preferredCouriers: parseCsv(formData.get("preferredCouriers")),
      needsUsComplianceSupport: formData.get("needsUsComplianceSupport") === "on",
      password: signupMode ? formData.get("password") : null,
    };

    const endpoint = signupMode ? "/api/buyers" : "/api/buyers/update-request";
    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (!response.ok) {
      error.textContent = result.error || "Could not save buyer.";
      error.classList.remove("hidden");
      return;
    }

    await refreshBootstrap();
    const flashMessage = signupMode
      ? `
      Buyer <strong>${result.companyName}</strong> saved in Supabase with id <strong>${result.id}</strong>.
      Type: <strong>${result.buyerType}</strong>.
      Destination: <strong>${result.destinationCountry}</strong>.
    `
      : `
      Buyer change request <strong>${result.id}</strong> submitted for approval.
      Changed fields: <strong>${(result.changedFields || []).join(", ")}</strong>.
    `;
    if (signupMode) {
      form.reset();
    }
    if (signupMode) {
      window.history.replaceState({}, "", "/buyer-preferences");
    }
    renderBuyerPreferences("/buyer-preferences", flashMessage);
  });
}

function renderCatalog(pathname) {
  const lots = state.bootstrap.lots;
  const recs = state.bootstrap.recommendations;
  const surveyRequired = state.bootstrap.surveyRequired;
  const recommendationMode = state.bootstrap.recommendationMode;
  const user = currentUser();
  app.innerHTML = `
    <div class="shell">
      ${nav(pathname)}
      <main class="section">
        <div class="section-head">
          <div>
            <h1 class="page-title">Coffee Catalog</h1>
            <p class="lead">${recommendationMode === "personalized" ? "The catalog is showing the larger personalized recommendation set for this buyer." : "The catalog is showing default recommendations for first-time or anonymous users. Buyers unlock more relevant matches after the recommendation survey popup is completed."}</p>
          </div>
        </div>
        <div class="catalog-layout">
          <aside class="panel sticky">
            <h3>Filters</h3>
            <label>Search<input id="catalog-search" class="input" placeholder="Search lots or suppliers" /></label>
            <label>Region<select id="catalog-region" class="select"><option value="">All regions</option><option value="Bababudangiri, Karnataka">Bababudangiri</option><option value="Coorg, Karnataka">Coorg</option></select></label>
            <div class="callout">
              <strong>Recommendation rule</strong><br>
              Non-compliant or non-ready lots should never outrank lower-risk alternatives.
            </div>
            ${user?.role === "buyer" && surveyRequired ? `
              <div class="callout" style="margin-top:18px;">
                <strong>Survey pending</strong><br>
                Complete the recommendation survey to move from default recommendations to a fuller personalized feed.
              </div>
            ` : ""}
          </aside>
          <section>
            <div class="recommendation-rail">
              ${recs.map((rec) => `
                <div class="recommendation-card" data-lot-id="${rec.lot_id}">
                  ${mediaFrame(coffeeImageFor(rec), `${rec.lot_name} recommendation`, "recommendation-media")}
                  <div class="recommendation-score">Recommended</div>
                  <strong>${rec.lot_name}</strong>
                  <p>${rec.recommendation_reason}</p>
                  <a class="button-ghost" href="/coffee/${rec.lot_id}" data-lot-id="${rec.lot_id}" data-track-type="recommendation_click" data-source-surface="catalog_recommendation">See fit details</a>
                </div>
              `).join("")}
            </div>
            <div id="catalog-results" class="catalog-grid grid-3">
              ${lots.map((lot) => lotCard(lot)).join("")}
            </div>
          </section>
        </div>
      </main>
      ${footer()}
    </div>
  `;
  bindGlobalActions();
  const search = document.getElementById("catalog-search");
  const region = document.getElementById("catalog-region");
  const results = document.getElementById("catalog-results");
  const renderResults = () => {
    const q = search.value.trim().toLowerCase();
    const r = region.value;
    const filtered = lots.filter((lot) => {
      const matchesQ = !q || lot.lot_name.toLowerCase().includes(q) || lot.supplier_name.toLowerCase().includes(q);
      const matchesR = !r || lot.region === r;
      return matchesQ && matchesR;
    });
    results.innerHTML = filtered.map((lot) => {
      const rec = recs.find((entry) => entry.lot_id === lot.id);
      return lotCard(lot, rec ? rec.recommendation_reason : "");
    }).join("");
  };
  search.addEventListener("input", renderResults);
  region.addEventListener("change", renderResults);
}

async function renderCoffeeDetail(pathname) {
  const lotId = pathname.split("/").pop();
  const data = await fetch(`/api/lots/${lotId}`).then((r) => r.json());
  state.lotDetail = data;
  const lot = data.lot;
  const similar = data.similar;
  const supplierReviews = data.supplierReviews || [];
  const canReviewSupplier = data.canReviewSupplier;
  const rec = state.bootstrap.recommendations.find((entry) => entry.lot_id === lot.id);
  const user = currentUser();
  const requestReady = lot.sample_ready && lot.export_ready && lot.compliance_ready;
  app.innerHTML = `
    <div class="shell">
      ${nav(pathname)}
      <main class="section">
        <div class="section-head">
          <div>
            <a href="/catalog" class="button-ghost">Back to Catalog</a>
            <h1 class="page-title" style="margin-top:14px;">${lot.lot_name}</h1>
            <p class="lead">${lot.supplier_name} · ${lot.region} · ${lot.process}</p>
          </div>
        </div>
        <div class="detail-layout">
          <section class="panel">
            <div class="detail-media-grid">
              ${mediaFrame(coffeeImageFor(lot), `${lot.lot_name} coffee`, "detail-media")}
              ${mediaFrame(estateImageFor(lot), `${lot.supplier_name} estate`, "detail-media")}
            </div>
            <div class="grid-3">
              <div class="card"><strong>Altitude</strong><div>${lot.altitude_meters || "TBD"}m</div></div>
              <div class="card"><strong>Harvest</strong><div>${lot.harvest_year || "TBD"}</div></div>
              <div class="card"><strong>Price</strong><div>$${lot.price_per_kg || "TBD"}/kg</div></div>
            </div>
            <div class="panel" style="margin-top:18px;">
              <h3>Logistics and Compliance</h3>
              ${renderStars(lot.supplier_average_rating, lot.supplier_review_count)}
              <div class="kpi"><span>Export Ready</span><strong>${lot.export_ready ? "Yes" : "No"}</strong></div>
              <div class="kpi"><span>Ships Samples</span><strong>${lot.sample_ready ? "Yes" : "No"}</strong></div>
              <div class="kpi"><span>Sample Size</span><strong>${lot.sample_size_grams || "TBD"}g</strong></div>
              <div class="kpi"><span>Courier</span><strong>${(lot.sample_couriers || []).join(", ") || "TBD"}</strong></div>
              <div class="kpi"><span>Prep + shipping</span><strong>${lot.sample_prep_days || "?"} + ${lot.sample_shipping_days || "?"} days</strong></div>
              <div class="kpi"><span>Prior Notice</span><strong>${lot.prior_notice_handler || "Unassigned"}</strong></div>
            </div>
            ${rec ? `
              <div class="panel" style="margin-top:18px;">
                <h3>Why This Matches You</h3>
                <div class="callout">${rec.recommendation_reason}</div>
              </div>
            ` : ""}
            <div class="panel" style="margin-top:18px;">
              <h3>Similar Lots</h3>
              <div class="grid-3">
                ${similar.map((item) => `
                  <div class="card">
                    ${mediaFrame(coffeeImageFor(item), `${item.lot_name} similar lot`, "card-media")}
                    <strong>${item.lot_name}</strong>
                    <p>${item.supplier_name}</p>
                    <p>${item.region} · ${item.process} · Cup ${item.cup_score || "TBD"}</p>
                    <a class="button-ghost" href="/coffee/${item.id}" data-lot-id="${item.id}" data-track-type="similar_lot_click" data-source-surface="similar_lots">View</a>
                  </div>
                `).join("")}
              </div>
            </div>
            <div class="panel" style="margin-top:18px;">
              <h3>Supplier Reviews</h3>
              ${renderReviewCards(supplierReviews, "No supplier reviews yet. Buyer feedback will appear here once samples and sourcing conversations start happening.")}
            </div>
          </section>
          <aside class="panel sticky">
            <h3>Request Sample</h3>
            <div class="callout">
              <strong>US-bound shipments:</strong><br>
              Prior Notice is required and ownership must be explicit before shipping.
            </div>
            <div class="kpi"><span>Sample price</span><strong>$${lot.sample_price || "TBD"}</strong></div>
            <div class="kpi"><span>Shipping paid by</span><strong>${lot.sample_shipping_paid_by || "TBD"}</strong></div>
            <div class="kpi"><span>Recommendation source</span><strong>${rec ? "Recommended surface" : "Catalog browse"}</strong></div>
            ${
              user && user.role === "buyer" && requestReady
                ? `
                <div id="inquiry-success" class="success-banner hidden"></div>
                <div id="inquiry-error" class="error-banner hidden"></div>
                <form id="sample-request-form" class="form-grid">
                  <label>Destination Country<select class="select" name="destinationCountry"><option value="US" ${user.destination_country === "US" ? "selected" : ""}>United States</option><option value="EU" ${user.destination_country === "EU" ? "selected" : ""}>European Union</option></select></label>
                  <label>Requested Sample (grams)<input class="input" name="requestedSampleGrams" type="number" value="${lot.sample_size_grams || ""}" /></label>
                  <label>Message to Supplier<textarea class="textarea" name="message" placeholder="Tell the supplier what you want to evaluate in the sample."></textarea></label>
                  <button class="button" type="submit">Submit Live Sample Request</button>
                </form>
                ${canReviewSupplier ? `
                  <div id="supplier-review-success" class="success-banner hidden" style="margin-top:18px;"></div>
                  <div id="supplier-review-error" class="error-banner hidden"></div>
                  <form id="supplier-review-form" class="form-grid" style="margin-top:18px;">
                    <label>Rate This Supplier
                      <select class="select" name="rating" required>
                        <option value="">Select stars</option>
                        <option value="5">5 stars</option>
                        <option value="4">4 stars</option>
                        <option value="3">3 stars</option>
                        <option value="2">2 stars</option>
                        <option value="1">1 star</option>
                      </select>
                    </label>
                    <label>Review<textarea class="textarea" name="reviewText" placeholder="How was communication, sample handling, and export readiness?"></textarea></label>
                    <button class="button-secondary" type="submit">Leave Supplier Review</button>
                  </form>
                ` : `
                  <div class="callout" style="margin-top:18px;">
                    <strong>Review locked</strong><br>
                    Supplier reviews unlock after a completed purchase relationship is recorded.
                  </div>
                `}
              `
                : user && user.role === "buyer"
                ? `
                <div class="callout" style="margin-top:18px;">
                  <strong>Request not available yet</strong><br>
                  This lot is still missing export, sample, or compliance readiness, so buyers cannot submit live requests until the supplier closes those gaps.
                </div>
                `
                : `
                <div class="callout" style="margin-top:18px;">
                  <strong>Buyer sign-in required</strong><br>
                  Sign in as a buyer to submit a live sample request into the <code>buyer_inquiries</code> table.
                </div>
                <div class="actions">
                  <a class="button" href="/auth">Sign In</a>
                </div>
              `
            }
            <div class="actions">
              <a class="button-secondary" href="/inquiries">Track live inquiries</a>
            </div>
          </aside>
        </div>
      </main>
      ${footer()}
    </div>
  `;
  bindGlobalActions();
  if (user && user.role === "buyer") {
    trackInteraction(lotId, "lot_view", rec ? "recommended_detail" : "catalog_detail");
  }
  const form = document.getElementById("sample-request-form");
  if (form) {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const success = document.getElementById("inquiry-success");
      const error = document.getElementById("inquiry-error");
      success.classList.add("hidden");
      error.classList.add("hidden");
      const formData = new FormData(form);
      const { response, result } = await postJson("/api/inquiries", {
          lotId,
          destinationCountry: formData.get("destinationCountry"),
          requestedSampleGrams: formData.get("requestedSampleGrams") ? Number(formData.get("requestedSampleGrams")) : null,
          message: formData.get("message"),
          sourceSurface: rec ? "recommended_detail" : "catalog_detail",
      });
      if (!response.ok) {
        error.textContent = result.error || "Could not submit request.";
        error.classList.remove("hidden");
        return;
      }
      await refreshBootstrap();
      success.innerHTML = `
        Live inquiry <strong>${result.id}</strong> created with status <strong>${result.shipmentStatus}</strong>.
        Prior Notice required: <strong>${result.priorNoticeRequired ? "Yes" : "No"}</strong>.
      `;
      success.classList.remove("hidden");
      form.reset();
    });
  }
  const reviewForm = document.getElementById("supplier-review-form");
  if (reviewForm) {
    reviewForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const success = document.getElementById("supplier-review-success");
      const error = document.getElementById("supplier-review-error");
      success.classList.add("hidden");
      error.classList.add("hidden");
      const formData = new FormData(reviewForm);
      const { response, result } = await postJson("/api/supplier-reviews", {
        supplierId: lot.supplier_id,
        rating: Number(formData.get("rating")),
        reviewText: formData.get("reviewText"),
      });
      if (!response.ok) {
        error.textContent = result.error || "Could not save supplier review.";
        error.classList.remove("hidden");
        return;
      }
      await refreshBootstrap();
      success.textContent = "Supplier review saved.";
      success.classList.remove("hidden");
      renderCoffeeDetail(pathname);
    });
  }
}

function renderInquiryTracking(pathname) {
  const inquiries = state.bootstrap.inquiries;
  const user = currentUser();
  const uniqueBuyers = user?.role === "supplier"
    ? Array.from(new Map(inquiries.filter((inquiry) => inquiry.shipment_status === "closed").map((inquiry) => [inquiry.buyer_id, inquiry])).values())
    : [];
  app.innerHTML = `
    <div class="shell">
      ${nav(pathname)}
      <main class="section">
        <div class="section-head">
          <div>
            <h1 class="page-title">Buyer Inquiry Tracking</h1>
            <p class="lead">${user ? "This view now shows live inquiry records scoped to the signed-in role." : "Sign in as a buyer, supplier, or admin to see live inquiry records from Supabase."}</p>
          </div>
        </div>
        ${user ? `
        <div id="inquiry-action-banner" class="success-banner hidden"></div>
        <div id="inquiry-action-error" class="error-banner hidden"></div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Buyer</th>
                <th>Supplier</th>
                <th>Lot</th>
                <th>Status</th>
                <th>Courier</th>
                <th>Tracking</th>
                <th>Prior Notice</th>
                ${user.role === "supplier" || user.role === "buyer" ? "<th>Action</th>" : ""}
              </tr>
            </thead>
            <tbody>
              ${inquiries.map((inquiry) => `
                <tr>
                  <td style="font-size:11px;color:#888">${inquiry.id}</td>
                  <td>${inquiry.buyer_name}</td>
                  <td>${inquiry.supplier_name}</td>
                  <td>${inquiry.lot_name}</td>
                  <td><span class="badge ${inquiry.shipment_status.includes("pending") ? "warn" : "muted"}">${inquiry.shipment_status}</span></td>
                  <td>${inquiry.courier || "-"}</td>
                  <td>${inquiry.tracking_number || "-"}</td>
                  <td>${inquiry.prior_notice_filed ? `Filed by ${inquiry.prior_notice_filed_by}` : `Pending (${inquiry.prior_notice_filed_by || "unassigned"})`}</td>
                  ${user.role === "supplier" || user.role === "buyer" ? `<td>${roleShipmentButtons(inquiry, user.role)}</td>` : ""}
                </tr>
              `).join("")}
            </tbody>
          </table>
        </div>
        ${user.role === "supplier" ? `
          <div class="panel" style="margin-top:18px;">
            <h3>Review Buyers You Worked With</h3>
            <div id="buyer-review-success" class="success-banner hidden"></div>
            <div id="buyer-review-error" class="error-banner hidden"></div>
            <div class="grid-3">
              ${uniqueBuyers.map((buyer) => `
                <form class="card buyer-review-form" data-buyer-id="${buyer.buyer_id}">
                  <strong>${buyer.buyer_name}</strong>
                  ${renderStars(buyer.buyer_average_rating, buyer.buyer_review_count)}
                  <label>Stars
                    <select class="select" name="rating" required>
                      <option value="">Select stars</option>
                      <option value="5">5 stars</option>
                      <option value="4">4 stars</option>
                      <option value="3">3 stars</option>
                      <option value="2">2 stars</option>
                      <option value="1">1 star</option>
                    </select>
                  </label>
                  <label>Review<textarea class="textarea" name="reviewText" placeholder="How was buyer responsiveness and evaluation clarity?"></textarea></label>
                  <button class="button-secondary" type="submit">Save Buyer Review</button>
                </form>
              `).join("") || '<p class="lead">Buyer reviews unlock after a closed relationship is recorded for this supplier.</p>'}
            </div>
          </div>
        ` : ""}
        ` : `
          <div class="panel">
            <div class="callout">
              <strong>Authentication required</strong><br>
              Sign in to see inquiry records relevant to your role.
            </div>
            <div class="actions">
              <a class="button" href="/auth">Sign In</a>
            </div>
          </div>
        `}
      </main>
      ${footer()}
    </div>
  `;
  bindGlobalActions();

  // Wire supplier/buyer shipment action buttons
  document.querySelectorAll(".role-shipment-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const inquiryId = btn.dataset.inquiryId;
      const newStatus = btn.dataset.status;
      const banner = document.getElementById("inquiry-action-banner");
      const errorEl = document.getElementById("inquiry-action-error");
      btn.disabled = true;
      btn.textContent = "Saving…";
      const payload = { shipmentStatus: newStatus };
      if (newStatus === "shipped") {
        payload.courier = prompt("Enter courier name (e.g. FedEx, DHL):") || "TBD";
        payload.trackingNumber = prompt("Enter tracking number:") || "TBD";
      }
      const { response, result } = await patchJson(`/api/inquiries/${inquiryId}/shipment`, payload);
      if (response.ok) {
        banner.textContent = `Inquiry updated → ${newStatus}`;
        banner.classList.remove("hidden");
        errorEl.classList.add("hidden");
        await refreshBootstrap();
        renderInquiryTracking(pathname);
      } else {
        errorEl.textContent = result?.detail || "Error updating shipment status";
        errorEl.classList.remove("hidden");
        banner.classList.add("hidden");
        btn.disabled = false;
        btn.textContent = newStatus;
      }
    });
  });

  document.querySelectorAll(".buyer-review-form").forEach((form) => {
    if (form.dataset.bound === "true") return;
    form.dataset.bound = "true";
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const success = document.getElementById("buyer-review-success");
      const error = document.getElementById("buyer-review-error");
      success.classList.add("hidden");
      error.classList.add("hidden");
      const formData = new FormData(form);
      const { response, result } = await postJson("/api/buyer-reviews", {
        buyerId: form.dataset.buyerId,
        rating: Number(formData.get("rating")),
        reviewText: formData.get("reviewText"),
      });
      if (!response.ok) {
        error.textContent = result.error || "Could not save buyer review.";
        error.classList.remove("hidden");
        return;
      }
      await refreshBootstrap();
      success.textContent = "Buyer review saved.";
      success.classList.remove("hidden");
      renderInquiryTracking(pathname);
    });
  });
}

// Returns action buttons for supplier/buyer roles based on valid transitions
function roleShipmentButtons(inq, role) {
  const supplierTransitions = {
    approved:             [{ status: "sample_preparing", label: "Start Sample Prep" }],
    sample_preparing:     [{ status: "prior_notice_pending", label: "Prior Notice Pending" }, { status: "shipped", label: "Mark Shipped" }],
    prior_notice_pending: [{ status: "shipped", label: "Mark Shipped" }],
  };
  const buyerTransitions = {
    shipped:   [{ status: "delivered", label: "Confirm Delivered" }],
    delivered: [{ status: "closed", label: "Close Deal" }],
  };
  const actions = (role === "supplier" ? supplierTransitions : buyerTransitions)[inq.shipment_status] || [];
  if (!actions.length) return '<span class="lead">—</span>';
  return actions.map((a) =>
    `<button class="button-secondary role-shipment-btn" style="font-size:12px;padding:4px 10px;margin-right:4px"
       data-inquiry-id="${inq.id}" data-status="${a.status}">${a.label}</button>`
  ).join("");
}

// Returns action buttons for each valid admin transition from the current status
function adminShipmentButtons(inq) {
  const transitions = {
    new:                    [{ status: "approved", label: "Approve" }, { status: "closed", label: "Close" }],
    approved:               [{ status: "sample_preparing", label: "Mark Sample Preparing" }],
    sample_preparing:       [{ status: "prior_notice_pending", label: "Prior Notice Pending" }, { status: "shipped", label: "Mark Shipped" }],
    prior_notice_pending:   [{ status: "shipped", label: "Mark Shipped" }],
    shipped:                [{ status: "delivered", label: "Mark Delivered" }],
    delivered:              [{ status: "closed", label: "Close Deal" }],
    closed:                 [],
  };
  const actions = transitions[inq.shipment_status] || [];
  if (!actions.length) return '<span class="lead">—</span>';
  return actions.map((a) =>
    `<button class="button-secondary admin-shipment-btn" style="margin-right:6px;font-size:12px;padding:4px 10px"
       data-inquiry-id="${inq.id}" data-status="${a.status}">${a.label}</button>`
  ).join("");
}

function renderAdmin(pathname) {
  const user = currentUser();
  if (!user || user.role !== "admin") {
    app.innerHTML = `
      <div class="shell">
        ${nav(pathname)}
        <main class="section">
          <div class="panel">
            <h1 class="page-title">Admin Access Required</h1>
            <p class="lead">Sign in as an admin to view supplier readiness, buyer profiles, inquiries, and platform metrics.</p>
            <div class="callout">
              <strong>Demo admin credentials</strong><br>
              admin@beanai.local / Admin123!
            </div>
            <div class="actions">
              <a class="button" href="/auth">Go to Sign In</a>
            </div>
          </div>
        </main>
        ${footer()}
      </div>
    `;
    bindGlobalActions();
    return;
  }
  const metrics = state.bootstrap.metrics;
  const suppliers = state.bootstrap.supplierReadiness;
  const recommendations = state.bootstrap.recommendations;
  const buyers = state.bootstrap.buyers;
  const changeRequests = state.bootstrap.profileChangeRequests || [];
  app.innerHTML = `
    <div class="shell">
      ${nav(pathname)}
      <main class="section admin-layout">
        <div class="section-head">
          <div>
            <h1 class="page-title">Admin Dashboard</h1>
            <p class="lead">The admin view now includes the missing recommendation analytics section alongside supplier readiness and inquiry operations.</p>
          </div>
        </div>
        <div class="metrics-grid">
          <div class="metric"><div class="metric-value">${metrics.supplier_count || 0}</div><div>Total Suppliers</div></div>
          <div class="metric"><div class="metric-value">${metrics.buyer_count || 0}</div><div>Total Buyers</div></div>
          <div class="metric"><div class="metric-value">${formatPercent(metrics.export_ready_pct)}</div><div>Suppliers Export-Ready</div></div>
          <div class="metric"><div class="metric-value">${formatPercent(metrics.sample_ready_pct)}</div><div>Suppliers Sample-Ready</div></div>
        </div>
        <div class="metrics-grid">
          <div class="metric"><div class="metric-value">${formatPercent(metrics.sample_to_shipment_pct)}</div><div>Sample → Shipment Rate</div></div>
          <div class="metric"><div class="metric-value">${formatPercent(metrics.recommendation_to_inquiry_pct)}</div><div>Recommendation → Inquiry Rate</div></div>
          <div class="metric"><div class="metric-value">${suppliers.filter((item) => item.approval_status === "approved").length}</div><div>Approved Suppliers</div></div>
          <div class="metric"><div class="metric-value">${buyers.filter((item) => item.requires_samples).length}</div><div>Buyers Requiring Samples</div></div>
        </div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Supplier</th><th>Region</th><th>Contact</th><th>Stars</th><th>Export Ready</th><th>Sample Ready</th><th>Compliance Ready</th><th>Status</th></tr></thead>
            <tbody>
              ${suppliers.map((supplier) => `
                <tr>
                  <td>${supplier.company_name}</td>
                  <td>${supplier.region}</td>
                  <td>${supplier.contact_name || "-"}<br><span class="lead">${supplier.contact_email || ""}</span></td>
                  <td>${renderStars(supplier.average_rating, supplier.review_count)}</td>
                  <td>${supplier.export_ready ? "Yes" : "No"}</td>
                  <td>${supplier.sample_ready ? "Yes" : "No"}</td>
                  <td>${supplier.compliance_ready ? "Yes" : "No"}</td>
                  <td>${supplier.approval_status}</td>
                </tr>
              `).join("")}
            </tbody>
          </table>
        </div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Buyer</th><th>Type</th><th>Destination</th><th>Stars</th><th>Survey</th><th>Preferred Regions</th><th>MOQ</th><th>Samples</th></tr></thead>
            <tbody>
              ${buyers.map((buyer) => `
                <tr>
                  <td>${buyer.company_name}<br><span class="lead">${buyer.contact_email || ""}</span></td>
                  <td>${buyer.buyer_type}</td>
                  <td>${buyer.destination_country}</td>
                  <td>${renderStars(buyer.average_rating, buyer.review_count)}</td>
                  <td>${buyer.survey_completed ? "Completed" : "Pending"}</td>
                  <td>${safeJoin(buyer.preferred_regions)}</td>
                  <td>${buyer.min_moq_kg || "-"} to ${buyer.max_moq_kg || "-"}</td>
                  <td>${buyer.requires_samples ? "Yes" : "No"}</td>
                </tr>
              `).join("")}
            </tbody>
          </table>
        </div>
        <div class="grid-3">
          <div class="panel">
            <h3>Top Recommendations</h3>
            ${recommendations.slice(0, 3).map((rec) => `
              <div class="kpi"><span>${rec.lot_name}</span><strong>${Math.round(rec.recommendation_score * 100)}%</strong></div>
            `).join("")}
          </div>
          <div class="panel">
            <h3>Design Gaps Closed</h3>
            <p>Added buyer preference onboarding, recommendation explanations, similar-lot modules, and recommendation analytics missing from the earlier handoff.</p>
          </div>
          <div class="panel">
            <h3>Suppression Logic</h3>
            <p>Lots with incomplete export, sample, or compliance readiness should be suppressed or demoted until gaps are resolved.</p>
          </div>
        </div>
        <div class="panel">
          <h3>Profile Change Requests</h3>
          <div id="admin-chgreq-banner" class="success-banner hidden"></div>
          <div id="admin-chgreq-error" class="error-banner hidden"></div>
          ${renderChangeRequestList(changeRequests, "No pending profile change requests right now.", true)}
        </div>
        <div class="panel">
          <h3>Inquiry Management</h3>
          <p class="lead">Approve, advance, or close inquiries. Actions available depend on the current shipment stage.</p>
          <div id="admin-inquiry-banner" class="success-banner hidden"></div>
          <div id="admin-inquiry-error" class="error-banner hidden"></div>
          ${state.bootstrap.inquiries && state.bootstrap.inquiries.length ? `
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Buyer</th>
                  <th>Supplier</th>
                  <th>Lot</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                ${state.bootstrap.inquiries.map((inq) => `
                  <tr>
                    <td style="font-size:11px;color:#888">${inq.id}</td>
                    <td>${inq.buyer_name}</td>
                    <td>${inq.supplier_name}</td>
                    <td>${inq.lot_name}</td>
                    <td><span class="badge ${inq.shipment_status === "new" ? "warn" : inq.shipment_status === "closed" ? "muted" : ""}">${inq.shipment_status}</span></td>
                    <td>${adminShipmentButtons(inq)}</td>
                  </tr>
                `).join("")}
              </tbody>
            </table>
          </div>
          ` : `<p class="lead">No inquiries yet.</p>`}
        </div>
      </main>
      ${footer()}
    </div>
  `;
  bindGlobalActions();

  // Wire up shipment action buttons
  document.querySelectorAll(".admin-shipment-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const inquiryId = btn.dataset.inquiryId;
      const newStatus = btn.dataset.status;
      const banner = document.getElementById("admin-inquiry-banner");
      const errorEl = document.getElementById("admin-inquiry-error");
      btn.disabled = true;
      btn.textContent = "Saving…";
      const payload = { shipmentStatus: newStatus };
      if (newStatus === "shipped") {
        payload.courier = "TBD";
        payload.trackingNumber = "TBD";
      }
      const { response, result } = await patchJson(`/api/inquiries/${inquiryId}/shipment`, payload);
      if (response.ok) {
        banner.textContent = `Inquiry ${inquiryId} → ${newStatus}`;
        banner.classList.remove("hidden");
        errorEl.classList.add("hidden");
        await refreshBootstrap();
        renderAdmin(window.location.pathname);
      } else {
        errorEl.textContent = result?.detail || `Error updating inquiry`;
        errorEl.classList.remove("hidden");
        banner.classList.add("hidden");
        btn.disabled = false;
        btn.textContent = newStatus;
      }
    });
  });

  // Wire up profile change request approve/deny buttons
  document.querySelectorAll(".admin-change-request-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const requestId = btn.dataset.requestId;
      const decision = btn.dataset.decision;
      const banner = document.getElementById("admin-chgreq-banner");
      const errorEl = document.getElementById("admin-chgreq-error");
      btn.disabled = true;
      btn.textContent = "Saving…";
      const { response, result } = await patchJson(`/api/profile-change-requests/${requestId}/decision`, { decision });
      if (response.ok) {
        banner.textContent = `Change request ${requestId} ${decision}.`;
        banner.classList.remove("hidden");
        errorEl.classList.add("hidden");
        await refreshBootstrap();
        renderAdmin(window.location.pathname);
      } else {
        errorEl.textContent = result?.detail || "Error processing change request";
        errorEl.classList.remove("hidden");
        banner.classList.add("hidden");
        btn.disabled = false;
        btn.textContent = decision === "approved" ? "✓ Approve" : "✗ Deny";
      }
    });
  });
}

function onboardingSection(title, description, content) {
  return `
    <section class="panel" style="margin-bottom:18px;">
      <h3>${title}</h3>
      <p class="lead">${description}</p>
      ${content}
    </section>
  `;
}

function renderSupplierOnboarding(pathname, flashMessage = "") {
  const user = currentUser();
  const signupMode = currentParams().get("signup") === "supplier";
  if (!signupMode && user?.role !== "supplier") {
    return renderAccessGate(pathname, "Supplier Workspace", "Sign in as a supplier to manage supplier onboarding, read supplier reviews, and handle buyer inquiry workflows.");
  }
  const supplier = state.bootstrap.supplierProfile;
  const reviews = state.bootstrap.supplierReviews || [];
  const changeRequests = state.bootstrap.profileChangeRequests || [];
  const isEditing = user?.role === "supplier" && !signupMode;
  app.innerHTML = `
    <div class="shell">
      ${nav(pathname)}
      <main class="section">
        <div class="section-head">
          <div>
            <h1 class="page-title">${signupMode ? "Supplier Signup" : "Supplier Workspace"}</h1>
            <p class="lead">${signupMode ? "Create a supplier account, then complete export, sample, and compliance onboarding." : "Supplier onboarding is role-gated now. This workspace lets suppliers update readiness data and see their star rating and reviews."}</p>
          </div>
        </div>
        <div class="split-layout">
          <aside class="panel sticky">
            <h3>Supplier Reputation</h3>
            ${supplier ? renderStars(supplier.average_rating, supplier.review_count) : '<p class="lead">New suppliers will build a rating once buyers start leaving feedback.</p>'}
            <div class="kpi"><span>1. Basic info</span><strong>Required</strong></div>
            <div class="kpi"><span>2. Estate info</span><strong>Improves ranking</strong></div>
            <div class="kpi"><span>3. Export readiness</span><strong>Approval gate</strong></div>
            <div class="kpi"><span>4. Sample shipping</span><strong>Approval gate</strong></div>
            <div class="kpi"><span>5. Compliance owner</span><strong>Approval gate</strong></div>
            <div class="callout" style="margin-top:18px;">
              <strong>Live database write</strong><br>
              This page sends data to the local Python server, which inserts into your Supabase database using the secure backend connection.
            </div>
          </aside>
          <section>
            <div id="form-success" class="success-banner ${flashMessage ? "" : "hidden"}">${flashMessage}</div>
            <div id="form-error" class="error-banner hidden"></div>
            <form id="supplier-form">
              ${onboardingSection("Basic Info", "Capture company identity and the core details buyers need to trust the supplier. Company name, contact email, and origin region are locked after onboarding and cannot be self-edited later.", `
                <div class="form-grid two">
                  <label>Company Name<input class="input" name="companyName" value="${supplier?.company_name || ""}" ${isEditing ? "readonly" : ""} required /></label>
                  <label>Contact Name<input class="input" name="contactName" value="${supplier?.contact_name || ""}" /></label>
                  <label>Contact Email<input class="input" name="contactEmail" type="email" value="${supplier?.contact_email || user?.email || ""}" ${isEditing ? "readonly" : ""} required /></label>
                  <label>Contact Phone<input class="input" name="contactPhone" value="${supplier?.contact_phone || ""}" /></label>
                  <label>Region<select class="select" name="region" ${isEditing ? "disabled" : ""} required><option value="">Select region</option><option value="Bababudangiri, Karnataka" ${supplier?.region === "Bababudangiri, Karnataka" ? "selected" : ""}>Bababudangiri</option><option value="Coorg, Karnataka" ${supplier?.region === "Coorg, Karnataka" ? "selected" : ""}>Coorg</option><option value="Chikmagalur, Karnataka" ${supplier?.region === "Chikmagalur, Karnataka" ? "selected" : ""}>Chikmagalur</option><option value="Wayanad, Kerala" ${supplier?.region === "Wayanad, Kerala" ? "selected" : ""}>Wayanad</option><option value="Araku Valley, Andhra Pradesh" ${supplier?.region === "Araku Valley, Andhra Pradesh" ? "selected" : ""}>Araku Valley</option></select></label>
                  <label>Website<input class="input" name="website" type="url" value="${supplier?.website || ""}" /></label>
                </div>
                ${isEditing ? '<div class="callout" style="margin-top:14px;"><strong>Approval workflow</strong><br>Editable supplier changes are submitted for review before they update the live supplier record.</div>' : ""}
              `)}
              ${onboardingSection("Estate Info", "Richer agronomic and storytelling fields improve catalog quality and future recommendation accuracy.", `
                <div class="form-grid two">
                  <label>Altitude (meters)<input class="input" name="altitudeMeters" type="number" value="${supplier?.altitude_meters || ""}" /></label>
                  <label>Varietals (comma separated)<input class="input" name="varietals" value="${csvValue(supplier?.varietals).replaceAll('"', "&quot;")}" placeholder="Selection 795, SLN9" /></label>
                  <label>Certifications (comma separated)<input class="input" name="certifications" value="${csvValue(supplier?.certifications).replaceAll('"', "&quot;")}" placeholder="Organic, Rainforest Alliance" /></label>
                  <label>Description<textarea class="textarea" name="description" placeholder="Tell buyers about the estate, processes, and positioning.">${supplier?.description || ""}</textarea></label>
                </div>
              `)}
              ${onboardingSection("Visual Storytelling", "Ask suppliers for estate and coffee imagery up front so the marketplace feels credible and future supplier galleries are easy to expand. These URLs can point to Supabase Storage files later.", `
                <div class="check-grid">
                  <label class="check-item"><input type="checkbox" name="wantsToAddImages" ${supplier?.wants_to_add_images ? "checked" : ""} /> We want to add our own estate and coffee images</label>
                </div>
                <div class="form-grid two">
                  <label>Estate Image URL<input class="input" name="estateImageUrl" type="url" value="${supplier?.estate_image_url || ""}" placeholder="https://..." /></label>
                  <label>Coffee Image URL<input class="input" name="coffeeImageUrl" type="url" value="${supplier?.coffee_image_url || ""}" placeholder="https://..." /></label>
                  <label style="grid-column: 1 / -1;">Gallery Image URLs (comma separated)<input class="input" name="galleryImageUrls" value="${csvValue(supplier?.gallery_image_urls).replaceAll('"', "&quot;")}" placeholder="https://..., https://..." /></label>
                </div>
                <div class="callout" style="margin-top:14px;">
                  <strong>Image handling path</strong><br>
                  Suppliers can start by pasting hosted image URLs, and later we can switch this form to direct uploads into a Supabase Storage bucket without changing the rest of the product.
                </div>
              `)}
              ${onboardingSection("Export Readiness", "These fields determine whether the supplier can be considered export-ready in the platform.", `
                <div class="form-grid two">
                  <label><input type="checkbox" name="exportsInternationally" ${supplier?.exports_internationally ? "checked" : ""} /> Exports internationally</label>
                  <label>Export Partner Name<input class="input" name="exportPartnerName" value="${supplier?.export_partner_name || ""}" /></label>
                  <label>Export Terms<select class="select" name="exportTerms"><option value="">Select terms</option><option value="FOB" ${supplier?.export_terms === "FOB" ? "selected" : ""}>FOB</option><option value="EXW" ${supplier?.export_terms === "EXW" ? "selected" : ""}>EXW</option></select></label>
                  <label>Minimum Export Order (kg)<input class="input" name="minExportOrderKg" type="number" value="${supplier?.min_export_order_kg || ""}" /></label>
                </div>
                <div class="check-grid">
                  <label class="check-item"><input type="checkbox" name="certificateOfOrigin" ${supplier?.certificate_of_origin ? "checked" : ""} /> Certificate of Origin available</label>
                  <label class="check-item"><input type="checkbox" name="phytosanitaryCertificate" ${supplier?.phytosanitary_certificate ? "checked" : ""} /> Phytosanitary certificate available</label>
                  <label class="check-item"><input type="checkbox" name="invoiceCapability" ${supplier?.invoice_capability ? "checked" : ""} /> Commercial invoice capability</label>
                </div>
              `)}
              ${onboardingSection("Sample Shipping", "These fields power the buyer-facing logistics section and sample-ready badge.", `
                <div class="form-grid two">
                  <label><input type="checkbox" name="canShipSamples" ${supplier?.can_ship_samples ? "checked" : ""} /> Can ship samples</label>
                  <label>Sample Size (grams)<input class="input" name="sampleSizeGrams" type="number" value="${supplier?.sample_size_grams || ""}" /></label>
                  <label>Couriers (comma separated)<input class="input" name="sampleCouriers" value="${csvValue(supplier?.sample_couriers).replaceAll('"', "&quot;")}" placeholder="DHL, FedEx" /></label>
                  <label>Shipping Paid By<select class="select" name="sampleShippingPaidBy"><option value="">Select</option><option value="buyer" ${supplier?.sample_shipping_paid_by === "buyer" ? "selected" : ""}>Buyer</option><option value="supplier" ${supplier?.sample_shipping_paid_by === "supplier" ? "selected" : ""}>Supplier</option></select></label>
                  <label>Prep Days<input class="input" name="samplePrepDays" type="number" value="${supplier?.sample_prep_days || ""}" /></label>
                  <label>Shipping Days<input class="input" name="sampleShippingDays" type="number" value="${supplier?.sample_shipping_days || ""}" /></label>
                  <label>Sample Price<input class="input" name="samplePrice" type="number" step="0.01" value="${supplier?.sample_price || ""}" /></label>
                </div>
              `)}
              ${onboardingSection("Compliance Responsibility", "This is an approval-blocking field for US-bound sample workflows.", `
                <label>Prior Notice Handler<select class="select" name="priorNoticeHandler" required><option value="">Select owner</option><option value="supplier" ${supplier?.prior_notice_handler === "supplier" ? "selected" : ""}>Supplier</option><option value="buyer" ${supplier?.prior_notice_handler === "buyer" ? "selected" : ""}>Buyer</option><option value="broker" ${supplier?.prior_notice_handler === "broker" ? "selected" : ""}>Freight Forwarder / Broker</option></select></label>
              `)}
              ${signupMode ? onboardingSection("Account Access", "Create a supplier account so this company can sign in, manage its presence, and later handle inquiry workflows.", `
                <div class="form-grid two">
                  <label>Password<input class="input" name="password" type="password" required /></label>
                  <label>Confirm Password<input class="input" name="confirmPassword" type="password" required /></label>
                </div>
              `) : ""}
              <div class="actions">
                <button class="button" type="submit">${signupMode ? "Create Supplier" : "Submit Supplier Change Request"}</button>
                <a class="button-secondary" href="/inquiries">See Live Inquiries</a>
              </div>
            </form>
            ${isEditing ? (() => {
              const pendingInquiries = (state.bootstrap.inquiries || []).filter(inq => inq.shipment_status === "new");
              return `
              <div class="panel" style="margin-top:18px;border-left:3px solid #f59e0b;">
                <h3>⏳ Pending Sample Requests</h3>
                <p class="lead">These buyers are waiting for your response. Accept to begin sample preparation, or decline to close the request.</p>
                <div id="supplier-accept-banner" class="success-banner hidden"></div>
                <div id="supplier-accept-error" class="error-banner hidden"></div>
                ${pendingInquiries.length ? `
                <div class="review-stack">
                  ${pendingInquiries.map(inq => `
                    <div class="review-card">
                      <div class="review-card-head">
                        <strong>${inq.buyer_name}</strong>
                        <span class="badge warn">awaiting response</span>
                      </div>
                      <p class="lead">Lot: ${inq.lot_name} &nbsp;·&nbsp; Destination: ${inq.destination_country}</p>
                      ${inq.buyer_message ? `<p class="lead" style="font-style:italic">"${inq.buyer_message}"</p>` : ""}
                      <div style="display:flex;gap:8px;margin-top:8px;">
                        <button class="button supplier-accept-btn" style="background:#16a34a;border-color:#16a34a;font-size:13px;padding:6px 16px"
                          data-inquiry-id="${inq.id}" data-action="approved">✓ Accept Request</button>
                        <button class="button-secondary supplier-accept-btn" style="color:#dc2626;border-color:#dc2626;font-size:13px;padding:6px 16px"
                          data-inquiry-id="${inq.id}" data-action="closed">✗ Decline</button>
                      </div>
                    </div>
                  `).join("")}
                </div>
                ` : `<p class="lead">No pending requests right now.</p>`}
              </div>`;
            })() : ""}
            <div class="panel" style="margin-top:18px;">
              <h3>Supplier Reviews</h3>
              ${renderReviewCards(reviews, "No supplier reviews yet. Buyer-side ratings will appear here once customers start reviewing this supplier.")}
            </div>
            ${isEditing ? `
              <div class="panel" style="margin-top:18px;">
                <h3>Pending Supplier Change Requests</h3>
                ${renderChangeRequestList(changeRequests, "No supplier change requests submitted yet.")}
              </div>
            ` : ""}
          </section>
        </div>
      </main>
      ${footer()}
    </div>
  `;
  bindGlobalActions();

  // Wire Accept / Decline buttons for pending inquiries
  document.querySelectorAll(".supplier-accept-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const inquiryId = btn.dataset.inquiryId;
      const action = btn.dataset.action;
      const banner = document.getElementById("supplier-accept-banner");
      const errorEl = document.getElementById("supplier-accept-error");
      btn.disabled = true;
      btn.textContent = "Saving…";
      const { response, result } = await patchJson(`/api/inquiries/${inquiryId}/shipment`, { shipmentStatus: action });
      if (response.ok) {
        const label = action === "approved" ? "accepted" : "declined";
        banner.textContent = `Inquiry ${label}. The buyer will be notified.`;
        banner.classList.remove("hidden");
        errorEl.classList.add("hidden");
        await refreshBootstrap();
        renderSupplierOnboarding(pathname);
      } else {
        errorEl.textContent = result?.detail || "Error updating inquiry";
        errorEl.classList.remove("hidden");
        banner.classList.add("hidden");
        btn.disabled = false;
        btn.textContent = action === "approved" ? "✓ Accept Request" : "✗ Decline";
      }
    });
  });

  const form = document.getElementById("supplier-form");
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const success = document.getElementById("form-success");
    const error = document.getElementById("form-error");
    success.classList.add("hidden");
    error.classList.add("hidden");

    const formData = new FormData(form);
    if (signupMode && formData.get("password") !== formData.get("confirmPassword")) {
      error.textContent = "Passwords do not match.";
      error.classList.remove("hidden");
      return;
    }
    const payload = {
      id: supplier?.id || undefined,
      companyName: isEditing ? supplier?.company_name : formData.get("companyName"),
      contactName: formData.get("contactName"),
      contactEmail: isEditing ? supplier?.contact_email : formData.get("contactEmail"),
      contactPhone: formData.get("contactPhone"),
      region: isEditing ? supplier?.region : formData.get("region"),
      website: formData.get("website"),
      altitudeMeters: formData.get("altitudeMeters") ? Number(formData.get("altitudeMeters")) : null,
      varietals: String(formData.get("varietals") || "").split(",").map((v) => v.trim()).filter(Boolean),
      certifications: String(formData.get("certifications") || "").split(",").map((v) => v.trim()).filter(Boolean),
      description: formData.get("description"),
      exportsInternationally: formData.get("exportsInternationally") === "on",
      exportPartnerName: formData.get("exportPartnerName"),
      exportTerms: formData.get("exportTerms"),
      minExportOrderKg: formData.get("minExportOrderKg") ? Number(formData.get("minExportOrderKg")) : null,
      documentationAvailable: {
        certificateOfOrigin: formData.get("certificateOfOrigin") === "on",
        phytosanitaryCertificate: formData.get("phytosanitaryCertificate") === "on",
        invoiceCapability: formData.get("invoiceCapability") === "on",
      },
      canShipSamples: formData.get("canShipSamples") === "on",
      sampleSizeGrams: formData.get("sampleSizeGrams") ? Number(formData.get("sampleSizeGrams")) : null,
      sampleCouriers: String(formData.get("sampleCouriers") || "").split(",").map((v) => v.trim()).filter(Boolean),
      sampleShippingPaidBy: formData.get("sampleShippingPaidBy"),
      samplePrepDays: formData.get("samplePrepDays") ? Number(formData.get("samplePrepDays")) : null,
      sampleShippingDays: formData.get("sampleShippingDays") ? Number(formData.get("sampleShippingDays")) : null,
      samplePrice: formData.get("samplePrice") ? Number(formData.get("samplePrice")) : null,
      priorNoticeHandler: formData.get("priorNoticeHandler"),
      wantsToAddImages: formData.get("wantsToAddImages") === "on",
      estateImageUrl: formData.get("estateImageUrl"),
      coffeeImageUrl: formData.get("coffeeImageUrl"),
      galleryImageUrls: String(formData.get("galleryImageUrls") || "").split(",").map((v) => v.trim()).filter(Boolean),
      password: signupMode ? formData.get("password") : null,
    };

    const endpoint = signupMode ? "/api/suppliers" : "/api/suppliers/update-request";
    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (!response.ok) {
      error.textContent = result.error || "Could not save supplier.";
      error.classList.remove("hidden");
      return;
    }

    const successMessage = signupMode
      ? `
      Supplier <strong>${result.companyName}</strong> saved in Supabase with id <strong>${result.id}</strong>.
      Export ready: <strong>${result.exportReady ? "Yes" : "No"}</strong>,
      Sample ready: <strong>${result.sampleReady ? "Yes" : "No"}</strong>,
      Compliance ready: <strong>${result.complianceReady ? "Yes" : "No"}</strong>,
      Status: <strong>${result.approvalStatus}</strong>.
    `
      : `
      Supplier change request <strong>${result.id}</strong> submitted for approval.
      Changed fields: <strong>${(result.changedFields || []).join(", ")}</strong>.
    `;
    await refreshBootstrap();
    if (signupMode) {
      window.history.replaceState({}, "", "/supplier-onboarding");
    }
    renderSupplierOnboarding("/supplier-onboarding", successMessage);
  });
}

async function router() {
  try {
    const response = await fetch("/api/bootstrap");
    if (!response.ok) throw new Error(`Bootstrap HTTP ${response.status}`);
    state.bootstrap = await response.json();
  } catch (error) {
    console.error("[router] bootstrap failed:", error);
    app.innerHTML = `
      <div class="shell">
        <main class="section" style="text-align:center;padding:80px 24px;">
          <h2>Could not connect to the server</h2>
          <p class="lead">Make sure the backend is running, then <a href="/">refresh the page</a>.</p>
          <p class="lead" style="font-size:0.85em;color:var(--muted)">${error.message}</p>
        </main>
      </div>`;
    return;
  }
  const pathname = window.location.pathname;
  if (pathname === "/") return renderHome(pathname);
  if (pathname === "/auth") return renderAuthPage(pathname);
  if (pathname === "/catalog") return renderCatalog(pathname);
  if (pathname === "/buyer-preferences") return renderBuyerPreferences(pathname);
  if (pathname === "/supplier-onboarding") return renderSupplierOnboarding(pathname);
  if (pathname === "/inquiries") return renderInquiryTracking(pathname);
  if (pathname === "/admin") return renderAdmin(pathname);
  if (pathname.startsWith("/coffee/")) return renderCoffeeDetail(pathname);
  renderHome("/");
}

router();
