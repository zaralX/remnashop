from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery
from loguru import logger

from src.core.constants import GOTO_PREFIX
from src.core.utils.formatters import format_user_log as log
from src.infrastructure.database.models.dto import UserDto

router = Router(name=__name__)


@router.callback_query(F.data.startswith(GOTO_PREFIX))
async def on_goto(callback: CallbackQuery, bot: Bot, user: UserDto) -> None:
    logger.info(f"{log(user)} Go to {callback.data}")
