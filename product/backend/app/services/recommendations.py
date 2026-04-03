from __future__ import annotations

from fastapi import HTTPException


class RecommendationService:
    def __init__(self, recommendation_repo):
        self.recommendation_repo = recommendation_repo

    def create_interaction(self, user: dict | None, payload: dict) -> dict:
        if not user or user.get("role") != "buyer" or not user.get("buyer_id"):
            return {"ok": True}
        allowed = {"lot_view", "recommendation_click", "similar_lot_click", "catalog_click"}
        if payload["interactionType"] not in allowed:
            raise HTTPException(status_code=400, detail="Unsupported interaction type")
        self.recommendation_repo.log_buyer_interaction(
            buyer_id=user["buyer_id"],
            lot_id=payload["lotId"],
            interaction_type=payload["interactionType"],
            source_surface=payload.get("sourceSurface"),
        )
        return {"ok": True}

    def save_survey(self, user: dict | None, payload: dict) -> dict:
        if not user or user.get("role") != "buyer" or not user.get("buyer_id"):
            raise HTTPException(status_code=403, detail="Buyer sign-in required")
        self.recommendation_repo.save_recommendation_survey(user["buyer_id"], payload)
        return {"ok": True}

    def score_lot_for_buyer(self, buyer: dict, lot: dict) -> dict | None:
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
        if process_fit >= 0.95 and lot.get("process"):
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
            "estate_image_url": lot.get("estate_image_url"),
            "coffee_image_url": lot.get("coffee_image_url"),
            "gallery_image_urls": lot.get("gallery_image_urls") or [],
        }

    def recommend_default_lots(self, lots: list[dict], limit: int = 1) -> list[dict]:
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
                    "estate_image_url": lot.get("estate_image_url"),
                    "coffee_image_url": lot.get("coffee_image_url"),
                    "gallery_image_urls": lot.get("gallery_image_urls") or [],
                    "is_default": True,
                }
            )
        return recommendations

    def recommend_for_buyer(self, buyer: dict | None, lots: list[dict], limit: int = 6) -> list[dict]:
        if not buyer:
            return self.recommend_default_lots(lots, limit=1)
        survey = self.recommendation_repo.get_buyer_survey(buyer["id"])
        if not survey:
            return self.recommend_default_lots(lots, limit=1)
        scored = [self.score_lot_for_buyer(buyer, lot) for lot in lots]
        filtered = [entry for entry in scored if entry is not None]
        filtered.sort(key=lambda item: item["recommendation_score"], reverse=True)
        return filtered[:limit]
