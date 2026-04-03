from __future__ import annotations

import pytest
from fastapi import HTTPException

from product.backend.app.services.reviews import ReviewService


class FakeReviewRepository:
    def __init__(self):
        self.calls = []

    def create_supplier_review(self, **kwargs):
        self.calls.append(kwargs)
        return {"id": "suprev_001", "supplierId": kwargs["supplier_id"], "rating": kwargs["rating"]}

    def create_buyer_review(self, **kwargs):
        self.calls.append(kwargs)
        return {"id": "buyrev_001", "buyerId": kwargs["buyer_id"], "rating": kwargs["rating"]}


class FakeMarketplaceRepository:
    def __init__(self, *, supplier_exists=True, buyer_exists=True):
        self._supplier_exists = supplier_exists
        self._buyer_exists = buyer_exists

    def supplier_exists(self, supplier_id: str) -> bool:
        return self._supplier_exists

    def buyer_exists(self, buyer_id: str) -> bool:
        return self._buyer_exists


class FakeInquiryService:
    def __init__(self, completed: bool):
        self.completed = completed

    def has_completed_relationship(self, buyer_id: str, supplier_id: str) -> bool:
        return self.completed


def test_supplier_review_requires_completed_relationship():
    service = ReviewService(
        FakeReviewRepository(),
        FakeMarketplaceRepository(),
        FakeInquiryService(completed=False),
    )

    with pytest.raises(HTTPException) as exc:
        service.create_supplier_review(
            {"role": "buyer", "buyer_id": "buyer_001", "email": "buyer@example.com", "buyer_name": "Roaster"},
            {"supplierId": "supplier_001", "rating": 5, "reviewText": "Great"},
        )

    assert exc.value.status_code == 403
    assert "completed purchase relationship" in str(exc.value.detail)


def test_supplier_review_succeeds_once_relationship_exists():
    repo = FakeReviewRepository()
    service = ReviewService(
        repo,
        FakeMarketplaceRepository(),
        FakeInquiryService(completed=True),
    )

    result = service.create_supplier_review(
        {
            "role": "buyer",
            "buyer_id": "buyer_001",
            "email": "buyer@example.com",
            "display_name": "Maya",
            "buyer_name": "North Harbor",
        },
        {"supplierId": "supplier_001", "rating": 5, "reviewText": "Fast sampling and clean docs."},
    )

    assert result["rating"] == 5
    assert repo.calls[0]["reviewer_name"] == "Maya"
    assert repo.calls[0]["reviewer_company"] == "North Harbor"
