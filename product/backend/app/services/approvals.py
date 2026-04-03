from __future__ import annotations

from fastapi import HTTPException


BUYER_IMMUTABLE_FIELDS = {"companyName", "contactEmail", "buyerType"}
SUPPLIER_IMMUTABLE_FIELDS = {"companyName", "contactEmail", "region"}


class ApprovalService:
    def __init__(self, approval_repo, marketplace_repo, notifier=None):
        self.approval_repo = approval_repo
        self.marketplace_repo = marketplace_repo
        self.notifier = notifier

    def _diff_fields(self, current: dict, requested: dict) -> list[str]:
        changed_fields = []
        for key, value in requested.items():
            current_value = current.get(key)
            if current_value != value:
                changed_fields.append(key)
        return changed_fields

    def submit_buyer_change_request(self, user: dict | None, payload: dict) -> dict:
        if not user or user.get("role") != "buyer" or not user.get("buyer_id"):
            raise HTTPException(status_code=403, detail="Buyer sign-in required")
        current = self.marketplace_repo.get_buyer_profile(user["buyer_id"])
        if not current:
            raise HTTPException(status_code=404, detail="Buyer profile not found")
        requested = {
            "companyName": current["company_name"],
            "contactName": payload.get("contactName"),
            "contactEmail": current["contact_email"],
            "buyerType": current["buyer_type"],
            "destinationCountry": payload.get("destinationCountry"),
            "preferredRegions": payload.get("preferredRegions", []),
            "preferredVarietals": payload.get("preferredVarietals", []),
            "preferredProcesses": payload.get("preferredProcesses", []),
            "targetTastingNotes": payload.get("targetTastingNotes", []),
            "preferredCertifications": payload.get("preferredCertifications", []),
            "minMoqKg": payload.get("minMoqKg"),
            "maxMoqKg": payload.get("maxMoqKg"),
            "maxPricePerKg": payload.get("maxPricePerKg"),
            "requiresSamples": payload.get("requiresSamples"),
            "preferredCouriers": payload.get("preferredCouriers", []),
            "needsUsComplianceSupport": payload.get("needsUsComplianceSupport"),
        }
        if any(payload.get(field) not in (None, current["company_name"] if field == "companyName" else current["contact_email"] if field == "contactEmail" else current["buyer_type"]) for field in BUYER_IMMUTABLE_FIELDS):
            raise HTTPException(status_code=400, detail="Company name, contact email, and buyer type cannot be changed after onboarding.")
        current_normalized = {
            "companyName": current["company_name"],
            "contactName": current.get("contact_name"),
            "contactEmail": current["contact_email"],
            "buyerType": current["buyer_type"],
            "destinationCountry": current.get("destination_country"),
            "preferredRegions": current.get("preferred_regions") or [],
            "preferredVarietals": current.get("preferred_varietals") or [],
            "preferredProcesses": current.get("preferred_processes") or [],
            "targetTastingNotes": current.get("target_tasting_notes") or [],
            "preferredCertifications": current.get("preferred_certifications") or [],
            "minMoqKg": current.get("min_moq_kg"),
            "maxMoqKg": current.get("max_moq_kg"),
            "maxPricePerKg": current.get("max_price_per_kg"),
            "requiresSamples": current.get("requires_samples"),
            "preferredCouriers": current.get("preferred_couriers") or [],
            "needsUsComplianceSupport": current.get("needs_us_compliance_support"),
        }
        changed_fields = self._diff_fields(current_normalized, requested)
        if not changed_fields:
            raise HTTPException(status_code=400, detail="No editable changes detected.")
        request = self.approval_repo.create_profile_change_request(
            entity_type="buyer",
            entity_id=user["buyer_id"],
            requested_by_user_id=user["id"],
            current_snapshot=current_normalized,
            requested_snapshot=requested,
            changed_fields=changed_fields,
        )
        if self.notifier:
            self.notifier.notify_profile_change_request(request)
        return request

    def submit_supplier_change_request(self, user: dict | None, payload: dict) -> dict:
        if not user or user.get("role") != "supplier" or not user.get("supplier_id"):
            raise HTTPException(status_code=403, detail="Supplier sign-in required")
        current = self.marketplace_repo.get_supplier_profile(user["supplier_id"])
        if not current:
            raise HTTPException(status_code=404, detail="Supplier profile not found")
        requested = {
            "companyName": current["company_name"],
            "contactName": payload.get("contactName"),
            "contactEmail": current["contact_email"],
            "contactPhone": payload.get("contactPhone"),
            "region": current["region"],
            "website": payload.get("website"),
            "altitudeMeters": payload.get("altitudeMeters"),
            "varietals": payload.get("varietals", []),
            "certifications": payload.get("certifications", []),
            "description": payload.get("description"),
            "exportsInternationally": payload.get("exportsInternationally"),
            "exportPartnerName": payload.get("exportPartnerName"),
            "exportTerms": payload.get("exportTerms"),
            "minExportOrderKg": payload.get("minExportOrderKg"),
            "documentationAvailable": payload.get("documentationAvailable", {}),
            "canShipSamples": payload.get("canShipSamples"),
            "sampleSizeGrams": payload.get("sampleSizeGrams"),
            "sampleCouriers": payload.get("sampleCouriers", []),
            "sampleShippingPaidBy": payload.get("sampleShippingPaidBy"),
            "sampleShippingDays": payload.get("sampleShippingDays"),
            "samplePrepDays": payload.get("samplePrepDays"),
            "samplePrice": payload.get("samplePrice"),
            "priorNoticeHandler": payload.get("priorNoticeHandler"),
            "wantsToAddImages": payload.get("wantsToAddImages"),
            "estateImageUrl": payload.get("estateImageUrl"),
            "coffeeImageUrl": payload.get("coffeeImageUrl"),
            "galleryImageUrls": payload.get("galleryImageUrls", []),
        }
        if any(payload.get(field) not in (None, current["company_name"] if field == "companyName" else current["contact_email"] if field == "contactEmail" else current["region"]) for field in SUPPLIER_IMMUTABLE_FIELDS):
            raise HTTPException(status_code=400, detail="Company name, contact email, and region cannot be changed after onboarding.")
        current_normalized = {
            "companyName": current["company_name"],
            "contactName": current.get("contact_name"),
            "contactEmail": current["contact_email"],
            "contactPhone": current.get("contact_phone"),
            "region": current["region"],
            "website": current.get("website"),
            "altitudeMeters": current.get("altitude_meters"),
            "varietals": current.get("varietals") or [],
            "certifications": current.get("certifications") or [],
            "description": current.get("description"),
            "exportsInternationally": current.get("exports_internationally"),
            "exportPartnerName": current.get("export_partner_name"),
            "exportTerms": current.get("export_terms"),
            "minExportOrderKg": current.get("min_export_order_kg"),
            "documentationAvailable": {
                "certificateOfOrigin": current.get("certificate_of_origin"),
                "phytosanitaryCertificate": current.get("phytosanitary_certificate"),
                "invoiceCapability": current.get("invoice_capability"),
            },
            "canShipSamples": current.get("can_ship_samples"),
            "sampleSizeGrams": current.get("sample_size_grams"),
            "sampleCouriers": current.get("sample_couriers") or [],
            "sampleShippingPaidBy": current.get("sample_shipping_paid_by"),
            "sampleShippingDays": current.get("sample_shipping_days"),
            "samplePrepDays": current.get("sample_prep_days"),
            "samplePrice": current.get("sample_price"),
            "priorNoticeHandler": current.get("prior_notice_handler"),
            "wantsToAddImages": current.get("wants_to_add_images"),
            "estateImageUrl": current.get("estate_image_url"),
            "coffeeImageUrl": current.get("coffee_image_url"),
            "galleryImageUrls": current.get("gallery_image_urls") or [],
        }
        changed_fields = self._diff_fields(current_normalized, requested)
        if not changed_fields:
            raise HTTPException(status_code=400, detail="No editable changes detected.")
        request = self.approval_repo.create_profile_change_request(
            entity_type="supplier",
            entity_id=user["supplier_id"],
            requested_by_user_id=user["id"],
            current_snapshot=current_normalized,
            requested_snapshot=requested,
            changed_fields=changed_fields,
        )
        if self.notifier:
            self.notifier.notify_profile_change_request(request)
        return request
