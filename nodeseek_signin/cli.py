from __future__ import annotations

import logging
import os
import traceback

from nodeseek_signin.app import App


_LOG_LEVELS = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
}


def main() -> int:
    logging.basicConfig(
        level=_log_level(),
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()],
    )
    try:
        return 0 if App().run() > 0 else 1
    except KeyboardInterrupt:
        logging.info("Interrupted")
        return 1
    except Exception as exc:
        logging.error("Fatal: %s", exc)
        logging.debug(traceback.format_exc())
        return 1


def _log_level() -> int:
    value = (os.environ.get("LOG_LEVEL") or "INFO").strip().upper()
    return _LOG_LEVELS.get(value, logging.INFO)
