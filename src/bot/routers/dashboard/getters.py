from typing import Any

from aiogram_dialog import DialogManager

from src.infrastructure.database.models.dto import UserDto


async def dashboard_getter(
    dialog_manager: DialogManager,
    user: UserDto,
    **kwargs: Any,
) -> dict[str, Any]:
    return {
        "is_dev": user.is_dev,
    }
