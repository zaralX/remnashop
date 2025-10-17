from datetime import datetime, timedelta
from typing import Optional

from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_dialog import DialogManager, ShowMode, SubManager
from aiogram_dialog.utils import remove_intent_id
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Select
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from loguru import logger

from src.bot.keyboards import goto_buttons
from src.bot.states import DashboardBroadcast
from src.core.constants import USER_KEY
from src.core.enums import BroadcastAudience, MediaType
from src.core.utils.formatters import format_user_log as log
from src.core.utils.message_payload import MessagePayload
from src.core.utils.time import datetime_now
from src.infrastructure.database.models.dto import PlanDto, UserDto
from src.services.notification import NotificationService
from src.services.plan import PlanService
from src.services.subscription import SubscriptionService
from src.services.user import UserService


@inject
async def on_audience_select(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
    user_service: FromDishka[UserService],
    subscription_service: FromDishka[SubscriptionService],
    plan_service: FromDishka[PlanService],
    notification_service: FromDishka[NotificationService],
) -> None:
    user: UserDto = dialog_manager.middleware_data[USER_KEY]

    if not callback.data:
        return

    audience = BroadcastAudience(remove_intent_id(callback.data)[-1])
    dialog_manager.dialog_data["audience_type"] = audience
    logger.info(f"{log(user)} Selected audience '{audience}'")

    if audience == BroadcastAudience.PLAN:
        if not await plan_service.get_all():
            await notification_service.notify_user(
                user=user,
                payload=MessagePayload(i18n_key="ntf-broadcast-plans-not-available"),
            )
            return

        await dialog_manager.switch_to(state=DashboardBroadcast.PLAN)
    else:
        if audience == BroadcastAudience.ALL:
            users = await user_service.get_all()
        elif audience == BroadcastAudience.SUBSCRIBED:
            users = await subscription_service.get_subscribed_users()
        elif audience == BroadcastAudience.UNSUBSCRIBED:
            users = await subscription_service.get_unsubscribed_users()
        elif audience == BroadcastAudience.EXPIRED:
            users = await subscription_service.get_expired_users()
        elif audience == BroadcastAudience.TRIAL:
            users = await subscription_service.get_trial_users()
        else:
            logger.warning(f"Unknown broadcast audience: {audience}")
            users = []

        if not users:
            await notification_service.notify_user(
                user=user,
                payload=MessagePayload(i18n_key="ntf-broadcast-audience-not-available"),
            )
            return

        dialog_manager.dialog_data["audience_count"] = len(users)
        await dialog_manager.switch_to(state=DashboardBroadcast.SEND)


@inject
async def on_plan_select(
    callback: CallbackQuery,
    widget: Select,
    dialog_manager: DialogManager,
    selected_plan_id: int,
    plan_service: FromDishka[PlanService],
) -> None:
    user: UserDto = dialog_manager.middleware_data[USER_KEY]
    plan: Optional[PlanDto] = await plan_service.get(plan_id=selected_plan_id)

    if not plan:
        logger.critical(f"{log(user)} Attempted to select non-existent plan '{selected_plan_id}'")
        return

    logger.info(f"{log(user)} Selected plan ID '{plan.id}'")

    dialog_manager.dialog_data["plan_id"] = plan.id
    await dialog_manager.switch_to(state=DashboardBroadcast.SEND)


