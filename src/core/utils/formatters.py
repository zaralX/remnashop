from __future__ import annotations

import re
from re import Match
from typing import TYPE_CHECKING, Final, Optional, Union

from src.infrastructure.database.models.dto.user import BaseUserDto

if TYPE_CHECKING:
    from src.infrastructure.database.models.dto import UserDto

from calendar import monthrange
from datetime import datetime, timedelta
from decimal import ROUND_HALF_UP, ROUND_UP, Decimal

from src.core.i18n.keys import ByteUnitKey, TimeUnitKey, UtilKey
from src.core.utils.time import datetime_now


def format_user_log(user: Union[BaseUserDto, UserDto]) -> str:
    return f"[{user.role.upper()}:{user.telegram_id} ({user.name})]"


def format_days_to_datetime(value: int, year: int = 2099) -> datetime:
    dt = datetime_now()

    if value == -1:  # UNLIMITED for panel
        try:
            return dt.replace(year=year)
        except ValueError:
            last_day = monthrange(year, dt.month)[1]
            return dt.replace(year=year, day=min(dt.day, last_day))

    return dt + timedelta(days=value)


def format_device_count(value: int) -> int:
    if value == 0:
        return -1  # UNLIMITED for bot

    if value == -1:
        return 0  # UNLIMITED for panel

    return value


def format_gb_to_bytes(value: int, *, binary: bool = True) -> int:
    gb_value = Decimal(value)

    if gb_value == -1:
        return 0  # UNLIMITED for panel

    multiplier = Decimal(1024**3) if binary else Decimal(10**9)
    bytes_value = (gb_value * multiplier).quantize(Decimal("1"), rounding=ROUND_HALF_UP)

    return max(0, int(bytes_value))


def format_bytes_to_gb(value: int, *, binary: bool = True) -> int:
    bytes_value = Decimal(value)

    if bytes_value == 0:
        return -1  # UNLIMITED for bot

    multiplier = Decimal(1024**3) if binary else Decimal(10**9)
    gb_value = (bytes_value / multiplier).quantize(Decimal("1"), rounding=ROUND_HALF_UP)

    return max(0, int(gb_value))


def format_percent(part: int, whole: int) -> str:
    if whole == 0:
        return "N/A"

    percent = (part / whole) * 100
    return f"{percent:.2f}"


def format_country_code(code: str) -> str:
    if not code.isalpha() or len(code) != 2:
        return "🏴‍☠️"

    return "".join(chr(ord("🇦") + ord(c.upper()) - ord("A")) for c in code)


def i18n_format_bytes_to_unit(
    value: Optional[Union[int, float]],
    *,
    round_up: bool = False,
    min_unit: ByteUnitKey = ByteUnitKey.GIGABYTE,
) -> tuple[str, dict[str, float]]:
    if not value or value == 0:
        return UtilKey.UNLIMITED, {}

    bytes_value = Decimal(value)
    units: Final[list[ByteUnitKey]] = list(ByteUnitKey)  # [B, KB, MB, GB]

    for i, unit in enumerate(units):
        if i + 1 < len(units):
            next_unit_threshold = Decimal(1024)
            if bytes_value >= next_unit_threshold:
                bytes_value /= Decimal(1024)
            else:
                break

    if units.index(unit) < units.index(min_unit):
        unit = min_unit
        factor = Decimal(1024) ** (units.index(min_unit))
        bytes_value = Decimal(value) / factor

    rounding = ROUND_UP if round_up else ROUND_HALF_UP
    size_formatted = bytes_value.quantize(Decimal("0.01"), rounding=rounding)

    return unit, {"value": float(size_formatted)}


def i18n_format_seconds(
    value: Union[int, float, str],
) -> list[tuple[str, dict[str, int]]]:
    remaining = int(value)
    parts = []

    if remaining < 60:
        return [(TimeUnitKey.MINUTE, {"value": 0})]

    units: dict[str, int] = {
        TimeUnitKey.DAY: 86400,
        TimeUnitKey.HOUR: 3600,
        TimeUnitKey.MINUTE: 60,
    }

    for unit, unit_seconds in units.items():
        value = remaining // unit_seconds
        if value > 0:
            parts.append((unit, {"value": value}))
            remaining %= unit_seconds

    if not parts:
        return [(TimeUnitKey.MINUTE, {"value": 1})]

    return parts


def i18n_format_days(value: int) -> tuple[str, dict[str, int]]:
    if value == -1:  # UNLIMITED
        return UtilKey.UNLIMITED, {}

    if value % 365 == 0:
        return TimeUnitKey.YEAR, {"value": value // 365}

    if value % 30 == 0:
        return TimeUnitKey.MONTH, {"value": value // 30}

    return TimeUnitKey.DAY, {"value": value}


def i18n_format_limit(value: int) -> tuple[str, dict[str, int]]:
    return UtilKey.UNIT_UNLIMITED, {"value": value}


def i18n_format_traffic_limit(value: int) -> tuple[str, dict[str, int]]:
    if value == -1:
        return UtilKey.UNIT_UNLIMITED, {"value": value}

    return ByteUnitKey.GIGABYTE, {"value": value}


def i18n_format_expire_time(expiry_time: timedelta) -> list[tuple[str, dict[str, int]]]:
    days = expiry_time.days
    seconds = expiry_time.seconds
    parts: list[tuple[str, dict[str, int]]] = []

    # > 1 year
    if days >= 365:
        years, days = divmod(days, 365)
        months, days = divmod(days, 30)
        parts.append((TimeUnitKey.YEAR, {"value": years}))
        if months:
            parts.append((TimeUnitKey.MONTH, {"value": months}))
        if days:
            parts.append((TimeUnitKey.DAY, {"value": days}))
        return parts

    # > 1 month
    if days >= 30:
        months, days = divmod(days, 30)
        hours, seconds = divmod(seconds, 3600)
        parts.append((TimeUnitKey.MONTH, {"value": months}))
        if days:
            parts.append((TimeUnitKey.DAY, {"value": days}))
        if hours:
            parts.append((TimeUnitKey.HOUR, {"value": hours}))
        return parts

    # < 30 days
    hours, seconds = divmod(seconds, 3600)
    minutes, _ = divmod(seconds, 60)
    if days:
        parts.append((TimeUnitKey.DAY, {"value": days}))
    if hours:
        parts.append((TimeUnitKey.HOUR, {"value": hours}))
    if minutes:
        parts.append((TimeUnitKey.MINUTE, {"value": minutes}))

    return parts or [(TimeUnitKey.MINUTE, {"value": 1})]


def i18n_format_collapse_tags(text: str) -> str:
    def replacer(match: Match[str]) -> str:
        tag = match.group(1)
        content = match.group(2).rstrip()
        return f"<{tag}>{content}</{tag}>"

    return re.sub(
        r"<(\w+)>[\n\r]+(.*?)[\n\r]+</\1>",
        replacer,
        text,
        flags=re.DOTALL,
    )
