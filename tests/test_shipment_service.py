"""
Tests for MAV-6: Inquiry Shipment Status — 7-Stage State Machine

Covers:
- All 8 valid transitions (happy paths)
- Invalid transitions → 422
- Role ownership violations → 403
- Unauthenticated → 401
- Not found → 404
- Business rules: tracking required for shipped, prior_notice guard
- deal_closed interaction logged on close
"""
from __future__ import annotations

import pytest
from fastapi import HTTPException

from product.backend.app.services.inquiries import InquiryService


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------

class FakeInquiryRepository:
    def __init__(self, inquiry: dict | None = None, lot_context: dict | None = None):
        self._inquiry = inquiry
        self._lot_context = lot_context
        self.updated: dict | None = None

    def get_lot_request_context(self, lot_id: str):
        return self._lot_context

    def create_inquiry(self, **kwargs):
        return "inq_001"

    def get_inquiry_by_id(self, inquiry_id: str):
        return self._inquiry

    def update_inquiry_shipment(self, inquiry_id: str, *, shipment_status: str, **kwargs):
        self.updated = {"id": inquiry_id, "shipment_status": shipment_status, **kwargs}
        return self.updated

    def has_completed_relationship(self, buyer_id, supplier_id):
        return False

    def get_admin_inquiries(self):
        return []

    def get_buyer_inquiries(self, buyer_id):
        return []

    def get_supplier_inquiries(self, supplier_id):
        return []


class FakeRecommendationRepository:
    def __init__(self):
        self.logged: list[dict] = []

    def log_buyer_interaction(self, **kwargs):
        self.logged.append(kwargs)


def make_service(inquiry: dict | None = None) -> tuple[InquiryService, FakeInquiryRepository, FakeRecommendationRepository]:
    inquiry_repo = FakeInquiryRepository(inquiry=inquiry)
    rec_repo = FakeRecommendationRepository()
    svc = InquiryService(inquiry_repo, rec_repo)
    return svc, inquiry_repo, rec_repo


def base_inquiry(**overrides) -> dict:
    defaults = {
        "id": "inq_001",
        "buyer_id": "buyer_001",
        "supplier_id": "supplier_001",
        "lot_id": "lot_001",
        "destination_country": "DE",
        "shipment_status": "new",
        "tracking_number": None,
        "courier": None,
        "prior_notice_required": False,
        "prior_notice_filed": False,
        "prior_notice_filed_by": None,
        "buyer_message": None,
        "source_surface": "catalog_detail",
    }
    return {**defaults, **overrides}


# ---------------------------------------------------------------------------
# Auth / 401
# ---------------------------------------------------------------------------

def test_unauthenticated_returns_401():
    svc, _, _ = make_service(base_inquiry())
    with pytest.raises(HTTPException) as exc:
        svc.update_shipment_status(None, "inq_001", {"shipmentStatus": "approved"})
    assert exc.value.status_code == 401


def test_missing_role_returns_401():
    svc, _, _ = make_service(base_inquiry())
    with pytest.raises(HTTPException) as exc:
        svc.update_shipment_status({}, "inq_001", {"shipmentStatus": "approved"})
    assert exc.value.status_code == 401


# ---------------------------------------------------------------------------
# 404
# ---------------------------------------------------------------------------

def test_inquiry_not_found_returns_404():
    svc, _, _ = make_service(inquiry=None)
    with pytest.raises(HTTPException) as exc:
        svc.update_shipment_status(
            {"role": "admin"},
            "inq_missing",
            {"shipmentStatus": "approved"},
        )
    assert exc.value.status_code == 404


# ---------------------------------------------------------------------------
# Valid transitions — happy paths
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("from_status,to_status,user", [
    ("new",                    "approved",               {"role": "supplier", "supplier_id": "supplier_001"}),
    ("new",                    "approved",               {"role": "admin"}),
    ("new",                    "closed",                 {"role": "supplier", "supplier_id": "supplier_001"}),
    ("new",                    "closed",                 {"role": "admin"}),
    ("approved",               "sample_preparing",       {"role": "supplier", "supplier_id": "supplier_001"}),
    ("approved",               "sample_preparing",       {"role": "admin"}),
    ("sample_preparing",       "prior_notice_pending",   {"role": "supplier", "supplier_id": "supplier_001"}),
    ("prior_notice_pending",   "shipped",                {"role": "supplier", "supplier_id": "supplier_001"}),
    ("shipped",                "delivered",              {"role": "buyer", "buyer_id": "buyer_001"}),
    ("shipped",                "delivered",              {"role": "admin"}),
    ("delivered",              "closed",                 {"role": "buyer", "buyer_id": "buyer_001"}),
    ("delivered",              "closed",                 {"role": "admin"}),
])
def test_valid_transitions(from_status, to_status, user):
    inquiry = base_inquiry(shipment_status=from_status)
    # shipped requires tracking + courier — supply them
    payload: dict = {"shipmentStatus": to_status}
    if to_status == "shipped":
        payload["trackingNumber"] = "TRACK123"
        payload["courier"] = "DHL"
    svc, repo, _ = make_service(inquiry)
    result = svc.update_shipment_status(user, "inq_001", payload)
    assert result["shipment_status"] == to_status


def test_sample_preparing_to_shipped_non_us():
    """Non-US inquiry can jump sample_preparing → shipped directly."""
    inquiry = base_inquiry(shipment_status="sample_preparing", prior_notice_required=False)
    svc, repo, _ = make_service(inquiry)
    result = svc.update_shipment_status(
        {"role": "supplier", "supplier_id": "supplier_001"},
        "inq_001",
        {"shipmentStatus": "shipped", "trackingNumber": "T999", "courier": "FedEx"},
    )
    assert result["shipment_status"] == "shipped"


