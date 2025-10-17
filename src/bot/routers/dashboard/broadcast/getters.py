from typing import Any

from aiogram_dialog import DialogManager
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from src.bot.keyboards import goto_buttons
from src.infrastructure.database.models.dto import PlanDto
from src.services.plan import PlanService


@inject
async def plans_getter(
    dialog_manager: DialogManager,
    plan_service: FromDishka[PlanService],
    **kwargs: Any,
) -> dict[str, Any]:
    plans: list[PlanDto] = await plan_service.get_all()
    formatted_plans = [
        {
            "id": plan.id,
            "name": plan.name,
        }
        for plan in plans
    ]

    return {
        "plans": formatted_plans,
    }


async def send_getter(
    dialog_manager: DialogManager,
    **kwargs: Any,
) -> dict[str, Any]:
    audience = dialog_manager.dialog_data["audience_type"]
    audience_count: int = dialog_manager.dialog_data["audience_count"]

    return {
        "audience_type": audience,
        "audience_count": audience_count,
    }


@inject
async def buttons_getter(
    dialog_manager: DialogManager,
    **kwargs: Any,
) -> dict[str, Any]:
    buttons = dialog_manager.dialog_data.get("buttons", [])

    if not buttons:
        buttons = [
            {
                "id": index,
                "text": goto_button.text,
                "selected": False,
            }
            for index, goto_button in enumerate(goto_buttons)
        ]
        dialog_manager.dialog_data["buttons"] = buttons

    return {
        "buttons": buttons,
    }
