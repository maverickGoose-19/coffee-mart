from __future__ import annotations

import json

from fastapi.encoders import jsonable_encoder

from ..db import execute, query_all, query_one
from ..utils import make_entity_id


class ApprovalRepository:
    def create_profile_change_request(
        self,
        *,
        entity_type: str,
        entity_id: str,
        requested_by_user_id: str,
        current_snapshot: dict,
        requested_snapshot: dict,
        changed_fields: list[str],
    ) -> dict:
        request_id = make_entity_id("chg", f"{entity_type}_{entity_id}")
        execute(
            """
            INSERT INTO profile_change_requests (
              id, entity_type, entity_id, requested_by_user_id,
              current_snapshot, requested_snapshot, changed_fields, status
            ) VALUES (%s, %s, %s, %s, %s::jsonb, %s::jsonb, %s, 'pending')
            """,
            (
                request_id,
                entity_type,
                entity_id,
                requested_by_user_id,
                json.dumps(jsonable_encoder(current_snapshot)),
                json.dumps(jsonable_encoder(requested_snapshot)),
                changed_fields,
            ),
        )
        return {
            "id": request_id,
            "entityType": entity_type,
            "entityId": entity_id,
            "changedFields": changed_fields,
            "status": "pending",
        }

    def get_profile_change_requests_for_user(self, user: dict | None) -> list[dict]:
        if not user:
            return []
        if user.get("role") == "admin":
            return query_all(
                """
                SELECT id, entity_type, entity_id, changed_fields, status, created_at
                FROM profile_change_requests
                ORDER BY created_at DESC
                LIMIT 25
                """
            )
        if user.get("role") == "buyer" and user.get("buyer_id"):
            return query_all(
                """
                SELECT id, entity_type, entity_id, changed_fields, status, created_at
                FROM profile_change_requests
                WHERE entity_type = 'buyer' AND entity_id = %s
                ORDER BY created_at DESC
                """,
                (user["buyer_id"],),
            )
        if user.get("role") == "supplier" and user.get("supplier_id"):
            return query_all(
                """
                SELECT id, entity_type, entity_id, changed_fields, status, created_at
                FROM profile_change_requests
                WHERE entity_type = 'supplier' AND entity_id = %s
                ORDER BY created_at DESC
                """,
                (user["supplier_id"],),
            )
        return []

    def get_change_request_by_id(self, request_id: str) -> dict | None:
        return query_one(
            """
            SELECT id, entity_type, entity_id, requested_by_user_id,
                   current_snapshot, requested_snapshot, changed_fields, status, created_at
            FROM profile_change_requests WHERE id = %s
            """,
            (request_id,),
        )

    def approve_change_request(self, request_id: str, reviewed_by_user_id: str) -> dict | None:
        """Mark as approved and apply requested_snapshot fields to the actual entity record."""
        row = self.get_change_request_by_id(request_id)
        if not row:
            return None
        execute(
            "UPDATE profile_change_requests SET status = 'approved', reviewed_by = %s WHERE id = %s",
            (reviewed_by_user_id, request_id),
        )
        snapshot = row["requested_snapshot"] if isinstance(row["requested_snapshot"], dict) else json.loads(row["requested_snapshot"])
        entity_type = row["entity_type"]
        entity_id = row["entity_id"]
        changed_fields = row["changed_fields"]
        if entity_type == "supplier":
            self._apply_supplier_snapshot(entity_id, snapshot, changed_fields)
        elif entity_type == "buyer":
            self._apply_buyer_snapshot(entity_id, snapshot, changed_fields)
        return {**row, "status": "approved"}

    def reject_change_request(self, request_id: str, reviewed_by_user_id: str) -> dict | None:
        """Mark as rejected — does NOT touch the live entity record."""
        row = self.get_change_request_by_id(request_id)
        if not row:
            return None
        execute(
            "UPDATE profile_change_requests SET status = 'rejected', reviewed_by = %s WHERE id = %s",
            (reviewed_by_user_id, request_id),
        )
        return {**row, "status": "rejected"}

    # ── field-name translation helpers ──────────────────────────────────────

    _SUPPLIER_CAMEL_TO_SNAKE = {
        "contactName": "contact_name",
        "contactPhone": "contact_phone",
        "website": "website",
        "altitudeMeters": "altitude_meters",
        "varietals": "varietals",
        "certifications": "certifications",
        "description": "description",
        "exportsInternationally": "exports_internationally",
        "exportPartnerName": "export_partner_name",
        "exportTerms": "export_terms",
        "minExportOrderKg": "min_export_order_kg",
        "canShipSamples": "can_ship_samples",
        "sampleSizeGrams": "sample_size_grams",
        "sampleCouriers": "sample_couriers",
        "sampleShippingPaidBy": "sample_shipping_paid_by",
        "sampleShippingDays": "sample_shipping_days",
        "samplePrepDays": "sample_prep_days",
        "samplePrice": "sample_price",
        "priorNoticeHandler": "prior_notice_handler",
        "estateImageUrl": "estate_image_url",
        "coffeeImageUrl": "coffee_image_url",
        "galleryImageUrls": "gallery_image_urls",
    }

    _BUYER_CAMEL_TO_SNAKE = {
        "contactName": "contact_name",
        "destinationCountry": "destination_country",
        "preferredRegions": "preferred_regions",
        "preferredVarietals": "preferred_varietals",
        "preferredProcesses": "preferred_processes",
        "targetTastingNotes": "target_tasting_notes",
        "preferredCertifications": "preferred_certifications",
        "minMoqKg": "min_moq_kg",
        "maxMoqKg": "max_moq_kg",
        "maxPricePerKg": "max_price_per_kg",
        "requiresSamples": "requires_samples",
        "preferredCouriers": "preferred_couriers",
        "needsUsComplianceSupport": "needs_us_compliance_support",
    }

    def _apply_supplier_snapshot(self, supplier_id: str, snapshot: dict, changed_fields: list[str]) -> None:
        mapping = self._SUPPLIER_CAMEL_TO_SNAKE
        set_parts, values = [], []
        for camel in changed_fields:
            snake = mapping.get(camel)
            if snake and camel in snapshot:
                set_parts.append(f"{snake} = %s")
                values.append(snapshot[camel])
        if not set_parts:
            return
        values.append(supplier_id)
        execute(f"UPDATE suppliers SET {', '.join(set_parts)} WHERE id = %s", tuple(values))

    def _apply_buyer_snapshot(self, buyer_id: str, snapshot: dict, changed_fields: list[str]) -> None:
        mapping = self._BUYER_CAMEL_TO_SNAKE
        set_parts, values = [], []
        for camel in changed_fields:
            snake = mapping.get(camel)
            if snake and camel in snapshot:
                set_parts.append(f"{snake} = %s")
                values.append(snapshot[camel])
        if not set_parts:
            return
        values.append(buyer_id)
        execute(f"UPDATE buyers SET {', '.join(set_parts)} WHERE id = %s", tuple(values))
