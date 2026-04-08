from __future__ import annotations

from fastapi import HTTPException

from ..utils import clean_number, clean_text

# ---------------------------------------------------------------------------
# Shipment state machine
# ---------------------------------------------------------------------------
# Maps (from_status, to_status) → set of roles allowed to make that transition.
_VALID_TRANSITIONS: dict[tuple[str, str], set[str]] = {
    ("new", "approved"):                    {"supplier", "admin"},
    ("new", "closed"):                      {"supplier", "admin"},
    ("approved", "sample_preparing"):       {"supplier", "admin"},
    ("sample_preparing", "prior_notice_pending"): {"supplier", "admin"},
    ("sample_preparing", "shipped"):        {"supplier", "admin"},
    ("prior_notice_pending", "shipped"):    {"supplier", "admin"},
    ("shipped", "delivered"):               {"buyer", "admin"},
    ("delivered", "closed"):               {"buyer", "admin"},
}


class InquiryService:
    def __init__(self, inquiry_repo, recommendation_repo, notifier=None):
        self.inquiry_repo = inquiry_repo
        self.recommendation_repo = recommendation_repo
        self.notifier = notifier

    def create_inquiry(self, user: dict | None, payload: dict) -> dict:
        if not user or user.get("role") != "buyer" or not user.get("buyer_id"):
            raise HTTPException(status_code=403, detail="Buyer sign-in required")
        lot = self.inquiry_repo.get_lot_request_context(payload["lotId"])
        if not lot:
            raise HTTPException(status_code=404, detail="Lot not found")
        if not lot["sample_ready"]:
            raise HTTPException(status_code=400, detail="This lot is not ready for sample requests yet")
        if not lot["export_ready"] or not lot["compliance_ready"]:
            raise HTTPException(status_code=400, detail="This lot is missing export or compliance readiness")
        destination_country = clean_text(payload.get("destinationCountry")) or user.get("destination_country") or "US"
        requested_sample_grams = clean_number(payload.get("requestedSampleGrams")) or lot.get("sample_size_grams")
        source_surface = clean_text(payload.get("sourceSurface")) or "lot_detail"
        buyer_message = clean_text(payload.get("message"))
        prior_notice_required = destination_country == "US"
        prior_notice_filed_by = lot.get("prior_notice_handler") if prior_notice_required else None
        inquiry_id = self.inquiry_repo.create_inquiry(
            buyer_id=user["buyer_id"],
            supplier_id=lot["supplier_id"],
            lot_id=payload["lotId"],
            destination_country=destination_country,
            requested_sample_grams=requested_sample_grams,
            prior_notice_required=prior_notice_required,
            prior_notice_filed_by=prior_notice_filed_by,
            buyer_message=buyer_message,
            source_surface=source_surface,
        )
        self.recommendation_repo.log_buyer_interaction(
            buyer_id=user["buyer_id"],
            lot_id=payload["lotId"],
            interaction_type="inquiry",
            source_surface=source_surface,
        )
        self.recommendation_repo.log_buyer_interaction(
            buyer_id=user["buyer_id"],
            lot_id=payload["lotId"],
            interaction_type="sample_request",
            source_surface=source_surface,
        )
        result = {
            "id": inquiry_id,
            "shipmentStatus": "new",
            "destinationCountry": destination_country,
            "requestedSampleGrams": requested_sample_grams,
            "priorNoticeRequired": prior_notice_required,
            "priorNoticeFiledBy": prior_notice_filed_by,
        }
        if self.notifier:
            self.notifier.notify_new_inquiry(result, user, lot)
        return result

    def has_completed_relationship(self, buyer_id: str, supplier_id: str) -> bool:
        return self.inquiry_repo.has_completed_relationship(buyer_id, supplier_id)

    def update_shipment_status(self, user: dict | None, inquiry_id: str, payload: dict) -> dict:
        # --- Auth: must be signed in ---
        if not user or not user.get("role"):
            raise HTTPException(status_code=401, detail="Authentication required")

        role = user["role"]
        if role not in {"admin", "supplier", "buyer"}:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        # --- Fetch inquiry ---
        inquiry = self.inquiry_repo.get_inquiry_by_id(inquiry_id)
        if not inquiry:
            raise HTTPException(status_code=404, detail="Inquiry not found")

        current_status = inquiry["shipment_status"]
        new_status = payload["shipmentStatus"]

        # --- Ownership checks ---
        if role == "supplier":
            if inquiry.get("supplier_id") != user.get("supplier_id"):
                raise HTTPException(status_code=403, detail="You can only update shipments for your own lots")
        elif role == "buyer":
            if inquiry.get("buyer_id") != user.get("buyer_id"):
                raise HTTPException(status_code=403, detail="You can only update your own inquiries")

        # --- Transition validity ---
        allowed_roles = _VALID_TRANSITIONS.get((current_status, new_status))
        if allowed_roles is None:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid transition: '{current_status}' → '{new_status}' is not allowed",
            )
        if role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Your role '{role}' cannot make the transition '{current_status}' → '{new_status}'",
            )

        # --- Business rules ---
        # tracking_number + courier required when shipping
        if new_status == "shipped":
            if not payload.get("trackingNumber") or not payload.get("courier"):
                raise HTTPException(
                    status_code=422,
                    detail="trackingNumber and courier are required when setting status to 'shipped'",
                )

        # Cannot skip prior_notice_pending for US shipments
        if (
            current_status == "sample_preparing"
            and new_status == "shipped"
            and inquiry.get("prior_notice_required")
        ):
            raise HTTPException(
                status_code=422,
                detail="US shipments require prior_notice_pending before shipped",
            )

        # --- Persist ---
        updated = self.inquiry_repo.update_inquiry_shipment(
            inquiry_id,
            shipment_status=new_status,
            tracking_number=payload.get("trackingNumber"),
            courier=payload.get("courier"),
            prior_notice_filed=payload.get("priorNoticeFiled") or None,
            prior_notice_filed_by=payload.get("priorNoticeFiledBy"),
        )

        # --- Log deal_closed interaction ---
        if new_status == "closed":
            self.recommendation_repo.log_buyer_interaction(
                buyer_id=inquiry["buyer_id"],
                lot_id=inquiry["lot_id"],
                interaction_type="deal_closed",
                source_surface="shipment_update",
            )

        return updated or {}

    def get_inquiries_for_user(self, current_user: dict | None) -> list[dict]:
        if not current_user:
            return []
        if current_user.get("role") == "admin":
            return self.inquiry_repo.get_admin_inquiries()
        if current_user.get("role") == "buyer" and current_user.get("buyer_id"):
            return self.inquiry_repo.get_buyer_inquiries(current_user["buyer_id"])
        if current_user.get("role") == "supplier" and current_user.get("supplier_id"):
            return self.inquiry_repo.get_supplier_inquiries(current_user["supplier_id"])
        return []
