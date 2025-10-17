from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .user import User

from datetime import datetime
from uuid import UUID

from sqlalchemy import JSON, BigInteger, Boolean, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.enums import SubscriptionStatus
from src.infrastructure.database.models.dto import PlanSnapshotDto

from .base import BaseSql
from .timestamp import TimestampMixin


class Subscription(BaseSql, TimestampMixin):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_remna_id: Mapped[UUID] = mapped_column(PG_UUID, nullable=False)

    status: Mapped[SubscriptionStatus] = mapped_column(
        Enum(
            SubscriptionStatus,
            name="subscription_status",
            create_constraint=True,
            validate_strings=True,
        ),
        nullable=False,
    )
    expire_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    url: Mapped[str] = mapped_column(String, nullable=False)
    plan: Mapped[PlanSnapshotDto] = mapped_column(JSON, nullable=False)
    is_trial: Mapped[bool] = mapped_column(Boolean, nullable=False)

    user_telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.telegram_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="subscriptions",
        primaryjoin="Subscription.user_telegram_id==User.telegram_id",
        foreign_keys="Subscription.user_telegram_id",
        lazy="joined",
    )
