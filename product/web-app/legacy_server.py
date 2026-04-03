from __future__ import annotations

import json
import os
import re
import hashlib
import secrets
from decimal import Decimal
from http import HTTPStatus, cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from uuid import uuid4
from urllib.parse import urlparse

from psycopg import connect
from psycopg.rows import dict_row


ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "static"
ENV_PATH = ROOT.parent / "backend" / "supabase" / ".env"
SPA_ROUTES = {
    "/",
    "/auth",
    "/catalog",
    "/supplier-onboarding",
    "/buyer-preferences",
    "/inquiries",
    "/admin",
}
SESSION_COOKIE = "coffee_session"
SESSION_MAX_AGE = 60 * 60 * 24 * 14


def load_env() -> None:
    if not ENV_PATH.exists():
        return
    for line in ENV_PATH.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key, value)


def get_db_url() -> str:
    load_env()
    db_url = os.environ["SUPABASE_DB_URL"]
    if "sslmode=" not in db_url:
        separator = "&" if "?" in db_url else "?"
        db_url = f"{db_url}{separator}sslmode=require"
    return db_url


def query_all(sql: str, params: tuple | None = None) -> list[dict]:
    with connect(get_db_url(), row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return list(cur.fetchall())


def query_one(sql: str, params: tuple | None = None) -> dict | None:
    rows = query_all(sql, params)
    return rows[0] if rows else None


def execute(sql: str, params: tuple | None = None) -> None:
    with connect(get_db_url()) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
        conn.commit()


def slugify(value: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return base or "supplier"


def make_entity_id(prefix: str, primary_value: str) -> str:
    return f"{slugify(primary_value)}_{prefix}_{uuid4().hex[:6]}"


def clean_text(value):
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def clean_array(values) -> list[str]:
    if not values:
        return []
    if isinstance(values, str):
        values = values.split(",")
    return [str(value).strip() for value in values if str(value).strip()]


def clean_number(value):
    if value in (None, "", []):
        return None
    return value


def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        310000,
    ).hex()
    return digest, salt


def verify_password(password: str, expected_hash: str, salt: str) -> bool:
    candidate_hash, _ = hash_password(password, salt)
    return secrets.compare_digest(candidate_hash, expected_hash)


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def supplier_payload_to_row(payload: dict) -> dict:
    documentation = payload.get("documentationAvailable", {})
    return {
        "id": payload.get("id") or make_entity_id("sup", payload["companyName"]),
        "company_name": clean_text(payload["companyName"]),
        "contact_name": clean_text(payload.get("contactName")),
        "contact_email": clean_text(payload["contactEmail"]),
        "contact_phone": clean_text(payload.get("contactPhone")),
        "region": clean_text(payload["region"]),
        "website": clean_text(payload.get("website")),
        "altitude_meters": clean_number(payload.get("altitudeMeters")),
        "varietals": clean_array(payload.get("varietals", [])),
        "certifications": clean_array(payload.get("certifications", [])),
        "description": clean_text(payload.get("description")),
        "exports_internationally": payload.get("exportsInternationally", False),
        "export_partner_name": clean_text(payload.get("exportPartnerName")),
        "export_terms": clean_text(payload.get("exportTerms")),
        "min_export_order_kg": clean_number(payload.get("minExportOrderKg")),
        "certificate_of_origin": documentation.get("certificateOfOrigin", False),
        "phytosanitary_certificate": documentation.get("phytosanitaryCertificate", False),
        "invoice_capability": documentation.get("invoiceCapability", False),
        "can_ship_samples": payload.get("canShipSamples", False),
        "sample_size_grams": clean_number(payload.get("sampleSizeGrams")),
        "sample_couriers": clean_array(payload.get("sampleCouriers", [])),
        "sample_shipping_paid_by": clean_text(payload.get("sampleShippingPaidBy")),
        "sample_shipping_days": clean_number(payload.get("sampleShippingDays")),
        "sample_prep_days": clean_number(payload.get("samplePrepDays")),
        "sample_price": clean_number(payload.get("samplePrice")),
        "prior_notice_handler": clean_text(payload.get("priorNoticeHandler")),
    }


def buyer_payload_to_row(payload: dict) -> dict:
    return {
        "id": payload.get("id") or make_entity_id("buy", payload["companyName"]),
        "company_name": clean_text(payload["companyName"]),
        "contact_name": clean_text(payload.get("contactName")),
        "contact_email": clean_text(payload["contactEmail"]),
        "buyer_type": clean_text(payload["buyerType"]),
        "destination_country": clean_text(payload["destinationCountry"]),
        "preferred_regions": clean_array(payload.get("preferredRegions", [])),
        "preferred_varietals": clean_array(payload.get("preferredVarietals", [])),
        "preferred_processes": clean_array(payload.get("preferredProcesses", [])),
        "target_tasting_notes": clean_array(payload.get("targetTastingNotes", [])),
        "preferred_certifications": clean_array(payload.get("preferredCertifications", [])),
        "min_moq_kg": clean_number(payload.get("minMoqKg")),
        "max_moq_kg": clean_number(payload.get("maxMoqKg")),
        "max_price_per_kg": clean_number(payload.get("maxPricePerKg")),
        "requires_samples": payload.get("requiresSamples", True),
        "preferred_couriers": clean_array(payload.get("preferredCouriers", [])),
        "needs_us_compliance_support": payload.get("needsUsComplianceSupport", False),
    }


def existing_supplier_id_for_email(email: str | None) -> str | None:
    if not email:
        return None
    record = query_one(
        "SELECT id FROM suppliers WHERE contact_email = %s ORDER BY created_at DESC LIMIT 1",
        (email,),
    )
    return record["id"] if record else None


def existing_buyer_id_for_email(email: str | None) -> str | None:
    if not email:
        return None
    record = query_one(
        "SELECT id FROM buyers WHERE contact_email = %s ORDER BY created_at DESC LIMIT 1",
        (email,),
    )
    return record["id"] if record else None


def supplier_is_export_ready(row: dict) -> bool:
    return bool(
        row["exports_internationally"]
        and row["export_terms"]
        and row["min_export_order_kg"] is not None
        and row["certificate_of_origin"]
        and row["phytosanitary_certificate"]
        and row["invoice_capability"]
    )


def supplier_is_sample_ready(row: dict) -> bool:
    return bool(
        row["can_ship_samples"]
        and row["sample_size_grams"] is not None
        and row["sample_couriers"]
        and row["sample_shipping_paid_by"]
        and row["sample_shipping_days"] is not None
        and row["sample_prep_days"] is not None
        and row["sample_price"] is not None
    )


def supplier_is_compliance_ready(row: dict) -> bool:
    return bool(row["prior_notice_handler"])


def create_supplier(payload: dict) -> dict:
    row = supplier_payload_to_row(payload)
    existing_id = existing_supplier_id_for_email(row["contact_email"])
    if existing_id:
        row["id"] = existing_id
    export_ready = supplier_is_export_ready(row)
    sample_ready = supplier_is_sample_ready(row)
    compliance_ready = supplier_is_compliance_ready(row)
    approval_status = "approved" if export_ready and sample_ready and compliance_ready else "pending"

    execute(
        """
        INSERT INTO suppliers (
          id, company_name, contact_name, contact_email, contact_phone, region, website,
          altitude_meters, varietals, certifications, description, exports_internationally,
          export_partner_name, export_terms, min_export_order_kg, certificate_of_origin,
          phytosanitary_certificate, invoice_capability, can_ship_samples, sample_size_grams,
          sample_couriers, sample_shipping_paid_by, sample_shipping_days, sample_prep_days,
          sample_price, prior_notice_handler, approval_status
        ) VALUES (
          %(id)s, %(company_name)s, %(contact_name)s, %(contact_email)s, %(contact_phone)s, %(region)s, %(website)s,
          %(altitude_meters)s, %(varietals)s, %(certifications)s, %(description)s, %(exports_internationally)s,
          %(export_partner_name)s, %(export_terms)s, %(min_export_order_kg)s, %(certificate_of_origin)s,
          %(phytosanitary_certificate)s, %(invoice_capability)s, %(can_ship_samples)s, %(sample_size_grams)s,
          %(sample_couriers)s, %(sample_shipping_paid_by)s, %(sample_shipping_days)s, %(sample_prep_days)s,
          %(sample_price)s, %(prior_notice_handler)s, %(approval_status)s
        )
        ON CONFLICT (id) DO UPDATE SET
          company_name = EXCLUDED.company_name,
          contact_name = EXCLUDED.contact_name,
          contact_email = EXCLUDED.contact_email,
          contact_phone = EXCLUDED.contact_phone,
          region = EXCLUDED.region,
          website = EXCLUDED.website,
          altitude_meters = EXCLUDED.altitude_meters,
          varietals = EXCLUDED.varietals,
          certifications = EXCLUDED.certifications,
          description = EXCLUDED.description,
          exports_internationally = EXCLUDED.exports_internationally,
          export_partner_name = EXCLUDED.export_partner_name,
          export_terms = EXCLUDED.export_terms,
          min_export_order_kg = EXCLUDED.min_export_order_kg,
          certificate_of_origin = EXCLUDED.certificate_of_origin,
          phytosanitary_certificate = EXCLUDED.phytosanitary_certificate,
          invoice_capability = EXCLUDED.invoice_capability,
          can_ship_samples = EXCLUDED.can_ship_samples,
          sample_size_grams = EXCLUDED.sample_size_grams,
          sample_couriers = EXCLUDED.sample_couriers,
          sample_shipping_paid_by = EXCLUDED.sample_shipping_paid_by,
          sample_shipping_days = EXCLUDED.sample_shipping_days,
          sample_prep_days = EXCLUDED.sample_prep_days,
          sample_price = EXCLUDED.sample_price,
          prior_notice_handler = EXCLUDED.prior_notice_handler,
          approval_status = EXCLUDED.approval_status,
          updated_at = NOW()
        """,
        {**row, "approval_status": approval_status},
    )

    return {
        "id": row["id"],
        "companyName": row["company_name"],
        "exportReady": export_ready,
        "sampleReady": sample_ready,
        "complianceReady": compliance_ready,
        "approvalStatus": approval_status,
    }


def create_buyer(payload: dict) -> dict:
    row = buyer_payload_to_row(payload)
    existing_id = existing_buyer_id_for_email(row["contact_email"])
    if existing_id:
        row["id"] = existing_id
    execute(
        """
        INSERT INTO buyers (
          id, company_name, contact_name, contact_email, buyer_type, destination_country,
          preferred_regions, preferred_varietals, preferred_processes, target_tasting_notes,
          preferred_certifications, min_moq_kg, max_moq_kg, max_price_per_kg, requires_samples,
          preferred_couriers, needs_us_compliance_support
        ) VALUES (
          %(id)s, %(company_name)s, %(contact_name)s, %(contact_email)s, %(buyer_type)s, %(destination_country)s,
          %(preferred_regions)s, %(preferred_varietals)s, %(preferred_processes)s, %(target_tasting_notes)s,
          %(preferred_certifications)s, %(min_moq_kg)s, %(max_moq_kg)s, %(max_price_per_kg)s, %(requires_samples)s,
          %(preferred_couriers)s, %(needs_us_compliance_support)s
        )
        ON CONFLICT (id) DO UPDATE SET
          company_name = EXCLUDED.company_name,
          contact_name = EXCLUDED.contact_name,
          contact_email = EXCLUDED.contact_email,
          buyer_type = EXCLUDED.buyer_type,
          destination_country = EXCLUDED.destination_country,
          preferred_regions = EXCLUDED.preferred_regions,
          preferred_varietals = EXCLUDED.preferred_varietals,
          preferred_processes = EXCLUDED.preferred_processes,
          target_tasting_notes = EXCLUDED.target_tasting_notes,
          preferred_certifications = EXCLUDED.preferred_certifications,
          min_moq_kg = EXCLUDED.min_moq_kg,
          max_moq_kg = EXCLUDED.max_moq_kg,
          max_price_per_kg = EXCLUDED.max_price_per_kg,
          requires_samples = EXCLUDED.requires_samples,
          preferred_couriers = EXCLUDED.preferred_couriers,
          needs_us_compliance_support = EXCLUDED.needs_us_compliance_support,
          updated_at = NOW()
        """,
        row,
    )
    return {
        "id": row["id"],
        "companyName": row["company_name"],
        "buyerType": row["buyer_type"],
        "destinationCountry": row["destination_country"],
        "requiresSamples": row["requires_samples"],
        "preferredRegions": row["preferred_regions"],
    }


def create_auth_user(
    *,
    email: str,
    password: str,
    role: str,
    display_name: str | None = None,
    supplier_id: str | None = None,
    buyer_id: str | None = None,
) -> dict:
    existing = query_one(
        """
        SELECT id, email, role, supplier_id, buyer_id
        FROM app_users
        WHERE email = %s
        """,
        (email,),
    )
    if existing:
        role_conflict = existing["role"] != role
        supplier_conflict = supplier_id and existing.get("supplier_id") and existing["supplier_id"] != supplier_id
        buyer_conflict = buyer_id and existing.get("buyer_id") and existing["buyer_id"] != buyer_id
        if role_conflict or supplier_conflict or buyer_conflict:
            raise ValueError(
                "This email is already linked to another account. Use a different email or sign in to the existing account."
            )
    password_hash, password_salt = hash_password(password)
    params = {
        "id": existing["id"] if existing else make_entity_id("usr", email),
        "email": email,
        "display_name": display_name,
        "role": role,
        "password_hash": password_hash,
        "password_salt": password_salt,
        "supplier_id": supplier_id,
        "buyer_id": buyer_id,
    }
    execute(
        """
        INSERT INTO app_users (
          id, email, display_name, role, password_hash, password_salt, supplier_id, buyer_id
        ) VALUES (
          %(id)s, %(email)s, %(display_name)s, %(role)s, %(password_hash)s, %(password_salt)s, %(supplier_id)s, %(buyer_id)s
        )
        ON CONFLICT (email) DO UPDATE SET
          display_name = EXCLUDED.display_name,
          role = EXCLUDED.role,
          password_hash = EXCLUDED.password_hash,
          password_salt = EXCLUDED.password_salt,
          supplier_id = COALESCE(EXCLUDED.supplier_id, app_users.supplier_id),
          buyer_id = COALESCE(EXCLUDED.buyer_id, app_users.buyer_id),
          updated_at = NOW()
        """,
        params,
    )
    return query_one(
        """
        SELECT id, email, display_name, role, supplier_id, buyer_id
        FROM app_users
        WHERE email = %s
        """,
        (email,),
    )


def create_session_for_user(user_id: str) -> str:
    token = secrets.token_urlsafe(32)
    execute(
        """
        INSERT INTO app_sessions (id, user_id, token_hash, expires_at)
        VALUES (%s, %s, %s, NOW() + INTERVAL '14 days')
        """,
        (
            make_entity_id("sess", user_id),
            user_id,
            hash_session_token(token),
        ),
    )
    return token


def delete_session(token: str) -> None:
    execute("DELETE FROM app_sessions WHERE token_hash = %s", (hash_session_token(token),))


def log_buyer_interaction(
    *,
    buyer_id: str,
    lot_id: str,
    interaction_type: str,
    source_surface: str | None = None,
) -> None:
    execute(
        """
        INSERT INTO buyer_lot_interactions (
          id, buyer_id, lot_id, interaction_type, source_surface
        ) VALUES (%s, %s, %s, %s, %s)
        """,
        (
            make_entity_id("itx", f"{buyer_id}_{lot_id}_{interaction_type}"),
            buyer_id,
            lot_id,
            interaction_type,
            source_surface,
        ),
    )


def get_user_by_email(email: str) -> dict | None:
    return query_one(
        """
        SELECT
          u.id,
          u.email,
          u.display_name,
          u.role,
          u.password_hash,
          u.password_salt,
          u.supplier_id,
          u.buyer_id,
          s.company_name AS supplier_name,
          b.company_name AS buyer_name,
          b.destination_country,
          b.requires_samples
        FROM app_users u
        LEFT JOIN suppliers s ON s.id = u.supplier_id
        LEFT JOIN buyers b ON b.id = u.buyer_id
        WHERE u.email = %s
          AND u.is_active = TRUE
        """,
        (email,),
    )


def ensure_email_can_create_role(email: str | None, role: str) -> None:
    if not email:
        return
    existing = query_one(
        "SELECT id, role FROM app_users WHERE email = %s",
        (email,),
    )
    if existing and existing["role"] != role:
        raise ValueError(
            "This email is already linked to another account. Use a different email or sign in to the existing account."
        )


def get_current_user_from_token(token: str | None) -> dict | None:
    if not token:
        return None
    return query_one(
        """
        SELECT
          u.id,
          u.email,
          u.display_name,
          u.role,
          u.supplier_id,
          u.buyer_id,
          s.company_name AS supplier_name,
          b.company_name AS buyer_name,
          b.destination_country,
          b.requires_samples
        FROM app_sessions sess
        JOIN app_users u ON u.id = sess.user_id
        LEFT JOIN suppliers s ON s.id = u.supplier_id
        LEFT JOIN buyers b ON b.id = u.buyer_id
        WHERE sess.token_hash = %s
          AND sess.expires_at > NOW()
          AND u.is_active = TRUE
        """,
        (hash_session_token(token),),
    )


def get_supplier_reviews(supplier_id: str) -> list[dict]:
    return query_all(
        """
        SELECT
          id,
          reviewer_name,
          reviewer_role,
          reviewer_company,
          rating,
          review_text,
          created_at
        FROM supplier_reviews
        WHERE supplier_id = %s
        ORDER BY created_at DESC
        LIMIT 8
        """,
        (supplier_id,),
    )


def get_buyer_reviews(buyer_id: str) -> list[dict]:
    return query_all(
        """
        SELECT
          id,
          reviewer_name,
          reviewer_role,
          reviewer_company,
          rating,
          review_text,
          created_at
        FROM buyer_reviews
        WHERE buyer_id = %s
        ORDER BY created_at DESC
        LIMIT 8
        """,
        (buyer_id,),
    )


def get_supplier_profile(supplier_id: str) -> dict | None:
    return query_one(
        """
        SELECT
          s.*,
          sr.export_ready,
          sr.sample_ready,
          sr.compliance_ready,
          COALESCE(srs.average_rating, 0) AS average_rating,
          COALESCE(srs.review_count, 0) AS review_count
        FROM suppliers s
        JOIN supplier_readiness sr ON sr.id = s.id
        LEFT JOIN supplier_review_summary srs ON srs.supplier_id = s.id
        WHERE s.id = %s
        """,
        (supplier_id,),
    )


def get_buyer_profile(buyer_id: str) -> dict | None:
    return query_one(
        """
        SELECT
          b.*,
          COALESCE(brs.average_rating, 0) AS average_rating,
          COALESCE(brs.review_count, 0) AS review_count,
          CASE WHEN surv.buyer_id IS NULL THEN FALSE ELSE TRUE END AS survey_completed,
          surv.completed_at AS survey_completed_at
        FROM buyers b
        LEFT JOIN buyer_review_summary brs ON brs.buyer_id = b.id
        LEFT JOIN buyer_recommendation_surveys surv ON surv.buyer_id = b.id
        WHERE b.id = %s
        """,
        (buyer_id,),
    )


def get_buyer_survey(buyer_id: str) -> dict | None:
    return query_one(
        """
        SELECT
          buyer_id,
          preferred_regions,
          preferred_varietals,
          preferred_processes,
          target_tasting_notes,
          preferred_couriers,
          min_moq_kg,
          max_moq_kg,
          max_price_per_kg,
          completed_at
        FROM buyer_recommendation_surveys
        WHERE buyer_id = %s
        """,
        (buyer_id,),
    )


def create_supplier_review(
    *,
    supplier_id: str,
    reviewer_name: str,
    reviewer_role: str,
    reviewer_company: str | None,
    rating: int,
    review_text: str | None,
) -> dict:
    review_id = make_entity_id("suprev", supplier_id)
    execute(
        """
        INSERT INTO supplier_reviews (
          id, supplier_id, reviewer_name, reviewer_role, reviewer_company, rating, review_text
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (review_id, supplier_id, reviewer_name, reviewer_role, reviewer_company, rating, review_text),
    )
    return {"id": review_id, "supplierId": supplier_id, "rating": rating}


def create_buyer_review(
    *,
    buyer_id: str,
    reviewer_name: str,
    reviewer_role: str,
    reviewer_company: str | None,
    rating: int,
    review_text: str | None,
) -> dict:
    review_id = make_entity_id("buyrev", buyer_id)
    execute(
        """
        INSERT INTO buyer_reviews (
          id, buyer_id, reviewer_name, reviewer_role, reviewer_company, rating, review_text
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (review_id, buyer_id, reviewer_name, reviewer_role, reviewer_company, rating, review_text),
    )
    return {"id": review_id, "buyerId": buyer_id, "rating": rating}


def save_recommendation_survey(buyer_id: str, payload: dict) -> None:
    row = {
        "buyer_id": buyer_id,
        "preferred_regions": clean_array(payload.get("preferredRegions", [])),
        "preferred_varietals": clean_array(payload.get("preferredVarietals", [])),
        "preferred_processes": clean_array(payload.get("preferredProcesses", [])),
        "target_tasting_notes": clean_array(payload.get("targetTastingNotes", [])),
        "preferred_couriers": clean_array(payload.get("preferredCouriers", [])),
        "min_moq_kg": clean_number(payload.get("minMoqKg")),
        "max_moq_kg": clean_number(payload.get("maxMoqKg")),
        "max_price_per_kg": clean_number(payload.get("maxPricePerKg")),
    }
    execute(
        """
        INSERT INTO buyer_recommendation_surveys (
          buyer_id, preferred_regions, preferred_varietals, preferred_processes,
          target_tasting_notes, preferred_couriers, min_moq_kg, max_moq_kg, max_price_per_kg
        ) VALUES (
          %(buyer_id)s, %(preferred_regions)s, %(preferred_varietals)s, %(preferred_processes)s,
          %(target_tasting_notes)s, %(preferred_couriers)s, %(min_moq_kg)s, %(max_moq_kg)s, %(max_price_per_kg)s
        )
        ON CONFLICT (buyer_id) DO UPDATE SET
          preferred_regions = EXCLUDED.preferred_regions,
          preferred_varietals = EXCLUDED.preferred_varietals,
          preferred_processes = EXCLUDED.preferred_processes,
          target_tasting_notes = EXCLUDED.target_tasting_notes,
          preferred_couriers = EXCLUDED.preferred_couriers,
          min_moq_kg = EXCLUDED.min_moq_kg,
          max_moq_kg = EXCLUDED.max_moq_kg,
          max_price_per_kg = EXCLUDED.max_price_per_kg,
          updated_at = NOW(),
          completed_at = NOW()
        """,
        row,
    )
    execute(
        """
        UPDATE buyers SET
          preferred_regions = %(preferred_regions)s,
          preferred_varietals = %(preferred_varietals)s,
          preferred_processes = %(preferred_processes)s,
          target_tasting_notes = %(target_tasting_notes)s,
          preferred_couriers = %(preferred_couriers)s,
          min_moq_kg = %(min_moq_kg)s,
          max_moq_kg = %(max_moq_kg)s,
          max_price_per_kg = %(max_price_per_kg)s,
          updated_at = NOW()
        WHERE id = %(buyer_id)s
        """,
        row,
    )


def get_catalog_lots() -> list[dict]:
    return query_all(
        """
        SELECT
          l.id,
          l.supplier_id,
          l.lot_name,
          l.region,
          l.altitude_meters,
          l.varietals,
          l.process,
          l.cup_score,
          l.tasting_notes,
          l.price_per_kg,
          l.quantity_kg,
          l.export_ready,
          l.sample_ready,
          l.compliance_ready,
          s.company_name AS supplier_name,
          s.min_export_order_kg,
          s.certifications,
          s.sample_couriers,
          s.sample_size_grams,
          s.sample_price,
          s.sample_shipping_days,
          s.sample_prep_days,
          s.sample_shipping_paid_by,
          s.prior_notice_handler,
          COALESCE(srs.average_rating, 0) AS supplier_average_rating,
          COALESCE(srs.review_count, 0) AS supplier_review_count
        FROM coffee_lots l
        JOIN suppliers s ON s.id = l.supplier_id
        LEFT JOIN supplier_review_summary srs ON srs.supplier_id = s.id
        ORDER BY l.cup_score DESC NULLS LAST, l.lot_name ASC
        """
    )


def get_buyers() -> list[dict]:
    return query_all(
        """
        SELECT
          buyers.id,
          buyers.company_name,
          buyers.contact_name,
          buyers.contact_email,
          buyers.buyer_type,
          buyers.destination_country,
          buyers.preferred_regions,
          buyers.preferred_varietals,
          buyers.preferred_processes,
          buyers.target_tasting_notes,
          buyers.preferred_certifications,
          buyers.min_moq_kg,
          buyers.max_moq_kg,
          buyers.max_price_per_kg,
          buyers.preferred_couriers,
          buyers.requires_samples,
          buyers.needs_us_compliance_support,
          COALESCE(brs.average_rating, 0) AS average_rating,
          COALESCE(brs.review_count, 0) AS review_count,
          CASE WHEN surv.buyer_id IS NULL THEN FALSE ELSE TRUE END AS survey_completed,
          buyers.created_at
        FROM buyers
        LEFT JOIN buyer_review_summary brs ON brs.buyer_id = buyers.id
        LEFT JOIN buyer_recommendation_surveys surv ON surv.buyer_id = buyers.id
        ORDER BY buyers.created_at DESC, buyers.company_name
        """
    )


def score_lot_for_buyer(buyer: dict, lot: dict) -> dict | None:
    if not lot["export_ready"] or not lot["compliance_ready"]:
        return None
    if buyer.get("requires_samples") and not lot["sample_ready"]:
        return None
    supplier_moq = lot.get("min_export_order_kg")
    if buyer.get("max_moq_kg") and supplier_moq and supplier_moq > buyer["max_moq_kg"]:
        return None

    buyer_regions = set(buyer.get("preferred_regions") or [])
    buyer_varietals = set(buyer.get("preferred_varietals") or [])
    buyer_processes = set(buyer.get("preferred_processes") or [])
    buyer_notes = set(buyer.get("target_tasting_notes") or [])
    buyer_certs = set(buyer.get("preferred_certifications") or [])
    buyer_couriers = set(buyer.get("preferred_couriers") or [])
    lot_varietals = set(lot.get("varietals") or [])
    lot_notes = set(lot.get("tasting_notes") or [])
    lot_certs = set(lot.get("certifications") or [])
    lot_couriers = set(lot.get("sample_couriers") or [])

    source_region_fit = 1.0 if buyer_regions and lot.get("region") in buyer_regions else 0.55
    varietal_fit = 1.0 if buyer_varietals and buyer_varietals.intersection(lot_varietals) else 0.5
    process_fit = 1.0 if buyer_processes and lot.get("process") in buyer_processes else 0.5
    note_fit = 1.0 if buyer_notes and buyer_notes.intersection(lot_notes) else 0.5
    cup_profile_fit = round((varietal_fit + process_fit + note_fit) / 3, 2)

    commercial_parts = []
    if buyer.get("max_price_per_kg") and lot.get("price_per_kg"):
      commercial_parts.append(1.0 if lot["price_per_kg"] <= buyer["max_price_per_kg"] else 0.35)
    if buyer.get("min_moq_kg") and supplier_moq:
      commercial_parts.append(1.0 if supplier_moq >= buyer["min_moq_kg"] else 0.75)
    if buyer.get("max_moq_kg") and supplier_moq:
      commercial_parts.append(1.0 if supplier_moq <= buyer["max_moq_kg"] else 0.35)
    commercial_fit = round(sum(commercial_parts) / len(commercial_parts), 2) if commercial_parts else 0.7

    logistics_parts = [1.0 if lot["sample_ready"] else 0.0]
    if buyer_couriers:
        logistics_parts.append(1.0 if buyer_couriers.intersection(lot_couriers) else 0.45)
    if lot.get("sample_shipping_days") is not None:
        logistics_parts.append(1.0 if lot["sample_shipping_days"] <= 7 else 0.6)
    logistics_fit = round(sum(logistics_parts) / len(logistics_parts), 2)

    compliance_parts = [1.0 if lot["compliance_ready"] else 0.0]
    if buyer.get("destination_country") == "US":
        compliance_parts.append(1.0 if lot.get("prior_notice_handler") else 0.0)
    if buyer_certs:
        compliance_parts.append(1.0 if buyer_certs.intersection(lot_certs) else 0.55)
    compliance_fit = round(sum(compliance_parts) / len(compliance_parts), 2)

    supplier_reliability_fit = round(
        (
            (1.0 if lot["export_ready"] else 0.0)
            + (1.0 if lot["sample_ready"] else 0.0)
            + (1.0 if lot["compliance_ready"] else 0.0)
        )
        / 3,
        2,
    )

    recommendation_score = round(
        (source_region_fit * 0.22)
        + (cup_profile_fit * 0.24)
        + (commercial_fit * 0.18)
        + (logistics_fit * 0.16)
        + (compliance_fit * 0.12)
        + (supplier_reliability_fit * 0.08),
        4,
    )

    reasons = []
    if source_region_fit >= 0.95:
        reasons.append(f"matches your preferred region in {lot['region']}")
    if process_fit >= 0.95:
        reasons.append(f"fits your {lot['process'].lower()} process preference")
    if note_fit >= 0.95:
        reasons.append("overlaps with your preferred cup notes")
    if buyer_couriers and buyer_couriers.intersection(lot_couriers):
        reasons.append(f"supports your preferred courier: {', '.join(sorted(buyer_couriers.intersection(lot_couriers)))}")
    if lot.get("prior_notice_handler") and buyer.get("destination_country") == "US":
        reasons.append(f"has explicit Prior Notice ownership via {lot['prior_notice_handler']}")
    if supplier_moq:
        reasons.append(f"fits around supplier MOQ of {supplier_moq}kg")

    return {
        "id": f"live_rec_{buyer['id']}_{lot['id']}",
        "buyer_id": buyer["id"],
        "lot_id": lot["id"],
        "model_version": "rules-live-v2",
        "recommendation_score": recommendation_score,
        "recommendation_reason": "Recommended because it " + ", ".join(reasons[:3]) + ".",
        "lot_name": lot["lot_name"],
        "region": lot["region"],
        "process": lot["process"],
        "cup_score": lot["cup_score"],
        "supplier_name": lot["supplier_name"],
    }


def recommend_default_lots(lots: list[dict], limit: int = 1) -> list[dict]:
    eligible = [
        lot for lot in lots
        if lot["export_ready"] and lot["sample_ready"] and lot["compliance_ready"]
    ]
    eligible.sort(
        key=lambda lot: (
            float(lot.get("supplier_average_rating") or 0),
            float(lot.get("cup_score") or 0),
            -float(lot.get("price_per_kg") or 0),
        ),
        reverse=True,
    )
    recommendations = []
    for lot in eligible[:limit]:
        reasons = [
            "is fully export-, sample-, and compliance-ready",
            f"has a strong cup score of {lot['cup_score']}" if lot.get("cup_score") else "is cupping well",
        ]
        if lot.get("supplier_review_count"):
            reasons.append(
                f"is backed by {lot['supplier_review_count']} supplier review"
                + ("" if lot["supplier_review_count"] == 1 else "s")
            )
        recommendations.append(
            {
                "id": f"default_rec_{lot['id']}",
                "buyer_id": None,
                "lot_id": lot["id"],
                "model_version": "default-catalog-v1",
                "recommendation_score": round(
                    (
                        (float(lot.get("cup_score") or 0) / 100) * 0.6
                        + min(float(lot.get("supplier_average_rating") or 0) / 5, 1) * 0.25
                        + 0.15
                    ),
                    4,
                ),
                "recommendation_reason": "Recommended because it " + ", ".join(reasons[:3]) + ".",
                "lot_name": lot["lot_name"],
                "region": lot["region"],
                "process": lot["process"],
                "cup_score": lot["cup_score"],
                "supplier_name": lot["supplier_name"],
                "is_default": True,
            }
        )
    return recommendations


def recommend_for_buyer(buyer: dict | None, lots: list[dict], limit: int = 6) -> list[dict]:
    if not buyer:
        return recommend_default_lots(lots, limit=1)
    survey = get_buyer_survey(buyer["id"])
    if not survey:
        return recommend_default_lots(lots, limit=1)
    scored = [score_lot_for_buyer(buyer, lot) for lot in lots]
    filtered = [entry for entry in scored if entry is not None]
    filtered.sort(key=lambda item: item["recommendation_score"], reverse=True)
    return filtered[:limit]


def get_admin_summary() -> dict:
    supplier_readiness = query_all(
        """
        SELECT
          sr.*,
          s.region,
          s.contact_name,
          s.contact_email,
          s.created_at,
          COALESCE(srs.average_rating, 0) AS average_rating,
          COALESCE(srs.review_count, 0) AS review_count
        FROM supplier_readiness sr
        JOIN suppliers s ON s.id = sr.id
        LEFT JOIN supplier_review_summary srs ON srs.supplier_id = s.id
        ORDER BY s.created_at DESC
        """
    )
    inquiries = query_all(
        """
        SELECT
          i.id,
          i.shipment_status,
          i.tracking_number,
          i.courier,
          i.prior_notice_required,
          i.prior_notice_filed,
          i.prior_notice_filed_by,
          i.buyer_message,
          i.source_surface,
          i.buyer_id,
          i.supplier_id,
          b.company_name AS buyer_name,
          COALESCE(brs.average_rating, 0) AS buyer_average_rating,
          COALESCE(brs.review_count, 0) AS buyer_review_count,
          s.company_name AS supplier_name,
          COALESCE(srs.average_rating, 0) AS supplier_average_rating,
          COALESCE(srs.review_count, 0) AS supplier_review_count,
          l.lot_name
        FROM buyer_inquiries i
        JOIN buyers b ON b.id = i.buyer_id
        JOIN suppliers s ON s.id = i.supplier_id
        JOIN coffee_lots l ON l.id = i.lot_id
        LEFT JOIN buyer_review_summary brs ON brs.buyer_id = b.id
        LEFT JOIN supplier_review_summary srs ON srs.supplier_id = s.id
        ORDER BY i.created_at DESC
        """
    )
    metrics = query_one(
        """
        WITH supplier_counts AS (
          SELECT
            COUNT(*)::float AS total,
            SUM(CASE WHEN export_ready THEN 1 ELSE 0 END)::float AS export_ready_count,
            SUM(CASE WHEN sample_ready THEN 1 ELSE 0 END)::float AS sample_ready_count
          FROM supplier_readiness
        ),
        inquiry_counts AS (
          SELECT
            COUNT(*) FILTER (WHERE shipment_status IN ('shipped', 'delivered', 'closed'))::float AS shipped_count,
            COUNT(*)::float AS inquiry_count
          FROM buyer_inquiries
        ),
        rec_counts AS (
          SELECT
            COUNT(*) FILTER (WHERE interaction_type = 'recommendation_click')::float AS clicks,
            COUNT(*) FILTER (WHERE interaction_type = 'sample_request')::float AS sample_requests
          FROM buyer_lot_interactions
        )
        SELECT
          (SELECT COUNT(*) FROM buyers) AS buyer_count,
          (SELECT COUNT(*) FROM suppliers) AS supplier_count,
          COALESCE(ROUND((export_ready_count / NULLIF(total, 0)) * 100), 0) AS export_ready_pct,
          COALESCE(ROUND((sample_ready_count / NULLIF(total, 0)) * 100), 0) AS sample_ready_pct,
          COALESCE(ROUND((shipped_count / NULLIF(inquiry_count, 0)) * 100), 0) AS sample_to_shipment_pct,
          COALESCE(ROUND((LEAST(sample_requests, clicks) / NULLIF(clicks, 0)) * 100), 0) AS recommendation_to_inquiry_pct
        FROM supplier_counts, inquiry_counts, rec_counts
        """
    ) or {}
    return {
        "supplierReadiness": supplier_readiness,
        "inquiries": inquiries,
        "metrics": metrics,
    }


def get_inquiries_for_user(current_user: dict | None) -> list[dict]:
    if not current_user:
        return []
    if current_user.get("role") == "admin":
        return get_admin_summary()["inquiries"]
    if current_user.get("role") == "buyer" and current_user.get("buyer_id"):
        return query_all(
            """
            SELECT
              i.id,
              i.shipment_status,
              i.tracking_number,
              i.courier,
              i.prior_notice_required,
              i.prior_notice_filed,
              i.prior_notice_filed_by,
              i.buyer_message,
              i.source_surface,
              i.buyer_id,
              i.supplier_id,
              b.company_name AS buyer_name,
              COALESCE(brs.average_rating, 0) AS buyer_average_rating,
              COALESCE(brs.review_count, 0) AS buyer_review_count,
              s.company_name AS supplier_name,
              COALESCE(srs.average_rating, 0) AS supplier_average_rating,
              COALESCE(srs.review_count, 0) AS supplier_review_count,
              l.lot_name
            FROM buyer_inquiries i
            JOIN buyers b ON b.id = i.buyer_id
            JOIN suppliers s ON s.id = i.supplier_id
            JOIN coffee_lots l ON l.id = i.lot_id
            LEFT JOIN buyer_review_summary brs ON brs.buyer_id = b.id
            LEFT JOIN supplier_review_summary srs ON srs.supplier_id = s.id
            WHERE i.buyer_id = %s
            ORDER BY i.created_at DESC
            """,
            (current_user["buyer_id"],),
        )
    if current_user.get("role") == "supplier" and current_user.get("supplier_id"):
        return query_all(
            """
            SELECT
              i.id,
              i.shipment_status,
              i.tracking_number,
              i.courier,
              i.prior_notice_required,
              i.prior_notice_filed,
              i.prior_notice_filed_by,
              i.buyer_message,
              i.source_surface,
              i.buyer_id,
              i.supplier_id,
              b.company_name AS buyer_name,
              COALESCE(brs.average_rating, 0) AS buyer_average_rating,
              COALESCE(brs.review_count, 0) AS buyer_review_count,
              s.company_name AS supplier_name,
              COALESCE(srs.average_rating, 0) AS supplier_average_rating,
              COALESCE(srs.review_count, 0) AS supplier_review_count,
              l.lot_name
            FROM buyer_inquiries i
            JOIN buyers b ON b.id = i.buyer_id
            JOIN suppliers s ON s.id = i.supplier_id
            JOIN coffee_lots l ON l.id = i.lot_id
            LEFT JOIN buyer_review_summary brs ON brs.buyer_id = b.id
            LEFT JOIN supplier_review_summary srs ON srs.supplier_id = s.id
            WHERE i.supplier_id = %s
            ORDER BY i.created_at DESC
            """,
            (current_user["supplier_id"],),
        )
    return []


def get_bootstrap(current_user: dict | None) -> dict:
    lots = get_catalog_lots()
    buyers = get_buyers()
    context_buyer = None
    buyer_profile = None
    supplier_profile = None
    survey_required = False
    recommendation_mode = "default"
    if current_user and current_user.get("role") == "buyer" and current_user.get("buyer_id"):
        buyer_profile = get_buyer_profile(current_user["buyer_id"])
        context_buyer = buyer_profile
        survey_required = not bool(buyer_profile and buyer_profile.get("survey_completed"))
        recommendation_mode = "personalized" if not survey_required else "default"
    elif current_user and current_user.get("role") == "supplier" and current_user.get("supplier_id"):
        supplier_profile = get_supplier_profile(current_user["supplier_id"])

    recommendations = recommend_for_buyer(context_buyer, lots)
    payload = {
        "currentUser": current_user,
        "recommendationContextBuyer": context_buyer,
        "recommendationMode": recommendation_mode,
        "surveyRequired": survey_required,
        "lots": lots,
        "recommendations": recommendations,
        "buyers": [],
        "supplierReadiness": [],
        "inquiries": get_inquiries_for_user(current_user),
        "buyerProfile": buyer_profile,
        "supplierProfile": supplier_profile,
        "buyerReviews": get_buyer_reviews(current_user["buyer_id"]) if current_user and current_user.get("role") == "buyer" and current_user.get("buyer_id") else [],
        "supplierReviews": get_supplier_reviews(current_user["supplier_id"]) if current_user and current_user.get("role") == "supplier" and current_user.get("supplier_id") else [],
        "metrics": {
            "buyer_count": len(buyers),
            "supplier_count": len(query_all("SELECT id FROM suppliers")),
        },
    }

    if current_user and current_user.get("role") == "admin":
        admin = get_admin_summary()
        payload["buyers"] = buyers
        payload["supplierReadiness"] = admin["supplierReadiness"]
        payload["inquiries"] = admin["inquiries"]
        payload["metrics"] = admin["metrics"]

    return {
        **payload,
    }


def ensure_demo_auth_records() -> None:
    admin_exists = query_one("SELECT id FROM app_users WHERE role = 'admin' LIMIT 1")
    if not admin_exists:
        create_auth_user(
            email="admin@beanai.local",
            password="Admin123!",
            role="admin",
            display_name="Platform Admin",
        )

    for supplier in query_all(
        "SELECT id, company_name, contact_name, contact_email FROM suppliers WHERE contact_email IS NOT NULL"
    ):
        existing = query_one(
            "SELECT id FROM app_users WHERE supplier_id = %s OR email = %s LIMIT 1",
            (supplier["id"], supplier["contact_email"]),
        )
        if not existing:
            create_auth_user(
                email=supplier["contact_email"],
                password="DemoSupplier123!",
                role="supplier",
                display_name=supplier["contact_name"] or supplier["company_name"],
                supplier_id=supplier["id"],
            )

    for buyer in query_all(
        "SELECT id, company_name, contact_name, contact_email FROM buyers WHERE contact_email IS NOT NULL"
    ):
        existing = query_one(
            "SELECT id FROM app_users WHERE buyer_id = %s OR email = %s LIMIT 1",
            (buyer["id"], buyer["contact_email"]),
        )
        if not existing:
            create_auth_user(
                email=buyer["contact_email"],
                password="DemoBuyer123!",
                role="buyer",
                display_name=buyer["contact_name"] or buyer["company_name"],
                buyer_id=buyer["id"],
            )


class AppHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        return

    def _send(self, status: int, body: bytes, content_type: str, extra_headers: list[tuple[str, str]] | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for key, value in extra_headers or []:
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, payload: dict | list, status: int = 200, extra_headers: list[tuple[str, str]] | None = None) -> None:
        self._send(
            status,
            json.dumps(payload, default=self._json_default).encode("utf-8"),
            "application/json",
            extra_headers=extra_headers,
        )

    @staticmethod
    def _json_default(value):
        if isinstance(value, Decimal):
            return float(value)
        if hasattr(value, "isoformat"):
            return value.isoformat()
        return str(value)

    def _serve_index(self) -> None:
        body = (STATIC_DIR / "index.html").read_bytes()
        self._send(200, body, "text/html; charset=utf-8")

    def _serve_static(self, path: str) -> None:
        relative_path = path.removeprefix("/static/")
        file_path = (STATIC_DIR / relative_path).resolve()
        if not str(file_path).startswith(str(STATIC_DIR.resolve())) or not file_path.exists():
            self._send_json({"error": "Not found"}, 404)
            return
        content_type = "text/plain; charset=utf-8"
        if file_path.suffix == ".css":
            content_type = "text/css; charset=utf-8"
        elif file_path.suffix == ".js":
            content_type = "application/javascript; charset=utf-8"
        elif file_path.suffix == ".html":
            content_type = "text/html; charset=utf-8"
        self._send(200, file_path.read_bytes(), content_type)

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def _get_cookie_value(self, key: str) -> str | None:
        cookie_header = self.headers.get("Cookie")
        if not cookie_header:
            return None
        parsed = cookies.SimpleCookie()
        parsed.load(cookie_header)
        morsel = parsed.get(key)
        return morsel.value if morsel else None

    def _current_user(self) -> dict | None:
        return get_current_user_from_token(self._get_cookie_value(SESSION_COOKIE))

    def _session_cookie_headers(self, token: str) -> list[tuple[str, str]]:
        return [
            (
                "Set-Cookie",
                f"{SESSION_COOKIE}={token}; HttpOnly; Path=/; Max-Age={SESSION_MAX_AGE}; SameSite=Lax",
            )
        ]

    def _clear_session_cookie_headers(self) -> list[tuple[str, str]]:
        return [
            (
                "Set-Cookie",
                f"{SESSION_COOKIE}=; HttpOnly; Path=/; Max-Age=0; SameSite=Lax",
            )
        ]

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith("/static/"):
            return self._serve_static(path)
        if path == "/api/bootstrap":
            return self._send_json(get_bootstrap(self._current_user()))
        if path == "/api/session":
            return self._send_json({"currentUser": self._current_user()})
        if path == "/api/buyers":
            user = self._current_user()
            if not user or user.get("role") != "admin":
                return self._send_json({"error": "Admin access required"}, 403)
            return self._send_json(query_all("SELECT * FROM buyers ORDER BY created_at DESC"))
        if path == "/api/suppliers":
            user = self._current_user()
            if not user or user.get("role") != "admin":
                return self._send_json({"error": "Admin access required"}, 403)
            return self._send_json(query_all("SELECT * FROM suppliers ORDER BY created_at DESC"))
        if path.startswith("/api/lots/"):
            lot_id = path.split("/")[-1]
            lot = query_one(
                """
                SELECT
                  l.*,
                  s.company_name AS supplier_name,
                  s.sample_couriers,
                  s.sample_size_grams,
                  s.sample_price,
                  s.sample_shipping_days,
                  s.sample_prep_days,
                  s.sample_shipping_paid_by,
                  s.prior_notice_handler,
                  s.description AS supplier_description,
                  s.certifications,
                  COALESCE(srs.average_rating, 0) AS supplier_average_rating,
                  COALESCE(srs.review_count, 0) AS supplier_review_count
                FROM coffee_lots l
                JOIN suppliers s ON s.id = l.supplier_id
                LEFT JOIN supplier_review_summary srs ON srs.supplier_id = s.id
                WHERE l.id = %s
                """,
                (lot_id,),
            )
            if not lot:
                return self._send_json({"error": "Lot not found"}, 404)
            similar = query_all(
                """
                SELECT
                  l.id,
                  l.lot_name,
                  l.region,
                  l.process,
                  l.cup_score,
                  s.company_name AS supplier_name
                FROM coffee_lots l
                JOIN suppliers s ON s.id = l.supplier_id
                WHERE l.id <> %s
                ORDER BY
                  CASE WHEN l.region = %s THEN 0 ELSE 1 END,
                  CASE WHEN l.process = %s THEN 0 ELSE 1 END,
                  ABS(COALESCE(l.cup_score, 0) - COALESCE(%s, 0))
                LIMIT 3
                """,
                (lot_id, lot["region"], lot["process"], lot["cup_score"]),
            )
            return self._send_json(
                {
                    "lot": lot,
                    "similar": similar,
                    "supplierReviews": get_supplier_reviews(lot["supplier_id"]),
                }
            )

        if path in SPA_ROUTES or path.startswith("/coffee/"):
            return self._serve_index()

        self._send_json({"error": "Not found"}, 404)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path not in {
            "/api/suppliers",
            "/api/buyers",
            "/api/auth/signin",
            "/api/auth/signout",
            "/api/inquiries",
            "/api/interactions",
            "/api/recommendation-survey",
            "/api/supplier-reviews",
            "/api/buyer-reviews",
        }:
            return self._send_json({"error": "Not found"}, 404)

        try:
            payload = self._read_json_body()
        except json.JSONDecodeError:
            return self._send_json({"error": "Invalid JSON"}, 400)

        if parsed.path == "/api/auth/signin":
            user = get_user_by_email(clean_text(payload.get("email", "")) or "")
            password = payload.get("password", "")
            if not user or not verify_password(password, user["password_hash"], user["password_salt"]):
                return self._send_json({"error": "Invalid email or password"}, 401)
            token = create_session_for_user(user["id"])
            current_user = get_current_user_from_token(token)
            return self._send_json(
                {"currentUser": current_user},
                200,
                extra_headers=self._session_cookie_headers(token),
            )

        if parsed.path == "/api/auth/signout":
            token = self._get_cookie_value(SESSION_COOKIE)
            if token:
                delete_session(token)
            return self._send_json(
                {"ok": True},
                200,
                extra_headers=self._clear_session_cookie_headers(),
            )

        if parsed.path == "/api/inquiries":
            current_user = self._current_user()
            if not current_user or current_user.get("role") != "buyer" or not current_user.get("buyer_id"):
                return self._send_json({"error": "Buyer sign-in required"}, 403)
            lot_id = clean_text(payload.get("lotId"))
            if not lot_id:
                return self._send_json({"error": "Missing required fields: lotId"}, 400)
            lot = query_one(
                """
                SELECT
                  l.id,
                  l.supplier_id,
                  l.export_ready,
                  l.sample_ready,
                  l.compliance_ready,
                  s.sample_size_grams,
                  s.prior_notice_handler
                FROM coffee_lots l
                JOIN suppliers s ON s.id = l.supplier_id
                WHERE l.id = %s
                """,
                (lot_id,),
            )
            if not lot:
                return self._send_json({"error": "Lot not found"}, 404)
            if not lot["sample_ready"]:
                return self._send_json({"error": "This lot is not ready for sample requests yet"}, 400)
            if not lot["export_ready"] or not lot["compliance_ready"]:
                return self._send_json({"error": "This lot is missing export or compliance readiness"}, 400)
            inquiry_id = make_entity_id("inq", lot_id)
            destination_country = clean_text(payload.get("destinationCountry")) or current_user.get("destination_country") or "US"
            requested_sample_grams = clean_number(payload.get("requestedSampleGrams")) or lot.get("sample_size_grams")
            source_surface = clean_text(payload.get("sourceSurface")) or "lot_detail"
            buyer_message = clean_text(payload.get("message"))
            prior_notice_required = destination_country == "US"
            prior_notice_filed_by = lot.get("prior_notice_handler") if prior_notice_required else None
            execute(
                """
                INSERT INTO buyer_inquiries (
                  id, buyer_id, supplier_id, lot_id, destination_country, requested_sample_grams,
                  shipment_status, prior_notice_required, prior_notice_filed, prior_notice_filed_by,
                  buyer_message, source_surface
                ) VALUES (
                  %s, %s, %s, %s, %s, %s,
                  'new', %s, FALSE, %s,
                  %s, %s
                )
                """,
                (
                  inquiry_id,
                  current_user["buyer_id"],
                  lot["supplier_id"],
                  lot_id,
                  destination_country,
                  requested_sample_grams,
                  prior_notice_required,
                  prior_notice_filed_by,
                  buyer_message,
                  source_surface,
                ),
            )
            log_buyer_interaction(
                buyer_id=current_user["buyer_id"],
                lot_id=lot_id,
                interaction_type="inquiry",
                source_surface=source_surface,
            )
            log_buyer_interaction(
                buyer_id=current_user["buyer_id"],
                lot_id=lot_id,
                interaction_type="sample_request",
                source_surface=source_surface,
            )
            return self._send_json(
                {
                    "id": inquiry_id,
                    "shipmentStatus": "new",
                    "destinationCountry": destination_country,
                    "requestedSampleGrams": requested_sample_grams,
                    "priorNoticeRequired": prior_notice_required,
                    "priorNoticeFiledBy": prior_notice_filed_by,
                },
                201,
            )

        if parsed.path == "/api/interactions":
            current_user = self._current_user()
            if not current_user or current_user.get("role") != "buyer" or not current_user.get("buyer_id"):
                return self._send_json({"ok": True}, 200)
            lot_id = clean_text(payload.get("lotId"))
            interaction_type = clean_text(payload.get("interactionType"))
            if not lot_id or not interaction_type:
                return self._send_json({"error": "Missing required fields: lotId, interactionType"}, 400)
            allowed_interactions = {"lot_view", "recommendation_click", "similar_lot_click", "catalog_click"}
            if interaction_type not in allowed_interactions:
                return self._send_json({"error": "Unsupported interaction type"}, 400)
            log_buyer_interaction(
                buyer_id=current_user["buyer_id"],
                lot_id=lot_id,
                interaction_type=interaction_type,
                source_surface=clean_text(payload.get("sourceSurface")),
            )
            return self._send_json({"ok": True}, 201)

        if parsed.path == "/api/recommendation-survey":
            current_user = self._current_user()
            if not current_user or current_user.get("role") != "buyer" or not current_user.get("buyer_id"):
                return self._send_json({"error": "Buyer sign-in required"}, 403)
            save_recommendation_survey(current_user["buyer_id"], payload)
            return self._send_json({"ok": True}, 201)

        if parsed.path == "/api/supplier-reviews":
            current_user = self._current_user()
            if not current_user or current_user.get("role") != "buyer" or not current_user.get("buyer_id"):
                return self._send_json({"error": "Buyer sign-in required"}, 403)
            supplier_id = clean_text(payload.get("supplierId"))
            rating = int(payload.get("rating") or 0)
            if not supplier_id or rating not in {1, 2, 3, 4, 5}:
                return self._send_json({"error": "Valid supplierId and rating are required"}, 400)
            if not query_one("SELECT id FROM suppliers WHERE id = %s", (supplier_id,)):
                return self._send_json({"error": "Supplier not found"}, 404)
            review = create_supplier_review(
                supplier_id=supplier_id,
                reviewer_name=current_user.get("display_name") or current_user["email"],
                reviewer_role="buyer",
                reviewer_company=current_user.get("buyer_name"),
                rating=rating,
                review_text=clean_text(payload.get("reviewText")),
            )
            return self._send_json(review, 201)

        if parsed.path == "/api/buyer-reviews":
            current_user = self._current_user()
            if not current_user or current_user.get("role") != "supplier" or not current_user.get("supplier_id"):
                return self._send_json({"error": "Supplier sign-in required"}, 403)
            buyer_id = clean_text(payload.get("buyerId"))
            rating = int(payload.get("rating") or 0)
            if not buyer_id or rating not in {1, 2, 3, 4, 5}:
                return self._send_json({"error": "Valid buyerId and rating are required"}, 400)
            if not query_one("SELECT id FROM buyers WHERE id = %s", (buyer_id,)):
                return self._send_json({"error": "Buyer not found"}, 404)
            review = create_buyer_review(
                buyer_id=buyer_id,
                reviewer_name=current_user.get("display_name") or current_user["email"],
                reviewer_role="supplier",
                reviewer_company=current_user.get("supplier_name"),
                rating=rating,
                review_text=clean_text(payload.get("reviewText")),
            )
            return self._send_json(review, 201)

        if parsed.path == "/api/suppliers":
            required = ["companyName", "contactEmail", "region", "priorNoticeHandler"]
        else:
            required = ["companyName", "contactEmail", "buyerType", "destinationCountry"]
        missing = [field for field in required if not payload.get(field)]
        if missing:
            return self._send_json({"error": f"Missing required fields: {', '.join(missing)}"}, 400)
        password = clean_text(payload.get("password"))
        if password and len(password) < 8:
            return self._send_json({"error": "Password must be at least 8 characters long"}, 400)

        try:
            if parsed.path == "/api/suppliers":
                if password:
                    ensure_email_can_create_role(clean_text(payload.get("contactEmail")), "supplier")
                created = create_supplier(payload)
                if password:
                    auth_user = create_auth_user(
                        email=created["companyName"] and clean_text(payload["contactEmail"]),
                        password=password,
                        role="supplier",
                        display_name=clean_text(payload.get("contactName")) or created["companyName"],
                        supplier_id=created["id"],
                    )
                    token = create_session_for_user(auth_user["id"])
                    return self._send_json(
                        {**created, "currentUser": get_current_user_from_token(token)},
                        201,
                        extra_headers=self._session_cookie_headers(token),
                    )
            else:
                if password:
                    ensure_email_can_create_role(clean_text(payload.get("contactEmail")), "buyer")
                created = create_buyer(payload)
                if password:
                    auth_user = create_auth_user(
                        email=clean_text(payload["contactEmail"]),
                        password=password,
                        role="buyer",
                        display_name=clean_text(payload.get("contactName")) or created["companyName"],
                        buyer_id=created["id"],
                    )
                    token = create_session_for_user(auth_user["id"])
                    return self._send_json(
                        {**created, "currentUser": get_current_user_from_token(token)},
                        201,
                        extra_headers=self._session_cookie_headers(token),
                    )
        except ValueError as exc:
            return self._send_json({"error": str(exc)}, 400)
        except Exception as exc:  # pragma: no cover
            return self._send_json({"error": str(exc)}, 500)
        return self._send_json(created, 201)


def main() -> None:
    ensure_demo_auth_records()
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer(("127.0.0.1", port), AppHandler)
    print(f"Server running at http://127.0.0.1:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
