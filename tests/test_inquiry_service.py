from __future__ import annotations

import pytest
from fastapi import HTTPException

from product.backend.app.services.inquiries import InquiryService


class FakeInquiryRepository:
    def __init__(self, lot_context):
        self.lot_context = lot_context
        self.calls = []

    def get_lot_request_context(self, lot_id: str):
        return self.lot_context

    def create_inquiry(self, **kwargs):
        self.calls.append(kwargs)
        return "inq_001"


class FakeRecommendationRepository:
    def __init__(self):
        self.logged = []

    def log_buyer_interaction(self, **kwargs):
        self.logged.append(kwargs)


def test_create_inquiry_requires_ready_lot():
    inquiry_service = InquiryService(
        FakeInquiryRepository(
            {
                "id": "lot_001",
                "supplier_id": "supplier_001",
                "export_ready": True,
                "sample_ready": False,
                "compliance_ready": True,
                "sample_size_grams": 200,
                "prior_notice_handler": "supplier",
            }
        ),
        FakeRecommendationRepository(),
    )

    with pytest.raises(HTTPException) as exc:
        inquiry_service.create_inquiry(
            {"role": "buyer", "buyer_id": "buyer_001", "destination_country": "US"},
            {"lotId": "lot_001", "sourceSurface": "catalog_detail"},
        )

    assert exc.value.status_code == 400
    assert "not ready for sample requests" in str(exc.value.detail)


def test_create_inquiry_writes_record_and_telemetry():
    inquiry_repo = FakeInquiryRepository(
        {
            "id": "lot_001",
            "supplier_id": "supplier_001",
            "export_ready": True,
            "sample_ready": True,
            "compliance_ready": True,
            "sample_size_grams": 200,
            "prior_notice_handler": "supplier",
        }
    )
    recommendation_repo = FakeRecommendationRepository()
    inquiry_service = InquiryService(inquiry_repo, recommendation_repo)

    result = inquiry_service.create_inquiry(
        {"role": "buyer", "buyer_id": "buyer_001", "destination_country": "US"},
        {
            "lotId": "lot_001",
            "destinationCountry": "US",
            "requestedSampleGrams": 250,
            "message": "Please include roast profile notes.",
            "sourceSurface": "recommended_detail",
        },
    )

    assert result["id"] == "inq_001"
    assert result["priorNoticeRequired"] is True
    assert inquiry_repo.calls[0]["requested_sample_grams"] == 250
    assert {entry["interaction_type"] for entry in recommendation_repo.logged} == {"inquiry", "sample_request"}
