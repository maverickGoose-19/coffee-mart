from __future__ import annotations

from fastapi import HTTPException, Request, Response, status

from .config import ROOT, settings
from .models import (
    BuyerCreateRequest,
    BuyerReviewCreateRequest,
    InquiryCreateRequest,
    InteractionCreateRequest,
    RecommendationSurveyRequest,
    SignInRequest,
    SupplierCreateRequest,
    SupplierReviewCreateRequest,
)
from .repositories.auth import AuthRepository
from .repositories.approvals import ApprovalRepository
from .repositories.inquiries import InquiryRepository
from .repositories.marketplace import MarketplaceRepository
from .repositories.recommendations import RecommendationRepository
from .repositories.reviews import ReviewRepository
from .notifications import EmailNotifier
from .services.approvals import ApprovalService
from .services.auth import AuthService
from .services.bootstrap import BootstrapService
from .services.inquiries import InquiryService
from .services.recommendations import RecommendationService
from .services.reviews import ReviewService


STATIC_DIR = ROOT / "product" / "web-app" / "static"
INDEX_FILE = STATIC_DIR / "index.html"
SPA_ROUTES = {
    "/",
    "/auth",
    "/catalog",
    "/supplier-onboarding",
    "/buyer-preferences",
    "/inquiries",
    "/admin",
}

auth_repository = AuthRepository()
marketplace_repository = MarketplaceRepository()
recommendation_repository = RecommendationRepository()
inquiry_repository = InquiryRepository()
review_repository = ReviewRepository()
approval_repository = ApprovalRepository()
notifier = EmailNotifier()

auth_service = AuthService(auth_repository, marketplace_repository, notifier=notifier)
recommendation_service = RecommendationService(recommendation_repository)
inquiry_service = InquiryService(inquiry_repository, recommendation_repository, notifier=notifier)
review_service = ReviewService(review_repository, marketplace_repository, inquiry_service)
approval_service = ApprovalService(approval_repository, marketplace_repository, notifier=notifier)
bootstrap_service = BootstrapService(
    marketplace_repository,
    recommendation_service,
    inquiry_service,
    review_repository,
    approval_repository,
)


def ensure_demo_data() -> None:
    auth_service.ensure_demo_data()


def current_user_from_request(request: Request):
    token = request.cookies.get(settings.session_cookie)
    return auth_service.current_user_from_token(token)


def current_user_from_token(token: str | None):
    return auth_service.current_user_from_token(token)


def set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.session_cookie,
        value=token,
        httponly=True,
        max_age=settings.session_max_age,
        samesite="lax",
        secure=settings.secure_cookies,
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(
        settings.session_cookie,
        path="/",
        secure=settings.secure_cookies,
        samesite="lax",
    )


def require_role(user: dict | None, role: str) -> dict:
    if not user or user.get("role") != role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"{role.capitalize()} sign-in required",
        )
    return user


def sign_in(payload: SignInRequest) -> tuple[dict, str]:
    return auth_service.sign_in(payload.email, payload.password)


def sign_out(request: Request) -> None:
    auth_service.sign_out(request.cookies.get(settings.session_cookie))


def create_supplier_account(payload: SupplierCreateRequest) -> tuple[dict, str | None]:
    return auth_service.create_supplier_account(payload.model_dump(mode="json"))


def create_buyer_account(payload: BuyerCreateRequest) -> tuple[dict, str | None]:
    return auth_service.create_buyer_account(payload.model_dump(mode="json"))


def submit_supplier_change_request(user: dict | None, payload: SupplierCreateRequest) -> dict:
    return approval_service.submit_supplier_change_request(user, payload.model_dump(mode="json"))


def submit_buyer_change_request(user: dict | None, payload: BuyerCreateRequest) -> dict:
    return approval_service.submit_buyer_change_request(user, payload.model_dump(mode="json"))


def create_interaction(user: dict | None, payload: InteractionCreateRequest) -> dict:
    return recommendation_service.create_interaction(user, payload.model_dump(mode="json"))


def create_inquiry(user: dict | None, payload: InquiryCreateRequest) -> dict:
    return inquiry_service.create_inquiry(user, payload.model_dump(mode="json"))


def has_completed_relationship(buyer_id: str, supplier_id: str) -> bool:
    return inquiry_service.has_completed_relationship(buyer_id, supplier_id)


def save_survey(user: dict | None, payload: RecommendationSurveyRequest) -> dict:
    return recommendation_service.save_survey(user, payload.model_dump(mode="json"))


def create_supplier_review(user: dict | None, payload: SupplierReviewCreateRequest) -> dict:
    return review_service.create_supplier_review(user, payload.model_dump(mode="json"))


def create_buyer_review(user: dict | None, payload: BuyerReviewCreateRequest) -> dict:
    return review_service.create_buyer_review(user, payload.model_dump(mode="json"))


def get_lot_detail(lot_id: str, user: dict | None) -> dict:
    return bootstrap_service.get_lot_detail(lot_id, user)


def bootstrap(user: dict | None) -> dict:
    return bootstrap_service.bootstrap(user)
