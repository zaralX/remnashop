import logging
from typing import Any, Awaitable, Callable, MutableMapping, Optional, Union

from aiogram.dispatcher.flags import get_flag
from aiogram.types import CallbackQuery, Message
from aiogram.types import User as AiogramUser
from cachetools import TTLCache

from app.core.constants import THROTTLING_KEY
from app.core.enums import MiddlewareEventType

from .base import EventTypedMiddleware

logger = logging.getLogger(__name__)

DEFAULT_KEY = "default"
DEFAULT_TTL = 0.5


class ThrottlingMiddleware(EventTypedMiddleware):
    __event_types__ = [MiddlewareEventType.MESSAGE, MiddlewareEventType.CALLBACK_QUERY]

    def __init__(
        self,
        default_key: str = DEFAULT_KEY,
        default_ttl: float = DEFAULT_TTL,
        ttl_map: Optional[dict[str, float]] = None,
    ) -> None:
        ttl_map = ttl_map or {}

        if default_key not in ttl_map:
            ttl_map[default_key] = default_ttl

        self.default_key = default_key
        self.caches: dict[str, MutableMapping[int, None]] = {}

        for name, ttl in ttl_map.items():
            self.caches[name] = TTLCache(maxsize=10_000, ttl=ttl)

        logger.debug("Throttling Middleware initialized")

    async def __call__(
        self,
        handler: Callable[[Union[Message, CallbackQuery], dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: dict[str, Any],
    ) -> Any:
        aiogram_user: Optional[AiogramUser] = None

        if isinstance(event, (CallbackQuery)):
            aiogram_user = event.from_user
        elif isinstance(event, (Message)):
            aiogram_user = event.from_user

        if aiogram_user is None:
            return await handler(event, data)

        key = get_flag(handler=data, name=THROTTLING_KEY, default=self.default_key)
        cache = self.caches.get(key, self.caches[DEFAULT_KEY])

        if aiogram_user.id in cache:
            logger.warning(f"[User:{aiogram_user.id} ({aiogram_user.full_name})] Throttled")
            return None
        else:
            logger.debug(f"[User:{aiogram_user.id} ({aiogram_user.full_name})] Not throttled")

        cache[aiogram_user.id] = None
        return await handler(event, data)
