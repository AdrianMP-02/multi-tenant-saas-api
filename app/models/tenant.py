from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TenantStatus(enum.StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    TRIAL = "trial"


class Tenant(Base):
    __tablename__ = "tenants"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    subdomain: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    schema_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    status: Mapped[TenantStatus] = mapped_column(
        Enum(TenantStatus, name="tenant_status", create_type=False),
        default=TenantStatus.TRIAL,
        nullable=False,
    )
    settings: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    users = relationship(
        "TenantUser", back_populates="tenant", lazy="selectin",
        cascade="all, delete-orphan", passive_deletes=True,
    )
    feature_flags = relationship(
        "TenantFeatureFlag", back_populates="tenant", lazy="selectin",
        cascade="all, delete-orphan", passive_deletes=True,
    )
    subscription = relationship(
        "Subscription", back_populates="tenant", uselist=False, lazy="selectin",
        cascade="all, delete-orphan", passive_deletes=True,
    )
    audit_logs = relationship(
        "AuditLog", back_populates="tenant", lazy="selectin",
        cascade="all, delete-orphan", passive_deletes=True,
    )
