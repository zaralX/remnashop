from typing import Final

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.states import Subscription
from src.core.constants import GOTO_PREFIX

CALLBACK_CHANNEL_CONFIRM: Final[str] = "channel_confirm"
CALLBACK_RULES_ACCEPT: Final[str] = "rules_accept"

goto_buttons = [
    InlineKeyboardButton(
        text="btn-goto-subscription",
        callback_data=f"{GOTO_PREFIX}:{Subscription.MAIN.state}",
    ),
    InlineKeyboardButton(
        text="btn-goto-promocode",
        callback_data=f"{GOTO_PREFIX}:{Subscription.PROMOCODE.state}",
    ),
]


def get_channel_keyboard(channel_link: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="btn-channel-join",
            url=channel_link,
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="btn-channel-confirm",
            callback_data=CALLBACK_CHANNEL_CONFIRM,
        ),
    )
    return builder.as_markup()


def get_rules_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="btn-rules-accept",
            callback_data=CALLBACK_RULES_ACCEPT,
        ),
    )
    return builder.as_markup()
