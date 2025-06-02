from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Row, Start

from app.bot.conditions import is_admin
from app.bot.states import DashboardState, MenuState
from app.bot.widgets import Audit, Banner, I18nFormat, IgnoreInput
from app.core.enums import BannerName


async def getter(dialog_manager: DialogManager, **kwargs):
    return {
        "status": "active",
        "devices": 1,
        "max_devices": 3,
        "expiry_time": "3 дня",
    }


dialog = Dialog(
    Window(
        Banner(BannerName.MENU),
        I18nFormat("msg-menu-profile"),
        I18nFormat("msg-space"),
        I18nFormat("msg-menu-subscription"),
        Row(Button(I18nFormat("btn-menu-connect"), id="menu.connect")),
        # Row(Button(I18nFormat("btn-menu-trial"), id="menu.trial")),
        Row(
            Button(I18nFormat("btn-menu-balance"), id="menu.balance"),
            Button(I18nFormat("btn-menu-subscription"), id="menu.subscription"),
        ),
        Row(
            Button(I18nFormat("btn-menu-invite"), id="menu.invite"),
            Button(I18nFormat("btn-menu-support"), id="menu.support"),
        ),
        # Row(Button(I18nFormat("btn-menu-promocode"), id="menu.promocode")),
        Row(
            Start(
                I18nFormat("btn-menu-dashboard"),
                id="menu.dashboard",
                state=DashboardState.main,
                when=is_admin,
            )
        ),
        IgnoreInput(),
        state=MenuState.main,
        getter=getter,
    )
)
