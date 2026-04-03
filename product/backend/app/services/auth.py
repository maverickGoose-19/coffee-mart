from __future__ import annotations

from fastapi import HTTPException, status

from ..security import verify_password
from ..utils import clean_text

DEMO_LOGIN_ALIASES = {
    "admin": "admin@beanai.local",
    "buyer-demo": "buyer.demo@beanai.local",
    "supplier-demo": "supplier.demo@beanai.local",
}


class AuthService:
    def __init__(self, auth_repo, marketplace_repo, notifier=None):
        self.auth_repo = auth_repo
        self.marketplace_repo = marketplace_repo
        self.notifier = notifier

    def current_user_from_token(self, token: str | None):
        return self.auth_repo.get_user_by_token(token)

    def sign_in(self, email: str, password: str) -> tuple[dict, str]:
        login = clean_text(email) or ""
        normalized_login = DEMO_LOGIN_ALIASES.get(login.lower(), login)
        user = self.auth_repo.get_user_by_email(normalized_login)
        if not user or not verify_password(password, user["password_hash"], user["password_salt"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        token = self.auth_repo.create_session_for_user(user["id"])
        return self.auth_repo.get_user_by_token(token), token

    def sign_out(self, token: str | None) -> None:
        if token:
            self.auth_repo.delete_session(token)

    def create_supplier_account(self, payload: dict) -> tuple[dict, str | None]:
        password = clean_text(payload.get("password"))
        if password and len(password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
        try:
            if password:
                self.auth_repo.ensure_email_can_create_role(clean_text(payload.get("contactEmail")), "supplier")
            created = self.marketplace_repo.create_supplier(payload)
            token = None
            if password:
                auth_user = self.auth_repo.create_auth_user(
                    email=clean_text(payload["contactEmail"]),
                    password=password,
                    role="supplier",
                    display_name=clean_text(payload.get("contactName")) or created["companyName"],
                    supplier_id=created["id"],
                )
                token = self.auth_repo.create_session_for_user(auth_user["id"])
            if self.notifier:
                self.notifier.notify_new_supplier(created)
            return created, token
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    def create_buyer_account(self, payload: dict) -> tuple[dict, str | None]:
        password = clean_text(payload.get("password"))
        if password and len(password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
        try:
            if password:
                self.auth_repo.ensure_email_can_create_role(clean_text(payload.get("contactEmail")), "buyer")
            created = self.marketplace_repo.create_buyer(payload)
            token = None
            if password:
                auth_user = self.auth_repo.create_auth_user(
                    email=clean_text(payload["contactEmail"]),
                    password=password,
                    role="buyer",
                    display_name=clean_text(payload.get("contactName")) or created["companyName"],
                    buyer_id=created["id"],
                )
                token = self.auth_repo.create_session_for_user(auth_user["id"])
            return created, token
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    def ensure_demo_data(self) -> None:
        self.auth_repo.create_auth_user(
            email="admin@beanai.local",
            password="Admin123!",
            role="admin",
            display_name="Platform Admin",
        )

        suppliers = self.marketplace_repo.list_suppliers_for_demo_auth()
        buyers = self.marketplace_repo.list_buyers_for_demo_auth()

        primary_supplier = next((supplier for supplier in suppliers if supplier["id"] == "supplier_001"), suppliers[0] if suppliers else None)
        primary_buyer = next((buyer for buyer in buyers if buyer["id"] == "buyer_001"), buyers[0] if buyers else None)

        if primary_supplier:
            self.auth_repo.create_auth_user(
                email="supplier.demo@beanai.local",
                password="DemoSupplier123!",
                role="supplier",
                display_name=primary_supplier["contact_name"] or primary_supplier["company_name"],
                supplier_id=primary_supplier["id"],
            )

        if primary_buyer:
            self.auth_repo.create_auth_user(
                email="buyer.demo@beanai.local",
                password="DemoBuyer123!",
                role="buyer",
                display_name=primary_buyer["contact_name"] or primary_buyer["company_name"],
                buyer_id=primary_buyer["id"],
            )

        for supplier in suppliers:
            if not self.auth_repo.find_supplier_auth_user(supplier["id"], supplier["contact_email"]):
                self.auth_repo.create_auth_user(
                    email=supplier["contact_email"],
                    password="DemoSupplier123!",
                    role="supplier",
                    display_name=supplier["contact_name"] or supplier["company_name"],
                    supplier_id=supplier["id"],
                )
        for buyer in buyers:
            if not self.auth_repo.find_buyer_auth_user(buyer["id"], buyer["contact_email"]):
                self.auth_repo.create_auth_user(
                    email=buyer["contact_email"],
                    password="DemoBuyer123!",
                    role="buyer",
                    display_name=buyer["contact_name"] or buyer["company_name"],
                    buyer_id=buyer["id"],
                )
