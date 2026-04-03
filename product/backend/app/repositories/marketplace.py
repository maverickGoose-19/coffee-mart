from __future__ import annotations

from ..db import execute, query_all, query_one
from ..utils import (
    buyer_payload_to_row,
    supplier_is_compliance_ready,
    supplier_is_export_ready,
    supplier_is_sample_ready,
    supplier_payload_to_row,
)


class MarketplaceRepository:
    def existing_supplier_id_for_email(self, email: str | None) -> str | None:
        if not email:
            return None
        record = query_one(
            "SELECT id FROM suppliers WHERE contact_email = %s ORDER BY created_at DESC LIMIT 1",
            (email,),
        )
        return record["id"] if record else None

    def existing_buyer_id_for_email(self, email: str | None) -> str | None:
        if not email:
            return None
        record = query_one(
            "SELECT id FROM buyers WHERE contact_email = %s ORDER BY created_at DESC LIMIT 1",
            (email,),
        )
        return record["id"] if record else None

    def create_supplier(self, payload: dict) -> dict:
        row = supplier_payload_to_row(payload)
        existing_id = self.existing_supplier_id_for_email(row["contact_email"])
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
              sample_price, prior_notice_handler, wants_to_add_images, estate_image_url,
              coffee_image_url, gallery_image_urls, approval_status
            ) VALUES (
              %(id)s, %(company_name)s, %(contact_name)s, %(contact_email)s, %(contact_phone)s, %(region)s, %(website)s,
              %(altitude_meters)s, %(varietals)s, %(certifications)s, %(description)s, %(exports_internationally)s,
              %(export_partner_name)s, %(export_terms)s, %(min_export_order_kg)s, %(certificate_of_origin)s,
              %(phytosanitary_certificate)s, %(invoice_capability)s, %(can_ship_samples)s, %(sample_size_grams)s,
              %(sample_couriers)s, %(sample_shipping_paid_by)s, %(sample_shipping_days)s, %(sample_prep_days)s,
              %(sample_price)s, %(prior_notice_handler)s, %(wants_to_add_images)s, %(estate_image_url)s,
              %(coffee_image_url)s, %(gallery_image_urls)s, %(approval_status)s
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
              wants_to_add_images = EXCLUDED.wants_to_add_images,
              estate_image_url = EXCLUDED.estate_image_url,
              coffee_image_url = EXCLUDED.coffee_image_url,
              gallery_image_urls = EXCLUDED.gallery_image_urls,
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
            "estateImageUrl": row["estate_image_url"],
            "coffeeImageUrl": row["coffee_image_url"],
            "galleryImageUrls": row["gallery_image_urls"],
        }

    def create_buyer(self, payload: dict) -> dict:
        row = buyer_payload_to_row(payload)
        existing_id = self.existing_buyer_id_for_email(row["contact_email"])
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

    def supplier_exists(self, supplier_id: str) -> bool:
        return bool(query_one("SELECT id FROM suppliers WHERE id = %s", (supplier_id,)))

    def buyer_exists(self, buyer_id: str) -> bool:
        return bool(query_one("SELECT id FROM buyers WHERE id = %s", (buyer_id,)))

    def get_supplier_profile(self, supplier_id: str) -> dict | None:
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

    def get_buyer_profile(self, buyer_id: str) -> dict | None:
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

    def get_catalog_lots(self) -> list[dict]:
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
              l.harvest_year,
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
              s.estate_image_url,
              s.coffee_image_url,
              s.gallery_image_urls,
              COALESCE(srs.average_rating, 0) AS supplier_average_rating,
              COALESCE(srs.review_count, 0) AS supplier_review_count
            FROM coffee_lots l
            JOIN suppliers s ON s.id = l.supplier_id
            LEFT JOIN supplier_review_summary srs ON srs.supplier_id = s.id
            ORDER BY l.cup_score DESC NULLS LAST, l.lot_name ASC
            """
        )

    def get_lot_detail(self, lot_id: str) -> dict | None:
        return query_one(
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
              s.estate_image_url,
              s.coffee_image_url,
              s.gallery_image_urls,
              COALESCE(srs.average_rating, 0) AS supplier_average_rating,
              COALESCE(srs.review_count, 0) AS supplier_review_count
            FROM coffee_lots l
            JOIN suppliers s ON s.id = l.supplier_id
            LEFT JOIN supplier_review_summary srs ON srs.supplier_id = s.id
            WHERE l.id = %s
            """,
            (lot_id,),
        )

    def get_similar_lots(self, lot_id: str, region: str | None, process: str | None, cup_score) -> list[dict]:
        return query_all(
            """
            SELECT
              l.id,
              l.lot_name,
              l.region,
              l.process,
              l.cup_score,
              s.company_name AS supplier_name,
              s.coffee_image_url,
              s.estate_image_url
            FROM coffee_lots l
            JOIN suppliers s ON s.id = l.supplier_id
            WHERE l.id <> %s
            ORDER BY
              CASE WHEN l.region = %s THEN 0 ELSE 1 END,
              CASE WHEN l.process = %s THEN 0 ELSE 1 END,
              ABS(COALESCE(l.cup_score, 0) - COALESCE(%s, 0))
            LIMIT 3
            """,
            (lot_id, region, process, cup_score),
        )

    def get_buyers(self) -> list[dict]:
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

    def get_supplier_readiness(self) -> list[dict]:
        return query_all(
            """
            SELECT
              sr.*,
              s.region,
              s.contact_name,
              s.contact_email,
              s.created_at,
              s.estate_image_url,
              s.coffee_image_url,
              COALESCE(srs.average_rating, 0) AS average_rating,
              COALESCE(srs.review_count, 0) AS review_count
            FROM supplier_readiness sr
            JOIN suppliers s ON s.id = sr.id
            LEFT JOIN supplier_review_summary srs ON srs.supplier_id = s.id
            ORDER BY s.created_at DESC
            """
        )

    def get_admin_metrics(self) -> dict:
        return (
            query_one(
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
            )
            or {}
        )

    def list_suppliers_for_demo_auth(self) -> list[dict]:
        return query_all(
            "SELECT id, company_name, contact_name, contact_email FROM suppliers WHERE contact_email IS NOT NULL"
        )

    def list_buyers_for_demo_auth(self) -> list[dict]:
        return query_all(
            "SELECT id, company_name, contact_name, contact_email FROM buyers WHERE contact_email IS NOT NULL"
        )

    def count_suppliers(self) -> int:
        row = query_one("SELECT COUNT(*) AS count FROM suppliers")
        return int(row["count"]) if row else 0
