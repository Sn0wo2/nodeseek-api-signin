from __future__ import annotations

import logging
import traceback

from nodeseek_signin.app import App


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
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
