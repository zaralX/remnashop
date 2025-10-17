from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode, StartMode
from loguru import logger

from src.bot.keyboards import CALLBACK_CHANNEL_CONFIRM, CALLBACK_RULES_ACCEPT
from src.bot.states import MainMenu
from src.core.utils.formatters import format_user_log as log
from src.infrastructure.database.models.dto import UserDto

router = Router(name=__name__)


async def on_start_dialog(
    user: UserDto,
    dialog_manager: DialogManager,
) -> None:
    logger.info(f"{log(user)} Started dialog")
    await dialog_manager.start(
        state=MainMenu.MAIN,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.DELETE_AND_SEND,
    )


@router.message(CommandStart())
async def on_start_command(
    message: Message,
    user: UserDto,
    dialog_manager: DialogManager,
) -> None:
    await on_start_dialog(user, dialog_manager)


@router.callback_query(F.data == CALLBACK_RULES_ACCEPT)
async def on_rules_accept(
    callback: CallbackQuery,
    user: UserDto,
    dialog_manager: DialogManager,
) -> None:
    logger.info(f"{log(user)} Cccepted rules")
    await on_start_dialog(user, dialog_manager)


@router.callback_query(F.data == CALLBACK_CHANNEL_CONFIRM)
async def on_channel_confirm(
    callback: CallbackQuery,
    user: UserDto,
    dialog_manager: DialogManager,
) -> None:
    logger.info(f"{log(user)} Cofirmed join channel")
    await on_start_dialog(user, dialog_manager)
