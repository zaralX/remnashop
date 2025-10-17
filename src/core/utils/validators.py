from src.core.constants import URL_PATTERN, USERNAME_PATTERN


def _is_valid_url(text: str) -> bool:
    return bool(URL_PATTERN.match(text))


def _is_valid_username(text: str) -> bool:
    return bool(USERNAME_PATTERN.match(text))
