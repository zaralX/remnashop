from typing import Any

from aiogram_dialog import DialogManager
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from remnawave import RemnawaveSDK

from src.core.utils.formatters import (
    i18n_format_expire_time,
    i18n_format_limit,
    i18n_format_traffic_limit,
)
from src.infrastructure.database.models.dto import UserDto
from src.services.plan import PlanService


@inject
async def menu_getter(
    dialog_manager: DialogManager,
    user: UserDto,
    remnawave: FromDishka[RemnawaveSDK],
    plan_service: FromDishka[PlanService],
    **kwargs: Any,
) -> dict[str, Any]:
    if not user.current_subscription:
        return {
            "id": str(user.telegram_id),
            "name": user.name,
            "status": None,
            "is_privileged": user.is_privileged,
        }

    expiry_time = (
        i18n_format_limit(user.current_subscription.plan.duration)
        if user.current_subscription.plan.is_unlimited_duration
        else i18n_format_expire_time(user.current_subscription.expiry_time)
        if user.current_subscription.expiry_time
        else "N/A"
    )

    return {
        "id": str(user.telegram_id),
        "name": user.name,
        "status": user.current_subscription.status,
        "type": user.current_subscription.plan.type,
        "traffic_limit": i18n_format_traffic_limit(user.current_subscription.plan.traffic_limit),
        "device_limit": i18n_format_limit(user.current_subscription.plan.device_limit),
        "expiry_time": expiry_time,
        "is_privileged": user.is_privileged,
    }
