from __future__ import annotations

import logging
import os
import subprocess
from collections.abc import Callable, Mapping


CommandRunner = Callable[..., subprocess.CompletedProcess[str]]


class GitHubSecretCookieStore:
    SECRET_NAME = "NS_COOKIE"

    def __init__(
        self,
        *,
        enabled: bool,
        environ: Mapping[str, str] | None = None,
        runner: CommandRunner = subprocess.run,
    ) -> None:
        self._enabled = enabled
        self._environ = os.environ if environ is None else environ
        self._runner = runner

    def save(self, value: str) -> bool:
        if not self._enabled:
            logging.info("NS_COOKIE secret write-back disabled")
            return False

        token = self._environ.get("NS_COOKIE_WRITE_TOKEN") or self._environ.get("GH_TOKEN")
        repository = self._environ.get("GITHUB_REPOSITORY", "")
        if not token or not repository:
            logging.warning("NS_COOKIE changed, but PAT or repository is missing")
            return False

        try:
            result = self._runner(
                [
                    "gh",
                    "secret",
                    "set",
                    self.SECRET_NAME,
                    "--repo",
                    repository,
                    "--app",
                    "actions",
                ],
                input=value,
                text=True,
                capture_output=True,
                check=False,
                env=self._command_env(token),
            )
        except FileNotFoundError:
            logging.warning("NS_COOKIE secret write-back failed: gh CLI is not installed")
            return False
        except OSError as exc:
            logging.warning("NS_COOKIE secret write-back failed: %s", exc)
            return False

        if result.returncode == 0:
            return True

        message = (result.stderr or result.stdout).strip()
        logging.warning("NS_COOKIE secret write-back failed: %s", message[:200])
        return False

    def _command_env(self, token: str) -> dict[str, str]:
        env = dict(os.environ)
        env.update(dict(self._environ))
        env.pop("NS_COOKIE", None)
        env.pop("NS_COOKIE_WRITE_TOKEN", None)
        env["GH_TOKEN"] = token
        return env
