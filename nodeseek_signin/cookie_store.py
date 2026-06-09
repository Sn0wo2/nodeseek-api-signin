from __future__ import annotations

import builtins
import logging
import os
import subprocess
from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import cast


class CookieStore(ABC):
    @abstractmethod
    def save(self, value: str) -> bool: ...


def create_cookie_store(*, store: str, enabled: bool) -> CookieStore | None:
    if not enabled or store == "none":
        return None

    resolved = store
    if store == "auto":
        resolved = "qinglong" if hasattr(builtins, "QLAPI") else "github"

    if resolved == "qinglong":
        return QingLongCookieStore(enabled=enabled)
    return GitHubCookieStore(enabled=enabled)


class GitHubCookieStore(CookieStore):
    SECRET_NAME: str = "NS_COOKIE"

    def __init__(self, *, enabled: bool) -> None:
        self._enabled = enabled

    def save(self, value: str) -> bool:
        if not self._enabled:
            logging.info("NS_COOKIE write-back disabled")
            return False

        token = os.environ.get("NS_COOKIE_WRITE_TOKEN") or os.environ.get("GH_TOKEN")
        repo = os.environ.get("GITHUB_REPOSITORY", "")
        if not token or not repo:
            logging.warning("NS_COOKIE changed, but PAT or repository is missing")
            return False

        env = dict(os.environ)
        env.pop("NS_COOKIE", None)
        env.pop("NS_COOKIE_WRITE_TOKEN", None)
        env["GH_TOKEN"] = token

        try:
            result = subprocess.run(
                ["gh", "secret", "set", self.SECRET_NAME, "--repo", repo, "--app", "actions"],
                input=value,
                text=True,
                capture_output=True,
                check=False,
                env=env,
            )
        except FileNotFoundError:
            logging.warning("NS_COOKIE write-back failed: gh CLI not installed")
            return False
        except OSError as exc:
            logging.warning("NS_COOKIE write-back failed: %s", exc)
            return False

        if result.returncode == 0:
            return True

        logging.warning("NS_COOKIE write-back failed: %s", (result.stderr or result.stdout).strip()[:200])
        return False


class QingLongCookieStore(CookieStore):
    ENV_NAME: str = "NS_COOKIE"

    def __init__(self, *, enabled: bool, api: object | None = None) -> None:
        self._enabled = enabled
        self._api = api if api is not None else getattr(builtins, "QLAPI", None)

    def save(self, value: str) -> bool:
        if not self._enabled:
            logging.info("QingLong NS_COOKIE write-back disabled")
            return False
        if self._api is None:
            logging.warning("QingLong write-back requires QLAPI (run inside QingLong)")
            return False

        env = self._find_env()
        if env is None:
            return False

        payload = {
            "id": env["id"],
            "name": self.ENV_NAME,
            "value": value,
            "remarks": env.get("remarks") or "",
        }
        result = self._api.updateEnv({"env": payload})  # type: ignore[attr-defined]
        if _is_ok(result):
            return True

        logging.warning("QingLong NS_COOKIE update failed: %s", _msg(result))
        return False

    def _find_env(self) -> dict[str, object] | None:
        result = self._api.getEnvs({"searchValue": self.ENV_NAME})  # type: ignore[attr-defined]
        if not _is_ok(result):
            logging.warning("QingLong env query failed: %s", _msg(result))
            return None

        for item in _data_list(result):
            if item.get("name") == self.ENV_NAME and item.get("id") is not None:
                return item

        logging.warning("QingLong env %s not found", self.ENV_NAME)
        return None


def _is_ok(result: object) -> bool:
    d = _as_dict(result)
    return d is not None and d.get("code") == 200


def _data_list(result: object) -> list[dict[str, object]]:
    d = _as_dict(result)
    if d is None:
        return []
    data = d.get("data")
    if not isinstance(data, list):
        return []
    return [item for raw in cast("list[object]", data) if (item := _as_dict(raw)) is not None]


def _msg(result: object) -> str:
    d = _as_dict(result)
    if d is not None:
        m = d.get("message") or d.get("msg")
        if isinstance(m, str) and m:
            return m[:200]
    return str(result)[:200]


def _as_dict(v: object) -> dict[str, object] | None:
    if not isinstance(v, Mapping):
        return None
    return {k: val for k, val in cast("Mapping[object, object]", v).items() if isinstance(k, str)}
