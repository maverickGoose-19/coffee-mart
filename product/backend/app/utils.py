from __future__ import annotations

import re
from uuid import uuid4


def clean_text(value):
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def clean_array(values) -> list[str]:
    if not values:
        return []
    if isinstance(values, str):
        values = values.split(",")
    return [str(value).strip() for value in values if str(value).strip()]


def clean_number(value):
    if value in (None, "", []):
        return None
    return value


def slugify(value: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return base or "entity"


def make_entity_id(prefix: str, primary_value: str) -> str:
    return f"{slugify(primary_value)}_{prefix}_{uuid4().hex[:6]}"


def supplier_payload_to_row(payload: dict) -> dict:
    documentation = payload.get("documentationAvailable", {})
    return {
        "id": payload.get("id") or make_entity_id("sup", payload["companyName"]),
        "company_name": clean_text(payload["companyName"]),
        "contact_name": clean_text(payload.get("contactName")),
        "contact_email": clean_text(payload["contactEmail"]),
        "contact_phone": clean_text(payload.get("contactPhone")),
        "region": clean_text(payload["region"]),
        "website": clean_text(payload.get("website")),
        "altitude_meters": clean_number(payload.get("altitudeMeters")),
        "varietals": clean_array(payload.get("varietals", [])),
        "certifications": clean_array(payload.get("certifications", [])),
        "description": clean_text(payload.get("description")),
        "exports_internationally": payload.get("exportsInternationally", False),
        "export_partner_name": clean_text(payload.get("exportPartnerName")),
        "export_terms": clean_text(payload.get("exportTerms")),
        "min_export_order_kg": clean_number(payload.get("minExportOrderKg")),
        "certificate_of_origin": documentation.get("certificateOfOrigin", False),
        "phytosanitary_certificate": documentation.get("phytosanitaryCertificate", False),
        "invoice_capability": documentation.get("invoiceCapability", False),
        "can_ship_samples": payload.get("canShipSamples", False),
        "sample_size_grams": clean_number(payload.get("sampleSizeGrams")),
        "sample_couriers": clean_array(payload.get("sampleCouriers", [])),
        "sample_shipping_paid_by": clean_text(payload.get("sampleShippingPaidBy")),
        "sample_shipping_days": clean_number(payload.get("sampleShippingDays")),
        "sample_prep_days": clean_number(payload.get("samplePrepDays")),
        "sample_price": clean_number(payload.get("samplePrice")),
        "prior_notice_handler": clean_text(payload.get("priorNoticeHandler")),
        "wants_to_add_images": bool(payload.get("wantsToAddImages", False)),
        "estate_image_url": clean_text(payload.get("estateImageUrl")),
        "coffee_image_url": clean_text(payload.get("coffeeImageUrl")),
        "gallery_image_urls": clean_array(payload.get("galleryImageUrls", [])),
    }


def buyer_payload_to_row(payload: dict) -> dict:
    return {
        "id": payload.get("id") or make_entity_id("buy", payload["companyName"]),
        "company_name": clean_text(payload["companyName"]),
        "contact_name": clean_text(payload.get("contactName")),
        "contact_email": clean_text(payload["contactEmail"]),
        "buyer_type": clean_text(payload["buyerType"]),
        "destination_country": clean_text(payload["destinationCountry"]),
        "preferred_regions": clean_array(payload.get("preferredRegions", [])),
        "preferred_varietals": clean_array(payload.get("preferredVarietals", [])),
        "preferred_processes": clean_array(payload.get("preferredProcesses", [])),
        "target_tasting_notes": clean_array(payload.get("targetTastingNotes", [])),
        "preferred_certifications": clean_array(payload.get("preferredCertifications", [])),
        "min_moq_kg": clean_number(payload.get("minMoqKg")),
        "max_moq_kg": clean_number(payload.get("maxMoqKg")),
        "max_price_per_kg": clean_number(payload.get("maxPricePerKg")),
        "requires_samples": payload.get("requiresSamples", True),
        "preferred_couriers": clean_array(payload.get("preferredCouriers", [])),
        "needs_us_compliance_support": payload.get("needsUsComplianceSupport", False),
    }


def supplier_is_export_ready(row: dict) -> bool:
    return bool(
        row["exports_internationally"]
        and row["export_terms"]
        and row["min_export_order_kg"] is not None
        and row["certificate_of_origin"]
        and row["phytosanitary_certificate"]
        and row["invoice_capability"]
    )


def supplier_is_sample_ready(row: dict) -> bool:
    return bool(
        row["can_ship_samples"]
        and row["sample_size_grams"] is not None
        and row["sample_couriers"]
        and row["sample_shipping_paid_by"]
        and row["sample_shipping_days"] is not None
        and row["sample_prep_days"] is not None
        and row["sample_price"] is not None
    )


def supplier_is_compliance_ready(row: dict) -> bool:
    return bool(row["prior_notice_handler"])
