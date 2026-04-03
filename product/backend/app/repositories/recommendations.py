from __future__ import annotations

from ..db import execute, query_one
from ..utils import clean_array, clean_number, make_entity_id


class RecommendationRepository:
    def log_buyer_interaction(
        self,
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
                source_surface or "unknown",
            ),
        )

    def get_buyer_survey(self, buyer_id: str) -> dict | None:
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

    def save_recommendation_survey(self, buyer_id: str, payload: dict) -> None:
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
