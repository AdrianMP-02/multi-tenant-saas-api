from __future__ import annotations

from datetime import timedelta
from typing import ClassVar

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    database_url: str = "postgresql+asyncpg://saas_user:saas_pass@localhost:5432/saas_db"
    private_key: str | None = None
    public_key: str | None = None
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    redis_url: str | None = None
    stripe_secret_key: str | None = None
    stripe_webhook_secret: str | None = None
    environment: str = "development"
    debug: bool = True
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    host: str = "0.0.0.0"
    port: int = 8000
    default_admin_email: str = "admin@saas.local"
    default_admin_password: str = "admin123"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def access_token_expire_delta(self) -> timedelta:
        return timedelta(minutes=self.access_token_expire_minutes)

    @property
    def refresh_token_expire_delta(self) -> timedelta:
        return timedelta(days=self.refresh_token_expire_days)

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def jwt_signing_key(self) -> str:
        if self.private_key:
            return self.private_key
        if self.is_development:
            return _generate_dev_private_key()
        raise RuntimeError(
            "PRIVATE_KEY must be set in production. "
            "Generate a key pair with: python -c \"from app.config import _generate_key_pair; print(_generate_key_pair())\""
        )

    @property
    def jwt_verification_key(self) -> str:
        if self.public_key:
            return self.public_key
        if self.is_development:
            return _generate_dev_public_key()
        raise RuntimeError(
            "PUBLIC_KEY must be set in production."
        )


_dev_private_key: str | None = None
_dev_public_key: str | None = None


def _generate_dev_private_key() -> str:
    global _dev_private_key
    if _dev_private_key is None:
        _generate_key_pair()
    return _dev_private_key


def _generate_dev_public_key() -> str:
    global _dev_public_key
    if _dev_public_key is None:
        _generate_key_pair()
    return _dev_public_key


def _generate_key_pair() -> str:
    global _dev_private_key, _dev_public_key
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    _dev_private_key = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    _dev_public_key = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    return _dev_private_key


settings = Settings()
