from __future__ import annotations

import secrets

from ..db import execute, query_all, query_one
from ..security import hash_password, hash_session_token
from ..utils import make_entity_id


class AuthRepository:
    def get_user_by_email(self, email: str) -> dict | None:
        return query_one(
            """
            SELECT
              u.id,
              u.email,
              u.display_name,
              u.role,
              u.password_hash,
              u.password_salt,
              u.supplier_id,
              u.buyer_id,
              s.company_name AS supplier_name,
              b.company_name AS buyer_name,
              b.destination_country,
              b.requires_samples
            FROM app_users u
            LEFT JOIN suppliers s ON s.id = u.supplier_id
            LEFT JOIN buyers b ON b.id = u.buyer_id
            WHERE u.email = %s
              AND u.is_active = TRUE
            """,
            (email,),
        )

    def get_user_by_token(self, token: str | None) -> dict | None:
        if not token:
            return None
        return query_one(
            """
            SELECT
              u.id,
              u.email,
              u.display_name,
              u.role,
              u.supplier_id,
              u.buyer_id,
              s.company_name AS supplier_name,
              b.company_name AS buyer_name,
              b.destination_country,
              b.requires_samples
            FROM app_sessions sess
            JOIN app_users u ON u.id = sess.user_id
            LEFT JOIN suppliers s ON s.id = u.supplier_id
            LEFT JOIN buyers b ON b.id = u.buyer_id
            WHERE sess.token_hash = %s
              AND sess.expires_at > NOW()
              AND u.is_active = TRUE
            """,
            (hash_session_token(token),),
        )

    def ensure_email_can_create_role(self, email: str | None, role: str) -> None:
        if not email:
            return
        existing = query_one("SELECT id, role FROM app_users WHERE email = %s", (email,))
        if existing and existing["role"] != role:
            raise ValueError(
                "This email is already linked to another account. Use a different email or sign in to the existing account."
            )

    def create_auth_user(
        self,
        *,
        email: str,
        password: str,
        role: str,
        display_name: str | None = None,
        supplier_id: str | None = None,
        buyer_id: str | None = None,
    ) -> dict:
        existing = query_one(
            """
            SELECT id, email, role, supplier_id, buyer_id
            FROM app_users
            WHERE email = %s
            """,
            (email,),
        )
        if existing:
            role_conflict = existing["role"] != role
            supplier_conflict = supplier_id and existing.get("supplier_id") and existing["supplier_id"] != supplier_id
            buyer_conflict = buyer_id and existing.get("buyer_id") and existing["buyer_id"] != buyer_id
            if role_conflict or supplier_conflict or buyer_conflict:
                raise ValueError(
                    "This email is already linked to another account. Use a different email or sign in to the existing account."
                )
        password_hash, password_salt = hash_password(password)
        params = {
            "id": existing["id"] if existing else make_entity_id("usr", email),
            "email": email,
            "display_name": display_name,
            "role": role,
            "password_hash": password_hash,
            "password_salt": password_salt,
            "supplier_id": supplier_id,
            "buyer_id": buyer_id,
        }
        execute(
            """
            INSERT INTO app_users (
              id, email, display_name, role, password_hash, password_salt, supplier_id, buyer_id
            ) VALUES (
              %(id)s, %(email)s, %(display_name)s, %(role)s, %(password_hash)s, %(password_salt)s, %(supplier_id)s, %(buyer_id)s
            )
            ON CONFLICT (email) DO UPDATE SET
              display_name = EXCLUDED.display_name,
              role = EXCLUDED.role,
              password_hash = EXCLUDED.password_hash,
              password_salt = EXCLUDED.password_salt,
              supplier_id = COALESCE(EXCLUDED.supplier_id, app_users.supplier_id),
              buyer_id = COALESCE(EXCLUDED.buyer_id, app_users.buyer_id),
              updated_at = NOW()
            """,
            params,
        )
        return query_one(
            """
            SELECT id, email, display_name, role, supplier_id, buyer_id
            FROM app_users
            WHERE email = %s
            """,
            (email,),
        )

    def create_session_for_user(self, user_id: str) -> str:
        token = secrets.token_urlsafe(32)
        execute(
            """
            INSERT INTO app_sessions (id, user_id, token_hash, expires_at)
            VALUES (%s, %s, %s, NOW() + INTERVAL '14 days')
            """,
            (
                make_entity_id("sess", user_id),
                user_id,
                hash_session_token(token),
            ),
        )
        return token

    def delete_session(self, token: str) -> None:
        execute("DELETE FROM app_sessions WHERE token_hash = %s", (hash_session_token(token),))

    def admin_exists(self) -> bool:
        return bool(query_one("SELECT id FROM app_users WHERE role = 'admin' LIMIT 1"))

    def find_supplier_auth_user(self, supplier_id: str, email: str) -> dict | None:
        return query_one(
            "SELECT id FROM app_users WHERE supplier_id = %s OR email = %s LIMIT 1",
            (supplier_id, email),
        )

    def find_buyer_auth_user(self, buyer_id: str, email: str) -> dict | None:
        return query_one(
            "SELECT id FROM app_users WHERE buyer_id = %s OR email = %s LIMIT 1",
            (buyer_id, email),
        )
