# Used to create a blank line between elements
msg-space = {"\u00A0"}

# Menu
msg-menu-subscription =
    <b>
    💳 Подписка:
    </b>
    { $status ->
    [active]
    <blockquote>
    • Количество устройств: { $devices } / { $max_devices }
    • Заканчивается через: { $expiry_time }
    </blockquote>
    [expired]
    <blockquote>
    • Срок действия истёк.
    • Чтобы продлить нажмите кнопку "💳 Подписка"
    </blockquote>
    *[none]
    <blockquote>
    • У вас нет подписки
    • Чтобы купить нажмите кнопку "💳 Подписка"
    </blockquote>
}
msg-menu-profile =
    <b>
    👤 Профиль:
    </b>
    <blockquote>
    • ID: { $id }
    • Имя: { $name }
    • Баланс: { $balance }
    </blockquote>


# Dashboard
msg-dashboard = <b>🛠 Панель управления:</b>
msg-dashboard-statistics = <b>📊 Статистика:</b>

msg-dashboard-users = <b>👥 Пользователи:</b>
msg-dashboard-banlist = <b>🚫 Черный список:</b>
msg-dashboard-broadcast = <b>📢 Рассылка:</b>
msg-dashboard-promocodes = <b>🎟 Промокоды:</b>
msg-dashboard-maintenance =
    <b>
    🚧 Режим обслуживания:
    </b>
    <blockquote>
    { $status ->
    [global] 🔴 Включен (глобальный)
    [purchase] 🟠 Включен (платежи)
    *[off] ⚪ Выключен 
    </blockquote>
}
msg-dashboard-remnawave = <b>🌊 RemnaWave:</b>
msg-dashboard-remnashop = <b>🛍 RemnaShop:</b>