# ---------------------------------------------------------------------------
# Invalid transitions → 422
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("from_status,to_status", [
    ("new",             "shipped"),
    ("new",             "delivered"),
    ("new",             "sample_preparing"),
    ("approved",        "shipped"),
    ("approved",        "delivered"),
    ("approved",        "closed"),
    ("delivered",       "new"),
    ("closed",          "new"),
    ("shipped",         "approved"),
])
def test_invalid_transitions_return_422(from_status, to_status):
    inquiry = base_inquiry(shipment_status=from_status)
    svc, _, _ = make_service(inquiry)
    with pytest.raises(HTTPException) as exc:
        svc.update_shipment_status(
            {"role": "admin"},
            "inq_001",
            {"shipmentStatus": to_status},
        )
    assert exc.value.status_code == 422
    assert "Invalid transition" in str(exc.value.detail)


# ---------------------------------------------------------------------------
# Role-based transition restrictions → 403
# ---------------------------------------------------------------------------

def test_buyer_cannot_approve_inquiry():
    inquiry = base_inquiry(shipment_status="new", buyer_id="buyer_001")
    svc, _, _ = make_service(inquiry)
    with pytest.raises(HTTPException) as exc:
        svc.update_shipment_status(
            {"role": "buyer", "buyer_id": "buyer_001"},
            "inq_001",
            {"shipmentStatus": "approved"},
        )
    assert exc.value.status_code == 403


def test_supplier_cannot_mark_delivered():
    inquiry = base_inquiry(shipment_status="shipped", supplier_id="supplier_001")
    svc, _, _ = make_service(inquiry)
    with pytest.raises(HTTPException) as exc:
        svc.update_shipment_status(
            {"role": "supplier", "supplier_id": "supplier_001"},
            "inq_001",
            {"shipmentStatus": "delivered"},
        )
    assert exc.value.status_code == 403


# ---------------------------------------------------------------------------
# Ownership violations → 403
# ---------------------------------------------------------------------------

def test_supplier_cannot_update_another_suppliers_inquiry():
    inquiry = base_inquiry(shipment_status="new", supplier_id="supplier_999")
    svc, _, _ = make_service(inquiry)
    with pytest.raises(HTTPException) as exc:
        svc.update_shipment_status(
            {"role": "supplier", "supplier_id": "supplier_001"},
            "inq_001",
            {"shipmentStatus": "approved"},
        )
    assert exc.value.status_code == 403
    assert "your own lots" in str(exc.value.detail)


def test_buyer_cannot_update_another_buyers_inquiry():
    inquiry = base_inquiry(shipment_status="shipped", buyer_id="buyer_999")
    svc, _, _ = make_service(inquiry)
    with pytest.raises(HTTPException) as exc:
        svc.update_shipment_status(
            {"role": "buyer", "buyer_id": "buyer_001"},
            "inq_001",
            {"shipmentStatus": "delivered"},
        )
    assert exc.value.status_code == 403
    assert "your own inquiries" in str(exc.value.detail)


# ---------------------------------------------------------------------------
# Business rules
# ---------------------------------------------------------------------------

def test_shipped_requires_tracking_number_and_courier():
    inquiry = base_inquiry(shipment_status="prior_notice_pending")
    svc, _, _ = make_service(inquiry)
    with pytest.raises(HTTPException) as exc:
        svc.update_shipment_status(
            {"role": "supplier", "supplier_id": "supplier_001"},
            "inq_001",
            {"shipmentStatus": "shipped"},  # missing tracking + courier
        )
    assert exc.value.status_code == 422
    assert "trackingNumber" in str(exc.value.detail)


def test_us_shipment_cannot_skip_prior_notice_pending():
    """US inquiry: sample_preparing → shipped must go through prior_notice_pending."""
    inquiry = base_inquiry(shipment_status="sample_preparing", prior_notice_required=True)
    svc, _, _ = make_service(inquiry)
    with pytest.raises(HTTPException) as exc:
        svc.update_shipment_status(
            {"role": "supplier", "supplier_id": "supplier_001"},
            "inq_001",
            {"shipmentStatus": "shipped", "trackingNumber": "T123", "courier": "DHL"},
        )
    assert exc.value.status_code == 422
    assert "prior_notice_pending" in str(exc.value.detail)


# ---------------------------------------------------------------------------
# deal_closed interaction logged
# ---------------------------------------------------------------------------

def test_closing_inquiry_logs_deal_closed_interaction():
    inquiry = base_inquiry(shipment_status="delivered")
    svc, _, rec_repo = make_service(inquiry)
    svc.update_shipment_status(
        {"role": "buyer", "buyer_id": "buyer_001"},
        "inq_001",
        {"shipmentStatus": "closed"},
    )
    assert any(e["interaction_type"] == "deal_closed" for e in rec_repo.logged)
    closed_entry = next(e for e in rec_repo.logged if e["interaction_type"] == "deal_closed")
    assert closed_entry["buyer_id"] == "buyer_001"
    assert closed_entry["lot_id"] == "lot_001"


def test_non_closing_transition_does_not_log_deal_closed():
    inquiry = base_inquiry(shipment_status="new")
    svc, _, rec_repo = make_service(inquiry)
    svc.update_shipment_status(
        {"role": "supplier", "supplier_id": "supplier_001"},
        "inq_001",
        {"shipmentStatus": "approved"},
    )
    assert not any(e["interaction_type"] == "deal_closed" for e in rec_repo.logged)
