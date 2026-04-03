from __future__ import annotations

from fastapi import HTTPException


class BootstrapService:
    def __init__(self, marketplace_repo, recommendation_service, inquiry_service, review_repo, approval_repo):
        self.marketplace_repo = marketplace_repo
        self.recommendation_service = recommendation_service
        self.inquiry_service = inquiry_service
        self.review_repo = review_repo
        self.approval_repo = approval_repo

    def get_lot_detail(self, lot_id: str, user: dict | None) -> dict:
        lot = self.marketplace_repo.get_lot_detail(lot_id)
        if not lot:
            raise HTTPException(status_code=404, detail="Lot not found")
        similar = self.marketplace_repo.get_similar_lots(
            lot_id,
            lot.get("region"),
            lot.get("process"),
            lot.get("cup_score"),
        )
        can_review = False
        if user and user.get("role") == "buyer" and user.get("buyer_id"):
            can_review = self.inquiry_service.has_completed_relationship(user["buyer_id"], lot["supplier_id"])
        return {
            "lot": lot,
            "similar": similar,
            "supplierReviews": self.review_repo.get_supplier_reviews(lot["supplier_id"]),
            "canReviewSupplier": can_review,
        }

    def bootstrap(self, current_user: dict | None) -> dict:
        lots = self.marketplace_repo.get_catalog_lots()
        buyers = self.marketplace_repo.get_buyers()
        context_buyer = None
        buyer_profile = None
        supplier_profile = None
        survey_required = False
        recommendation_mode = "default"
        if current_user and current_user.get("role") == "buyer" and current_user.get("buyer_id"):
            buyer_profile = self.marketplace_repo.get_buyer_profile(current_user["buyer_id"])
            context_buyer = buyer_profile
            survey_required = not bool(buyer_profile and buyer_profile.get("survey_completed"))
            recommendation_mode = "personalized" if not survey_required else "default"
        elif current_user and current_user.get("role") == "supplier" and current_user.get("supplier_id"):
            supplier_profile = self.marketplace_repo.get_supplier_profile(current_user["supplier_id"])

        recommendations = self.recommendation_service.recommend_for_buyer(context_buyer, lots)
        payload = {
            "currentUser": current_user,
            "recommendationContextBuyer": context_buyer,
            "recommendationMode": recommendation_mode,
            "surveyRequired": survey_required,
            "lots": lots,
            "recommendations": recommendations,
            "buyers": [],
            "supplierReadiness": [],
            "inquiries": self.inquiry_service.get_inquiries_for_user(current_user),
            "buyerProfile": buyer_profile,
            "supplierProfile": supplier_profile,
            "buyerReviews": self.review_repo.get_buyer_reviews(current_user["buyer_id"]) if current_user and current_user.get("role") == "buyer" and current_user.get("buyer_id") else [],
            "supplierReviews": self.review_repo.get_supplier_reviews(current_user["supplier_id"]) if current_user and current_user.get("role") == "supplier" and current_user.get("supplier_id") else [],
            "profileChangeRequests": self.approval_repo.get_profile_change_requests_for_user(current_user),
            "metrics": {
                "buyer_count": len(buyers),
                "supplier_count": self.marketplace_repo.count_suppliers(),
            },
        }
        if current_user and current_user.get("role") == "admin":
            payload["buyers"] = buyers
            payload["supplierReadiness"] = self.marketplace_repo.get_supplier_readiness()
            payload["inquiries"] = self.inquiry_service.get_inquiries_for_user(current_user)
            payload["metrics"] = self.marketplace_repo.get_admin_metrics()
        return payload
