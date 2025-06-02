import logging
from typing import Any, Awaitable, Callable, Optional

from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramNotFound,
)
from aiogram.types import ErrorEvent
from aiogram.types import User as AiogramUser
from aiogram.utils.formatting import Bold, Text
from aiogram_dialog.api.exceptions import UnknownState

from app.core.enums import MiddlewareEventType

from .base import EventTypedMiddleware

logger = logging.getLogger(__name__)


class ErrorMiddleware(EventTypedMiddleware):
    __event_types__ = [MiddlewareEventType.ERROR]

    def __init__(self) -> None:
        logger.debug("Error Middleware initialized")

    async def __call__(
        self,
        handler: Callable[[ErrorEvent, dict[str, Any]], Awaitable[Any]],
        event: ErrorEvent,
        data: dict[str, Any],
    ) -> Any:
        aiogram_user: Optional[AiogramUser] = None

        if event.update.message:
            aiogram_user = event.update.message.from_user
        elif event.update.callback_query:
            aiogram_user = event.update.callback_query.from_user

        if isinstance(event.exception, TelegramForbiddenError):
            logger.info(f"[User:{aiogram_user.id} ({aiogram_user.full_name})] Blocked the bot")
            # TODO: handle user.is_bot_blocked
        elif isinstance(event.exception, TelegramBadRequest):
            logger.warning(f"[User:{aiogram_user.id} ({aiogram_user.full_name})] Bad request")
        elif isinstance(event.exception, TelegramNotFound):
            logger.warning(f"[User:{aiogram_user.id} ({aiogram_user.full_name})] Not found")
        elif isinstance(event.exception, UnknownState):
            logger.warning(f"[User:{aiogram_user.id} ({aiogram_user.full_name})] Unknown state")
        else:
            logger.exception(f"Update: {event.update}\nException: {event.exception}")

        try:
            text = Text(
                Bold((type(event.exception).__name__)), f": {str(event.exception)[:1021]}..."
            )
            # TODO: send error details to developer

        except TelegramBadRequest as exception:
            logger.warning(f"Failed to send error details: {exception}")
        except Exception as exception:
            logger.error(f"Unexpected error in error handler: {exception}")

        return await handler(event, data)
