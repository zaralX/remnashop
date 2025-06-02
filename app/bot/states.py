from aiogram.fsm.state import State, StatesGroup


class MenuState(StatesGroup):
    main = State()


class DashboardState(StatesGroup):
    main = State()
    statistics = State()
    users = State()
    broadcast = State()
    promocodes = State()
    banlist = State()
    maintenance = State()

    # remnashop only dev
    remnashop = State()
    admins = State()
    referral = State()
    ads = State()
    plans = State()
    notifications = State()
    logs = State()

    # remnawave only dev
    remnawave = State()
