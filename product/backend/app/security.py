from __future__ import annotations

import hashlib
import secrets


def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        310000,
    ).hex()
    return digest, salt


def verify_password(password: str, expected_hash: str, salt: str) -> bool:
    candidate_hash, _ = hash_password(password, salt)
    return secrets.compare_digest(candidate_hash, expected_hash)


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
