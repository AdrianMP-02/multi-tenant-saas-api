from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.config import settings


ALGORITHM = "RS256"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def create_access_token(subject: str, tenant_id: str | None = None) -> str:
    now = datetime.now(UTC)
    claims: dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "exp": now + settings.access_token_expire_delta,
        "type": "access",
    }
    if tenant_id:
        claims["tenant_id"] = tenant_id
    return jwt.encode(claims, settings.jwt_signing_key, algorithm=ALGORITHM)


def create_refresh_token(subject: str) -> str:
    now = datetime.now(UTC)
    claims: dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "exp": now + settings.refresh_token_expire_delta,
        "type": "refresh",
    }
    return jwt.encode(claims, settings.jwt_signing_key, algorithm=ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.jwt_verification_key, algorithms=[ALGORITHM])
    except JWTError:
        raise ValueError("Invalid or expired token")
