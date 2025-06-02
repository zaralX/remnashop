from aiogram.types import CallbackQuery
from aiogram_dialog.api.protocols import DialogManager, DialogProtocol
from aiogram_dialog.widgets.kbd import Button, Keyboard

from app.core.constants import AUDIT_KEY


class Audit(Keyboard):
    def __init__(self, button: Button):
        super().__init__()
        self.button = button

    async def _render_keyboard(self, data: dict, manager: DialogManager) -> str:
        return await self.button._render_keyboard(data, manager)

    async def process_callback(
        self,
        callback: CallbackQuery,
        dialog: DialogProtocol,
        manager: DialogManager,
    ) -> bool:
        # audit: Audit = manager.middleware_data[AUDIT_KEY] # TODO: Implement audit logging
        return await self.button.process_callback(callback, dialog, manager)
