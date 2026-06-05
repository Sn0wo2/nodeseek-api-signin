from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass

from nodeseek_signin.models import AccountConfig


TRUE_VALUES = frozenset({"1", "true", "yes", "y", "on"})
FALSE_VALUES = frozenset({"0", "false", "no", "n", "off"})


@dataclass(frozen=True, slots=True)
class AppConfig:
    cookie_writeback: bool
    enable_statistics: bool
    proxy_url: str
    random_mode: bool
    timeout: int


class ConfigLoader:
    def __init__(self, environ: Mapping[str, str] | None = None) -> None:
        self._environ = os.environ if environ is None else environ

    def load_app_config(self) -> AppConfig:
        return AppConfig(
            cookie_writeback=self._env_bool(
                "COOKIE_WRITEBACK",
                default=self._environ.get("GITHUB_ACTIONS") == "true",
            ),
            enable_statistics=self._env_bool("ENABLE_STATISTICS", default=True),
            proxy_url=self._environ.get("PROXY_URL", "").strip(),
            random_mode=self._env_bool("NS_RANDOM", default=True),
            timeout=self._env_int("TIMEOUT", default=30, minimum=1),
        )

    def load_accounts(self) -> list[AccountConfig]:
        return [
            AccountConfig(index=index, display_name=f"Account{index}", cookie=cookie)
            for index, cookie in enumerate(self._parse_cookies(), start=1)
        ]

    def _env_bool(self, name: str, *, default: bool) -> bool:
        value = self._environ.get(name)
        if value is None:
            return default

        normalized = value.strip().lower()
        if not normalized:
            return default
        if normalized in TRUE_VALUES:
            return True
        if normalized in FALSE_VALUES:
            return False
        raise ValueError(f"{name} must be a boolean value")

    def _env_int(self, name: str, *, default: int, minimum: int) -> int:
        value = self._environ.get(name)
        if value is None:
            return default

        normalized = value.strip()
        if not normalized:
            return default

        try:
            parsed = int(normalized)
        except ValueError as exc:
            raise ValueError(f"{name} must be an integer") from exc

        if parsed < minimum:
            raise ValueError(f"{name} must be greater than or equal to {minimum}")
        return parsed

    def _parse_cookies(self) -> list[str]:
        raw = self._environ.get("NS_COOKIE", "")
        if not raw:
            return []
        return [cookie.strip() for cookie in raw.split("&") if cookie.strip()]
