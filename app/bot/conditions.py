from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.common import Whenable

from app.core.config import AppConfig
from app.core.constants import CONFIG_KEY, USER_KEY
from app.core.enums import UserRole
from app.db.models import User


def is_admin(data: dict, widget: Whenable, manager: DialogManager) -> bool:
    user: User = manager.middleware_data.get(USER_KEY)
    return user.role == UserRole.ADMIN


def is_dev(data: dict, widget: Whenable, manager: DialogManager) -> bool:
    user: User = manager.middleware_data.get(USER_KEY)
    config: AppConfig = manager.middleware_data.get(CONFIG_KEY)
    return user.telegram_id == config.bot.dev_id
