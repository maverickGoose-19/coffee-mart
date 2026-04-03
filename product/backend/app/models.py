from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class DocumentationAvailable(BaseModel):
    certificateOfOrigin: bool = False
    phytosanitaryCertificate: bool = False
    invoiceCapability: bool = False


class SignInRequest(BaseModel):
    email: str
    password: str


class SupplierCreateRequest(BaseModel):
    id: str | None = None
    companyName: str
    contactName: str | None = None
    contactEmail: str
    contactPhone: str | None = None
    region: str
    website: HttpUrl | None = None
    altitudeMeters: float | None = None
    varietals: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    description: str | None = None
    exportsInternationally: bool = False
    exportPartnerName: str | None = None
    exportTerms: str | None = None
    minExportOrderKg: float | None = None
    documentationAvailable: DocumentationAvailable = Field(default_factory=DocumentationAvailable)
    canShipSamples: bool = False
    sampleSizeGrams: float | None = None
    sampleCouriers: list[str] = Field(default_factory=list)
    sampleShippingPaidBy: str | None = None
    sampleShippingDays: int | None = None
    samplePrepDays: int | None = None
    samplePrice: float | None = None
    priorNoticeHandler: str
    wantsToAddImages: bool = False
    estateImageUrl: str | None = None
    coffeeImageUrl: str | None = None
    galleryImageUrls: list[str] = Field(default_factory=list)
    password: str | None = None


class BuyerCreateRequest(BaseModel):
    id: str | None = None
    companyName: str
    contactName: str | None = None
    contactEmail: str
    buyerType: str
    destinationCountry: str
    preferredRegions: list[str] = Field(default_factory=list)
    preferredVarietals: list[str] = Field(default_factory=list)
    preferredProcesses: list[str] = Field(default_factory=list)
    targetTastingNotes: list[str] = Field(default_factory=list)
    preferredCertifications: list[str] = Field(default_factory=list)
    minMoqKg: float | None = None
    maxMoqKg: float | None = None
    maxPricePerKg: float | None = None
    requiresSamples: bool = True
    preferredCouriers: list[str] = Field(default_factory=list)
    needsUsComplianceSupport: bool = False
    password: str | None = None


class InquiryCreateRequest(BaseModel):
    lotId: str
    destinationCountry: str | None = None
    requestedSampleGrams: float | None = None
    message: str | None = None
    sourceSurface: str | None = None


class InteractionCreateRequest(BaseModel):
    lotId: str
    interactionType: str
    sourceSurface: str | None = None


class RecommendationSurveyRequest(BaseModel):
    preferredRegions: list[str] = Field(default_factory=list)
    preferredVarietals: list[str] = Field(default_factory=list)
    preferredProcesses: list[str] = Field(default_factory=list)
    targetTastingNotes: list[str] = Field(default_factory=list)
    preferredCouriers: list[str] = Field(default_factory=list)
    minMoqKg: float | None = None
    maxMoqKg: float | None = None
    maxPricePerKg: float | None = None


class SupplierReviewCreateRequest(BaseModel):
    supplierId: str
    rating: int = Field(ge=1, le=5)
    reviewText: str | None = None


class BuyerReviewCreateRequest(BaseModel):
    buyerId: str
    rating: int = Field(ge=1, le=5)
    reviewText: str | None = None


class JsonEnvelope(BaseModel):
    data: dict[str, Any]
