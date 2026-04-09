from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError

from . import db as _db
from .config import settings
from .models import (
    BuyerCreateRequest,
    BuyerReviewCreateRequest,
    InquiryCreateRequest,
    InteractionCreateRequest,
    RecommendationSurveyRequest,
    ShipmentUpdateRequest,
    SignInRequest,
    SupplierCreateRequest,
    SupplierReviewCreateRequest,
)
from .service import (
    INDEX_FILE,
    SPA_ROUTES,
    STATIC_DIR,
    bootstrap,
    clear_session_cookie,
    create_buyer_account,
    create_buyer_review,
    create_inquiry,
    create_interaction,
    update_inquiry_shipment,
    create_supplier_account,
    create_supplier_review,
    current_user_from_request,
    current_user_from_token,
    ensure_demo_data,
    get_lot_detail,
    save_survey,
    set_session_cookie,
    sign_in,
    sign_out,
    submit_buyer_change_request,
    submit_supplier_change_request,
    decide_change_request,
)

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    _db.get_pool()        # open pool eagerly so first request isn't slow
    ensure_demo_data()
    yield
    _db.close_pool()      # clean shutdown


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    root_path=settings.root_path,
    docs_url="/docs" if settings.docs_enabled else None,
    redoc_url="/redoc" if settings.docs_enabled else None,
    openapi_url="/openapi.json" if settings.docs_enabled else None,
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts_list or ["*"])

# CORS — allow Vite/React dev server and any configured origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=512)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(_request: Request, exc: RequestValidationError):
    first_error = exc.errors()[0] if exc.errors() else {}
    message = first_error.get("msg") or "Invalid request"
    return JSONResponse(status_code=422, content={"error": message, "details": exc.errors()})


def current_user(request: Request):
    return current_user_from_request(request)


@app.get("/health")
def health():
    return {"ok": True, "service": settings.app_name, "version": settings.app_version, "env": settings.app_env}


@app.get("/healthz")
def healthz():
    return health()


@app.get("/ready")
def ready():
    db_check = _db.query_one("SELECT 1 AS ok")
    return {
        "ok": True,
        "database": bool(db_check and db_check.get("ok") == 1),
        "alertsConfigured": bool(settings.alert_email_to and (settings.resend_api_key or settings.smtp_host)),
    }


@app.get("/readyz")
def readyz():
    return ready()


@app.get("/api/bootstrap")
def api_bootstrap(user=Depends(current_user)):
    return bootstrap(user)


@app.get("/api/session")
def api_session(user=Depends(current_user)):
    return {"currentUser": user}


@app.post("/api/auth/signin")
def api_signin(payload: SignInRequest, response: Response):
    user, token = sign_in(payload)
    set_session_cookie(response, token)
    return {"currentUser": user}


@app.post("/api/auth/signout")
def api_signout(request: Request, response: Response):
    sign_out(request)
    clear_session_cookie(response)
    return {"ok": True}


@app.post("/api/suppliers", status_code=201)
def api_create_supplier(payload: SupplierCreateRequest, response: Response):
    created, token = create_supplier_account(payload)
    if token:
        set_session_cookie(response, token)
        return {**created, "currentUser": current_user_from_token(token)}
    return created


@app.post("/api/buyers", status_code=201)
def api_create_buyer(payload: BuyerCreateRequest, response: Response):
    created, token = create_buyer_account(payload)
    if token:
        set_session_cookie(response, token)
        return {**created, "currentUser": current_user_from_token(token)}
    return created


@app.post("/api/buyers/update-request", status_code=201)
def api_buyer_update_request(payload: BuyerCreateRequest, user=Depends(current_user)):
    return submit_buyer_change_request(user, payload)


@app.post("/api/interactions", status_code=201)
def api_interactions(payload: InteractionCreateRequest, user=Depends(current_user)):
    return create_interaction(user, payload)


@app.post("/api/suppliers/update-request", status_code=201)
def api_supplier_update_request(payload: SupplierCreateRequest, user=Depends(current_user)):
    return submit_supplier_change_request(user, payload)


@app.patch("/api/profile-change-requests/{request_id}/decision")
def api_decide_change_request(request_id: str, payload: dict, user=Depends(current_user)):
    return decide_change_request(user, request_id, payload.get("decision", ""))


@app.post("/api/inquiries", status_code=201)
def api_inquiries(payload: InquiryCreateRequest, user=Depends(current_user)):
    return create_inquiry(user, payload)


@app.patch("/api/inquiries/{inquiry_id}/shipment")
def api_patch_inquiry_shipment(
    inquiry_id: str,
    payload: ShipmentUpdateRequest,
    user=Depends(current_user),
):
    return update_inquiry_shipment(user, inquiry_id, payload.model_dump(mode="json"))


@app.post("/api/recommendation-survey", status_code=201)
def api_recommendation_survey(payload: RecommendationSurveyRequest, user=Depends(current_user)):
    return save_survey(user, payload)


@app.post("/api/supplier-reviews", status_code=201)
def api_supplier_reviews(payload: SupplierReviewCreateRequest, user=Depends(current_user)):
    return create_supplier_review(user, payload)


@app.post("/api/buyer-reviews", status_code=201)
def api_buyer_reviews(payload: BuyerReviewCreateRequest, user=Depends(current_user)):
    return create_buyer_review(user, payload)


@app.get("/api/lots/{lot_id}")
def api_lot_detail(lot_id: str, user=Depends(current_user)):
    return get_lot_detail(lot_id, user)


@app.get("/{full_path:path}")
def spa(full_path: str):
    path = "/" + full_path
    # Unknown /api/ paths should 404, not silently serve the SPA shell.
    if path.startswith("/api/"):
        raise HTTPException(status_code=404, detail="API route not found")
    return FileResponse(INDEX_FILE)
