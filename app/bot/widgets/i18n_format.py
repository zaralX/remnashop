import re
from re import Match
from typing import Any, Protocol

from aiogram_dialog.api.protocols import DialogManager
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.text import Text

from app.core.constants import I18N_FORMAT_KEY


class Values(Protocol):
    def __getitem__(self, item: Any) -> Any:
        raise NotImplementedError


def collapse_closing_tags(text: str) -> str:
    def replacer(match: Match) -> str:
        tag = match.group(1)
        content = match.group(2).rstrip()
        return f"<{tag}>{content}</{tag}>"

    return re.sub(
        r"<(\w+)>[\n\r]+(.*?)[\n\r]+</\1>",
        replacer,
        text,
        flags=re.DOTALL,
    )


def default_format_text(text: str, data: Values) -> str:
    return text.format_map(data)


class I18nFormat(Text):
    def __init__(self, key: str, when: WhenCondition = None) -> None:
        super().__init__(when)
        self.key = key

    async def _render_text(self, data: dict, manager: DialogManager) -> str:
        format_text = manager.middleware_data.get(
            I18N_FORMAT_KEY,
            default_format_text,
        )
        return collapse_closing_tags(format_text(self.key, data))
