from aiogram_dialog import Dialog, StartMode, Window
from aiogram_dialog.widgets.kbd import Button, Row, Start, SwitchTo

from src.bot.states import (
    Dashboard,
    DashboardAccess,
    DashboardBroadcast,
    DashboardPromocodes,
    DashboardRemnashop,
    DashboardUsers,
    MainMenu,
)
from src.bot.widgets import Banner, I18nFormat, IgnoreUpdate
from src.core.enums import BannerName

from .getters import dashboard_getter
from .remnawave.handlers import start_remnawave_window

dashboard = Window(
    Banner(BannerName.DASHBOARD),
    I18nFormat("msg-dashboard-main"),
    Row(
        SwitchTo(
            text=I18nFormat("btn-dashboard-statistics"),
            id="statistics",
            state=Dashboard.STATISTICS,
        ),
        Start(
            text=I18nFormat("btn-dashboard-users"),
            id="users",
            state=DashboardUsers.MAIN,
            mode=StartMode.RESET_STACK,
        ),
    ),
    Row(
        Start(
            text=I18nFormat("btn-dashboard-broadcast"),
            id="broadcast",
            state=DashboardBroadcast.MAIN,
            mode=StartMode.RESET_STACK,
        ),
        Start(
            text=I18nFormat("btn-dashboard-promocodes"),
            id="promocodes",
            state=DashboardPromocodes.MAIN,
            mode=StartMode.RESET_STACK,
        ),
    ),
    Row(
        Start(
            text=I18nFormat("btn-dashboard-access"),
            id="access",
            state=DashboardAccess.MAIN,
            mode=StartMode.RESET_STACK,
        ),
    ),
    Row(
        Button(
            text=I18nFormat("btn-dashboard-remnawave"),
            id="remnawave",
            on_click=start_remnawave_window,
        ),
        Start(
            text=I18nFormat("btn-dashboard-remnashop"),
            id="remnashop",
            state=DashboardRemnashop.MAIN,
            mode=StartMode.RESET_STACK,
        ),
        when="is_dev",
    ),
    Row(
        Start(
            text=I18nFormat("btn-back-menu"),
            id="back",
            state=MainMenu.MAIN,
            mode=StartMode.RESET_STACK,
        ),
    ),
    IgnoreUpdate(),
    state=Dashboard.MAIN,
    getter=dashboard_getter,
)

statistics = Window(
    Banner(BannerName.DASHBOARD),
    I18nFormat("msg-statistics-main"),
    Row(
        SwitchTo(
            text=I18nFormat("btn-back"),
            id="back",
            state=Dashboard.MAIN,
        ),
    ),
    IgnoreUpdate(),
    state=Dashboard.STATISTICS,
)

router = Dialog(
    dashboard,
    statistics,
)
