from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Optional, Union

from aiogram.types import CallbackQuery, ErrorEvent, Message
from aiogram.types import User as AiogramUser

from app.bot.middlewares import I18nMiddleware
from app.core.config import AppConfig
from app.core.constants import (
    CONFIG_KEY,
    I18N_MIDDLEWARE_KEY,
    SESSION_POOL_KEY,
    USER_KEY,
    USER_SERVICE_KEY,
)
from app.core.enums import MiddlewareEventType
from app.db.services import UserService

from .base import EventTypedMiddleware

if TYPE_CHECKING:
    from app.db.models import User

logger = logging.getLogger(__name__)


class UserMiddleware(EventTypedMiddleware):
    __event_types__ = [
        MiddlewareEventType.MESSAGE,
        MiddlewareEventType.CALLBACK_QUERY,
        MiddlewareEventType.ERROR,
    ]

    def __init__(self) -> None:
        logger.debug("User Middleware initialized")

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery, ErrorEvent],
        data: dict[str, Any],
    ) -> Optional[Any]:
        aiogram_user: Optional[AiogramUser] = None

        if isinstance(event, (CallbackQuery)):
            aiogram_user = event.from_user
        elif isinstance(event, (Message)):
            aiogram_user = event.from_user
        elif isinstance(event, (ErrorEvent)):
            if event.update.callback_query:
                aiogram_user = event.update.callback_query.from_user
            elif event.update.message:
                aiogram_user = event.update.message.from_user

        if aiogram_user is None or aiogram_user.is_bot:
            return await handler(event, data)

        user_service = data[USER_SERVICE_KEY] = UserService(session_pool=data[SESSION_POOL_KEY])
        user: Optional[User] = await user_service.get(telegram_id=aiogram_user.id)

        if user is None:
            i18n: I18nMiddleware = data[I18N_MIDDLEWARE_KEY]
            config: AppConfig = data[CONFIG_KEY]
            is_dev = True if config.bot.dev_id == aiogram_user.id else False
            user = await user_service.create(aiogram_user=aiogram_user, i18n=i18n, is_dev=is_dev)

        if user.is_bot_blocked:
            await user_service.set_bot_blocked(telegram_id=aiogram_user.id, blocked=False)

        data[USER_KEY] = user
        return await handler(event, data)
