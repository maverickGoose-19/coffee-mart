from __future__ import annotations

from fastapi import HTTPException

from ..utils import clean_text


class ReviewService:
    def __init__(self, review_repo, marketplace_repo, inquiry_service):
        self.review_repo = review_repo
        self.marketplace_repo = marketplace_repo
        self.inquiry_service = inquiry_service

    def create_supplier_review(self, user: dict | None, payload: dict) -> dict:
        if not user or user.get("role") != "buyer":
            raise HTTPException(status_code=403, detail="Buyer sign-in required")
        if payload["rating"] not in {1, 2, 3, 4, 5}:
            raise HTTPException(status_code=400, detail="Valid supplierId and rating are required")
        if not user.get("buyer_id") or not self.inquiry_service.has_completed_relationship(user["buyer_id"], payload["supplierId"]):
            raise HTTPException(
                status_code=403,
                detail="Supplier reviews are only available after a completed purchase relationship is recorded.",
            )
        if not self.marketplace_repo.supplier_exists(payload["supplierId"]):
            raise HTTPException(status_code=404, detail="Supplier not found")
        return self.review_repo.create_supplier_review(
            supplier_id=payload["supplierId"],
            reviewer_name=user.get("display_name") or user["email"],
            reviewer_role="buyer",
            reviewer_company=user.get("buyer_name"),
            rating=payload["rating"],
            review_text=clean_text(payload.get("reviewText")),
        )

    def create_buyer_review(self, user: dict | None, payload: dict) -> dict:
        if not user or user.get("role") != "supplier":
            raise HTTPException(status_code=403, detail="Supplier sign-in required")
        if payload["rating"] not in {1, 2, 3, 4, 5}:
            raise HTTPException(status_code=400, detail="Valid buyerId and rating are required")
        if not user.get("supplier_id") or not self.inquiry_service.has_completed_relationship(payload["buyerId"], user["supplier_id"]):
            raise HTTPException(
                status_code=403,
                detail="Buyer reviews are only available after a completed purchase relationship is recorded.",
            )
        if not self.marketplace_repo.buyer_exists(payload["buyerId"]):
            raise HTTPException(status_code=404, detail="Buyer not found")
        return self.review_repo.create_buyer_review(
            buyer_id=payload["buyerId"],
            reviewer_name=user.get("display_name") or user["email"],
            reviewer_role="supplier",
            reviewer_company=user.get("supplier_name"),
            rating=payload["rating"],
            review_text=clean_text(payload.get("reviewText")),
        )
