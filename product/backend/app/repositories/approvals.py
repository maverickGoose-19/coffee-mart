from __future__ import annotations

import json

from fastapi.encoders import jsonable_encoder

from ..db import execute, query_all
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
