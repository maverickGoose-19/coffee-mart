from __future__ import annotations

from product.backend.app.security import hash_password
from product.backend.app.services.auth import AuthService


class FakeAuthRepository:
    def __init__(self):
        password_hash, password_salt = hash_password("DemoBuyer123!")
        self.user = {
            "id": "user_001",
            "email": "buyer.demo@beanai.local",
            "display_name": "Demo Buyer",
            "role": "buyer",
            "buyer_id": "buyer_001",
            "supplier_id": None,
            "password_hash": password_hash,
            "password_salt": password_salt,
        }
        self.last_email = None

    def get_user_by_email(self, email: str):
        self.last_email = email
        return self.user if email == "buyer.demo@beanai.local" else None

    def create_session_for_user(self, user_id: str):
        return "token_001"

    def get_user_by_token(self, token: str):
        return {k: v for k, v in self.user.items() if not k.startswith("password_")}


def test_demo_alias_signin_maps_to_stable_demo_email():
    auth_repo = FakeAuthRepository()
    service = AuthService(auth_repo, marketplace_repo=None)

    user, token = service.sign_in("buyer-demo", "DemoBuyer123!")

    assert auth_repo.last_email == "buyer.demo@beanai.local"
    assert token == "token_001"
    assert user["email"] == "buyer.demo@beanai.local"
