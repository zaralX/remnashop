from typing import Any, Union, cast

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode, SubManager
from aiogram_dialog.widgets.kbd import Button, Select
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from loguru import logger

from src.bot.states import DashboardUser, MainMenu
from src.core.config import AppConfig
from src.core.constants import USER_KEY
from src.core.enums import MessageEffect, UserRole
from src.core.utils.formatters import format_user_log as log
from src.core.utils.message_payload import MessagePayload
from src.infrastructure.database.models.dto import UserDto
from src.infrastructure.taskiq.tasks.redirects import redirect_to_main_menu_task
from src.services.notification import NotificationService
from src.services.user import UserService


@inject
async def handle_role_switch_preconditions(
    user: UserDto,
    target_user: UserDto,
    manager: Union[DialogManager, SubManager],
    config: FromDishka[AppConfig],
    notification_service: FromDishka[NotificationService],
    user_service: FromDishka[UserService],
) -> bool:
    if target_user.telegram_id == user.telegram_id:
        logger.info(f"{log(user)} Attempted to switch role to self")
        await notification_service.notify_user(
            user=user,
            payload=MessagePayload(
                i18n_key="ntf-user-switch-role-self",
                message_effect=MessageEffect.POOP,
            ),
        )
        return True

    if target_user.telegram_id == config.bot.dev_id:
        logger.critical(f"{log(user)} Attempted to modify role of SUPER DEV")
        await user_service.set_role(user=user, role=UserRole.USER)
        await user_service.set_block(user=user, blocked=True)
        logger.warning(f"{log(user)} Demoted and blocked")

        await manager.start(state=MainMenu.MAIN, mode=StartMode.RESET_STACK)
        await notification_service.notify_super_dev(
            payload=MessagePayload(
                i18n_key="ntf-user-switch-role-dev",
                auto_delete_after=None,
                add_close_button=True,
                i18n_kwargs={
                    "id": str(user.telegram_id),
                    "name": user.name,
                },
            ),
        )
        return True

    if user.role != UserRole.DEV and user.role <= target_user.role:
        logger.warning(
            f"{log(user)} Attempted to modify role of equal/higher user ({log(target_user)})"
        )
        await notification_service.notify_user(
            user=user,
            payload=MessagePayload(
                i18n_key="ntf-user-switch-role-equal",
            ),
        )
        return True

    return False


async def start_user_window(
    manager: Union[DialogManager, SubManager],
    target_telegram_id: int,
) -> None:
    await manager.start(
        state=DashboardUser.MAIN,
        data={"target_telegram_id": target_telegram_id},
        mode=StartMode.RESET_STACK,
    )


@inject
async def on_block_toggle(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
    config: FromDishka[AppConfig],
    notification_service: FromDishka[NotificationService],
    user_service: FromDishka[UserService],
) -> None:
    start_data = cast(dict[str, Any], dialog_manager.start_data)
    user: UserDto = dialog_manager.middleware_data[USER_KEY]
    target_telegram_id = start_data["target_telegram_id"]
    target_user = await user_service.get(telegram_id=target_telegram_id)

    if not target_user:
        logger.critical(
            f"{log(user)} Attempted to toggle block for non-existent user '{target_telegram_id}'"
        )
        return

    blocked = not target_user.is_blocked

    if target_user.telegram_id == user.telegram_id:
        logger.debug(f"{log(user)} Attempted to block self")
        await notification_service.notify_user(
            user=user,
            payload=MessagePayload(
                i18n_key="ntf-user-block-self",
                message_effect=MessageEffect.POOP,
            ),
        )
        return

    if target_user.telegram_id == config.bot.dev_id:
        logger.critical(f"{log(user)} Attempted to block SUPER DEV")
        await user_service.set_role(user=user, role=UserRole.USER)
        await user_service.set_block(user=user, blocked=True)
        logger.warning(f"{log(user)} Demoted and blocked")

        await dialog_manager.start(state=MainMenu.MAIN, mode=StartMode.RESET_STACK)
        await notification_service.notify_super_dev(
            payload=MessagePayload(
                i18n_key="ntf-user-block-dev",
                i18n_kwargs={
                    "id": str(user.telegram_id),
                    "name": user.name,
                },
            ),
        )
        return

    if user.role <= target_user.role:
        logger.warning(
            f"{log(user)} Attempted to block equal/higher role user ({log(target_user)})"
        )
        await notification_service.notify_user(
            user=user,
            payload=MessagePayload(
                i18n_key="ntf-user-block-equal",
            ),
        )
        return

    await user_service.set_block(user=target_user, blocked=blocked)
    await redirect_to_main_menu_task.kiq(target_user)
    logger.info(
        f"{log(user)} Successfully {'blocked' if blocked else 'unblocked'} {log(target_user)}"
    )


@inject
async def on_role_select(
    callback: CallbackQuery,
    widget: Select[UserRole],
    dialog_manager: DialogManager,
    selected_role: UserRole,
    user_service: FromDishka[UserService],
) -> None:
    start_data = cast(dict[str, Any], dialog_manager.start_data)
    user: UserDto = dialog_manager.middleware_data[USER_KEY]
    target_telegram_id = start_data["target_telegram_id"]
    target_user = await user_service.get(telegram_id=target_telegram_id)

    if not target_user:
        logger.critical(
            f"{log(user)} Attempted to change role for non-existent user '{target_telegram_id}'"
        )
        return

    if await handle_role_switch_preconditions(user, target_user, dialog_manager):
        logger.info(
            f"{log(user)} Role change for {log(target_user)} "
            f"to '{selected_role}' aborted by pre-conditions"
        )
        return

    await user_service.set_role(user=target_user, role=selected_role)
    await redirect_to_main_menu_task.kiq(target_user)
    logger.info(
        f"{log(user)} Successfully changed role for {log(target_user)} to '{selected_role}'"
    )
