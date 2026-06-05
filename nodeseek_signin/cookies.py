from __future__ import annotations

from collections.abc import Iterable, Mapping


CookieUpdates = dict[str, str]


def join_account_cookies(cookies: Iterable[str]) -> str:
    return "&".join(cookie.strip() for cookie in cookies if cookie.strip())


def merge_response_cookies(cookie_header: str, response: object) -> str:
    updates = extract_response_cookies(response)
    if not updates:
        return cookie_header
    return merge_cookie_values(cookie_header, updates)


def merge_cookie_values(cookie_header: str, updates: Mapping[str, str]) -> str:
    existing = _parse_cookie_header(cookie_header)
    seen: set[str] = set()
    merged: list[tuple[str, str]] = []

    for name, value in existing:
        seen.add(name)
        merged.append((name, updates.get(name, value)))

    for name, value in updates.items():
        if name not in seen:
            merged.append((name, value))

    return "; ".join(f"{name}={value}" for name, value in merged)


def extract_response_cookies(response: object) -> CookieUpdates:
    return _extract_cookie_jar(getattr(response, "cookies", None))


def _parse_cookie_header(cookie_header: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for raw_part in cookie_header.split(";"):
        part = raw_part.strip()
        if not part or "=" not in part:
            continue

        name, value = part.split("=", maxsplit=1)
        name = name.strip()
        if name:
            pairs.append((name, value.strip()))
    return pairs


def _extract_cookie_jar(cookies: object) -> CookieUpdates:
    if cookies is None:
        return {}

    get_dict = getattr(cookies, "get_dict", None)
    if callable(get_dict):
        try:
            return _valid_cookie_updates(get_dict().items())
        except (AttributeError, TypeError, ValueError):
            pass

    items = getattr(cookies, "items", None)
    if callable(items):
        try:
            return _valid_cookie_updates(items())
        except (TypeError, ValueError):
            pass

    try:
        return _valid_cookie_updates(
            (getattr(cookie, "name", ""), getattr(cookie, "value", ""))
            for cookie in cookies
        )
    except TypeError:
        return {}


def _valid_cookie_updates(items: Iterable[tuple[object, object]]) -> CookieUpdates:
    updates: CookieUpdates = {}
    for raw_name, raw_value in items:
        name = str(raw_name)
        value = str(raw_value)
        if name and value:
            updates[name] = value
    return updates