@inject
async def on_content_input(
    message: Message,
    widget: MessageInput,
    dialog_manager: DialogManager,
    notification_service: FromDishka[NotificationService],
) -> None:
    dialog_manager.show_mode = ShowMode.EDIT
    user: UserDto = dialog_manager.middleware_data[USER_KEY]
    logger.debug(f"{log(user)} Attempted to set content")

    media_type: Optional[MediaType] = None
    file_id: Optional[str] = None

    if message.photo:
        media_type = MediaType.PHOTO
        file_id = message.photo[-1].file_id
    elif message.video:
        media_type = MediaType.VIDEO
        file_id = message.video.file_id
    elif message.document:
        media_type = MediaType.DOCUMENT
        file_id = message.document.file_id

    if not (message.text or message.caption or file_id):
        logger.warning(f"{log(user)} Provided invalid or empty content")
        await notification_service.notify_user(
            user=user,
            payload=MessagePayload(i18n_key="ntf-broadcast-wrong-content"),
        )
        return

    dialog_manager.dialog_data["content"] = {
        "text": message.text or message.caption,
        "media_type": media_type.value if media_type else None,
        "media_id": file_id,
    }

    logger.info(f"{log(user)} Successfully set broadcast content")
    await notification_service.notify_user(
        user=user,
        payload=MessagePayload(i18n_key="ntf-broadcast-content-saved"),
    )


async def on_button_select(
    callback: CallbackQuery,
    widget: Button,
    sub_manager: SubManager,
) -> None:
    await sub_manager.load_data()
    user: UserDto = sub_manager.middleware_data[USER_KEY]

    selected_id = int(sub_manager.item_id)
    logger.debug(f"{log(user)} Selected button id={selected_id}")

    buttons = sub_manager.manager.dialog_data.get("buttons", [])

    for button in buttons:
        if button["id"] == selected_id:
            button["selected"] = not button.get("selected", False)
            break

    sub_manager.manager.dialog_data["buttons"] = buttons

    logger.debug(f"{log(user)} Updated button states: {buttons}")


@inject
async def on_preview(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
    notification_service: FromDishka[NotificationService],
) -> None:
    user: UserDto = dialog_manager.middleware_data[USER_KEY]

    content: Optional[dict] = dialog_manager.dialog_data.get("content")
    buttons: list = dialog_manager.dialog_data.get("buttons", [])

    if not content:
        await notification_service.notify_user(
            user=user,
            payload=MessagePayload(i18n_key="ntf-broadcast-empty-content"),
        )
        return

    text = content["text"] or ""
    media_type_str = content["media_type"]
    media_id = content["media_id"]
    media_type = MediaType(media_type_str) if media_type_str else None

    builder = InlineKeyboardBuilder()
    for button in buttons:
        if button["selected"]:
            builder.row(goto_buttons[int(button["id"])])

    await notification_service.notify_user(
        user=user,
        payload=MessagePayload(
            i18n_key="ntf-broadcast-preview",
            i18n_kwargs={"content": text},
            media_type=media_type,
            media_id=media_id,
            auto_delete_after=None,
            add_close_button=True,
            reply_markup=builder.as_markup() or None,
        ),
    )


@inject
async def on_send(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
    notification_service: FromDishka[NotificationService],
) -> None:
    user = dialog_manager.middleware_data[USER_KEY]
    content: Optional[dict] = dialog_manager.dialog_data.get("content")
    buttons: list = dialog_manager.dialog_data.get("buttons", [])
    audience_type = dialog_manager.dialog_data.get("audience_type")
    plan_id = dialog_manager.dialog_data.get("plan_id")

    if not content:
        await notification_service.notify_user(
            user=user,
            payload=MessagePayload(i18n_key="ntf-broadcast-empty-content"),
        )
        return

    key = "broadcast_confirm"
    now = datetime_now()
    last_click_str: Optional[str] = dialog_manager.dialog_data.get(key)

    if last_click_str:
        last_click = datetime.fromisoformat(last_click_str.replace("Z", "+00:00"))
        if now - last_click < timedelta(seconds=10):
            # TODO: start broadcast
            dialog_manager.dialog_data.pop(key, None)
            return

    dialog_manager.dialog_data[key] = now.isoformat()
    await notification_service.notify_user(
        user=user,
        payload=MessagePayload(i18n_key="ntf-broadcast-click-for-confirm"),
    )
    logger.debug(f"{log(user)} Awaiting confirmation for broadcast send.")
