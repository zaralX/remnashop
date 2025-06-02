from . import dashboard, menu

routers = [
    menu.router,
    menu.dialog,
    dashboard.router,
    dashboard.dialog,
]

__all__ = [
    "routers",
]
